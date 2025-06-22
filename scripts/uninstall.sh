#!/bin/bash

echo "Uninstalling Pomodoro Lock..."

# Stop and disable the service
echo "Stopping service..."
systemctl --user stop pomodoro-lock.service 2>/dev/null || true
systemctl --user disable pomodoro-lock.service 2>/dev/null || true

# Kill processes more gracefully
echo "Stopping running processes..."
pkill -TERM -f "pomodoro-ui.py" 2>/dev/null || true
pkill -TERM -f "test-system-tray.py" 2>/dev/null || true
pkill -TERM -f "pomodoro-service.py" 2>/dev/null || true

# Wait a moment for graceful shutdown
sleep 1

# Force kill if still running
echo "Force stopping any remaining processes..."
pkill -KILL -f "pomodoro-ui.py" 2>/dev/null || true
pkill -KILL -f "test-system-tray.py" 2>/dev/null || true
pkill -KILL -f "pomodoro-service.py" 2>/dev/null || true

# Remove service file
echo "Removing service file..."
rm -f ~/.config/systemd/user/pomodoro-lock.service
systemctl --user daemon-reload

# Remove application files
echo "Removing application files..."
rm -rf ~/.local/share/pomodoro-lock/

echo "✅ Pomodoro Lock has been completely uninstalled. All files and processes have been removed." 