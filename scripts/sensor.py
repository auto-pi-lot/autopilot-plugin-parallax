import autopilot
from autopilot.networking import Net_Node
from autopilot.transform import make_transform
from threading import Lock
from autopilot.core.loggers import init_logger

M_PER_PX = .05/100

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
        'resolution': (320,240),
        'fps': 15,
        'rotate': 3
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

    global position
    position = 0
    def get_dlc(value):
        global fusion
        global logger
        global position
        logger.debug('dlc points: '+ str(value))
        position = float(value[0,0])*M_PER_PX
        measurement = fusion.Measurement(measure_type='position', value=position)
        update_fusion(measurement)

    def update_fusion(value:fusion.Measurement):
        global fusion_lock
        global fusion
        global node
        with fusion_lock:
            motion = fusion.process(value)
            node.send(to='plaxer', key='VELOCITY', value=float(motion.velocity), flags={'NOLOG':True})
            logger.debug(f'sending velocity: {float(motion.velocity)} from input value: {value}')
        return motion


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

    plot_node = Net_Node(
        id='sensor_plot',
        upstream='plotter',
        port=6000,
        listens={},
        upstream_ip='192.168.0.100',
        router_port=6000,
        daemon=False
    )

    cam.capture()
    logger.info('camera capture initialized')

    while True:
        rotation = imu.rotation
        accel, gyro = imu._acceleration, imu._gyro

        y_accel = float(imu_transform.process((accel, rotation)))
        measurement = fusion.Measurement(measure_type='acceleration', value=y_accel)
        motion = update_fusion(measurement)
        plot_node.send(to='plotter', key='DATA',
                       value={'rotation':rotation,'accel':accel,'gyro':gyro,'velocity':[float(motion.velocity), y_accel], 'position': position},
                       flags={'NOREPEAT':True})


