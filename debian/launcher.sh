#!/bin/bash
# Pomodoro Lock Launcher - Userspace Installation
# This script manages the virtual environment and runs the application

set -e

# Get the installation directory
INSTALL_DIR="/usr/share/pomodoro-lock"
USER_DIR="$HOME/.local/share/pomodoro-lock"
VENV_DIR="$USER_DIR/venv"

# Create user directory if it doesn't exist
mkdir -p "$USER_DIR"

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
    pip install psutil python-xlib
    
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
        cp "$INSTALL_DIR/config/config.json" "$USER_DIR/config/"
    fi
}

# Function to setup systemd service
setup_service() {
    if [ ! -f "$HOME/.config/systemd/user/pomodoro-lock.service" ]; then
        echo "Setting up systemd user service..."
        mkdir -p "$HOME/.config/systemd/user"
        
        # Create service file with correct paths
        cat > "$HOME/.config/systemd/user/pomodoro-lock.service" << EOF
[Unit]
Description=Pomodoro Lock Service with Multi-Display Overlay
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
Environment=DISPLAY=:0
Environment=XAUTHORITY=\$HOME/.Xauthority
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/\$(id -u)/bus
Environment=XDG_RUNTIME_DIR=/run/user/\$(id -u)
WorkingDirectory=$USER_DIR
ExecStart=$VENV_DIR/bin/python3 $INSTALL_DIR/pomodoro-ui.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical-session.target
EOF
        
        systemctl --user daemon-reload
        systemctl --user enable pomodoro-lock.service
        echo "Systemd service configured and enabled."
    fi
}

# Function to start service
start_service() {
    echo "Starting Pomodoro Lock service..."
    systemctl --user start pomodoro-lock.service
    echo "Service started. Use 'systemctl --user status pomodoro-lock.service' to check status."
}

# Function to stop service
stop_service() {
    echo "Stopping Pomodoro Lock service..."
    systemctl --user stop pomodoro-lock.service
    echo "Service stopped."
}

# Function to show service status
show_status() {
    echo "Pomodoro Lock Service Status:"
    systemctl --user status pomodoro-lock.service --no-pager
}

# Function to run UI only
run_ui() {
    echo "Starting Pomodoro Lock UI..."
    source "$VENV_DIR/bin/activate"
    cd "$USER_DIR"
    exec python3 "$INSTALL_DIR/pomodoro-ui.py" "$@"
}

# Main execution
main() {
    # Setup virtual environment
    setup_venv
    
    # Setup user configuration
    setup_config
    
    # Setup systemd service
    setup_service
    
    # Parse command line arguments
    case "${1:-ui}" in
        "service"|"start")
            start_service
            ;;
        "stop")
            stop_service
            ;;
        "status")
            show_status
            ;;
        "ui")
            run_ui
            ;;
        "help"|"-h"|"--help")
            echo "Pomodoro Lock Launcher"
            echo "====================="
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  ui      - Start UI client (default)"
            echo "  service - Start the systemd service"
            echo "  start   - Alias for service"
            echo "  stop    - Stop the systemd service"
            echo "  status  - Show service status"
            echo "  help    - Show this help"
            echo ""
            echo "Examples:"
            echo "  $0              # Start UI client"
            echo "  $0 service      # Start service"
            echo "  $0 ui          # Start UI client"
            echo "  $0 status      # Check service status"
            echo ""
            echo "Architecture:"
            echo "  - Service: Manages timer, notifications, and overlays"
            echo "  - UI: Lightweight display client that reads from service"
            ;;
        *)
            echo "Unknown command: $1"
            echo "Use '$0 help' for usage information."
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 