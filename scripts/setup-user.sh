#!/bin/bash
# Pomodoro Lock User Setup Script
# This script sets up the personal environment for any user

set -e

# Get current user
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)

echo "Setting up Pomodoro Lock for user: $CURRENT_USER"

# Application paths
APP_DIR="/usr/share/pomodoro-lock"
USER_DIR="$USER_HOME/.local/share/pomodoro-lock"
VENV_DIR="$USER_DIR/venv"

# Check if application exists
if [ ! -f "$APP_DIR/pomodoro-ui-crossplatform.py" ]; then
    echo "Error: Pomodoro Lock is not installed in system directory"
    echo "Please install the package first: sudo apt install pomodoro-lock"
    exit 1
fi

# Create user's .local/bin directory for symlinks
echo "Creating executable symlinks..."
mkdir -p "$USER_HOME/.local/bin"
ln -sf /usr/bin/pomodoro-lock "$USER_HOME/.local/bin/pomodoro-lock"
ln -sf /usr/bin/pomodoro-service "$USER_HOME/.local/bin/pomodoro-service"
ln -sf /usr/bin/pomodoro-configure "$USER_HOME/.local/bin/pomodoro-configure"

# Create user's applications directory for desktop file
echo "Installing desktop launcher..."
mkdir -p "$USER_HOME/.local/share/applications"
cp /usr/share/applications/pomodoro-lock.desktop "$USER_HOME/.local/share/applications/"

# Create user's icons directory for icon
echo "Installing application icon..."
mkdir -p "$USER_HOME/.local/share/icons/hicolor/scalable/apps"
cp /usr/share/icons/hicolor/scalable/apps/pomodoro-lock.svg "$USER_HOME/.local/share/icons/hicolor/scalable/apps/"

# Update desktop file to point to system-wide executables
echo "Updating desktop file paths..."
sed -i "s|^Exec=.*|Exec=/usr/bin/pomodoro-lock ui|" "$USER_HOME/.local/share/applications/pomodoro-lock.desktop"
sed -i "s|^Icon=.*|Icon=pomodoro-lock|" "$USER_HOME/.local/share/applications/pomodoro-lock.desktop"

# Create user's systemd directory for service file
echo "Installing systemd service..."
mkdir -p "$USER_HOME/.config/systemd/user"
cp /usr/share/pomodoro-lock/systemd/pomodoro-lock.service "$USER_HOME/.config/systemd/user/"

# Update service file to point to system-wide location
echo "Updating service file paths..."
sed -i "s|ExecStart=.*|ExecStart=/usr/bin/pomodoro-lock ui|" "$USER_HOME/.config/systemd/user/pomodoro-lock.service"
sed -i "s|WorkingDirectory=.*|WorkingDirectory=/usr/share/pomodoro-lock|" "$USER_HOME/.config/systemd/user/pomodoro-lock.service"

# Update icon cache
echo "Updating icon cache..."
gtk-update-icon-cache -f -t "$USER_HOME/.local/share/icons/hicolor" || true

# Reload systemd for the user
echo "Reloading systemd..."
systemctl --user daemon-reload 2>/dev/null || echo "Note: Systemd daemon-reload failed (this is normal)"

echo ""
echo "✅ Pomodoro Lock has been set up for user: $CURRENT_USER"
echo ""
echo "📁 Application location: /usr/share/pomodoro-lock"
echo "🔧 Executables: $USER_HOME/.local/bin/pomodoro-lock"
echo "⚙️  Service: $USER_HOME/.config/systemd/user/pomodoro-lock.service"
echo ""
echo "🚀 To start the application:"
echo "   pomodoro-lock"
echo ""
echo "🔗 Autostart will be enabled automatically on first launch."
echo ""
echo "📋 To configure:"
echo "   pomodoro-configure" 