#!/bin/bash

# Pomodoro Lock Uninstaller - System-wide Installation
# This script removes Pomodoro Lock from system-wide locations
# Copyright © 2024 Vinay Gundala (vg@ivdata.dev)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation paths
INSTALL_DIR="/usr/share/pomodoro-lock"
BIN_DIR="/usr/bin"
DESKTOP_DIR="/usr/share/applications"
ICON_DIR="/usr/share/icons/hicolor/scalable/apps"

echo -e "${BLUE}Pomodoro Lock Uninstaller - System-wide Installation${NC}"
echo "========================================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This uninstaller must be run as root for system-wide removal.${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

echo -e "${GREEN}Uninstalling Pomodoro Lock...${NC}"
echo ""

# Stop and disable all pomodoro-related services for all users
echo -e "${BLUE}🛑 Stopping services for all users...${NC}"

# Get all users with home directories
USERS=$(cut -d: -f1,6 /etc/passwd | grep -E ":/home/" | cut -d: -f1)

for USER in $USERS; do
    if [ -d "/home/$USER" ]; then
        echo "Stopping services for user: $USER"
        # Stop service if running
        sudo -u "$USER" systemctl --user stop pomodoro-lock.service 2>/dev/null || true
        # Disable service
        sudo -u "$USER" systemctl --user disable pomodoro-lock.service 2>/dev/null || true
        # Reload systemd
        sudo -u "$USER" systemctl --user daemon-reload 2>/dev/null || true
        # Clean up lingering systemd state
        sudo -u "$USER" systemctl --user reset-failed 2>/dev/null || true
    fi
done

# Stop any running instances
echo -e "${BLUE}🛑 Stopping any running instances...${NC}"
pkill -TERM -f "pomodoro-ui-crossplatform.py" 2>/dev/null || true

# Wait a moment for graceful shutdown
sleep 2

# Force kill if still running
echo -e "${BLUE}🛑 Force stopping any remaining processes...${NC}"
pkill -KILL -f "pomodoro-ui-crossplatform.py" 2>/dev/null || true

# Remove system-wide files
echo -e "${BLUE}🗑️  Removing system-wide files...${NC}"

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing: $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
fi

# Remove system binaries
echo -e "${BLUE}🔧 Removing system binaries...${NC}"
rm -f "$BIN_DIR/pomodoro-lock"
rm -f "$BIN_DIR/pomodoro-configure"
rm -f "$BIN_DIR/pomodoro-service"

# Remove desktop file
echo -e "${BLUE}🖥️  Removing desktop launcher...${NC}"
rm -f "$DESKTOP_DIR/pomodoro-lock.desktop"

# Remove icon
echo -e "${BLUE}🎨 Removing application icon...${NC}"
rm -f "$ICON_DIR/pomodoro-lock.svg"

# Update icon cache
echo -e "${BLUE}🔄 Updating icon cache...${NC}"
gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true

# Remove user-specific files for all users
echo -e "${BLUE}👥 Removing user-specific files...${NC}"

for USER in $USERS; do
    if [ -d "/home/$USER" ]; then
        echo "Cleaning up for user: $USER"
        # Stop service if running
        sudo -u "$USER" systemctl --user stop pomodoro-lock.service 2>/dev/null || true
        # Disable service before removing
        sudo -u "$USER" systemctl --user disable pomodoro-lock.service 2>/dev/null || true
        # Remove user service files
        rm -f "/home/$USER/.config/systemd/user/pomodoro-lock.service"
        
        # Remove user application files
        rm -rf "/home/$USER/.local/share/pomodoro-lock"
        
        # Remove user symlinks
        rm -f "/home/$USER/.local/bin/pomodoro-lock"
        rm -f "/home/$USER/.local/bin/pomodoro-configure"
        rm -f "/home/$USER/.local/bin/pomodoro-service"
        
        # Remove user desktop file
        rm -f "/home/$USER/.local/share/applications/pomodoro-lock.desktop"
        
        # Remove user icons
        rm -f "/home/$USER/.local/share/icons/hicolor/scalable/apps/pomodoro-lock.svg"
        
        # Update user icon cache
        gtk-update-icon-cache -f -t "/home/$USER/.local/share/icons/hicolor" 2>/dev/null || true
        # Clean up lingering systemd state
        sudo -u "$USER" systemctl --user daemon-reload 2>/dev/null || true
        sudo -u "$USER" systemctl --user reset-failed 2>/dev/null || true
    fi
done

# Remove current user's files (in case not in /home/)
CURRENT_USER=$(who am i | awk '{print $1}')
if [ -n "$CURRENT_USER" ] && [ "$CURRENT_USER" != "root" ]; then
    echo "Cleaning up for current user: $CURRENT_USER"
    # Stop service if running
    sudo -u "$CURRENT_USER" systemctl --user stop pomodoro-lock.service 2>/dev/null || true
    # Disable service before removing
    sudo -u "$CURRENT_USER" systemctl --user disable pomodoro-lock.service 2>/dev/null || true
    # Remove user service files
    rm -f "/home/$CURRENT_USER/.config/systemd/user/pomodoro-lock.service"
    
    # Remove user application files
    rm -rf "/home/$CURRENT_USER/.local/share/pomodoro-lock"
    
    # Remove user symlinks
    rm -f "/home/$CURRENT_USER/.local/bin/pomodoro-lock"
    rm -f "/home/$CURRENT_USER/.local/bin/pomodoro-configure"
    rm -f "/home/$CURRENT_USER/.local/bin/pomodoro-service"
    
    # Remove user desktop file
    rm -f "/home/$CURRENT_USER/.local/share/applications/pomodoro-lock.desktop"
    
    # Remove user icons
    rm -f "/home/$CURRENT_USER/.local/share/icons/hicolor/scalable/apps/pomodoro-lock.svg"
    
    # Update user icon cache
    gtk-update-icon-cache -f -t "/home/$CURRENT_USER/.local/share/icons/hicolor" 2>/dev/null || true
    # Clean up lingering systemd state
    sudo -u "$CURRENT_USER" systemctl --user daemon-reload 2>/dev/null || true
    sudo -u "$CURRENT_USER" systemctl --user reset-failed 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}✅ Pomodoro Lock has been completely uninstalled!${NC}"
echo ""
echo -e "${BLUE}🗑️  Removed:${NC}"
echo "   • System-wide installation: $INSTALL_DIR"
echo "   • System binaries: $BIN_DIR/pomodoro-*"
echo "   • Desktop launcher: $DESKTOP_DIR/pomodoro-lock.desktop"
echo "   • Application icon: $ICON_DIR/pomodoro-lock.svg"
echo "   • User-specific files for all users"
echo "   • All running processes and services"
echo ""
echo -e "${GREEN}🎉 Uninstallation complete!${NC}" 