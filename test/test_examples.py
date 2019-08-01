from os import environ
from json import loads
from shutil import which
from pathlib import Path
from subprocess import run
from collections import namedtuple

from pytest import mark
from deepdiff import DeepDiff

from flowbber.main import main
from flowbber.logging import get_logger, setup_logging


Arguments = namedtuple('Arguments', ['pipeline', 'dry_run'])


log = get_logger(__name__)
examples = Path(__file__).parent.parent / 'examples'


def setup_module(module):
    setup_logging(verbosity=2)


def run_pipeline(name, pipelinedef):
    args = Arguments(
        pipeline=examples / name / pipelinedef,
        dry_run=False,
    )
    result = main(args)
    assert result == 0


@mark.parametrize(['name', 'pipelinedef'], [
    ['sloc', 'pipeline.toml'],
    ['basic', 'pipeline.toml'],
    ['local', 'pipeline.toml'],
    ['advanced', 'pipeline.json'],
    ['advanced', 'pipeline.toml'],
    ['test', 'pipeline.toml'],
    ['valgrind', 'pipeline.toml'],
    ['config', 'pipeline.toml'],
    ['archive', 'compress.toml'],
    ['archive', 'extract.toml'],
])
def test_pipeline(name, pipelinedef):
    run_pipeline(name, pipelinedef)


@mark.skipif(
    'GITHUB_TOKEN' not in environ,
    reason='Missing GITHUB_TOKEN environment variable'
)
def test_pipeline_github():
    run_pipeline('github', 'pipeline.toml')


@mark.skipif(
    not which('make'),
    reason='"make" is unavailable in your environment'
)
def test_pipeline_lcov():
    # Create coverage files
    run([which('make'), '-C', str(examples / 'lcov')], check=True)
    run_pipeline('lcov', 'pipeline.toml')


def test_pipeline_filter():
    run_pipeline('filter', 'pipeline.toml')

    actual = loads(
        Path(examples / 'filter' / 'data.json').read_text(encoding='utf-8')
    )

    expected = {
        'input': {
            'exclude2': {
                'neverthese': False,
            },
            'exclude1': {
                'butnotthis': {
                    'andsome': 'more',
                    'some': 'data',
                },
            },
        },
    }

    differences = DeepDiff(actual, expected)
    assert not differences


@mark.parametrize(['script'], [
    ['cpud/cpud.py'],
    # Aug 22 2018:
    #   The package pytestspeed is broken.
    #   https://github.com/fopina/pyspeedtest/issues/15
    # ['speedd/speedd.py'],
])
def test_daemons(script):
    run(str(examples / script), check=True)


def test_pipeline_mongo():
    """
    Test the mongo sink
    """
    # Run the pipeline twice to verify the "overwrite" flag works
    run_pipeline('mongo', 'pipeline.toml')
    run_pipeline('mongo', 'pipeline.toml')
