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
from setproctitle import setproctitle


log = logging.getLogger(__name__)

PrintRequest = namedtuple('PrintRequest', ['string', 'fd'])


def multiprocess_except_hook(exctype, value, traceback):
    """
    Unhandled exception hook that works in a multiprocess environment.
    """
    log.critical(
        'Uncaught exception',
        exc_info=(exctype, value, traceback)
    )


class QueueListener:
    """
    Object that will wait for messages in a queue and print or log them.

    :param multiprocessing.Queue queue: A multiprocessing queue to listen to.
    :param logging.Handler handler: A logging handler to delegate logging
     requests to.
    :param dict fds: Dictionary mapping a name with a file descriptor.
     If ``None`` is passed, a basic dictionary with stdout and stderr will be
     used.
    """

    def __init__(self, queue, handler, fds=None):
        self._queue = queue
        self._handler = handler
        self._fds = fds

        if fds is None:
            self._fds = {
                'stdout': sys.stdout,
                'stderr': sys.stderr,
            }

    def start(self):
        """
        Start listening on the queue.

        This method blocks until a ``None`` is submitted to the queue managed
        by this instance.
        """

        # Start listening for records
        self._run_loop(True)
        # There might still be records in the queue.
        self._run_loop(False)

    def _run_loop(self, block):
        """
        Perform the listening and execution look.

        :param bool block: Block on the queue or not.
        """
        while True:
            try:
                # Handle stop
                record = self._queue.get(block)
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
                    continue

                # Handle logging
                self._handler.handle(record)
            except Empty:
                if not block:
                    break
                pass


class LoggingManager:
    """
    Logging manager class.

    This class is expected to run as a singleton. It allows to setup the
    logging subprocess and handlers for all main process and later work
    subprocesses with one single call.
    """

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
        Logging subprocess target function.

        This function will setup the basic logging configuration and start
        the listener on the logging queue.
        """

        # Setup logging for logging subprocess
        setproctitle('flowbber - logging manager')

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

        # # Configure baisc logging
        logging.basicConfig(handlers=[handler], level=level)

        # Start listening for logs and prints
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

        :param int verbosity: Verbosity level, as defined by
         ``LoggingManager.LEVELS``. The greater the number the more information
         is provided, with 0 as initial level.
        """

        # Perform first time setup in main process and start the logging
        # subprocess
        if self._log_queue is None:

            # Change system exception hook
            sys.excepthook = multiprocess_except_hook

            # Create logging subprocess
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
        Stop the logging subprocess.

        This shouldn't be called unless the application is quitting.
        """

        self._log_queue.put_nowait(None)
        self._log_subprocess.join()

    def enqueue_print(self, obj, fd='stdout'):
        """
        Enqueue a print to the given fd.

        :param obj: Object to print.
        :param str fd: Name of the file descriptor.
         Either stdout or stderr only.
        """
        self._log_queue.put_nowait(
            PrintRequest(string=str(obj) + '\n', fd=fd)
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
