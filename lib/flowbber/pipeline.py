# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 KuraLabs S.R.L
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Base class for Flowbber pipeline.
"""

from os import getpid
from pathlib import Path
from collections import OrderedDict
from tempfile import NamedTemporaryFile, gettempdir

from ujson import dumps
from setproctitle import setproctitle

from .logging import get_logger
from .components import CrashError, TimeExceededError
from .loaders import SourcesLoader, AggregatorsLoader, SinksLoader


log = get_logger(__name__)


class Pipeline:
    """
    Pipeline executor class.

    This class will fetch all components from locally declared components and
    entrypoint plugins, create instance of all of them and execute the pipeline
    in order, creating subprocesses when needed.

    Execution of the pipeline is registered in a journal that is returned
    and / or saved when the execution of the pipeline ends.

    :param dict pipeline: A pipeline definition data structure.
    :param str name: Name of the pipeline. Used only for pretty printing only.
    :param str app: Name of the application running the pipeline. This name
     is used mainly to set the process name and the journals directory.
    :param bool save_journal: Save the journal to a temporal location when the
     pipeline execution ends.
    """

    def __init__(self, pipeline, name, app='flowbber', save_journal=True):
        super().__init__()

        self._pipeline = pipeline
        self._name = name
        self._app = app
        self._save_journal = save_journal

        self._executed = 0
        self._data = OrderedDict()

        log.info('Loading plugins ...')
        self._load_plugins()

        log.info('Building pipeline ...')
        self._build_pipeline()

    @property
    def name(self):
        """
        Name of this pipeline.
        """
        return self._name

    @property
    def executed(self):
        """
        Number of times this pipeline has been executed.
        """
        return self._executed

    def __str__(self):
        return '\n'.join([
            '[Pipeline:{}]',
            'executed = {}',
            'sources = {}',
            'aggregators = {}',
            'sinks = {}',
        ]).format(
            self._name,
            self._executed,
            len(self._sources),
            len(self._aggregators),
            len(self._sinks),
        )

    def __repr__(self):
        return str(self)

    def _load_plugins(self):
        """
        Load all plugins available.

        This method will set the following attributes with the loader classes:

        ::

            self._sources_loader
            self._aggregators_loader
            self._sinks_loader

        And also will set the following attributes with the loaded plugin
        classes:

        ::

            self._sources_available
            self._aggregators_available
            self._sinks_available
        """

        for component, loader_clss in (
            ('source', SourcesLoader),
            ('aggregator', AggregatorsLoader),
            ('sink', SinksLoader),
        ):
            loader = loader_clss()
            available = loader.load_plugins()

            setattr(self, '_{}s_loader'.format(component), loader)
            setattr(self, '_{}s_available'.format(component), available)

            log.info('{}s available: {}'.format(
                component.capitalize(),
                list(available.keys()))
            )

    def _build_pipeline(self):
        """
        Create instances of all components as defined in the pipeline
        definition.

        This method will set the following attributes with the list of
        component instances as declared in the pipeline definition:

        ::

            self._sources
            self._aggregators
            self._sinks
        """

        for component_name in ['source', 'aggregator', 'sink']:
            destination = []

            available = getattr(self, '_{}s_available'.format(component_name))
            defined = self._pipeline['{}s'.format(component_name)]

            for index, component in enumerate(defined):
                component_type = component['type']

                if component_type not in available:
                    raise ValueError('Unknown {} {}'.format(
                        component_name, component_type
                    ))

                clss = available[component_type]
                instance = clss(
                    index,
                    component['type'],
                    component['id'],
                    optional=component.get('optional', False),
                    timeout=component.get('timeout', None),
                    config=component.get('config', None),
                )

                destination.append(instance)

                log.info('Created {} instance {}'.format(
                    component_name, instance
                ))

            log.debug('Pipeline {}s created : {}'.format(
                component_name, len(destination)
            ))

            setattr(self, '_{}s'.format(component_name), destination)

    def run(self):
        """
        Execute pipeline.

        This method can be called several times after instantiating the
        pipeline.

        :return: The journal of the execution.
        :rtype: dict
        """
        if self._executed > 0:
            log.info('Re-running pipeline ...')
            self._data = OrderedDict()
        else:
            log.info('Running pipeline ...')

        self._executed += 1

        journal = OrderedDict((
            ('sources', []),
            ('aggregators', []),
            ('sinks', []),
        ))

        setproctitle('{} - running sources'.format(self._app))
        log.info('Running sources ...')
        self._run_sources(journal['sources'])

        setproctitle('{} - running aggregators'.format(self._app))
        log.info('Running aggregators ...')
        self._run_aggregators(journal['aggregators'])

        setproctitle('{} - running sinks'.format(self._app))
        log.info('Running sinks ...')
        self._run_sinks(journal['sinks'])

        if not self._save_journal:
            return journal

        setproctitle('{} - saving journal'.format(self._app))
        log.info('Saving journal ...')
        journal_dir = Path(gettempdir()) / '{}-journals'.format(self._app)
        journal_dir.mkdir(parents=True, exist_ok=True)

        with NamedTemporaryFile(
            mode='wt',
            encoding='utf-8',
            prefix='journal-{}-'.format(getpid()),
            dir=str(journal_dir),
            delete=False
        ) as jfd:
            jfd.write(dumps(journal, indent=4, ensure_ascii=False))
        log.info('Journal saved to {}'.format(jfd.name))

        return journal

    def _run_components(
        self, name, components, journal,
        mutator, provider,
        parallel=True
    ):
        """
        Main function to run a collection of components.

        Components can be run sequentially or in parallel.

        :param str name: Name of the component type to run.
        :param list components: Collection of components.
        :param list journal: Journal to add entries.
        :param function mutator: Function that will grab the context of the
         current execution and return the value to be accumulated between
         joins to the components.
        :param function provider: Function that will grab the context of the
         current execution and return the parameters that must be provided
         to the component being created.
        :param bool parallel: Run in parallel or sequentially.

        :return: The final value set to the accumulator, as returned by the
         mutator function.
        :rtype: Variable, depending on the return value of the mutator.
        """

        # Accumulator for the mutator function
        accumulator = None

        # Execution schedule
        schedule = components

        def start(component):
            """
            Helper to log and start a component.
            """
            log.info(
                'Starting {name} #{component.index} "{component.id}"'.format(
                    name=name,
                    component=component,
                )
            )
            args = provider(accumulator, component)
            component.start(*args)

        # Start components in parallel if requested
        if parallel:

            # Re-order components using timeout in ascending order
            schedule = sorted(components)

            for component in components:
                start(component)

        # Join components according to schedule
        for component in schedule:

            # Start components in series if requested
            if not parallel:
                start(component)

            log.info(
                'Joining {name} #{component.index} "{component.id}"'.format(
                    name=name,
                    component=component
                )
            )

            try:
                execution = component.join()
                accumulator = mutator(
                    accumulator, component, execution.data
                )

                log.info(
                    '{name} #{component.index} "{component.id}" (PID '
                    '{execution.pid}) finished successfully after '
                    '{execution.duration:.4f} seconds'.format(
                        name=name.capitalize(),
                        component=component,
                        execution=execution,
                    )
                )

            except (CrashError, TimeExceededError) as e:
                execution = e.execution

                errmsg = (
                    'Process PID {execution.pid} for {name} '
                    '#{component.index} "{component.id}" {execution.status} '
                    'with exit code {execution.exitcode}'.format(
                        name=name,
                        component=component,
                        execution=execution,
                    )
                )

                if not component.optional:

                    log.fatal(errmsg)
                    log.fatal('Pipeline is shutting down ...')

                    # Pipeline is shuting down. Kill all child processes.
                    # This avoids a deadlock condition were still alive child
                    # processes try to put data to a queue but the master
                    # process is shuting down and blocked at waitpid() call.
                    for component in schedule:
                        try:
                            component.stop()
                        except Exception as e:
                            log.exception(
                                'Component {} crashed when stopping.'.format(
                                    component
                                )
                            )
                            continue
                    raise

                log.warning(errmsg)
                log.warning(
                    '{name} #{component.index} "{component.id}" is marked as '
                    'optional. Keep going...'.format(
                        name=name.capitalize(),
                        component=component,
                    )
                )

            # Add entry to the journal
            journal_entry = {
                'index': component.index,
                'id': component.id,
                name: str(component),
                'pid': execution.pid,
                'status': execution.status,
                'exitcode': execution.exitcode,
                'duration': execution.duration,
            }
            journal.append(journal_entry)

        return accumulator

    def _run_sources(self, journal):
        """
        Run the sources of the pipeline.
        """

        def mutator(accumulator, component, data):
            if accumulator is None:
                accumulator = OrderedDict()
            accumulator[component.id] = data
            return accumulator

        def provider(accumulator, component):
            return ()

        results = self._run_components(
            'source', self._sources, journal,
            mutator, provider,
            parallel=True
        )

        # Re-order data from scheduling
        for source in self._sources:
            if source.id in results:
                self._data[source.id] = results[source.id]

    def _run_aggregators(self, journal):
        """
        Run the aggregators of the pipeline.
        """

        if not self._aggregators:
            return

        def mutator(accumulator, component, data):
            return data

        def provider(accumulator, component):
            if accumulator is None:
                accumulator = self._data
            return (accumulator, )

        self._data = self._run_components(
            'aggregator', self._aggregators, journal,
            mutator, provider,
            parallel=False
        )

    def _run_sinks(self, journal):
        """
        Run the sinks of the pipeline.
        """

        def mutator(accumulator, component, data):
            return None

        def provider(accumulator, component):
            return (self._data, )

        self._run_components(
            'sink', self._sinks, journal,
            mutator, provider,
            parallel=True
        )


__all__ = ['Pipeline']
