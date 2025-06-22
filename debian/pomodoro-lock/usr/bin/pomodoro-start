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

# Try to get DBUS_SESSION_BUS_ADDRESS and XDG_RUNTIME_DIR more robustly
# First try from systemctl, but don't fail if it doesn't work
if command -v systemctl >/dev/null 2>&1; then
    DBUS_ENV_VARS=$(systemctl --user show-environment 2>/dev/null | grep -E "(DBUS_SESSION_BUS_ADDRESS|XDG_RUNTIME_DIR)=" || true)
    if [ -n "$DBUS_ENV_VARS" ]; then
        eval "$DBUS_ENV_VARS"
        export DBUS_SESSION_BUS_ADDRESS
        export XDG_RUNTIME_DIR
        echo "Found DBUS_SESSION_BUS_ADDRESS: $DBUS_SESSION_BUS_ADDRESS"
        echo "Found XDG_RUNTIME_DIR: $XDG_RUNTIME_DIR"
    fi
fi

# Fallback: try to get from process environment
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ] || [ -z "$XDG_RUNTIME_DIR" ]; then
    echo "Trying to get environment from running processes..."
    
    # Try to get from a running process
    if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
        DBUS_ENV=$(ps e -o command | grep -E "dbus-daemon.*session" | head -1 | grep -o "DBUS_SESSION_BUS_ADDRESS=[^[:space:]]*" || true)
        if [ -n "$DBUS_ENV" ]; then
            export $DBUS_ENV
            echo "Found DBUS_SESSION_BUS_ADDRESS from process: $DBUS_SESSION_BUS_ADDRESS"
        fi
    fi
    
    if [ -z "$XDG_RUNTIME_DIR" ]; then
        export XDG_RUNTIME_DIR="/run/user/$USER_ID"
        echo "Set XDG_RUNTIME_DIR to: $XDG_RUNTIME_DIR"
    fi
fi

# Final fallback: use default values
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$USER_ID/bus"
    echo "Using default DBUS_SESSION_BUS_ADDRESS: $DBUS_SESSION_BUS_ADDRESS"
fi

if [ -z "$XDG_RUNTIME_DIR" ]; then
    export XDG_RUNTIME_DIR="/run/user/$USER_ID"
    echo "Using default XDG_RUNTIME_DIR: $XDG_RUNTIME_DIR"
fi

export GTK_THEME=Adwaita
export GDK_SCALE=1
export GDK_DPI_SCALE=1

# Change to working directory
cd "/home/$CURRENT_USER/.local/share/pomodoro-lock"

echo "Starting Pomodoro Lock service..."
exec python3 "$SCRIPT_PATH" 