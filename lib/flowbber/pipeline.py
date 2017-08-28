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
from multiprocessing import Process
from tempfile import NamedTemporaryFile, gettempdir

from ujson import dumps
from setproctitle import setproctitle

from .logging import get_logger
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
                    component.get('config', {}),
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
            jfd.write(dumps(journal, indent=4))
        log.info('Journal saved to {}'.format(jfd.name))

        return journal

    def _run_sources(self, journal):
        """
        Run the sources of the pipeline.
        """

        sources_processes = [
            (
                index,
                source,
                Process(
                    target=source.execute,
                    name=str(source),
                ),
            )
            for index, source in enumerate(self._sources)
        ]

        for index, source, process in sources_processes:
            log.info(
                'Starting source #{} "{}"'.format(
                    index, source.id
                )
            )
            process.start()

        for index, source, process in sources_processes:
            log.info(
                'Collecting data from source #{} "{}"'.format(
                    index, source.id
                )
            )
            result = source.result.get()
            self._data.update(result)

        for index, source, process in sources_processes:
            process.join()

            journal_entry = {
                'index': index,
                'id': source.id,
                'pid': process.pid,
                'source': str(source),
                'exitcode': process.exitcode,
                'duration': source.duration.get(),
            }
            journal.append(journal_entry)

            log.debug('Process {} exited with {}'.format(
                process.pid, process.exitcode
            ))
            if process.exitcode != 0:
                raise RuntimeError(
                    'Process PID {pid} for source #{index} "{id}" crashed '
                    'with exit code {exitcode}'.format(
                        **journal_entry
                    )
                )

            log.info(
                'Source #{index} "{id}" (PID {pid}) finished collecting data '
                'successfully after {duration:.4f} seconds'.format(
                    **journal_entry
                )
            )

    def _run_aggregators(self, journal):
        """
        Run the aggregators of the pipeline.
        """

        for index, aggregator in enumerate(self._aggregators):

            log.info('Executing data aggregator #{} "{}"'.format(
                index, aggregator.id
            ))
            aggregator.execute(self._data)

            journal_entry = {
                'index': index,
                'id': aggregator.id,
                'aggregator': str(aggregator),
                'duration': aggregator.duration,
            }
            journal.append(journal_entry)

            log.info(
                'Aggregator #{index} "{id}" finished accumulating data '
                'successfully after {duration:.4f} seconds'.format(
                    **journal_entry
                )
            )

    def _run_sinks(self, journal):
        """
        Run the sinks of the pipeline.
        """

        sink_processes = [
            (
                index,
                sink,
                Process(
                    target=sink.execute,
                    args=(self._data, ),
                    name=str(sink),
                ),
            )
            for index, sink in enumerate(self._sinks)
        ]

        for index, sink, process in sink_processes:
            log.info(
                'Executing data sink #{} "{}"'.format(
                    index, sink.id
                )
            )
            process.start()

        for index, sink, process in sink_processes:
            process.join()

            journal_entry = {
                'index': index,
                'id': sink.id,
                'pid': process.pid,
                'sink': str(sink),
                'exitcode': process.exitcode,
                'duration': sink.duration.get(),
            }
            journal.append(journal_entry)

            log.debug('Process {} exited with {}'.format(
                process.pid, process.exitcode
            ))
            if process.exitcode != 0:
                raise RuntimeError(
                    'Process PID {pid} for sink #{index} "{id}" crashed '
                    'with exit code {exitcode}'.format(
                        **journal_entry
                    )
                )

            log.info(
                'Sink #{index} "{id}" (PID {pid}) finished successfully after '
                '{duration:.4f} seconds'.format(
                    **journal_entry
                )
            )


__all__ = ['Pipeline']
