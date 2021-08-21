from autopilot.tasks.children import Transformer
from time import sleep
import sys
if __name__ == "__main__":

    tfm = Transformer(
        transform = ({'transform':'DLC',
                'kwargs': {
                    'model_dir': 'parallax'
                }
        },),
        operation='stream',
        value_subset='picam',
        return_id='sensor',
        return_ip='192.168.0.240',
        return_port=5000,
        return_key="DLC",
        router_port = 5001,
        forward_id='plotter',
        forward_ip='192.168.0.100',
        forward_key='IMAGE',
        forward_port=6000,
        forward_what='both'
    )

    while True:
        try:
            sleep(1)
        except KeyboardInterrupt:
            sys.exit()