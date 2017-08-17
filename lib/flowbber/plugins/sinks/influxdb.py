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
Simple InfluxDB storage sink plugin.
"""

from logging import getLogger
from datetime import datetime

from pprintpp import pformat

from flowbber.entities import Sink


log = getLogger(__name__)


def transform_to_flat(data, keysjoiner, keysjoinerreplace):
    """
    """
    influxdb_supported = (str, int, float, bool)

    def joinkey(path, key):
        parts = [*path, key]

        if keysjoinerreplace is not None:
            parts = [
                part.replace(keysjoiner, keysjoinerreplace)
                for part in parts
            ]

        return keysjoiner.join(parts)

    def flat(dictionary, path):
        assert isinstance(dictionary, dict)

        for key, value in dictionary.items():
            if isinstance(value, influxdb_supported):
                yield joinkey(path, key), value
                continue

            if isinstance(value, dict):
                yield from flat(value, path + [key])
                continue

            if isinstance(value, list):
                value_as_dict = {
                    str(index): subvalue
                    for index, subvalue in enumerate(value)
                }
                yield from flat(value_as_dict, path)
                continue

            raise ValueError('Unable to flat value ({}): {}'.format(
                type(value), value
            ))

    return {
        key: {
            subkey: subvalue
            for subkey, subvalue in flat(value, [])
        }
        for key, value in data.items()
    }


def transform_to_points(timestamp, flat):
    """
    FIXME: Document.
    FIXME: Transform deeper collected values into flat structure.

    A point is in the form::

        {
            "measurement": "cpu_load_short",
            "tags": {
                "host": "server01",
                "region": "us-west"
            },
            "time": "2009-11-10T23:00:00Z",
            "fields": {
                "value": 0.64
            }
        }

    Field value must be string, float, integer, or boolean.
    """
    points = [
        {
            'measurement': source,
            'tags': {},
            'time': timestamp,
            'fields': {
                key: value
                for key, value in collected.items()
            }
        }
        for source, collected in flat.items()
    ]

    return points


class InfluxDBSink(Sink):
    def declare_config(self, config):

        # Connection options
        config.add_option(
            'uri',
            default=None,
            optional=True,
            type=str,
            secret=True,
        )

        config.add_option(
            'host',
            default='localhost',
            optional=True,
            type=str,
        )

        config.add_option(
            'port',
            default=8086,
            optional=True,
            type=int,
        )

        config.add_option(
            'username',
            default='root',
            optional=True,
            type=str,
        )

        config.add_option(
            'password',
            default='root',
            optional=True,
            type=str,
            secret=True,
        )

        config.add_option(
            'ssl',
            default=False,
            optional=True,
            type=bool,
        )

        config.add_option(
            'verify_ssl',
            default=False,
            optional=True,
            type=bool,
        )

        # Data options
        config.add_option(
            'database',
            type=str,
        )

        config.add_option(
            'key',
            default='timestamp.iso8601',
            optional=True,
            type=lambda opt: None if opt is None else str(opt),
        )

        config.add_option(
            'keysjoiner',
            default='.',
            optional=True,
            type=str,
        )

        config.add_option(
            'keysjoinerreplace',
            default=':',
            optional=True,
            type=lambda opt: None if opt is None else str(opt),
        )

        # Check if uri is defined and if so then delete other keys
        def custom_validator(validated):
            if validated['uri'] is not None:
                del validated['host']
                del validated['port']
                del validated['username']
                del validated['password']
            else:
                del validated['uri']

        config.add_validator(custom_validator)

    def distribute(self, data):
        from influxdb import InfluxDBClient

        # Get key
        if self.config.key.value is None:
            key = datetime.now().isoformat()

        else:
            current = data
            for part in self.config.key.value.split('.'):
                current = current[part]

            key = current

        # Connect to database
        if self.config.uri.value is None:
            client = InfluxDBClient(
                host=self.config.host.value,
                port=self.config.port.value,
                username=self.config.username.value,
                password=self.config.password.value,
                database=self.config.database.value,
                ssl=self.config.ssl.value,
                verify_ssl=self.config.verify_ssl.value,
            )
        else:
            client = InfluxDBClient.from_DSN(
                self.config.uri.value,
                database=self.config.database.value,
                ssl=self.config.ssl.value,
                verify_ssl=self.config.verify_ssl.value,
            )

        # Flat data
        log.info('Flattening data for InfluxDB')
        flat = transform_to_flat(
            data,
            self.config.keysjoiner.value,
            self.config.keysjoinerreplace.value,
        )
        del data  # Release a bit of ram here
        log.debug('Flat data:\n{}'.format(pformat(flat)))

        # Insert points
        log.info('Creating points using timestamp {}'.format(key))
        points = transform_to_points(key, flat)
        del flat  # Release a bit of ram here
        log.debug('Points data:\n{}'.format(pformat(points)))

        log.info('Inserting points to InfluxDB: {}'.format([
            point['measurement'] for point in points
        ]))
        client.write_points(points)


__all__ = ['InfluxDBSink']
