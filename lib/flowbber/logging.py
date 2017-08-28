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
from functools import wraps
from collections import namedtuple
from logging.handlers import QueueHandler
from multiprocessing import Queue, Process

from colorlog import ColoredFormatter

log = logging.getLogger(__name__)

PrintRequest = namedtuple('PrintRequest', ['string', 'fd'])


class QueueListener:

    def __init__(self, queue, handler):
        self._queue = queue
        self._handler = handler
        self._fds = {
            'stdout': sys.stdout,
            'stderr': sys.stderr,
        }

    def start(self):
        # Start listening for records
        self._run_loop(True)
        # There might still be records in the queue.
        self._run_loop(False)

    def _run_loop(self, block):

        while True:
            try:
                # Handle stop
                record = self._queue.get(False)
                if record is None:
                    break

                # Handle printing
                if isinstance(record, PrintRequest):
                    if record.fd not in self._fds.keys():
                        log.error(
                            'Unknown fd to print to: {}'.format(record.fd)
                        )
                        continue

                    fd = self._fds[record.fd]
                    fd.write(record.string)
                    fd.write('\n')
                    continue

                # Handle logging
                self._handler.handle(record)
            except Empty:
                if not block:
                    break
                pass


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

        listener = QueueListener(self._log_queue, handler)
        listener.start()

    def setup_logging(self, verbosity=0):
        """
        Setup logging for this process.

        The first time it is called it will create a subprocess to manage the
        logging and printing, setup the subprocess for stream logging to stdout
        and setup the main process to queue logging.

        In consequence, any subprocess of the main process will inherit the
        queue logging and become multiprocess logging safe.

        This method can be called from subprocesses, but if at least one
        logging has been performed it will fail as the handler will already
        exists.

        :param str string: String to print.
        :param str fd: Name of the file descriptor.
         Either stdout or stderr only.
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

    def enqueue_print(self, string, fd='stdout'):
        """
        Enqueue a print to the given fd.

        :param str string: String to print.
        :param str fd: Name of the file descriptor.
         Either stdout or stderr only.
        """
        self._log_queue.put_nowait(
            PrintRequest(string=string, fd=fd)
        )


_INSTANCE = LoggingManager()


@wraps(_INSTANCE.setup_logging)
def setup_logging(verbosity=0):
    _INSTANCE.setup_logging(verbosity=verbosity)


@wraps(_INSTANCE.enqueue_print)
def print(string, fd='stdout'):
    _INSTANCE.enqueue_print(string, fd=fd)


def get_logger(name):
    """
    Return a multiprocess safe logger.

    :param str name: Name of the logger.

    :return: A multiprocess safe logger.
    :rtype: :py:class:`logging.Logger`.
    """
    return logging.getLogger(name)


__all__ = ['setup_logging', 'print', 'get_logger']
