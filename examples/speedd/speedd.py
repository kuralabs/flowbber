#!/usr/bin/env python3

from toml import loads

from flowbber.pipeline import Pipeline
from flowbber.scheduler import Scheduler
from flowbber.logging import setup_logging
from flowbber.inputs import validate_definition


CONFIG = """
[speedd]
verbosity = 3

# Take a sample each 10 seconds
frequency = 30

# Number of samples to take
samples = 2

# InfluxDB settings
uri = "influxdb://localhost:8086/"
database = "speedd"
"""


def build_definition(config):
    """
    Build a pipeline definition based on given configuration.
    """
    definition = {
        'sources': [
            {
                'type': 'timestamp',
                'id': 'timekey',
                'config': {
                    'iso8601': True,  # Key for InfluxDB
                }
            },
            {
                'type': 'speed',
                'id': 'speed'
            },
        ],
        'sinks': [
            {
                'type': 'influxdb',
                'id': 'influxdb',
                'config': {
                    'uri': config['uri'],
                    'database': config['database'],
                    'key': 'timekey.iso8601',
                },
            },
        ],
        'aggregators': [],
    }

    return definition


def main():

    # Read configuration
    config = loads(CONFIG)['speedd']

    # Setup multiprocess logging
    setup_logging(config['verbosity'])

    # Build pipeline definition
    definition = build_definition(config)

    # Validate pipeline definition
    validated = validate_definition(definition)

    # Build pipeline
    pipeline = Pipeline(
        validated,
        'speedd',
        app='speedd',
        save_journal=False,
    )

    # Build and run scheduler
    scheduler = Scheduler(
        pipeline,
        config['frequency'],
        samples=config['samples'],
        stop_on_failure=True
    )

    scheduler.run()


if __name__ == '__main__':
    main()
