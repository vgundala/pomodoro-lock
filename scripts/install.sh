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

echo "Installing Pomodoro Lock for user: $CURRENT_USER (UID: $USER_ID)"

# Create necessary directories
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

# Choose service file based on environment
echo "Detecting desktop environment..."
if [ -n "$XDG_CURRENT_DESKTOP" ]; then
    echo "Desktop environment: $XDG_CURRENT_DESKTOP"
    SERVICE_FILE="config/pomodoro-lock.service"
else
    echo "No specific desktop environment detected, using simple service"
    SERVICE_FILE="config/pomodoro-lock-simple.service"
fi

# Install systemd service
echo "Installing systemd service: $SERVICE_FILE"
cp "$SERVICE_FILE" ~/.config/systemd/user/pomodoro-lock.service

# Update the service file with correct user and paths
sed -i "s/User=vinay/User=$CURRENT_USER/g" ~/.config/systemd/user/pomodoro-lock.service
sed -i "s|/home/vinay|/home/$CURRENT_USER|g" ~/.config/systemd/user/pomodoro-lock.service
sed -i "s|/run/user/1000|/run/user/$USER_ID|g" ~/.config/systemd/user/pomodoro-lock.service

# Reload systemd and enable service
systemctl --user daemon-reload
systemctl --user enable pomodoro-lock.service

# Start the service automatically
echo "Starting Pomodoro Lock service..."
systemctl --user start pomodoro-lock.service

echo "Installation complete!"
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
echo "The service is now running and will start automatically on login." 