#!/bin/bash
# Pomodoro Lock Launcher - System-wide Installation
# This script automatically sets up each user's environment on first run

set -e

# Get current user
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)

# Application paths - system-wide installation
APP_DIR="/usr/share/pomodoro-lock"
MAIN_SCRIPT="$APP_DIR/pomodoro-ui-crossplatform.py"

# Check if application is installed in system directory
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "Error: Pomodoro Lock is not installed in system directory"
    echo "Expected location: $MAIN_SCRIPT"
    echo "Please install the application first"
    exit 1
fi

# User-specific directories
USER_DIR="$USER_HOME/.local/share/pomodoro-lock"
VENV_DIR="$USER_DIR/venv"

# Function to setup user environment on first run
setup_user_environment() {
    echo "First time setup for user: $CURRENT_USER"
    echo "Setting up Pomodoro Lock environment..."
    
    # Create user directory structure
    mkdir -p "$USER_DIR"
    mkdir -p "$USER_HOME/.config/systemd/user"
    
    # Setup virtual environment
    setup_venv
    
    # Setup configuration
    setup_config
    
    # Setup systemd service
    setup_service
    
    echo "✅ User environment setup complete!"
    echo ""
}

# Function to install dependencies in virtual environment
setup_venv() {
    echo "Setting up virtual environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    pip install psutil python-xlib notify2 dbus-python
    
    # Copy system GTK bindings to virtual environment if needed
    VENV_SITE_PACKAGES="$VENV_DIR/lib/python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages"
    
    # Copy gi module from dist-packages if it exists
    SYSTEM_GI_PATH="/usr/lib/python3/dist-packages/gi"
    if [ -d "$SYSTEM_GI_PATH" ] && [ ! -d "$VENV_SITE_PACKAGES/gi" ]; then
        echo "Copying GTK bindings to virtual environment..."
        cp -r "$SYSTEM_GI_PATH" "$VENV_SITE_PACKAGES/"
        # Also copy any .so files that gi depends on
        if [ -f "$SYSTEM_GI_PATH/_gi.so" ]; then
            cp "$SYSTEM_GI_PATH/_gi.so" "$VENV_SITE_PACKAGES/gi/"
        fi
        if [ -f "$SYSTEM_GI_PATH/_gi_cairo.so" ]; then
            cp "$SYSTEM_GI_PATH/_gi_cairo.so" "$VENV_SITE_PACKAGES/gi/"
        fi
    fi
    
    # Copy AppIndicator3 bindings from dist-packages if it exists
    SYSTEM_APPINDICATOR_PATH="/usr/lib/python3/dist-packages/gi/overrides"
    if [ -d "$SYSTEM_APPINDICATOR_PATH" ]; then
        VENV_OVERRIDES="$VENV_SITE_PACKAGES/gi/overrides"
        mkdir -p "$VENV_OVERRIDES"
        if [ ! -f "$VENV_OVERRIDES/AppIndicator3.py" ]; then
            echo "Copying AppIndicator3 bindings to virtual environment..."
            cp "$SYSTEM_APPINDICATOR_PATH/AppIndicator3.py" "$VENV_OVERRIDES/" 2>/dev/null || true
        fi
    fi
    
    # Copy notify2 module from dist-packages if it exists
    SYSTEM_NOTIFY2_PATH="/usr/lib/python3/dist-packages/notify2"
    if [ -d "$SYSTEM_NOTIFY2_PATH" ] && [ ! -d "$VENV_SITE_PACKAGES/notify2" ]; then
        echo "Copying notify2 to virtual environment..."
        cp -r "$SYSTEM_NOTIFY2_PATH" "$VENV_SITE_PACKAGES/"
    fi
    
    echo "Virtual environment setup complete."
}

# Function to create user configuration
setup_config() {
    if [ ! -f "$USER_DIR/config/config.json" ]; then
        echo "Creating user configuration..."
        mkdir -p "$USER_DIR/config"
        cp "$APP_DIR/config/config.json" "$USER_DIR/config/"
    fi
}

# Function to setup systemd service
setup_service() {
    if [ ! -f "$USER_HOME/.config/systemd/user/pomodoro-lock.service" ]; then
        echo "Setting up systemd user service..."
        
        # Create service file with correct paths
        cat > "$USER_HOME/.config/systemd/user/pomodoro-lock.service" << EOF
[Unit]
Description=Pomodoro Lock UI - Standalone Timer Application
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/scripts/start-pomodoro.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical-session.target
EOF
        
        systemctl --user daemon-reload
        echo "Systemd service configured."
    fi
}

# Function to check if user environment is set up
check_user_setup() {
    # Check if key user files exist
    if [ ! -d "$VENV_DIR" ] || \
       [ ! -f "$USER_DIR/config/config.json" ] || \
       [ ! -f "$USER_HOME/.config/systemd/user/pomodoro-lock.service" ]; then
        return 1  # Setup needed
    fi
    return 0  # Setup complete
}

# Function to show help
show_help() {
    echo "Pomodoro Lock Launcher"
    echo "====================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  ui      - Start UI (default)"
    echo "  start   - Alias for ui"
    echo "  service - Start the systemd service"
    echo "  stop    - Stop the systemd service"
    echo "  status  - Show service status"
    echo "  help    - Show this help"
    echo ""
    echo "Installation location: $APP_DIR"
    echo "User directory: $USER_DIR"
    echo "Service file: $USER_HOME/.config/systemd/user/pomodoro-lock.service"
    echo "Autostart will be enabled automatically on first launch."
}

# Function to start the UI
start_ui() {
    echo "Starting Pomodoro Lock UI..."
    echo "Application: $MAIN_SCRIPT"
    
    # Check if already running for this user
    if pgrep -f "pomodoro-ui-crossplatform.py" > /dev/null; then
        echo "Note: Pomodoro Lock appears to be already running"
        echo "The application will handle multiple instance detection and show existing timer window"
    fi
    
    # Activate virtual environment and start the application
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    exec python pomodoro-ui-crossplatform.py
}

# Function to manage systemd service
manage_service() {
    case "$1" in
        "start")
            echo "Starting Pomodoro Lock service..."
            systemctl --user start pomodoro-lock.service
            ;;
        "stop")
            echo "Stopping Pomodoro Lock service..."
            systemctl --user stop pomodoro-lock.service
            ;;
        "status")
            echo "Pomodoro Lock service status:"
            systemctl --user status pomodoro-lock.service --no-pager
            ;;
        *)
            echo "Unknown service command: $1"
            echo "Use: $0 service [start|stop|status]"
            exit 1
            ;;
    esac
}

# Main command handling
case "${1:-ui}" in
    "ui"|"start")
        # Auto-setup user environment if needed
        if ! check_user_setup; then
            setup_user_environment
            echo ""
        fi
        
        # Start the UI
        start_ui
        ;;
    "service")
        # Auto-setup user environment if needed
        if ! check_user_setup; then
            setup_user_environment
            echo ""
        fi
        
        manage_service "${2:-start}"
        ;;
    "stop")
        manage_service "stop"
        ;;
    "status")
        manage_service "status"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use: $0 help"
        exit 1
        ;;
esac 