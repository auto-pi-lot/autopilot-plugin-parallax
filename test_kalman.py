import numpy as np
import sys
from .kalman_position import KPos_Measurement, Kalman_Position
import pytest

def sine_data(fs=500, total_time=30,
              accel_noise=5,accel_jitter=0.0002,
              pos_fs = 30, pos_noise = 0.05, pos_jitter = 0.01):
    """generate a sinusoid movement with noise and asynchronous sampling from an accelerometer and position"""
    pos_skip = round(fs/pos_fs)

    t = np.linspace(0, total_time, int(fs*total_time), endpoint=False)

    true_sin = np.sin(2*np.pi*t)

    # accelerometer
    accel = np.diff(np.diff(true_sin)*fs)*fs
    accel += (np.random.rand(len(true_sin)-2)-0.5)*accel_noise
    accel_ts = t[:-2]+(np.random.rand(len(t)-2)-0.5)*accel_jitter
    accels = []
    for ts, val in zip(accel_ts, accel):
        accels.append(KPos_Measurement(measure_type='acceleration', timestamp=ts, value=val))

    vel = np.diff(true_sin)*fs

    # position
    pos = true_sin[::pos_skip]
    pos += (np.random.rand(len(pos))-0.5)*pos_noise
    pos_ts = t[::pos_skip]
    pos_ts += (np.random.rand(len(pos_ts))-0.5)*pos_jitter
    poss = []
    for ts, val in zip(pos_ts, pos):
        poss.append(KPos_Measurement(measure_type='position', timestamp=ts, value=val))

    return poss, vel, accels

def test_kalman_position(pos=None, accel=None):
    if pos is None or accel is None:
        pos, _, accel = sine_data(total_time=5)
    else:
        pos, accel = pos.copy(), accel.copy()

    pos_ret, accel_ret = pos.copy(), accel.copy()

    kalman = Kalman_Position(use_timestamps=True)

    measurements = []

    while len(pos)>0 and len(accel)>0:
        if pos[0].timestamp < accel[0].timestamp:
            measurement = pos.pop(0)
        else:
            measurement = accel.pop(0)

        measurements.append(kalman.process(measurement))

    return measurements, pos_ret, accel_ret

if __name__ == "__main__":
    from tests import utils
    measurements, pos, accel = test_kalman_position()

    utils.plot_kalman(pos, accel, measurements)


