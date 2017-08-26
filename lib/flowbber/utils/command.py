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
Utilities for calling commands.
"""

from traceback import format_exc
from shlex import split as shsplit
from collections import namedtuple
from subprocess import Popen, PIPE, DEVNULL

from ..logging import get_logger


log = get_logger(__name__)


CommandResult = namedtuple(
    'CommandResult',
    ['stdout', 'stderr', 'returncode']
)


def run(command):
    """
    Execute a command safely and returns its results.

    Returns a namedtuple with the following attributes:

    - ``stdout``: Standard output of the command as UTF-8.
    - ``stderr``: Standard error of the command as UTF-8.
    - ``returncode``: Return code of the command.
    """
    if isinstance(command, str):
        command = shsplit(command)

    try:
        process = Popen(
            command,
            stdin=DEVNULL,
            stderr=PIPE,
            stdout=PIPE,
            env={'LC_ALL': 'C', 'LANG': 'C'}
        )
        stdout, stderr = process.communicate()

    except OSError:  # E.g. command not found
        log.debug(format_exc())
        return None

    return CommandResult(
        stdout=stdout.decode('utf-8').strip(),
        stderr=stderr.decode('utf-8').strip(),
        returncode=process.returncode
    )


__all__ = ['run']
