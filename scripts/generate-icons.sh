#!/bin/bash

# Generate PNG icons from SVG for Pomodoro Lock
# Requires: inkscape or rsvg-convert

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

# Check for required tools
if command -v inkscape >/dev/null 2>&1; then
    CONVERTER="inkscape"
    INKSCAPE_OPTS="--export-type=png --export-filename"
elif command -v rsvg-convert >/dev/null 2>&1; then
    CONVERTER="rsvg-convert"
    RSVG_OPTS="-w"
else
    print_error "Neither inkscape nor rsvg-convert found. Please install one of them:"
    echo "  sudo apt-get install inkscape"
    echo "  sudo apt-get install librsvg2-bin"
    exit 1
fi

print_status "Using $CONVERTER to generate PNG icons..."

# Create icon directories
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps/
mkdir -p AppDir/usr/share/icons/hicolor/128x128/apps/
mkdir -p AppDir/usr/share/icons/hicolor/64x64/apps/
mkdir -p AppDir/usr/share/icons/hicolor/48x48/apps/
mkdir -p AppDir/usr/share/icons/hicolor/32x32/apps/
mkdir -p AppDir/usr/share/icons/hicolor/16x16/apps/

# Generate PNG icons
SVG_SOURCE="AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.svg"

if [ "$CONVERTER" = "inkscape" ]; then
    print_status "Generating 256x256 PNG..."
    inkscape $INKSCAPE_OPTS AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.png -w 256 -h 256 "$SVG_SOURCE"
    
    print_status "Generating 128x128 PNG..."
    inkscape $INKSCAPE_OPTS AppDir/usr/share/icons/hicolor/128x128/apps/pomodoro-lock.png -w 128 -h 128 "$SVG_SOURCE"
    
    print_status "Generating 64x64 PNG..."
    inkscape $INKSCAPE_OPTS AppDir/usr/share/icons/hicolor/64x64/apps/pomodoro-lock.png -w 64 -h 64 "$SVG_SOURCE"
    
    print_status "Generating 48x48 PNG..."
    inkscape $INKSCAPE_OPTS AppDir/usr/share/icons/hicolor/48x48/apps/pomodoro-lock.png -w 48 -h 48 "$SVG_SOURCE"
    
    print_status "Generating 32x32 PNG..."
    inkscape $INKSCAPE_OPTS AppDir/usr/share/icons/hicolor/32x32/apps/pomodoro-lock.png -w 32 -h 32 "$SVG_SOURCE"
    
    print_status "Generating 16x16 PNG..."
    inkscape $INKSCAPE_OPTS AppDir/usr/share/icons/hicolor/16x16/apps/pomodoro-lock.png -w 16 -h 16 "$SVG_SOURCE"
    
elif [ "$CONVERTER" = "rsvg-convert" ]; then
    print_status "Generating 256x256 PNG..."
    rsvg-convert $RSVG_OPTS 256 -h 256 -o AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.png "$SVG_SOURCE"
    
    print_status "Generating 128x128 PNG..."
    rsvg-convert $RSVG_OPTS 128 -h 128 -o AppDir/usr/share/icons/hicolor/128x128/apps/pomodoro-lock.png "$SVG_SOURCE"
    
    print_status "Generating 64x64 PNG..."
    rsvg-convert $RSVG_OPTS 64 -h 64 -o AppDir/usr/share/icons/hicolor/64x64/apps/pomodoro-lock.png "$SVG_SOURCE"
    
    print_status "Generating 48x48 PNG..."
    rsvg-convert $RSVG_OPTS 48 -h 48 -o AppDir/usr/share/icons/hicolor/48x48/apps/pomodoro-lock.png "$SVG_SOURCE"
    
    print_status "Generating 32x32 PNG..."
    rsvg-convert $RSVG_OPTS 32 -h 32 -o AppDir/usr/share/icons/hicolor/32x32/apps/pomodoro-lock.png "$SVG_SOURCE"
    
    print_status "Generating 16x16 PNG..."
    rsvg-convert $RSVG_OPTS 16 -h 16 -o AppDir/usr/share/icons/hicolor/16x16/apps/pomodoro-lock.png "$SVG_SOURCE"
fi

print_success "All PNG icons generated successfully!"
print_status "Icons are now available in multiple sizes for better compatibility." 