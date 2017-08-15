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
Simple timestamp source.
"""

from flowbber.entities import Source


class TimestampSource(Source):

    def declare_config(self, config):
        """
        FIXME: Document.

            seconds since the EPOCH as integer
            seconds since the EPOCH as float
            ISO 8601
            strftime format as in:
                https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        """
        config.add_option(
            'epoch',
            default=True,
            optional=True,
            type=bool
        )

        config.add_option(
            'epochf',
            default=False,
            optional=True,
            type=bool
        )

        config.add_option(
            'iso8601',
            default=False,
            optional=True,
            type=bool
        )

        config.add_option(
            'strftime',
            default=None,
            optional=True,
            type=str
        )

        # Check that at least one format is enabled
        def custom_validator(validated):
            if not any(validated.values()):
                raise ValueError(
                    'The timestamp source requires at least one timestamp '
                    'format enabled'
                )

        config.add_validator(custom_validator)

    def collect(self):
        from datetime import datetime

        now = datetime.now()

        entry = {}

        if self.config.epoch.value:
            entry[self.config.epoch.key] = int(now.timestamp())

        if self.config.epochf.value:
            entry[self.config.epochf.key] = now.timestamp()

        if self.config.iso8601.value:
            entry[self.config.iso8601.key] = \
                now.replace(microsecond=0).isoformat()

        if self.config.strftime.value:
            entry[self.config.strftime.key] = \
                now.strftime(self.config.strftime.value)

        # FIXME: Understand and maybe add RFC 3339 timestamp

        return entry


__all__ = ['TimestampSource']
