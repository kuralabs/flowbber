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
Argument management module.
"""

from pathlib import Path

from . import __version__
from .logging import get_logger, setup_logging


log = get_logger(__name__)


def validate_args(args):
    """
    Validate that arguments are valid.

    :param args: An arguments namespace.
    :type args: :py:class:`argparse.Namespace`

    :return: The validated namespace.
    :rtype: :py:class:`argparse.Namespace`
    """
    setup_logging(args.verbose)
    log.debug('Raw arguments:\n{}'.format(args))

    # Check if pipeline file exists
    args.pipeline = Path(args.pipeline)

    if not args.pipeline.is_file():
        log.error('No such file {}'.format(args.pipeline))
        exit(1)

    args.pipeline = args.pipeline.resolve()

    return args


def parse_args(argv=None):
    """
    Argument parsing routine.

    :param argv: A list of argument strings.
    :type argv: list

    :return: A parsed and verified arguments namespace.
    :rtype: :py:class:`argparse.Namespace`
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description=(
            'Flowbber is a generic tool and framework that allows to execute '
            'custom pipelines for data gathering, publishing and analysis.'
        )
    )
    parser.add_argument(
        '-v', '--verbose',
        help='Increase verbosity level',
        default=0,
        action='count'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='Flowbber v{}'.format(__version__)
    )

    parser.add_argument(
        'pipeline',
        help='Pipeline definition file'
    )

    args = parser.parse_args(argv)
    args = validate_args(args)
    return args


__all__ = ['parse_args']
