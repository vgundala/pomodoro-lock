#!/bin/bash

# Pomodoro Lock System Installation Script
# Copyright © 2024 Vinay Gundala (vg@ivdata.dev)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Installing Pomodoro Lock as system service..."

# Get the current user (who invoked sudo)
CURRENT_USER=${SUDO_USER:-$USER}
if [[ -z "$CURRENT_USER" ]]; then
    print_error "Could not determine current user"
    exit 1
fi

print_status "Installing for user: $CURRENT_USER"

# Install system dependencies
print_status "Installing system dependencies..."
apt-get update
apt-get install -y python3-gi python3-psutil python3-xlib python3-notify2

# Create system directories
print_status "Creating system directories..."
mkdir -p /usr/local/bin
mkdir -p /usr/local/share/pomodoro-lock/{config,scripts}
mkdir -p /etc/pomodoro-lock
mkdir -p /etc/systemd/system

# Copy files to system locations
print_status "Installing application files..."
cp src/pomodoro-lock.py /usr/local/bin/
chmod +x /usr/local/bin/pomodoro-lock.py

# Copy startup script
cp scripts/start-pomodoro.sh /usr/local/share/pomodoro-lock/
chmod +x /usr/local/share/pomodoro-lock/start-pomodoro.sh

# Copy configuration script
cp scripts/configure-pomodoro.py /usr/local/share/pomodoro-lock/
chmod +x /usr/local/share/pomodoro-lock/configure-pomodoro.py

# Copy default config
cp config/config.json /etc/pomodoro-lock/

# Create user-specific directories
print_status "Setting up user directories..."
mkdir -p /home/$CURRENT_USER/.local/share/pomodoro-lock/{bin,config,scripts}
mkdir -p /home/$CURRENT_USER/.config/pomodoro-lock

# Copy user-specific files
cp src/pomodoro-lock.py /home/$CURRENT_USER/.local/share/pomodoro-lock/bin/
cp scripts/start-pomodoro.sh /home/$CURRENT_USER/.local/share/pomodoro-lock/
cp scripts/configure-pomodoro.py /home/$CURRENT_USER/.local/share/pomodoro-lock/
cp config/config.json /home/$CURRENT_USER/.local/share/pomodoro-lock/config/

# Set proper ownership
chown -R $CURRENT_USER:$CURRENT_USER /home/$CURRENT_USER/.local/share/pomodoro-lock
chown -R $CURRENT_USER:$CURRENT_USER /home/$CURRENT_USER/.config/pomodoro-lock
chmod +x /home/$CURRENT_USER/.local/share/pomodoro-lock/bin/pomodoro-lock.py
chmod +x /home/$CURRENT_USER/.local/share/pomodoro-lock/start-pomodoro.sh
chmod +x /home/$CURRENT_USER/.local/share/pomodoro-lock/configure-pomodoro.py

# Install systemd service
print_status "Installing systemd service..."
cp config/pomodoro-lock-system.service /etc/systemd/system/pomodoro-lock@$CURRENT_USER.service

# Enable and start the service
print_status "Enabling and starting service..."
systemctl daemon-reload
systemctl enable pomodoro-lock@$CURRENT_USER.service
systemctl start pomodoro-lock@$CURRENT_USER.service

# Create desktop shortcuts
print_status "Creating desktop shortcuts..."
mkdir -p /usr/local/share/applications
cat > /usr/local/share/applications/pomodoro-lock.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Pomodoro Lock
Comment=Multi-display Pomodoro timer with screen overlay
Exec=pomodoro-configure
Icon=appointment
Terminal=false
Categories=Utility;Productivity;
Keywords=pomodoro;timer;productivity;focus;
EOF

# Create user-specific desktop shortcut
mkdir -p /home/$CURRENT_USER/.local/share/applications
cat > /home/$CURRENT_USER/.local/share/applications/pomodoro-lock.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Pomodoro Lock
Comment=Multi-display Pomodoro timer with screen overlay
Exec=pomodoro-configure
Icon=appointment
Terminal=false
Categories=Utility;Productivity;
Keywords=pomodoro;timer;productivity;focus;
EOF

chown $CURRENT_USER:$CURRENT_USER /home/$CURRENT_USER/.local/share/applications/pomodoro-lock.desktop

# Create symlinks for easy access
print_status "Creating command shortcuts..."
ln -sf /usr/local/share/pomodoro-lock/configure-pomodoro.py /usr/local/bin/pomodoro-configure
ln -sf /usr/local/share/pomodoro-lock/start-pomodoro.sh /usr/local/bin/pomodoro-start

# Check service status
print_status "Checking service status..."
if systemctl is-active --quiet pomodoro-lock@$CURRENT_USER.service; then
    print_success "Pomodoro Lock system service is running!"
else
    print_warning "Service may not be running. Check status with: systemctl status pomodoro-lock@$CURRENT_USER.service"
fi

print_success "Pomodoro Lock has been installed as a system service!"
echo ""
echo "Installation Summary:"
echo "====================="
echo "• Application: /usr/local/bin/pomodoro-lock.py"
echo "• Configuration: /etc/pomodoro-lock/config.json"
echo "• User Config: /home/$CURRENT_USER/.local/share/pomodoro-lock/config/config.json"
echo "• Service: pomodoro-lock@$CURRENT_USER.service"
echo "• Desktop Shortcut: /usr/local/share/applications/pomodoro-lock.desktop"
echo ""
echo "Available Commands:"
echo "=================="
echo "• pomodoro-configure  - Configure the application"
echo "• pomodoro-start      - Start the service manually"
echo ""
echo "Service Management:"
echo "=================="
echo "• Check status: systemctl status pomodoro-lock@$CURRENT_USER.service"
echo "• Start service: systemctl start pomodoro-lock@$CURRENT_USER.service"
echo "• Stop service: systemctl stop pomodoro-lock@$CURRENT_USER.service"
echo "• Restart service: systemctl restart pomodoro-lock@$CURRENT_USER.service"
echo "• View logs: journalctl -u pomodoro-lock@$CURRENT_USER.service -f"
echo ""
echo "Next Steps:"
echo "==========="
echo "1. Configure the application: pomodoro-configure"
echo "2. The service will start automatically on login"
echo "3. For more users, run: sudo systemctl enable pomodoro-lock@USERNAME.service"
echo ""
print_success "Installation complete!" 