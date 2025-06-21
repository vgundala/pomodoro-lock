#!/bin/bash

# Build AppImage for Pomodoro Lock
# Copyright © 2024 Vinay Gundala (vg@ivdata.dev)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Get version from setup.py or use default
VERSION=$(python3 setup.py --version 2>/dev/null || echo "1.0.0")
print_status "Building AppImage for version: $VERSION"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run as root"
    exit 1
fi

# Create build directory
BUILD_DIR="build-appimage"
print_status "Creating build directory: $BUILD_DIR"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Create AppDir structure
print_status "Creating AppDir structure..."
mkdir -p "$BUILD_DIR/AppDir/usr/bin"
mkdir -p "$BUILD_DIR/AppDir/usr/lib/python3/dist-packages"
mkdir -p "$BUILD_DIR/AppDir/usr/share/pomodoro-lock/config"
mkdir -p "$BUILD_DIR/AppDir/usr/share/pomodoro-lock/scripts"
mkdir -p "$BUILD_DIR/AppDir/usr/share/applications"
mkdir -p "$BUILD_DIR/AppDir/usr/share/metainfo"
mkdir -p "$BUILD_DIR/AppDir/usr/share/icons/hicolor/256x256/apps"

# Copy application files
print_status "Copying application files..."
cp src/pomodoro-lock.py "$BUILD_DIR/AppDir/usr/bin/"
chmod +x "$BUILD_DIR/AppDir/usr/bin/pomodoro-lock.py"

cp scripts/start-pomodoro.sh "$BUILD_DIR/AppDir/usr/share/pomodoro-lock/scripts/"
chmod +x "$BUILD_DIR/AppDir/usr/share/pomodoro-lock/scripts/start-pomodoro.sh"

cp scripts/configure-pomodoro.py "$BUILD_DIR/AppDir/usr/share/pomodoro-lock/scripts/"
chmod +x "$BUILD_DIR/AppDir/usr/share/pomodoro-lock/scripts/configure-pomodoro.py"

cp config/config.json "$BUILD_DIR/AppDir/usr/share/pomodoro-lock/config/"
cp config/pomodoro-lock.service "$BUILD_DIR/AppDir/usr/share/pomodoro-lock/"

# Copy AppDir files
cp AppDir/AppRun "$BUILD_DIR/AppDir/"
chmod +x "$BUILD_DIR/AppDir/AppRun"

cp AppDir/pomodoro-lock.desktop "$BUILD_DIR/AppDir/usr/share/applications/"
cp AppDir/pomodoro-lock.appdata.xml "$BUILD_DIR/AppDir/usr/share/metainfo/"

# Copy the attractive icon
mkdir -p "$BUILD_DIR/AppDir/usr/share/icons/hicolor/256x256/apps/"
cp AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.svg "$BUILD_DIR/AppDir/usr/share/icons/hicolor/256x256/apps/"

# Also create smaller icon sizes for better compatibility
mkdir -p "$BUILD_DIR/AppDir/usr/share/icons/hicolor/128x128/apps/"
mkdir -p "$BUILD_DIR/AppDir/usr/share/icons/hicolor/64x64/apps/"
mkdir -p "$BUILD_DIR/AppDir/usr/share/icons/hicolor/48x48/apps/"
mkdir -p "$BUILD_DIR/AppDir/usr/share/icons/hicolor/32x32/apps/"
mkdir -p "$BUILD_DIR/AppDir/usr/share/icons/hicolor/16x16/apps/"

# Copy SVG to all sizes (SVG scales automatically)
cp AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.svg "$BUILD_DIR/AppDir/usr/share/icons/hicolor/128x128/apps/"
cp AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.svg "$BUILD_DIR/AppDir/usr/share/icons/hicolor/64x64/apps/"
cp AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.svg "$BUILD_DIR/AppDir/usr/share/icons/hicolor/48x48/apps/"
cp AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.svg "$BUILD_DIR/AppDir/usr/share/icons/hicolor/32x32/apps/"
cp AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.svg "$BUILD_DIR/AppDir/usr/share/icons/hicolor/16x16/apps/"

# Copy PNG icons if they exist (for better compatibility)
if [ -f "AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.png" ]; then
    print_status "Including PNG icons for better compatibility..."
    cp AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.png "$BUILD_DIR/AppDir/usr/share/icons/hicolor/256x256/apps/"
    cp AppDir/usr/share/icons/hicolor/128x128/apps/pomodoro-lock.png "$BUILD_DIR/AppDir/usr/share/icons/hicolor/128x128/apps/" 2>/dev/null || true
    cp AppDir/usr/share/icons/hicolor/64x64/apps/pomodoro-lock.png "$BUILD_DIR/AppDir/usr/share/icons/hicolor/64x64/apps/" 2>/dev/null || true
    cp AppDir/usr/share/icons/hicolor/48x48/apps/pomodoro-lock.png "$BUILD_DIR/AppDir/usr/share/icons/hicolor/48x48/apps/" 2>/dev/null || true
    cp AppDir/usr/share/icons/hicolor/32x32/apps/pomodoro-lock.png "$BUILD_DIR/AppDir/usr/share/icons/hicolor/32x32/apps/" 2>/dev/null || true
    cp AppDir/usr/share/icons/hicolor/16x16/apps/pomodoro-lock.png "$BUILD_DIR/AppDir/usr/share/icons/hicolor/16x16/apps/" 2>/dev/null || true
fi

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --target="$BUILD_DIR/AppDir/usr/lib/python3/dist-packages" psutil python-xlib notify2 PyGObject

# Download and use appimagetool
print_status "Downloading appimagetool..."
APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
APPIMAGETOOL="$BUILD_DIR/appimagetool"

if [ ! -f "$APPIMAGETOOL" ]; then
    wget -O "$APPIMAGETOOL" "$APPIMAGETOOL_URL"
    chmod +x "$APPIMAGETOOL"
fi

# Build AppImage
print_status "Building AppImage..."
APPIMAGE_NAME="Pomodoro_Lock-${VERSION}-x86_64.AppImage"
"$APPIMAGETOOL" "$BUILD_DIR/AppDir" "$APPIMAGE_NAME"

# Clean up
print_status "Cleaning up build directory..."
rm -rf "$BUILD_DIR"

print_success "AppImage built successfully: $APPIMAGE_NAME"
print_status "You can now distribute this AppImage file to users."
print_status "Users can run it directly without installation." 