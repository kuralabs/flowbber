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
from logging import getLogger
from collections import OrderedDict
from multiprocessing import Process
from tempfile import NamedTemporaryFile, gettempdir

from ujson import dumps
from setproctitle import setproctitle

from .loaders import SourcesLoader, AggregatorsLoader, SinksLoader


log = getLogger(__name__)


class Pipeline:
    """
    FIXME: Document.
    """

    def __init__(self, pipeline):
        super().__init__()

        self._pipeline = pipeline
        self._data = OrderedDict()

        log.info('Loading plugins ...')
        self._load_plugins()

        log.info('Building pipeline ...')
        self._build_pipeline()

    def _load_plugins(self):
        """
        FIXME: Document.
        """

        for entity, loader_clss in (
            ('source', SourcesLoader),
            ('aggregator', AggregatorsLoader),
            ('sink', SinksLoader),
        ):
            loader = loader_clss()
            available = loader.load_plugins()

            setattr(self, '_{}s_loader'.format(entity), loader)
            setattr(self, '_{}s_available'.format(entity), available)

            log.info('{}s available: {}'.format(
                entity.capitalize(),
                list(available.keys()))
            )

    def _build_pipeline(self):
        """
        FIXME: Document.
        """

        for entity_name in ['source', 'aggregator', 'sink']:
            destination = []

            available = getattr(self, '_{}s_available'.format(entity_name))
            defined = self._pipeline['{}s'.format(entity_name)]

            for index, entity in enumerate(defined):
                entity_type = entity['type']

                if entity_type not in available:
                    raise ValueError('Unknown {} {}'.format(
                        entity_name, entity_type
                    ))

                clss = available[entity_type]
                instance = clss(
                    index,
                    entity['type'],
                    entity['key'],
                    entity.get('config', {}),
                )

                destination.append(instance)

                log.info('Created {} instance of type {}'.format(
                    entity_name, instance
                ))

            log.debug('Pipeline {}s created : {}'.format(
                entity_name, len(destination)
            ))

            setattr(self, '_{}s'.format(entity_name), destination)

    def run(self):
        """
        FIXME: Document.
        """
        log.info('Running pipeline ...')

        journal = OrderedDict((
            ('sources', []),
            ('aggregators', []),
            ('sinks', []),
        ))

        setproctitle('flowbber - running sources')
        log.info('Running sources ...')
        self._run_sources(journal['sources'])

        setproctitle('flowbber - running aggregators')
        log.info('Running aggregators ...')
        self._run_aggregators(journal['aggregators'])

        setproctitle('flowbber - running sinks')
        log.info('Running sinks ...')
        self._run_sinks(journal['sinks'])

        setproctitle('flowbber - saving journal')
        log.info('Saving journal ...')
        journal_dir = Path(gettempdir()) / 'flowbber-journals'
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

    def _run_sources(self, journal):
        """
        FIXME: Document.
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
                'Starting source #{} of type {}'.format(
                    index, source
                )
            )
            process.start()

        for index, source, process in sources_processes:
            log.info(
                'Collecting {} data from source #{} of type {}'.format(
                    source.key, index, source
                )
            )
            result = source.result.get()
            self._data.update(result)

        for index, source, process in sources_processes:
            process.join()

            journal_entry = {
                'index': index,
                'id': str(source),
                'key': source.key,
                'pid': process.pid,
                'exitcode': process.exitcode,
                'duration': source.duration.get(),
            }
            journal.append(journal_entry)

            log.debug('Process {} exited with {}'.format(
                process.pid, process.exitcode
            ))
            if process.exitcode != 0:
                raise RuntimeError(
                    'Process PID {pid} for source #{index} of type {id} '
                    'crashed with exit code {exitcode}'.format(
                        **journal_entry
                    )
                )

            log.info(
                'Source {id} finished collecting data successfully after '
                '{duration:.4f} seconds'.format(
                    **journal_entry
                )
            )

    def _run_aggregators(self, journal):
        """
        FIXME: Document.
        """

        for index, aggregator in enumerate(self._aggregators):

            log.info('Executing data aggregator #{} of type {}'.format(
                index, aggregator
            ))
            aggregator.accumulate(self._data)

            journal_entry = {
                'index': index,
                'id': str(aggregator),
                'duration': aggregator.duration,
            }
            journal.append(journal_entry)

            log.info(
                'Aggregator {id} finished accumulating data successfully '
                'after {duration:.4f} seconds'.format(
                    **journal_entry
                )
            )

    def _run_sinks(self, journal):
        """
        FIXME: Document.
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
                'Executing data sink #{} of type {}'.format(
                    index, sink
                )
            )
            process.start()

        for index, sink, process in sink_processes:
            process.join()

            journal_entry = {
                'index': index,
                'id': str(sink),
                'pid': process.pid,
                'exitcode': process.exitcode,
                'duration': sink.duration.get(),
            }
            journal.append(journal_entry)

            log.debug('Process {} exited with {}'.format(
                process.pid, process.exitcode
            ))
            if process.exitcode != 0:
                raise RuntimeError(
                    'Process PID {pid} for sink #{index} of type {id} '
                    'crashed with exit code {exitcode}'.format(
                        **journal_entry
                    )
                )

            log.info(
                'Sink {id} finished successfully after '
                '{duration:.4f} seconds'.format(
                    **journal_entry
                )
            )


__all__ = ['Pipeline']
