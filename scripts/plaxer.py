import autopilot
from autopilot.networking import Net_Node

if __name__ == "__main__":

    global state
    state = {}

    global platform
    platform = autopilot.get('hardware', 'Parallax_Platform')()

    platform.move_mode = platform.Move_Modes.VELOCITY

    def set_state(value:dict):
        global state
        print(value)
        state.update(value)


    def set_velocity(value:float):
        global platform
        print(value)
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

