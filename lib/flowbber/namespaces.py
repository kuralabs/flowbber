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
Namespaces for variables replacement.
"""

from re import match
from os import environ
from collections import namedtuple


from .schema import SLUG_REGEX
from .logging import get_logger


log = get_logger(__name__)


def namespace_env(path):
    """
    Fetch data from the environment.

    :param Path path: Path to the pipeline definition file.

    :return: A named tuple with information from the environment.
    :rtype: namedtuple
    """

    env_safe = {key for key in environ.keys() if match(SLUG_REGEX, key)}
    env_available = set(environ.keys())
    env_ignored = env_available - env_safe

    if env_ignored:
        log.debug('Environment variables unsafe to load: {}'.format(
            sorted(env_ignored)
        ))

    env_type = namedtuple(
        'env',
        env_safe
    )
    env = env_type(**{key: environ[key] for key in env_safe})

    log.debug('env namespace: {}'.format(env._replace(
        **{key: '****' for key in env_safe}
    )))
    return env


def namespace_pipeline(path):
    """
    Fetch information relative to the pipeline definition file.

    :param Path path: Path to the pipeline definition file.

    :return: A named tuple with information about the pipeline definition file.

     Values available:

     - dir : Parent directory of the definition file.
     - ext : Extension of the definition file.
     - file : Complete filename of the definition file.
     - name : Filename without the extension.

    :rtype: namedtuple
    """

    # Get pipeline object
    pipeline_type = namedtuple(
        'pipeline',
        ['dir', 'ext', 'file', 'name']
    )
    pipeline = pipeline_type(
        dir=str(path.parent),
        ext=path.suffix,
        file=path.name,
        name=path.stem,
    )

    log.debug('pipeline namespace: {}'.format(pipeline))
    return pipeline


def namespace_git(path):
    """
    Fetch information relative to the git vcs versioning the pipeline
    definition file, if any.

    :param Path path: Path to the pipeline definition file.

    :return: A named tuple with information about the git vcs.

     Values available:

     - root : git repository root.
     - branch : current branch.
     - rev : current revision hash.

    :rtype: namedtuple
    """

    from .utils.git import (
        find_root, find_branch, find_revision,
        GitNotFound, GitError,
    )

    parent = str(path.parent)

    # Try to determine git namespace
    try:
        root = find_root(directory=parent)
        branch = find_branch(directory=parent)
        rev = find_revision(directory=parent)
    except GitError as e:
        log.debug(str(e))
        return None
    except GitNotFound as e:
        return None

    # Create git namespace object
    git_type = namedtuple(
        'git',
        ['root', 'branch', 'rev']
    )

    git = git_type(
        root=root,
        branch=branch,
        rev=rev,
    )

    log.debug('git namespace: {}'.format(git))
    return git


def get_namespaces(path):
    """
    Get all replacement namespaces.

    Currently supported namespaces are:

    - env : fetch data from the environment.
    - pipeline : fetch information relative to the pipeline definition file.
    - git : fetch information relative to the git vcs versioning the pipeline
      definition file, if any.

    :param Path path: Path to the pipeline definition file.

    :return: A dictionary mapping the name of the namespace with the class
     implementing it.
    :rtype: dict
    """

    return {
        'env': namespace_env(path),
        'pipeline': namespace_pipeline(path),
        'git': namespace_git(path),
    }


__all__ = ['get_namespaces']
