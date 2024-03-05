from __init__ import create_app

import signal
import sys

def signal_handler(sig, frame):
    print('You pressed CTRL+C! Cleaning up...')
    # Perform any necessary cleanup here
    sys.exit(0)
    
app = create_app()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    app.run()