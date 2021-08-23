import autopilot
import numpy as np
from autopilot.networking import Net_Node
from autopilot.core.loggers import init_logger
import time

if __name__ == "__main__":
    logger = init_logger(module_name='main', class_name='main')
    global state
    state = {}

    global platform
    platform = autopilot.get('hardware', 'Parallax_Platform')()
    logger.info('platform initialized')
    platform.level()
    mask = np.zeros((6,6))
    mask[2,:] = 1
    platform.mask = mask
    platform.height = platform.MAX_HEIGHT/2
    platform.join()

    platform.move_mode = platform.Move_Modes.VELOCITY

    def set_state(value:dict):
        global state
        global logger
        logger.info('set state: ' + str(value))
        state.update(value)


    def set_velocity(value:float):
        global platform
        global logger
        logger.info('set velocity: ' + str(value))
        platform.velocity = value

    node = Net_Node(
        id='plaxer',
        upstream = '',
        port = 6000,
        listens = {
            'STATE': set_state,
            'VELOCITY': set_velocity
        },
        router_port=5000,
        daemon=False
    )
    logger.info('networking init')
    while True:
        time.sleep(1)


