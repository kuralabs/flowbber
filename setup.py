#!/usr/bin/env python3
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
Usage:

::

    ./setup.py sdist
    ./setup.py bdist_wheel
    ./setup.py bdist_wheel --binary

"""

from os import environ
from setuptools import setup


def check_directory():
    """
    You must always change directory to the parent of this file before
    executing the setup.py script. setuptools will fail reading files,
    including and excluding files from the MANIFEST.in, defining the library
    path, etc, if not.
    """
    from os import getcwd
    from os.path import dirname, abspath
    return getcwd() == abspath(dirname(__file__))


assert check_directory(), 'Call setup.py from its parent directory'


#####################
# Utilities         #
#####################

def read(filename):
    """
    Read the content of a file.

    :param str filename: The file to read.

    :return: The content of the file.
    :rtype: str
    """
    with open(filename, mode='r', encoding='utf-8') as fd:
        return fd.read()


def find_files(search_path, include=('*', ), exclude=('.*', )):
    """
    Find files in a directory.

    :param str search_path: Path to search for files.
    :param tuple include: Patterns of files to include.
    :param tuple exclude: Patterns of files to exclude.

    :return: List of files found that matched the include collection but didn't
     matched the exclude collection.
    :rtype: list
    """
    from os import walk
    from fnmatch import fnmatch
    from os.path import join, normpath

    def included_in(fname, patterns):
        return any(fnmatch(fname, pattern) for pattern in patterns)

    files_collected = []

    for root, folders, files in walk(search_path):
        files_collected.extend(
            normpath(join(root, fname)) for fname in files
            if included_in(fname, include) and not included_in(fname, exclude)
        )

    files_collected.sort()
    return files_collected


#####################
# Finders           #
#####################

def find_version(filename):
    """
    Find version of a package.

    This will read and parse a Python module that has defined a __version__
    variable. This function does not import the file.

    ::

        setup(
            ...
            version=find_version('lib/package/__init__.py'),
            ...
        )

    :param str filename: Path to a Python module with a __version__ variable.

    :return: The version of the package.
    :rtype: str
    """
    import re

    content = read(filename)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M
    )
    if not version_match:
        raise RuntimeError('Unable to find version string.')

    version = version_match.group(1)

    print('Version found:')
    print('  {}'.format(version))
    print('--')

    return version


def find_scripts(search_path):
    """
    Find scripts in a directory.

    ::

        setup(
            ...
            scripts=find_scripts('bin'),
            ...
        )

    :param str search_path: Path to search for scripts.

    :return: Scripts found.
    :rtype: list
    """
    from os import access, X_OK

    files_collected = find_files(search_path)
    scripts = [fname for fname in files_collected if access(fname, X_OK)]

    print('Scripts found:')
    for script in scripts:
        print('  {}'.format(script))
    print('--')

    return scripts


def find_requirements(filename):
    """
    Finds PyPI compatible requirements in a pip requirements.txt file.

    In this way requirements needs to be specified only in one, centralized
    place:

    ::

        setup(
            ...
            install_requires=find_requirements('requirements.txt'),
            ...
        )

    Supports comments and non PyPI requirements (which are ignored).

    :param str filename: Path to a requirements.txt file.

    :return: List of requirements with version.
    :rtype: list
    """
    import string

    content = read(filename)
    requirements = []
    ignored = []

    for line in content.splitlines():
        line = line.strip()

        # Comments
        if line.startswith('#') or not line:
            continue

        if line[:1] not in string.ascii_letters:
            ignored.append(line)
            continue

        requirements.append(line)

    print('Requirements found:')
    for requirement in requirements:
        print('  {}'.format(requirement))
    print('--')

    print('Requirements ignored:')
    for requirement in ignored:
        print('  {}'.format(requirement))
    print('--')

    return requirements


def find_data(package_path, data_path, **kwargs):
    """
    Find data files in a package.

    ::

        setup(
            ...
            package_data={
                'package': find_data(
                    'lib/package',
                    'data',
                )
            },
            ...
        )

    :param str package_path: Path to the root of the package.
    :param str data_path: Relative path from the root of the package to the
     data directory.
    :param kwargs: Function supports inclusion and exclusion patterns as
     specified in the find_files function.

    :return: List of data files found.
    :rtype: list
    """
    from os.path import join, relpath

    files_collected = find_files(join(package_path, data_path), **kwargs)
    data_files = [relpath(fname, package_path) for fname in files_collected]

    print('Data files found:')
    for data_file in data_files:
        print('  {}'.format(data_file))
    print('--')

    return data_files


def find_packages(lib_directory):
    """
    Determine packaging options depending on the packaging mode and flags.

    Supports:

    - Source distribution.
    - Pure Python wheels.
    - Cythonized binary wheels.

    ::

        setup(
            ...
            **find_packages('lib')
        )

    :param str lib_directory: Path to the location of the packages.

    :return: A dictionary with options for the setup() call depending on
     calling parameters.
    :rtype: dict
    """
    from sys import argv
    from os.path import join

    if 'bdist_wheel' in argv and '--binary' in argv:

        argv.remove('--binary')

        from Cython.Build import cythonize

        packaging = {
            'ext_modules': cythonize(
                join(lib_directory, '**/*.py')
            ),
        }

        print('Extension modules found:')
        for ext_module in packaging['ext_modules']:
            print('  {}'.format(ext_module.name))
        print('--')

    else:

        from setuptools import find_packages as find_source_packages

        packaging = {
            'package_dir': {'': lib_directory},
            'packages': find_source_packages(lib_directory),
        }

        print('Packages found (under {}):'.format(lib_directory))
        for package in sorted(packaging['packages']):
            print('  {}'.format(package))
        print('--')

    return packaging


setup(
    name='flowbber',
    version=find_version('lib/flowbber/__init__.py'),

    # Scripts
    scripts=find_scripts('bin'),

    # Dependencies
    install_requires=find_requirements('requirements.txt'),

    # Data files
    package_data={
        'flowbber': find_data(
            'lib/flowbber',
            'data',
        )
    },

    # Metadata
    author='KuraLabs S.R.L',
    author_email='info@kuralabs.io',
    description=(
        'Flowbber is a generic tool and framework that allows to execute '
        'custom pipelines for data gathering, publishing and analysis.'
    ),
    long_description=read('README.rst'),
    url='https://flowbber.readthedocs.io',
    keywords='flowbber',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
    ],

    # Sphinx autodoc cannot extract the documentation of zipped eggs with the
    # ``.. autodata::`` directive, causing chaos in AutoAPI. This disables zip
    # installation for correct AutoAPI generation.
    zip_safe='READTHEDOCS' not in environ,

    # Entry points
    entry_points={
        'flowbber_plugin_sources_1_0': [
            'user = flowbber.plugins.sources.user:UserSource',
            'timestamp = flowbber.plugins.sources.timestamp:TimestampSource',
        ],
        'flowbber_plugin_aggregators_1_0': [],
        'flowbber_plugin_sinks_1_0': [
            'pprintpp = flowbber.plugins.sinks.pprintpp:PPrintPPSink',
            'archive = flowbber.plugins.sinks.archive:ArchiveSink',
            'template = flowbber.plugins.sinks.template:TemplateSink',
            'mongo = flowbber.plugins.sinks.mongodb:MongoDBSink',
        ]
    },

    # Multiple packaging options
    **find_packages('lib')
)
