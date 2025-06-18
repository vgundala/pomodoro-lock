#!/bin/bash

# Exit on error
set -e

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run as root"
    exit 1
fi

# Create necessary directories
mkdir -p ~/.local/share/pomodoro-lock/{bin,config,scripts}

# Install dependencies
echo "Installing dependencies..."
#sudo apt-get update
sudo apt-get install -y python3-gi python3-psutil python3-xlib

# Copy files to their locations
echo "Installing Pomodoro Lock..."
cp pomodoro-lock.py ~/.local/share/pomodoro-lock/bin/
chmod +x ~/.local/share/pomodoro-lock/bin/pomodoro-lock.py

# Install systemd service
echo "Installing systemd service..."
cp pomodoro-lock.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable pomodoro-lock.service

echo "Installation complete!"
echo "To start the service, run: systemctl --user start pomodoro-lock.service"
echo "To check status, run: systemctl --user status pomodoro-lock.service"
echo "Configuration file is located at: ~/.local/share/pomodoro-lock/config/config.json" 