#!/bin/bash

echo "Uninstalling Pomodoro Lock..."

# Stop and disable the service
echo "Stopping service..."
systemctl --user stop pomodoro-lock.service 2>/dev/null || true
systemctl --user disable pomodoro-lock.service 2>/dev/null || true

# Stop any running instances
echo "Stopping Pomodoro Lock UI..."
pkill -TERM -f "pomodoro-ui.py" 2>/dev/null || true

# Wait a moment for graceful shutdown
sleep 2

# Force kill if still running
echo "Force stopping any remaining processes..."
pkill -KILL -f "pomodoro-ui.py" 2>/dev/null || true

# Remove service file
echo "Removing service file..."
rm -f ~/.config/systemd/user/pomodoro-lock.service
systemctl --user daemon-reload

# Remove application files
echo "Removing application files..."
rm -rf ~/.local/share/pomodoro-lock/

# Remove installed icon
echo "Removing application icon..."
rm -f ~/.local/share/icons/hicolor/scalable/apps/pomodoro-lock.svg
gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor || true

# Remove desktop launcher
echo "Removing application launcher..."
rm -f ~/.local/share/applications/pomodoro-lock.desktop

echo "✅ Pomodoro Lock has been completely uninstalled. All files and processes have been removed." 