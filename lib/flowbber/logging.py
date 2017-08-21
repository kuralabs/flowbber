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
Multiprocess logging management module.
"""

import sys
import logging
from queue import Empty
from atexit import register
from collections import namedtuple
from logging.handlers import QueueHandler
from multiprocessing import Queue, Process

from colorlog import ColoredFormatter


PrintRequest = namedtuple('PrintRequest', ['string'])


class LoggingManager:

    FORMAT = (
        '  {log_color}{levelname:8}{reset} | '
        '{log_color}{message}{reset}'
    )
    FORMAT_DEBUG = (
        '  {log_color}{levelname:8}{reset} | '
        '{process} - {log_color}{message}{reset}'
    )

    LEVELS = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
    }

    def __init__(self):
        self._verbosity = 0
        self._log_queue = None
        self._log_subprocess = None

    def _logging_subprocess(self):
        """
        FIXME: Document.
        """

        # Setup logging for logging subprocess

        # # Level
        level = self.LEVELS.get(self._verbosity, logging.DEBUG)

        # # Format
        if level != logging.DEBUG:
            format_tpl = self.FORMAT
        else:
            format_tpl = self.FORMAT_DEBUG
        formatter = ColoredFormatter(fmt=format_tpl, style='{')

        # # Handler
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logging.basicConfig(handlers=[handler], level=level)

        # Start listening for records
        while True:
            try:
                record = self._log_queue.get(True)
                if record is None:
                    break
                if isinstance(record, PrintRequest):
                    sys.stdout.write(record.string)
                    sys.stdout.write('\n')
                    continue
                handler.handle(record)
            except Empty:
                pass

        # There might still be records in the queue.
        while True:
            try:
                record = self._log_queue.get(False)
                if record is None:
                    break
                if isinstance(record, PrintRequest):
                    sys.stdout.write(record.string)
                    sys.stdout.write('\n')
                    continue
                handler.handle(record)
            except Empty:
                break

    def setup_logging(self, verbosity=0):
        """
        FIXME: Document.
        """

        # Perform first time setup in main process and start the logging
        # subprocess
        if self._log_queue is None:
            self._verbosity = verbosity
            self._log_queue = Queue()
            self._log_subprocess = Process(
                target=self._logging_subprocess
            )
            self._log_subprocess.start()

            register(self.stop_logging)

        # Check that no call to loggers have been made
        root = logging.getLogger()
        assert not root.hasHandlers()

        # Create handler for main process and all subsequent subprocesses
        level = self.LEVELS.get(self._verbosity, logging.DEBUG)
        handler = QueueHandler(self._log_queue)
        logging.basicConfig(handlers=[handler], level=level)

    def stop_logging(self):
        """
        FIXME: Document.
        """

        self._log_queue.put_nowait(None)
        self._log_subprocess.join()

    def enqueue_print(self, string):
        """
        FIXME: Document.
        """
        self._log_queue.put_nowait(PrintRequest(string=string))


_instance = LoggingManager()

setup_logging = _instance.setup_logging
print = _instance.enqueue_print
get_logger = logging.getLogger


__all__ = ['setup_logging', 'print', 'get_logger']
