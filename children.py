from autopilot.tasks import Task

class Parallax_Child(Task):

    HARDWARE = {
        'MOTION': {
            'IMU': I2C_9DOF
        },
        'CAMS':{
            'SIDE': PiCamera
        }
    }

    def __init__(self, *args, **kwargs):
        super(Parallax_Child, self).__init__(*args, **kwargs)


