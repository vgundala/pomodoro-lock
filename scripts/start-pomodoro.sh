#!/bin/bash

# Pomodoro Lock Startup Script
# This script ensures proper initialization before starting the pomodoro service

set -e

# Get current user info
CURRENT_USER=$(whoami)
USER_ID=$(id -u)

echo "Starting Pomodoro Lock for user: $CURRENT_USER"

# Wait for display to be ready
echo "Waiting for display to be ready..."
until xset q >/dev/null 2>&1; do
    echo "Display not ready, waiting..."
    sleep 2
done
echo "Display is ready!"

# Wait a bit more for everything to settle
sleep 5

# Check if the script exists
SCRIPT_PATH="/home/$CURRENT_USER/.local/share/pomodoro-lock/bin/pomodoro-lock.py"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Pomodoro script not found at $SCRIPT_PATH"
    exit 1
fi

# Set environment variables
export DISPLAY=:0
export XAUTHORITY="/home/$CURRENT_USER/.Xauthority"
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$USER_ID/bus"
export XDG_RUNTIME_DIR="/run/user/$USER_ID"
export GTK_THEME=Adwaita
export GDK_SCALE=1
export GDK_DPI_SCALE=1

# Change to working directory
cd "/home/$CURRENT_USER/.local/share/pomodoro-lock"

echo "Starting Pomodoro Lock service..."
exec python3 "$SCRIPT_PATH" 