# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2019 KuraLabs S.R.L
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

from os import getpid

from .pipeline import Pipeline
from .logging import get_logger
from .scheduler import Scheduler
from .inputs import load_pipeline
from .local import load_configuration


log = get_logger(__name__)


def main(args):
    """
    Application main function.

    :param args: An arguments namespace.
    :type args: :py:class:`argparse.Namespace`

    :return: Exit code.
    :rtype: int
    """
    log.info('flowbber PID {} starting ...'.format(
        getpid()
    ))

    # Load user's flowconf.py
    log.info('Loading local configuration from {} ...'.format(
        args.pipeline.parent
    ))
    load_configuration(args.pipeline.parent)

    # Load pipeline
    log.info('Loading pipeline definition from {} ...'.format(
        args.pipeline
    ))
    pipeline_definition = load_pipeline(args.pipeline)

    # Instance pipeline
    log.info('Creating pipeline ...')
    pipeline = Pipeline(pipeline_definition, args.pipeline.stem)

    # Check if scheduling was configured
    schedule = pipeline_definition.get('schedule', None)

    if schedule is None:

        # Everything is ready, do not run if dry run
        if args.dry_run:
            log.info('Dry run complete! Exiting ...')
            return 0

        pipeline.run()
        return 0

    # A scheduler was requested, create it
    log.info('Creating scheduler for pipeline ...')

    scheduler = Scheduler(
        pipeline,
        schedule['frequency'],
        samples=schedule['samples'],
        start=schedule['start'],
        stop_on_failure=schedule['stop_on_failure'],
    )

    # Everything is ready, do not run if dry run
    if args.dry_run:
        log.info('Dry run complete! Exiting ...')
        return 0

    scheduler.run()
    return 0


__all__ = ['main']
