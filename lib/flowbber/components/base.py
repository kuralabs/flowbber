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
Base class for all Flowbber components.

All Flowbber components extend from the Component class.
"""

from time import time
from queue import Empty
from abc import ABCMeta, abstractmethod
from multiprocessing import Queue, Process

from setproctitle import setproctitle

from ..config import Configurator
from ..logging import get_logger


log = get_logger(__name__)


class ComponentError(Exception):
    """
    Generic exception raised when a component fails.
    """

    def __init__(self, execution):
        super().__init__(str(execution))
        self.execution = execution


class TimeExceededError(ComponentError):
    """
    Exception raised when a component execution time was exceeded.
    """
    pass


class CrashError(ComponentError):
    """
    Exception raised when a component crashed.
    """
    pass


class ExecutionInfo:
    """
    Component execution information object.

    :var status: Word used to describe the status of the execution.
     For example: ``succeeded``, ``crashed``, ``killed``, ``hanged`` or
     ``timed out``.
    :var duration: Duration time in seconds of the execution of the process.
    :var pid: Pid of the executing process.
    :var exitcode: Exit code of the executing process.
     Can be None if status is ``hanged``.
    :var data: Data returned by the executing process, if any.
    """

    def __init__(self, status, duration, pid, exitcode, data):
        self.status = status
        self.duration = duration
        self.pid = pid
        self.exitcode = exitcode
        self.data = data

    def __str__(self):
        return (
            'Execution of PID {execution.pid} {execution.status}. '
            'Exit code is {execution.exitcode} and the process ran for '
            '{execution.duration} seconds'.format(execution=self)
        )

    def __repr__(self):
        return str(self)


class NamedABCMeta(ABCMeta):
    """
    Base metaclass for abstract classes that pretty print the name of the
    class.
    """

    def __str__(cls):  # noqa: False N805
        return cls.__name__

    def __repr__(cls):  # noqa: False N805
        return str(cls)


class Component(metaclass=NamedABCMeta):
    """
    Base Component class.

    All Component classes (Sink, Aggregator, Source) extend from this class.

    **Properties**:

    :var int index: Position of this component in the pipeline definition.
    :var str id: Unique identifier for this component.
    :var bool optional: Successful execution of this component is optional.
     That is, it is allowed to fail and the pipeline won't fail.
    :var int timeout: Execution timeout for this component, in seconds.
     None means no timeout, wait forever.
    :var namedtuple config: Frozen configuration after validation.

    **Parameters**:

    :param int index: Value to set the index property.
    :param str type_: Type key used to fetch this component.
    :param str id_: Value to set the id property.
    :param bool optional: Value to set the optional property.
    :param int timeout: Value to set the timeout property.
    :param dict config: User configuration for this component.
    """

    @abstractmethod
    def __init__(
        self, index, type_, id_,
        optional=False, timeout=None, config=None
    ):
        self._index = index
        self._type_ = type_
        self._id = id_
        self._optional = optional
        self._timeout = timeout

        self._result = None
        self._start = None
        self._process = None

        configurator = Configurator()
        self.declare_config(configurator)
        self.config = configurator.validate(config or {})

    @property
    def index(self):
        """
        Index of this component in the stage.
        """
        return self._index

    @property
    def id(self):
        """
        Component unique identifier.
        """
        return self._id

    @property
    def optional(self):
        """
        Component successful execution is optional or not.
        """
        return self._optional

    @property
    def timeout(self):
        """
        Timeout for this component.
        """
        return self._timeout

    def declare_config(self, config):
        """
        Declare the configuration options of this component.

        :param config: The configuration manager for this component.
        :type config: :class:`flowbber.config.Configurator`
        """
        pass

    @abstractmethod
    def _component_execute(self, *args):
        """
        Abstract method that components must implement to provide its specific
        behavior.

        Implementations can receive arbitrary arguments and must return the
        data they want to return back to the called process.
        """
        pass

    def _process_execute(self, *args):
        """
        Execute this component.

        This method MUST be run in a subprocess.
        """
        setproctitle(str(self))

        assert self._result.empty()

        # We reset the start time so that the measurement is more accurate
        # and will not account for the time the process took to start
        self.start = time()
        data = None

        try:
            data = self._component_execute(*args)

        finally:
            self._result.put(
                (time() - self.start, data)
            )

    def _reset(self, procargs):
        """
        Reset this component so its ready for another execution.

        :param tuple procargs: Process execution arguments.
        """
        self._result = Queue(maxsize=1)
        self._start = time()
        self._process = Process(
            target=self._process_execute,
            name=str(self),
            args=procargs,
        )

    def start(self, *args):
        """
        Start the component execution.
        """
        self._reset(args)
        self._process.start()

    def stop(self):
        """
        Force stop this component.

        Use only when the result of the source is not longer relevant.
        """
        assert self._process is not None
        self._process.terminate()

    def join(self):
        """
        Join the component and get its execution information.

        :return: The execution information of this component.
        :rtype: :class:`ExecutionInfo`.
        """

        # Calculate timeout from elapsed time
        timeout = None
        if self.timeout is not None:
            timeout = max([0, self.timeout - (time() - self.start)])

        # Get results
        try:
            duration, data = self._result.get(True, timeout)

            # Got data back, wait for the process to die
            self._process.join(0.1)
            if self._process.is_alive():
                log.warning(
                    '{name} #{component.index} "{component.id}" driving '
                    'process with PID {process.pid} took too long to die '
                    'after submitting its result. Exit code might '
                    'be None'.format(
                        name=self.__class__.__name__,
                        component=self,
                        process=self._process,
                    )
                )

            # Standard Python crash
            if data is None:
                execution = ExecutionInfo(
                    'crashed', duration,
                    self._process.pid,
                    self._process.exitcode,
                    None
                )
                raise CrashError(execution)

            # All good
            execution = ExecutionInfo(
                'succeeded', duration,
                self._process.pid,
                self._process.exitcode,
                data
            )
            return execution

        except Empty as e:
            # In most cases the duration of the process will be unable to be
            # determined
            duration = None

            # Check if killed without executing the finally clause
            if not self._process.is_alive():
                log.warning(
                    '{name} #{component.index} "{component.id}" driving '
                    'process with PID {process.pid} was killed '
                    '({process.exitcode}).\n'
                    'Possible causes can be a segfault, SIGTERM, SIGKILL '
                    'or OOM killer'.format(
                        name=self.__class__.__name__,
                        component=self,
                        process=self._process,
                    )
                )

                status = 'killed'

            # Real timeout, process still alive, lets kill it
            else:
                self._process.terminate()

                # Check if process hanged
                self._process.join(0.1)
                if self._process.is_alive():
                    log.warning(
                        'Execution of {name} #{component.index} '
                        '"{component.id}" timed out and its driving process '
                        'with PID {component.pid} seems to have hanged'.format(
                            name=self.__class__.__name__.lower(),
                            component=self,
                            process=self._process,
                        )
                    )

                    status = 'hanged'

                else:
                    # At least we can offer an estimate if we kill the process
                    duration = time() - self.start
                    status = 'timed out'

            # Note: exitcode can be None if the process hanged
            execution = ExecutionInfo(
                status, duration,
                self._process.pid,
                self._process.exitcode,
                None
            )
            raise TimeExceededError(execution)

    def __lt__(self, other):
        """
        "Less than" magic method allows to sort a collection of this objects
        by its timeout.
        """

        if self.timeout is None and other.timeout is None:
            return False
        if self.timeout is None:
            return False
        if other.timeout is None:
            return True

        return self.timeout < other.timeout

    def __str__(self):
        return '#{} {}.{}.{}'.format(
            self._index,
            self.__class__.__name__,
            self._type_,
            self._id
        )

    def __repr__(self):
        return str(self)


__all__ = [
    'TimeExceededError',
    'CrashError',
    'ExecutionInfo',
    'Component',
]
