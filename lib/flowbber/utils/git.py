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
Utilities for git repositories.
"""

from re import match
from shutil import which
from collections import OrderedDict

from .command import run
from ..logging import get_logger


log = get_logger(__name__)


class GitError(Exception):
    """
    Typed exception raised when a call to a git executable failed.
    """


class GitNotFound(Exception):
    """
    Typed exception raised when the git executable wasn't found on the system.
    """

    def __init__(self):
        super().__init__('Git executable not found in your system.')


def find_git():
    """
    Find the git executable.

    :return: Absolute path to the git executable.
    :rtype: str
    """
    git = which('git')
    if git is None:
        log.debug('Git executable not found in your system.')
        raise GitNotFound()
    return git


def find_root(git=None, directory='.'):
    """
    Find the root of the git repository.

    :param str git: Path to git executable.
     If None, the default, will try to find it using :func:`find_git`.
    :param str directory: Run as if git was started in ``directory`` instead of
     the current working directory.

    :return: Absolute path to root of the git repository.
    :rtype: str
    """
    if git is None:
        git = find_git()

    call = run([
        git, '-C', directory,
        'rev-parse', '--show-toplevel'
    ])
    if call.returncode != 0:
        raise GitError('Unable to determine git repository root:\n{}'.format(
            call.stderr
        ))

    return call.stdout


def find_branch(git=None, directory='.'):
    """
    Find the current branch of the git repository.

    :param str git: Path to git executable.
     If None, the default, will try to find it using :func:`find_git`.
    :param str directory: Run as if git was started in ``directory`` instead of
     the current working directory.

    :return: The name of the branch the git repository is currently on.
    :rtype: str
    """
    if git is None:
        git = find_git()

    # Get current branch
    call = run([
        git, '-C', directory,
        'rev-parse', '--abbrev-ref', 'HEAD'
    ])
    if call.returncode != 0:
        raise GitError('Unable to determine git branch:\n{}'.format(
            call.stderr
        ))

    return call.stdout


def find_revision(git=None, directory='.'):
    """
    Find the current revision (short hash) of the git repository.

    :param str git: Path to git executable.
     If None, the default, will try to find it using :func:`find_git`.
    :param str directory: Run as if git was started in ``directory`` instead of
     the current working directory.

    :return: The short version of the revision the git repository is currently
     on.
    :rtype: str
    """
    if git is None:
        git = find_git()

    # Get current revision
    call = run([
        git, '-C', directory,
        'rev-parse', '--short', '--verify', 'HEAD'
    ])
    if call.returncode != 0:
        raise GitError('Unable to determine git revision:\n{}'.format(
            call.stderr
        ))

    return call.stdout


class Author:

    def __init__(self, name, email):
        self._name = name
        self._email = email
        self._lines = 0

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    @property
    def lines(self):
        return self._lines

    def __add__(self, other):
        self._lines += other
        return self


class LineOfCode:
    def __init__(self, linenum, code, author, date):
        self._linenum = linenum
        self._code = code
        self._author = author
        self._date = date


class Blame:

    EMAIL_LINE_REGEX = (
        r'^'                            # Regex start
        r'(?P<rev>[0-9A-Fa-f]+)'        # Match revision SHA hexadecimal hash
        r'\s+\(<'                       # Separation, a literal ( and <
        r'(?P<email>.+@.+)'             # Match email
        r'>\s+'                         # A literal >, separation
        r'(?P<timestamp>\d+)'           # Match timestamp
        r'\s+'                          # Separation
        r'(?P<timezone>(-|\+)?\d+)'     # Match timezone
        r'\s+(?P<linenum>\d+)'          # Match line number
        r'\)'                           # A literal )
        r'(?P<code>.*)'                 # Trailing is code line
        r'$'                            # Regex end
    )

    NAME_LINE_REGEX = (
        r'^'                            # Regex start
        r'(?P<rev>[0-9A-Fa-f]+)'        # Match revision SHA hexadecimal hash
        r'\s+\('                        # Separation, a literal (
        r'(?P<name>.+?)'                # Match email
        r'\s+'                          # Separation
        r'(?P<timestamp>\d+)'           # Match timestamp
        r'.+$'                          # Regex end
    )

    def __init__(self, filename, git=None, directory='.'):
        if git is None:
            git = find_git()

        self._filename = filename
        self._git = git
        self._directory = directory

        self._authors = OrderedDict()
        self._raw_blame = []
        self._parse()

    def _git_blame(self, email=True):
        args = [
            self._git, '-C', self._directory, '--no-pager',
            'annotate', '-t', self._filename,
        ]
        if email:
            args.append('-e')

        call = run(args)

        if call.returncode != 0:
            raise GitError('Unable to blame file {}:\n{}'.format(
                self._filename,
                call.stderr
            ))

        return call.stdout

    def _parse(self):
        with_emails = self._git_blame(email=True).split('\n')
        with_names = self._git_blame(email=False).split('\n')

        del self._raw_blame[:]

        for linenum, (email_line, name_line) in enumerate(zip(
            with_emails, with_names
        ), 1):

            email_match = match(Blame.EMAIL_LINE_REGEX, email_line)
            if not email_match:
                raise Exception(email_line)  # FIXME: Type

            name_match = match(Blame.NAME_LINE_REGEX, name_line)
            if not name_match:
                raise Exception(name_line)  # FIXME: Type

            email_group = email_match.groupdict()
            name_group = name_match.groupdict()

            assert int(email_group['linenum']) == linenum
            assert email_group['rev'] == name_group['rev']
            assert email_group['timestamp'] == name_group['timestamp']

            self._raw_blame.append({
                'name': name_group['name'],
                'email': email_group['email'],
                'rev': email_group['rev'],
                'timestamp': int(email_group['timestamp']),
                'timezone': email_group['timezone'],
                'linenum': linenum,
                'code': email_group['code'],
            })


__all__ = [
    'find_git',
    'find_root',
    'find_branch',
    'find_revision',
]
