# The final, definitive __main__.py that handles signals directly.

import os
import sys
import signal
import time
from subprocess import Popen
import argparse
import emoji

# Global variable to hold the process object so the handler can access it
wine_process = None

def handle_shutdown_signal(signum, frame):
    """
    This is our self-contained signal handler. It prints, flushes,
    kills the child process group, and exits gracefully.
    """
    global wine_process
    print("\nCtrl+C detected. Shutting down server gracefully...", flush=True)
    
    if wine_process and wine_process.poll() is None:
        try:
            # Kill the entire process group to clean up wine and its children
            os.killpg(os.getpgid(wine_process.pid), signal.SIGTERM)
            print("Termination signal sent to server process group.", flush=True)
        except ProcessLookupError:
            print("Process group already gone.", flush=True)
            pass
            
    sys.exit(0)

def main():
    global wine_process

    # Register our custom handler to listen for Ctrl+C (SIGINT)
    signal.signal(signal.SIGINT, handle_shutdown_signal)

    parser = argparse.ArgumentParser(description='Iris-MT5-Bridge Server Launcher.')
    parser.add_argument('python', type=str, help='Path to the python.exe inside your Wine prefix.')
    parser.add_argument('-p', '--port', type=int, default=18812, help='The TCP listener port.')
    args = parser.parse_args()

    try:
        package_dir = os.path.dirname(os.path.abspath(__file__))
        server_path = os.path.join(package_dir, 'server.py')
    except Exception as e:
        print(f"Error: Could not locate server.py within the package. {e}")
        sys.exit(1)

    #command = [ 'wine', args.python, '-m', 'pdb', server_path, '-p', str(args.port) ]
    command = [ 'wine', args.python, server_path, '-p', str(args.port) ]

    env = os.environ.copy()
    env["WINEDEBUG"] = "-all"
    
    print("🪬 Launching Iris-MT5-Bridge Server 🪬")
    # preexec_fn=os.setsid is crucial for killing the whole process group
    wine_process = Popen(command, env=env, preexec_fn=os.setsid)
    print(f"✅ Server process started with PID: {wine_process.pid}.\n❎ Press Ctrl+C to stop the server.")

    # The script will now wait here indefinitely until a signal is caught.
    # Our custom handler will then take over and exit the script.
    wine_process.wait()
    print("Shutting down server and wine stuff... Goodbye 👋")


if __name__ == '__main__':
    main()