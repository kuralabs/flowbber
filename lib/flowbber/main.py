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
Application entry point module.
"""

from ujson import loads
from logging import getLogger
from multiprocessing import Process
from collections import OrderedDict

from .loaders import SourcesLoader, SinksLoader


log = getLogger(__name__)


def main(args):
    """
    Application main function.

    :param args: An arguments namespace.
    :type args: :py:class:`argparse.Namespace`

    :return: Exit code.
    :rtype: int
    """
    pipeline = loads(args.pipeline.read_text(encoding='utf-8'))

    sources_loader = SourcesLoader()
    sinks_loader = SinksLoader()

    sources = sources_loader.load_plugins()
    sinks = sinks_loader.load_plugins()

    print(sources)
    data = OrderedDict()

    my_sources = [
        sources[source['type']](
            source['type'], source['key'], source['config']
        )
        for source in pipeline['sources']
    ]

    my_sources_processes = [
        (Process(target=my_source.execute), my_source)
        for my_source in my_sources
    ]

    for my_process, my_source in my_sources_processes:
        my_process.start()

    for my_process, my_source in my_sources_processes:
        result = my_source.result.get()
        data.update(result)

    for my_process, my_source in my_sources_processes:
        my_process.join()
        print('Process {} exited with {}'.format(
            my_process.pid, my_process.exitcode
        ))

    my_sinks = [
        sinks[sink['type']](
            sink['type'], sink['config'], data
        )
        for sink in pipeline['sinks']
    ]
    for my_sink in my_sinks:
        my_sink.distribute()

    return 0


__all__ = ['main']
