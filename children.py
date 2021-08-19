import typing
from threading import Event, Thread

import autopilot
from autopilot.tasks.children import Child
from autopilot import prefs
from autopilot.transform import make_transform


class Parallax_Child(Child):

    HARDWARE = {
        'MOTION': {
            'IMU': 'I2C_9DOF'
        },
        'CAMS':{
            'SIDE': 'PiCamera'
        }
    }


    IMU_Transform = (
        {
            'transform': 'Rotate',
            'kwargs': {'dims': 'xy'}
        },
        {
            'transform': 'Slice',
            'kwargs': {'select': slice(1)}
        },
        {
            'transform': 'Add',
            'kwargs': {'value': -9.8}
        }
    ) # type: typing.Tuple[dict]
    """
    Take the accelerometer, gyro, and orientation readings through to
    an estimation of absolute vertical acceleration
    """



    def __init__(self,
                 parent:dict, # dict of return id, ip, port
                 transformer:dict, # dict of id, ip, port of transformer

                 *args, **kwargs):
        super(Parallax_Child, self).__init__(*args, **kwargs)

        self.stopping = Event()

        imu_prefs = prefs.get('HARDWARE')['MOTION']['IMU']
        cam_prefs = prefs.get('HARDWARE')['CAMS']['SIDE']

        self.imu = autopilot.get_hardware('I2C_9DOF')(**imu_prefs)
        self.cam = autopilot.get_hardware('PiCamera')(**cam_prefs)

        self.imu_transform = make_transform(self.IMU_Transform)
        self.fusion = autopilot.get('transform', 'Kalman_Position')()

    def _read_imu(self):

        while not self.stopping.is_set():
            rotation = self.imu.





