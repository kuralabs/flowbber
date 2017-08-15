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
Simple MongoDB storage sink plugin.
"""

from logging import getLogger

from flowbber.entities import Sink


log = getLogger(__name__)


class MongoDBSink(Sink):
    def declare_config(self, config):
        """
        FIXME: Document.
        """
        config.add_option(
            'uri',
            type=str,
            secret=True,
        )

        config.add_option(
            'database',
            type=str,
        )

        config.add_option(
            'collection',
            type=str,
        )

        config.add_option(
            'key',
            default='timestamp.epoch',
            optional=True,
            type=str,
        )

    def distribute(self, data):
        from pymongo import MongoClient

        # Get key
        if self.config.key.value is None:
            key = None

        else:
            current = data
            for part in self.config.key.value.split('.'):
                current = current[part]

            key = current

        # Connect to database
        client = MongoClient(self.config.uri.value)

        version = client.server_info()['version']
        log.info('Connected to MongoDB database version {}'.format(version))

        # Get database, collection and insert document
        database = client[self.config.database.value]
        collection = database[self.config.collection.value]

        if key is not None:
            log.info('Using key {} = {}'.format(self.config.key.value, key))
            data['_id'] = key

        data_id = collection.insert_one(data).inserted_id
        log.info(
            'Inserted document with id {} in {}.{}'.format(
                data_id, database.name, collection.name
            )
        )


__all__ = ['MongoDBSink']
