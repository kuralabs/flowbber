#!/usr/bin/env python3

from toml import loads

from flowbber.pipeline import Pipeline
from flowbber.scheduler import Scheduler
from flowbber.logging import setup_logging
from flowbber.inputs import validate_definition


CONFIG = """
[cpud]
verbosity = 3

# Take a sample each 10 seconds
frequency = 10

# Number of samples to take
samples = 2

[influxdb]
uri = "influxdb://localhost:8086/"
database = "cpud"
key = "timestamp.iso8601"

[mongodb]
uri = "mongodb://localhost:27017/"
database = "cpud"
collection = "cpuddata"
"""


def build_definition(config):
    """
    Build a pipeline definition based on given configuration.
    """
    definition = {
        'sources': [
            {'type': 'timestamp', 'id': 'timekeys', 'config': {
                'epoch': True,  # Key for MongoDB
                'iso8601': True,  # Key for InfluxDB
            }},
            {'type': 'cpu', 'id': 'cpu'},
        ],
        'sinks': [],
        'aggregators': [],
    }

    if config['influxdb']:
        definition['sinks'].append({
            'type': 'influxdb',
            'id': 'influxdb',
            'config': {
                'uri': config['influxdb']['uri'],
                'database': config['influxdb']['database'],
                'key': 'timekeys.iso8601',
            }
        })

    if config['mongodb']:
        definition['sinks'].append({
            'type': 'mongodb',
            'id': 'mongodb',
            'config': {
                'uri': config['mongodb']['uri'],
                'database': config['mongodb']['database'],
                'collection': config['mongodb']['collection'],
                'key': 'timekeys.epoch',
            }
        })

    if not definition['sinks']:
        raise RuntimeError('No sinks configured')

    return definition


def main():

    # Read configuration
    config = loads(CONFIG)

    # Setup multiprocess logging
    setup_logging(config['cpud']['verbosity'])

    # Build pipeline definition
    definition = build_definition(config)

    # Validate pipeline definition
    validated = validate_definition(definition)

    # Build pipeline
    pipeline = Pipeline(
        validated,
        'cpud',
        app='cpud',
        save_journal=False,
    )

    # Build and run scheduler
    scheduler = Scheduler(
        pipeline,
        config['cpud']['frequency'],
        samples=config['cpud']['samples'],
        stop_on_failure=True
    )

    scheduler.run()


if __name__ == '__main__':
    main()
