#!/bin/bash

# Pomodoro Lock Installer - System-wide Installation
# This script installs Pomodoro Lock to system-wide locations
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

echo -e "${BLUE}Pomodoro Lock Installer - System-wide Installation${NC}"
echo "======================================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This installer must be run as root for system-wide installation.${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

echo -e "${GREEN}Installing Pomodoro Lock system-wide...${NC}"
echo ""

# Check system dependencies
echo -e "${BLUE}Checking system dependencies...${NC}"

# Check Python 3
if command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Python 3: Available ($(python3 --version))${NC}"
else
    echo -e "${RED}❌ Python 3: Not found${NC}"
    echo "Please install Python 3: sudo apt-get install python3"
    exit 1
fi

# Check GTK
if python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" 2>/dev/null; then
    echo -e "${GREEN}✅ GTK: Available${NC}"
else
    echo -e "${RED}❌ GTK: Not found${NC}"
    echo "Please install GTK: sudo apt-get install python3-gi"
    exit 1
fi

# Check virtual environment support
if python3 -m venv --help >/dev/null 2>&1; then
    echo -e "${GREEN}✅ python3-venv: Available${NC}"
else
    echo -e "${RED}❌ python3-venv: Not found${NC}"
    echo "Please install: sudo apt-get install python3-venv"
    exit 1
fi

# Check if already installed
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠️  Pomodoro Lock appears to be already installed in $INSTALL_DIR${NC}"
    read -p "Do you want to reinstall? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    echo -e "${BLUE}Removing existing installation...${NC}"
    rm -rf "$INSTALL_DIR"
fi

# Create installation directories
echo ""
echo -e "${BLUE}📁 Creating installation directories...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$INSTALL_DIR/scripts"
mkdir -p "$INSTALL_DIR/systemd"
mkdir -p "$INSTALL_DIR/docs"
mkdir -p "$INSTALL_DIR/tests"

# Copy source files
echo -e "${BLUE}📋 Copying application files...${NC}"
cp src/pomodoro-ui-crossplatform.py "$INSTALL_DIR/"
cp -r src/platform_abstraction/ "$INSTALL_DIR/"
cp -r src/gui/ "$INSTALL_DIR/"
cp scripts/configure-pomodoro.py "$INSTALL_DIR/scripts/"
cp config/config.json "$INSTALL_DIR/config/"
cp config/pomodoro-lock.service "$INSTALL_DIR/systemd/"
cp pomodoro-lock.svg "$INSTALL_DIR/"
cp README.md "$INSTALL_DIR/docs/"
cp LICENSE "$INSTALL_DIR/docs/"

# Copy test files
echo -e "${BLUE}🧪 Copying test files...${NC}"
cp -r tests/* "$INSTALL_DIR/tests/" 2>/dev/null || true

# Make scripts executable
chmod +x "$INSTALL_DIR/scripts/configure-pomodoro.py"

# Create launcher scripts
echo -e "${BLUE}🔧 Creating launcher scripts...${NC}"

# Copy the launcher scripts from debian directory
cp debian/launcher.sh "$BIN_DIR/pomodoro-lock"
cp debian/pomodoro-lock/usr/bin/pomodoro-configure "$BIN_DIR/pomodoro-configure"
cp debian/pomodoro-lock/usr/bin/pomodoro-service "$BIN_DIR/pomodoro-service"

# Make launcher scripts executable
chmod +x "$BIN_DIR/pomodoro-lock"
chmod +x "$BIN_DIR/pomodoro-configure"
chmod +x "$BIN_DIR/pomodoro-service"

# Create desktop file
echo -e "${BLUE}🖥️  Creating desktop launcher...${NC}"
cat > "$DESKTOP_DIR/pomodoro-lock.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Pomodoro Lock
Comment=Focus timer with screen overlay
Exec=/usr/bin/pomodoro-lock ui
Icon=pomodoro-lock
Terminal=false
Categories=Utility;TimeManagement;
Keywords=pomodoro;timer;focus;productivity;
EOF

# Install icon
echo -e "${BLUE}🎨 Installing application icon...${NC}"
mkdir -p "$ICON_DIR"
cp pomodoro-lock.svg "$ICON_DIR/"

# Update icon cache
echo -e "${BLUE}🔄 Updating icon cache...${NC}"
gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true

echo ""
echo -e "${GREEN}✅ Pomodoro Lock has been installed successfully!${NC}"
echo ""
echo -e "${BLUE}📁 Installation location: $INSTALL_DIR${NC}"
echo -e "${BLUE}🔧 Executables: $BIN_DIR/pomodoro-lock${NC}"
echo -e "${BLUE}🖥️  Desktop launcher: $DESKTOP_DIR/pomodoro-lock.desktop${NC}"
echo ""
echo -e "${GREEN}🚀 To start the application:${NC}"
echo "   pomodoro-lock"
echo ""
echo -e "${GREEN}📋 To configure:${NC}"
echo "   pomodoro-configure"
echo ""
echo -e "${GREEN}⚙️  To manage service:${NC}"
echo "   pomodoro-service"
echo ""
echo -e "${YELLOW}📝 Note: Each user's environment will be set up automatically on first run.${NC}"
echo -e "${YELLOW}   This includes virtual environment, configuration, and systemd service.${NC}"
echo ""
echo -e "${GREEN}🎉 Installation complete!${NC}" 