from autopilot.transform.timeseries import Kalman
import numpy as np
import typing
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime
from time import time
import pdb

@dataclass
class KPos_Measurement:
    """
    Dataclass for giving measurements to :class:`.Kalman_Position`
    that could either be position or acceleration.
    """
    measure_type: str
    """The type of measurement contained, either 'acceleration' or 'position'"""
    timestamp: datetime
    """Time that the measurement was taken"""
    value: float
    """value of the measurement!"""


@dataclass
class Motion:
    """
    Container for second-order motion:
    position, velocity, and acceleration
    """
    position: float = field(metadata={'unit': 'm'})
    velocity: float = field(metadata={'unit': 'm/s'})
    acceleration: float = field(metadata={'unit': 'm/s/s'})
    timestamp: datetime = field(default_factory=datetime.now)


class Kalman_Position(Kalman):
    """
    A 2nd-order Kalman filter for jointly estimating 1-dimensional (vertical)
    position, velocity, and acceleration from orientation-corrected accelerometer measurements
    (from :class:`~autopilot.transform.geometry.IMU_Orientation`) and position measurements
    (from :class:`~autopilot.transform.image.DLC`).
    """

    def __init__(self, use_timestamps:bool=False, **kwargs):
        """

        :param use_timestamps: If True, use timestamp field from inputs in process method. Otherwise (default) keep track of time internally.
        :type use_timestamps: bool
        :param kwargs:
        :type kwargs:
        """
        super(Kalman_Position, self).__init__(dim_state=3, dim_measurement=3, **kwargs)


        # adjust the measurement array -- we never measure Velocity, so it should be zero.
        # we will adjust the other elements (accel, position) in process
        self.H_measure[1,1] = 0

        self.use_timestamps = bool(use_timestamps)

        self._dt = 0 # type: float
        self._last_update = None # type: typing.Optional[float]
        self._last_position = None # type: typing.Optional[KPos_Measurement]
        self._last_acceleration = None # type: typing.Optional[KPos_Measurement]
        self._z = np.zeros(3) # type: np.ndarray

    # make a ufunc for scaling the F array by dt
    def scale_F(self, F: np.ndarray, dt: float):
        F[(0, 1), (1, 2)] = dt
        F[0, 2] = 0.5 * dt * dt
        return F

    def dt(self, now:typing.Optional[datetime]=None) -> float:
        """Time elapsed since *any* update, used to update F"""
        if now is None:
            now = time()
        elif isinstance(now, datetime):
            now = now.timestamp()

        if self._last_update is not None:
            self._dt = now-self._last_update
        self._last_update = now
        return self._dt

    def process(self, input: KPos_Measurement) -> Motion:
        """
        Process either an acceleration or position measurement
        and return the acceleration, velocity, and position as a
        :class:`.Motion` instance

        :param input:
        :type input:
        :return:
        :rtype:
        """
        if input.measure_type == 'position':
            self.H_measure[0,0] = 1
            self.H_measure[2,2] = 0
            self._z[:] = (input.value, 0, 0)
        elif input.measure_type == 'acceleration':
            self.H_measure[0,0] = 0
            self.H_measure[2,2] = 1
            self._z[:] = (0, 0, input.value)
        else:
            e_text = f'Dont know what to do with measurement {input}, need a position or acceleration'
            self.logger.exception(e_text)
            raise ValueError(e_text)

        if self.use_timestamps:
            dt = self.dt(input.timestamp)
        else:
            dt = self.dt()

        # update F state transition matrix for prediction step
        self.F_state_trans = self.scale_F(self.F_state_trans, dt)
        self.predict()
        estimate = self.update(self._z).copy()
        if self.use_timestamps:
            return Motion(*estimate, timestamp=input.timestamp)
        else:
            return Motion(*estimate)











