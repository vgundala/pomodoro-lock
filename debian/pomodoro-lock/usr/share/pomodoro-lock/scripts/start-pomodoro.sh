#!/bin/bash
# Pomodoro Lock Startup Script for Systemd Service
# This script activates the virtual environment and starts the application

set -e

# Get current user
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)

# Application paths
APP_DIR="/usr/share/pomodoro-lock"
USER_DIR="$USER_HOME/.local/share/pomodoro-lock"
VENV_DIR="$USER_DIR/venv"
MAIN_SCRIPT="$APP_DIR/pomodoro-ui-crossplatform.py"

# Check if application exists
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "Error: Pomodoro Lock is not installed in system directory"
    echo "Expected location: $MAIN_SCRIPT"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR"
    echo "Please run 'pomodoro-lock' first to set up the environment"
    exit 1
fi

# Activate virtual environment and start the application
cd "$APP_DIR"
source "$VENV_DIR/bin/activate"
exec python pomodoro-ui-crossplatform.py 