from autopilot.tasks.children import Transformer
from time import sleep
import sys

tfm = Transformer(
    transform = ({'transform':'DLC',
            'kwargs': {
                'model_dir': 'parallax'
            }
    },),
    operation='stream',
    return_id='sensor',
    return_ip='192.168.0.240',
    return_key="DLC",
    router_port = 5002
)

while True:
    try:
        sleep(1)
    except KeyboardInterrupt:
        sys.exit()