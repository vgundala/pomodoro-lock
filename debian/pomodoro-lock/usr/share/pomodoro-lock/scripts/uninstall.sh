#!/bin/bash

echo "Uninstalling Pomodoro Lock..."

# Stop and disable all pomodoro-related services
echo "Stopping services..."
systemctl --user stop pomodoro-lock.service 2>/dev/null || true
systemctl --user disable pomodoro-lock.service 2>/dev/null || true
systemctl --user stop pomodoro.service 2>/dev/null || true
systemctl --user disable pomodoro.service 2>/dev/null || true

# Stop any running instances
echo "Stopping Pomodoro Lock UI..."
pkill -TERM -f "pomodoro-ui-crossplatform.py" 2>/dev/null || true
pkill -TERM -f "pomodoro-ui.py" 2>/dev/null || true
pkill -TERM -f "pomodoro" 2>/dev/null || true

# Wait a moment for graceful shutdown
sleep 2

# Force kill if still running
echo "Force stopping any remaining processes..."
pkill -KILL -f "pomodoro-ui-crossplatform.py" 2>/dev/null || true
pkill -KILL -f "pomodoro-ui.py" 2>/dev/null || true
pkill -KILL -f "pomodoro" 2>/dev/null || true

# Remove service files from all possible locations
echo "Removing service files..."
rm -f ~/.config/systemd/user/pomodoro-lock.service
rm -f ~/.config/systemd/user/pomodoro.service
rm -f /etc/systemd/user/pomodoro-lock.service
rm -f /etc/systemd/user/pomodoro.service
rm -f /usr/lib/systemd/user/pomodoro-lock.service
rm -f /usr/lib/systemd/user/pomodoro.service

# Reload systemd daemon
systemctl --user daemon-reload

# Remove application files from all possible locations
echo "Removing application files..."
rm -rf ~/.local/share/pomodoro-lock/
rm -rf ~/.local/share/pomodoro/
rm -rf ~/AppData/Local/pomodoro-lock/ 2>/dev/null || true

# Remove installed icons
echo "Removing application icons..."
rm -f ~/.local/share/icons/hicolor/scalable/apps/pomodoro-lock.svg
rm -f ~/.local/share/icons/hicolor/*/apps/pomodoro-lock.*
rm -f ~/.local/share/icons/hicolor/*/apps/appimagekit_*_pomodoro-lock.*
rm -f ~/.local/share/icons/Fluent/scalable/apps/org.gnome.Pomodoro.svg
rm -f ~/.local/share/icons/Fluent/scalable/apps/gnome-pomodoro.svg
rm -f ~/.local/share/icons/Fluent/scalable/apps/Pomodoro.svg
gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor || true

# Remove desktop launcher
echo "Removing application launcher..."
rm -f ~/.local/share/applications/pomodoro-lock.desktop
rm -f /usr/share/applications/pomodoro-lock.desktop 2>/dev/null || true

# Remove binaries/symlinks
echo "Removing binaries..."
rm -f ~/.local/bin/pomodoro-configure
rm -f ~/.local/bin/pomodoro-lock
rm -f /usr/bin/pomodoro-configure 2>/dev/null || true
rm -f /usr/bin/pomodoro-lock 2>/dev/null || true
rm -f /usr/bin/pomodoro-service 2>/dev/null || true

# Remove deb package files if installed
echo "Removing deb package files..."
rm -rf /usr/share/pomodoro-lock/ 2>/dev/null || true

echo "✅ Pomodoro Lock has been completely uninstalled. All files and processes have been removed." 