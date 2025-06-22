#!/bin/bash

# Pomodoro Lock Installer - Service-Based Architecture
# This script installs Pomodoro Lock using the new service/UI separation
# Copyright © 2024 Vinay Gundala (vg@ivdata.dev)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get current user info
CURRENT_USER=$(whoami)
USER_ID=$(id -u)

echo -e "${BLUE}Pomodoro Lock Installer - Service-Based Architecture${NC}"
echo "=========================================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: This installer should not be run as root.${NC}"
    echo "Please run as a regular user."
    exit 1
fi

echo -e "${GREEN}Installing for user: $CURRENT_USER${NC}"
echo ""

# Check system dependencies
echo -e "${BLUE}Checking system dependencies...${NC}"
EXISTING_COUNT=0

# Check Python 3
if command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Python 3: Available ($(python3 --version))${NC}"
    EXISTING_COUNT=$(expr $EXISTING_COUNT + 1)
else
    echo -e "${RED}❌ Python 3: Not found${NC}"
    echo "Please install Python 3: sudo apt-get install python3"
    exit 1
fi

# Check GTK
if python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" 2>/dev/null; then
    echo -e "${GREEN}✅ GTK: Available${NC}"
    EXISTING_COUNT=$(expr $EXISTING_COUNT + 1)
else
    echo -e "${RED}❌ GTK: Not found${NC}"
    echo "Please install GTK: sudo apt-get install python3-gi"
    exit 1
fi

# Check psutil
if python3 -c "import psutil" 2>/dev/null; then
    echo -e "${GREEN}✅ psutil: Available${NC}"
    EXISTING_COUNT=$(expr $EXISTING_COUNT + 1)
else
    echo -e "${YELLOW}⚠️  psutil: Not found (will install in venv)${NC}"
fi

# Check notify2
if python3 -c "import notify2" 2>/dev/null; then
    echo -e "${GREEN}✅ notify2: Available${NC}"
    EXISTING_COUNT=$(expr $EXISTING_COUNT + 1)
else
    echo -e "${YELLOW}⚠️  notify2: Not found (will install in venv)${NC}"
fi

# Check python-xlib
if python3 -c "import Xlib" 2>/dev/null; then
    echo -e "${GREEN}✅ python-xlib: Available${NC}"
    EXISTING_COUNT=$(expr $EXISTING_COUNT + 1)
else
    echo -e "${YELLOW}⚠️  python-xlib: Not found (will install in venv)${NC}"
fi

# Check virtual environment support
if python3 -m venv --help >/dev/null 2>&1; then
    VENV_AVAILABLE=true
    echo -e "${GREEN}✅ python3-venv: Available${NC}"
else
    VENV_AVAILABLE=false
    echo -e "${RED}❌ python3-venv: Not found${NC}"
    echo "Please install: sudo apt-get install python3-venv"
    exit 1
fi

# Create necessary directories
echo ""
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p ~/.local/share/pomodoro-lock/{config,scripts}
mkdir -p ~/.local/bin

# Create virtual environment
echo ""
echo -e "${BLUE}🐍 Creating virtual environment...${NC}"
python3 -m venv ~/.local/share/pomodoro-lock/venv

echo -e "${BLUE}📦 Installing packages in virtual environment...${NC}"
source ~/.local/share/pomodoro-lock/venv/bin/activate
pip install --upgrade pip
pip install psutil python-xlib

# Copy system GTK bindings to virtual environment if needed
VENV_SITE_PACKAGES="$HOME/.local/share/pomodoro-lock/venv/lib/python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages"

# Copy gi module from dist-packages if it exists
SYSTEM_GI_PATH="/usr/lib/python3/dist-packages/gi"
if [ -d "$SYSTEM_GI_PATH" ] && [ ! -d "$VENV_SITE_PACKAGES/gi" ]; then
    echo -e "${BLUE}📋 Copying GTK bindings to virtual environment...${NC}"
    cp -r "$SYSTEM_GI_PATH" "$VENV_SITE_PACKAGES/"
    # Also copy any .so files that gi depends on
    if [ -f "$SYSTEM_GI_PATH/_gi.so" ]; then
        cp "$SYSTEM_GI_PATH/_gi.so" "$VENV_SITE_PACKAGES/gi/"
    fi
    if [ -f "$SYSTEM_GI_PATH/_gi_cairo.so" ]; then
        cp "$SYSTEM_GI_PATH/_gi_cairo.so" "$VENV_SITE_PACKAGES/gi/"
    fi
fi

# Copy notify2 module from dist-packages if it exists
SYSTEM_NOTIFY2_PATH="/usr/lib/python3/dist-packages/notify2"
if [ -d "$SYSTEM_NOTIFY2_PATH" ] && [ ! -d "$VENV_SITE_PACKAGES/notify2" ]; then
    echo -e "${BLUE}📋 Copying notify2 to virtual environment...${NC}"
    cp -r "$SYSTEM_NOTIFY2_PATH" "$VENV_SITE_PACKAGES/"
fi

# Copy application files
echo ""
echo -e "${BLUE}📋 Installing application files...${NC}"
cp src/pomodoro-service.py ~/.local/share/pomodoro-lock/
cp src/pomodoro-ui.py ~/.local/share/pomodoro-lock/
cp src/pomodoro-lock.py ~/.local/share/pomodoro-lock/  # Keep for reference

if [ ! -f ~/.local/share/pomodoro-lock/config/config.json ]; then
    echo -e "${BLUE}📄 Creating default configuration...${NC}"
    cp config/config.json ~/.local/share/pomodoro-lock/config/
fi

cp scripts/configure-pomodoro.py ~/.local/share/pomodoro-lock/
chmod +x ~/.local/share/pomodoro-lock/configure-pomodoro.py

# Create launcher scripts
echo -e "${BLUE}🔧 Creating launcher scripts...${NC}"
cat > ~/.local/bin/pomodoro-lock << 'EOF'
#!/bin/bash
# Pomodoro Lock Launcher
source ~/.local/share/pomodoro-lock/venv/bin/activate
cd ~/.local/share/pomodoro-lock

case "${1:-ui}" in
    "service"|"start")
        echo "Starting Pomodoro Lock service..."
        exec python3 pomodoro-service.py
        ;;
    "ui")
        echo "Starting Pomodoro Lock UI..."
        exec python3 pomodoro-ui.py
        ;;
    "stop")
        echo "Stopping Pomodoro Lock service..."
        systemctl --user stop pomodoro-lock.service
        ;;
    "status")
        echo "Service status:"
        systemctl --user status pomodoro-lock.service
        ;;
    "help"|"-h"|"--help")
        echo "Pomodoro Lock Launcher"
        echo "====================="
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  ui      - Start UI client (default)"
        echo "  service - Start the service"
        echo "  start   - Alias for service"
        echo "  stop    - Stop the service"
        echo "  status  - Show service status"
        echo "  help    - Show this help"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac
EOF

cat > ~/.local/bin/pomodoro-configure << 'EOF'
#!/bin/bash
source ~/.local/share/pomodoro-lock/venv/bin/activate
cd ~/.local/share/pomodoro-lock
exec python3 configure-pomodoro.py "$@"
EOF

chmod +x ~/.local/bin/pomodoro-lock
chmod +x ~/.local/bin/pomodoro-configure

# Install desktop file for application menu
echo ""
echo -e "${BLUE}🔧 Installing application launcher...${NC}"
mkdir -p ~/.local/share/applications/
cp debian/pomodoro-lock.desktop ~/.local/share/applications/pomodoro-lock.desktop
# Update Exec to point to the user's local bin
sed -i "s|^Exec=.*|Exec=$HOME/.local/bin/pomodoro-lock ui|" ~/.local/share/applications/pomodoro-lock.desktop
# Update Icon to be an absolute path
sed -i "s|^Icon=.*|Icon=$PWD/pomodoro-lock.svg|" ~/.local/share/applications/pomodoro-lock.desktop

# Setup systemd service
echo ""
echo -e "${BLUE}🔧 Installing systemd service...${NC}"
mkdir -p ~/.config/systemd/user/

# Copy the service template and replace %h with the actual home directory
cp config/pomodoro-lock.service ~/.config/systemd/user/pomodoro-lock.service
sed -i "s|%h|$HOME|g" ~/.config/systemd/user/pomodoro-lock.service

# Enable and start service
systemctl --user daemon-reload
systemctl --user enable pomodoro-lock.service

echo ""
echo -e "${BLUE}🚀 Starting service...${NC}"
systemctl --user start pomodoro-lock.service

# Launch UI in the background
echo -e "${BLUE}🚀 Launching UI...${NC}"
if [ -f "$HOME/.local/bin/pomodoro-lock" ]; then
    nohup "$HOME/.local/bin/pomodoro-lock" ui >/dev/null 2>&1 &
fi

# Final output
echo ""
echo -e "${GREEN}🎉 Installation Complete!${NC}"
echo "========================"
echo ""
echo -e "${GREEN}✅ Pomodoro Lock has been installed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Service Management:${NC}"
echo "  Start:   systemctl --user start pomodoro-lock.service"
echo "  Stop:    systemctl --user stop pomodoro-lock.service"
echo "  Status:  systemctl --user status pomodoro-lock.service"
echo "  Logs:    journalctl --user -u pomodoro-lock.service -f"
echo ""
echo -e "${BLUE}🔧 Convenience Commands:${NC}"
echo "  UI:      pomodoro-lock ui"
echo "  Service: pomodoro-lock service"
echo "  Config:  pomodoro-configure"
echo ""
echo -e "${BLUE}📁 Files:${NC}"
echo "  Config:  ~/.local/share/pomodoro-lock/config/config.json"
echo "  Venv:    ~/.local/share/pomodoro-lock/venv/"
echo ""
echo -e "${BLUE}🏗️  Architecture:${NC}"
echo "  - Service: Manages timer, notifications, and overlays"
echo "  - UI: Lightweight display client that reads from service"
echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo "  - Add ~/.local/bin to your PATH if not already there:"
echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo -e "${GREEN}🌐 The service will start automatically on login.${NC}"
echo ""
echo -e "${BLUE}❓ Need help? Check: https://github.com/vgundala/pomodoro-lock#readme${NC}" 