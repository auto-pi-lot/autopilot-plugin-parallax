from matplotlib import pyplot as plt
import typing

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..kalman_position import KPos_Measurement


def plot_sines(pos:typing.List['KPos_Measurement'], accel:typing.List['KPos_Measurement']):
    pos_x = [x.timestamp for x in pos]
    pos_y = [x.value for x in pos]

    accel_x = [x.timestamp for x in accel]
    accel_y = [x.value for x in accel]

    fig, ax = plt.subplots()
    ax.plot(pos_x, pos_y)
    ax.plot(accel_x, accel_y)
    plt.show()



def plot_kalman(pos, vel, accel, measurements):

    pos_x = [x.timestamp for x in pos]
    pos_y = [x.value for x in pos]

    accel_x = [x.timestamp for x in accel]
    accel_y = [x.value for x in accel]

    meas_x = [x.timestamp for x in measurements]
    meas_pos = [x.position for x in measurements]
    meas_vel = [x.velocity for x in measurements]
    meas_acc = [x.acceleration for x in measurements]

    fig, ax = plt.subplots(3, 1) # type: typing.List[plt.axes]

    ax[0].plot(pos_x, pos_y, 'k-', linewidth=0.5, label='sensor reading')
    ax[0].plot(meas_x, meas_pos, 'r-', linewidth=0.5, label='estimated')

    ax[0].legend()
    ax[0].set_title('Position')

    ax[1].plot(accel_x, vel[:-1],'k-', linewidth=0.5, label='real')
    ax[1].plot(meas_x, meas_vel, 'r-', linewidth=0.5, label='estimated')

    ax[1].set_title('Velocity')
    ax[1].legend()

    ax[2].plot(accel_x, accel_y, 'k-', linewidth=0.5, label='sensor reading')
    ax[2].plot(meas_x, meas_acc, 'r-', linewidth=0.5, label='estimated')

    ax[2].set_title('Acceleration')
    ax[2].legend()
    # plt.show()





