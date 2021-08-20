import autopilot
from autopilot.networking import Net_Node
from autopilot.transform import make_transform
from threading import Lock
from autopilot.core.loggers import init_logger

if __name__ == "__main__":
    logger = init_logger(module_name='main', class_name='main')

    fusion_lock = Lock()


    imu_prefs = {
        'name':'imu',
        'invert_gyro': (0, 1),
    }
    cam_prefs = {
        'name':'picam',
        'format':'grayscale',
        'resolution': (640,480),
        'fps': 30
    }

    IMU_Transform = (
            {
                'transform': 'Rotate',
                'kwargs': {'dims': 'xy', 'inverse': 'y'}
            },
            {
                'transform': 'Slice',
                'kwargs': {'select': 2}
            },
            {
                'transform': 'Add',
                'kwargs': {'value': -9.8}
            }
    )
    """
    Take the accelerometer, gyro, and orientation readings through to
    an estimation of absolute vertical acceleration
    """

    imu = autopilot.get_hardware('I2C_9DOF')(**imu_prefs)
    logger.info('imu initialized')
    cam = autopilot.get_hardware('PiCamera')(**cam_prefs)
    logger.info('picam initialized')

    imu_transform = make_transform(IMU_Transform)
    fusion = autopilot.get('transform', 'Kalman_Position')()

    cam.stream(to='dlc_TRANSFORMER',ip='192.168.0.249',port=5002,min_size=1)

    global state
    state = {}
    def set_state(value:dict):
        global state
        global logger
        logger.info('set state: '+ str(value))
        state.update(value)

    def get_dlc(value):
        global fusion
        global logger
        logger.info('dlc points: '+ str(value))
        measurement = fusion.Measurement(measure_type='position', value=value)
        update_fusion(measurement)

    def update_fusion(value:fusion.Measurement):
        global fusion_lock
        global fusion
        global node
        with fusion_lock:
            motion = fusion.process(value)
            node.send(to='plaxer', key='VELOCITY', value=float(motion.velocity), flags={'NOLOG':True})
            logger.info(f'sending velocity: {float(motion.velocity)} from input value: {value}')


    node = Net_Node(
        id='sensor',
        upstream='plaxer',
        port=5000,
        listens={
            'DLC':get_dlc
        },
        upstream_ip='192.168.0.101',
        router_port=5001,
        daemon=False
    )

    cam.capture()
    logger.info('camera capture initialized')

    while True:
        rotation = imu.rotation
        accel = imu._acceleration

        y_accel = float(imu_transform.process((accel, rotation)))
        measurement = fusion.Measurement(measure_type='acceleration', value=y_accel)
        update_fusion(measurement)


