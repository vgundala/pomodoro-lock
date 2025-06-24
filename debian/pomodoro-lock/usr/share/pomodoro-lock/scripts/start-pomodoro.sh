#!/bin/bash

# Pomodoro Lock - Start Script
# This script starts the Pomodoro Lock application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current user
CURRENT_USER=$(whoami)
USER_ID=$(id -u)

echo -e "${GREEN}Pomodoro Lock - Start Script${NC}"
echo "=================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: This script should not be run as root${NC}"
    echo "Please run as a regular user"
    exit 1
fi

# Check if application is installed
if [ ! -f "/usr/share/pomodoro-lock/pomodoro-ui-crossplatform.py" ]; then
    echo -e "${RED}Error: Pomodoro Lock is not installed${NC}"
    echo "Please install the application first"
    exit 1
fi

# Set the script path to the cross-platform UI
SCRIPT_PATH="/usr/share/pomodoro-lock/pomodoro-ui-crossplatform.py"

echo "Starting Pomodoro Lock..."
echo "Application: $SCRIPT_PATH"

# Check if already running
if pgrep -f "pomodoro-ui-crossplatform.py" > /dev/null; then
    echo -e "${YELLOW}Warning: Pomodoro Lock is already running${NC}"
    echo "Stopping existing instance..."
    pkill -f "pomodoro-ui-crossplatform.py"
    sleep 2
fi

# Start the application
echo "Launching Pomodoro Lock..."
cd /usr/share/pomodoro-lock
exec python3 pomodoro-ui-crossplatform.py 