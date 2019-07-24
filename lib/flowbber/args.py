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
Argument management module.
"""

from pathlib import Path
from collections import OrderedDict
from argparse import Action, ArgumentParser

from pprintpp import pformat

from . import __version__
from .utils.types import autocast
from .logging import get_logger, setup_logging


log = get_logger(__name__)


class InvalidArguments(Exception):
    """
    Typed exception that allows to fail in argument parsing and verification
    without quiting the process.
    """
    pass


class ExtendAction(Action):
    """
    Action that allows to combine nargs='+' with the action='append' behavior
    but generating a flat list.

    This allow to specify in a argument parser class an action that allows
    to specify multiple values per argument and multiple arguments.

    Usage::

        parser = ArgumentParser(...)
        parser.register('action', 'extend', ExtendAction)

        parser.add_argument(
            '-o', '--option',
            nargs='+',
            dest='options',
            action='extend',
            help='Some description'
        )

    Then, in CLI::

        executable --option var1=var1 var2=var2 --option var3=var3

    And this generates a::

        Namespace(options=['var1=var1', 'var2=var2', 'var3=var3'])
    """

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest) or []
        items.extend(values)
        setattr(namespace, self.dest, items)


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
        raise InvalidArguments(
            'No such file {}'.format(args.pipeline)
        )

    args.pipeline = args.pipeline.resolve()

    # Check if values are provided
    is_dynamic = args.pipeline.suffix == '.tpl'

    if args.values_files:
        if is_dynamic:

            args.values_files = [
                Path(values_file)
                for values_file in args.values_files
            ]

            missing = [
                values_file
                for values_file in args.values_files
                if not values_file.is_file()
            ]
            if missing:
                raise InvalidArguments(
                    'No such files {}'.format(', '.join(map(str, missing)))
                )

            args.values_files = [
                values_file.resolve()
                for values_file in args.values_files
            ]
        else:
            log.warning(
                'Passing --values-file on a non-dynamic pipeline does nothing'
            )

    if args.values:
        if is_dynamic:
            values = OrderedDict()

            for pair in args.values:

                if '=' not in pair:
                    raise InvalidArguments(
                        'Invalid value "{}"'.format(pair)
                    )

                key, value = pair.split('=', 1)
                values[key] = autocast(value)

            args.values = values
            log.debug('Values given:\n{}'.format(pformat(values)))

        else:
            log.warning(
                'Passing --values on a non-dynamic pipeline does nothing'
            )

    return args


def parse_args(argv=None):
    """
    Argument parsing routine.

    :param argv: A list of argument strings.
    :type argv: list

    :return: A parsed and verified arguments namespace.
    :rtype: :py:class:`argparse.Namespace`
    """

    parser = ArgumentParser(
        description=(
            'Flowbber is a generic tool and framework that allows to execute '
            'custom pipelines for data gathering, publishing and analysis.'
        )
    )
    parser.register('action', 'extend', ExtendAction)

    # Standard options
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

    # Dry run
    parser.add_argument(
        '-d', '--dry-run',
        help='Dry run the pipeline',
        default=False,
        action='store_true'
    )

    # Dynamic pipelines
    parser.add_argument(
        '-a', '--values',
        nargs='+',
        action='extend',
        metavar='KEY=VALUE',
        help='Values to render dynamic pipelines with'
    )
    parser.add_argument(
        '-f', '--values-file',
        dest='values_files',
        action='append',
        metavar='VALUES_FILE',
        help=(
            'One or more paths to files with values to render dynamic '
            'pipelines with. Must be a .toml, .yaml or .json'
        ),
    )

    parser.add_argument(
        'pipeline',
        help='Pipeline definition file'
    )

    args = parser.parse_args(argv)

    try:
        args = validate_args(args)
    except InvalidArguments as e:
        log.critical(e)
        raise e

    return args


__all__ = ['parse_args']
