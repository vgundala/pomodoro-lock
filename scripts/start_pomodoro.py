#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    """
    Python wrapper to execute the start-pomodoro.sh script.
    This allows it to be used as a setuptools entry point.
    """
    # Find the absolute path to the .sh script, which should be in the same directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "start-pomodoro.sh")

    if not os.path.exists(script_path):
        print(f"Error: start-pomodoro.sh not found at {script_path}", file=sys.stderr)
        sys.exit(1)

    # Pass all command-line arguments to the shell script
    process = subprocess.run([script_path] + sys.argv[1:], check=False)
    sys.exit(process.returncode)

if __name__ == "__main__":
    main() 