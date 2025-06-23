#!/bin/bash

# Exit on error
set -e

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run as root"
    exit 1
fi

# Get current user
CURRENT_USER=$(whoami)
USER_ID=$(id -u)

echo "=========================================="
echo "Pomodoro Lock - Desktop Installation"
echo "=========================================="
echo "Installing for user: $CURRENT_USER (UID: $USER_ID)"
echo ""

# Check if we're in a desktop environment
if [ -z "$DISPLAY" ]; then
    echo "Error: No display detected. Please run this from a desktop environment."
    exit 1
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p ~/.local/share/pomodoro-lock/{bin,config,scripts}

# Install dependencies
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y python3-gi python3-psutil python3-xlib python3-notify2

# Copy files to their locations
echo "Installing Pomodoro Lock..."
cp src/pomodoro-lock.py ~/.local/share/pomodoro-lock/bin/
chmod +x ~/.local/share/pomodoro-lock/bin/pomodoro-lock.py

# Copy startup script
cp scripts/start-pomodoro.sh ~/.local/share/pomodoro-lock/
chmod +x ~/.local/share/pomodoro-lock/start-pomodoro.sh

# Copy default config if it doesn't exist
if [ ! -f ~/.local/share/pomodoro-lock/config/config.json ]; then
    echo "Creating default configuration..."
    cp config/config.json ~/.local/share/pomodoro-lock/config/
fi

# Copy configuration script
cp scripts/configure-pomodoro.py ~/.local/share/pomodoro-lock/
chmod +x ~/.local/share/pomodoro-lock/configure-pomodoro.py

# Update systemd service with correct user and paths
echo "Installing systemd service..."
cp config/pomodoro-lock.service ~/.config/systemd/user/

# Update the service file with correct user and paths
sed -i "s/User=vinay/User=$CURRENT_USER/g" ~/.config/systemd/user/pomodoro-lock.service
sed -i "s/Group=vinay/Group=$CURRENT_USER/g" ~/.config/systemd/user/pomodoro-lock.service
sed -i "s|/home/vinay|/home/$CURRENT_USER|g" ~/.config/systemd/user/pomodoro-lock.service
sed -i "s|/run/user/1000|/run/user/$USER_ID|g" ~/.config/systemd/user/pomodoro-lock.service

# Reload systemd and enable service
systemctl --user daemon-reload
systemctl --user enable pomodoro-lock.service

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Service Management Commands:"
echo "  Start service:     systemctl --user start pomodoro-lock.service"
echo "  Stop service:      systemctl --user stop pomodoro-lock.service"
echo "  Check status:      systemctl --user status pomodoro-lock.service"
echo "  View logs:         journalctl --user -u pomodoro-lock.service -f"
echo ""
echo "Configuration:"
echo "  Config file:       ~/.local/share/pomodoro-lock/config/config.json"
echo "  Log file:          ~/.local/share/pomodoro-lock/pomodoro.log"
echo ""
echo "The service will start automatically on login."
echo ""
echo "Would you like to start the service now? (y/n)"
read -r response
if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    echo "Starting Pomodoro Lock service..."
    systemctl --user start pomodoro-lock.service
    echo "Service started! Check status with: systemctl --user status pomodoro-lock.service"
else
    echo "To start the service later, run: systemctl --user start pomodoro-lock.service"
fi 