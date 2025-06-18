#!/bin/bash

# Exit on error
set -e

echo "Installing Pomodoro Lock as a desktop application..."

# Create necessary directories
INSTALL_DIR="$HOME/.local/share/pomodoro-lock"
BIN_DIR="$INSTALL_DIR/bin"
CONFIG_DIR="$INSTALL_DIR/config"
DESKTOP_DIR="$HOME/.local/share/applications"

mkdir -p "$BIN_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$DESKTOP_DIR"

# Copy the Python script
echo "Copying application files..."
cp pomodoro-lock.py "$BIN_DIR/"

# Create default config if it doesn't exist
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    echo "Creating default configuration..."
    cat > "$CONFIG_DIR/config.json" << EOL
{
    "work_time_minutes": 30,
    "break_time_minutes": 5,
    "notification_time_minutes": 2,
    "inactivity_threshold_minutes": 10
}
EOL
fi

# Create desktop entry
echo "Creating desktop entry..."
cat > "$DESKTOP_DIR/pomodoro-lock.desktop" << EOL
[Desktop Entry]
Type=Application
Name=Pomodoro Lock
Comment=Work-break timer with screen lock
Exec=python3 $BIN_DIR/pomodoro-lock.py
Icon=alarm-clock
Terminal=false
Categories=Utility;
EOL

# Make the script executable
chmod +x "$BIN_DIR/pomodoro-lock.py"

echo "Installation complete!"
echo "You can now run Pomodoro Lock from your application launcher or by running:"
echo "python3 $BIN_DIR/pomodoro-lock.py" 