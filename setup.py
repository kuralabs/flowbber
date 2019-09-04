#!/usr/bin/env python3
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
Usage:

::

    ./setup.py sdist
    ./setup.py bdist_wheel
    ./setup.py bdist_wheel --binary

"""

from pathlib import Path

from setuptools import setup


def check_directory():
    """
    You must always change directory to the parent of this file before
    executing the setup.py script. setuptools will fail reading files,
    including and excluding files from the MANIFEST.in, defining the library
    path, etc, if not.
    """
    from os import chdir

    here = Path(__file__).parent.resolve()
    if Path.cwd().resolve() != here:
        print('Changing path to {}'.format(here))
        chdir(str(here))


check_directory()


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

    # Optional dependencies
    extras_require={
        ###########
        # Sources #
        ###########

        # CoberturaSource
        'cobertura': ['pycobertura'],
        # ConfigSource
        'config': [],
        # CPUSource
        'cpu': ['psutil'],
        # EnvSource
        'env': [],
        # GitSource
        'git': [],
        # GitHubSource
        'github': ['pygithub'],
        # JSONSource
        'json': [],
        # GTestSource
        'gtest': [],
        # LcovSource
        'lcov': ['lcov_cobertura'],
        # PyTestSource
        'pytest': [],
        # SLOCSource
        'sloc': ['pygount'],
        # SpeedSource
        'speed': ['pyspeedtest'],
        # TimestampSource
        'timestamp': [],
        # UserSource
        'user': [],
        # ValgrindMemcheckSource
        'valgrind_memcheck': ['xmltodict'],

        ###############
        # Aggregators #
        ###############
        'expander': [],
        'filter': [],
        'lcov_merger': ['lcov_cobertura'],

        ###########
        # Sinks   #
        ###########

        # ArchiveSink
        'archive': [],
        # DataSplitterSink
        'data_splitter': [],
        # InfluxDBSink
        'influx': ['influxdb'],
        # LcovHTMLSink
        'lcov_html': [],
        # MongoDBSink
        'mongo': ['pymongo'],
        # PrintSink
        'print': [],
        # TemplateSink
        'template': ['jinja2'],
    },

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
    url='https://docs.kuralabs.io/flowbber/',
    keywords='flowbber',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
    ],

    # Sphinx autodoc cannot extract the documentation of zipped eggs with the
    # ``.. autodata::`` directive, causing chaos in AutoAPI. This disables zip
    # installation for correct AutoAPI generation.
    zip_safe=False,

    # Entry points
    entry_points={
        'flowbber_plugin_sources_1_0': [
            'cobertura = flowbber.plugins.sources.cobertura:CoberturaSource',
            'config = flowbber.plugins.sources.config:ConfigSource',
            'cpu = flowbber.plugins.sources.cpu:CPUSource',
            'env = flowbber.plugins.sources.env:EnvSource',
            'git = flowbber.plugins.sources.git:GitSource',
            'github = flowbber.plugins.sources.github:GitHubSource',
            'json = flowbber.plugins.sources.json:JSONSource',
            'gtest = flowbber.plugins.sources.gtest:GTestSource',
            'lcov = flowbber.plugins.sources.lcov:LcovSource',
            'pytest = flowbber.plugins.sources.pytest:PytestSource',
            'sloc = flowbber.plugins.sources.sloc:SLOCSource',
            'speed = flowbber.plugins.sources.speed:SpeedSource',
            'timestamp = flowbber.plugins.sources.timestamp:TimestampSource',
            'user = flowbber.plugins.sources.user:UserSource',
            'valgrind_memcheck = flowbber.plugins.sources.valgrind.memcheck:ValgrindMemcheckSource',  # noqa
            'valgrind_helgrind = flowbber.plugins.sources.valgrind.helgrind:ValgrindHelgrindSource',  # noqa
            'valgrind_drd = flowbber.plugins.sources.valgrind.drd:ValgrindDrdSource',  # noqa
        ],
        'flowbber_plugin_aggregators_1_0': [
            'expander = flowbber.plugins.aggregators.expander:ExpanderAggregator',  # noqa
            'filter = flowbber.plugins.aggregators.filter:FilterAggregator',
            'lcov_merger = flowbber.plugins.aggregators.lcov_merger:LcovMergerAggregator',  # noqa
        ],
        'flowbber_plugin_sinks_1_0': [
            'archive = flowbber.plugins.sinks.archive:ArchiveSink',
            'data_splitter = flowbber.plugins.sinks.data_splitter:DataSplitterSink',  # noqa
            'influxdb = flowbber.plugins.sinks.influxdb:InfluxDBSink',
            'lcov_html = flowbber.plugins.sinks.lcov_html:LcovHTMLSink',
            'mongodb = flowbber.plugins.sinks.mongodb:MongoDBSink',
            'print = flowbber.plugins.sinks.print:PrintSink',
            'template = flowbber.plugins.sinks.template:TemplateSink',
        ]
    },

    # Multiple packaging options
    **find_packages('lib')
)
