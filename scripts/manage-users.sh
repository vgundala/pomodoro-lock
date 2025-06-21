#!/bin/bash

# Pomodoro Lock User Management Script
# Copyright © 2024 Vinay Gundala (vg@ivdata.dev)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if running as root
if [ $EUID -ne 0 ]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Function to show usage
show_usage() {
    echo "Pomodoro Lock User Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [USERNAME]"
    echo ""
    echo "Commands:"
    echo "  add USERNAME     - Add Pomodoro Lock service for a user"
    echo "  remove USERNAME  - Remove Pomodoro Lock service for a user"
    echo "  list             - List all users with Pomodoro Lock service"
    echo "  status USERNAME  - Check service status for a user"
    echo "  start USERNAME   - Start service for a user"
    echo "  stop USERNAME    - Stop service for a user"
    echo "  restart USERNAME - Restart service for a user"
    echo "  logs USERNAME    - Show logs for a user's service"
    echo ""
    echo "Examples:"
    echo "  $0 add john"
    echo "  $0 remove jane"
    echo "  $0 list"
    echo "  $0 status john"
}

# Function to add user
add_user() {
    local username=$1
    
    if [ -z "$username" ]; then
        print_error "Username is required"
        exit 1
    fi
    
    # Check if user exists
    if ! id "$username" &>/dev/null; then
        print_error "User '$username' does not exist"
        exit 1
    fi
    
    print_status "Adding Pomodoro Lock service for user: $username"
    
    # Create user directories
    mkdir -p /home/$username/.local/share/pomodoro-lock/{bin,config,scripts}
    mkdir -p /home/$username/.config/pomodoro-lock
    
    # Copy user-specific files
    cp src/pomodoro-lock.py /home/$username/.local/share/pomodoro-lock/bin/
    cp scripts/start-pomodoro.sh /home/$username/.local/share/pomodoro-lock/
    cp scripts/configure-pomodoro.py /home/$username/.local/share/pomodoro-lock/
    
    # Copy default config if it doesn't exist
    if [ ! -f /home/$username/.local/share/pomodoro-lock/config/config.json ]; then
        cp config/config.json /home/$username/.local/share/pomodoro-lock/config/
    fi
    
    # Set proper ownership
    chown -R $username:$username /home/$username/.local/share/pomodoro-lock
    chown -R $username:$username /home/$username/.config/pomodoro-lock
    chmod +x /home/$username/.local/share/pomodoro-lock/bin/pomodoro-lock.py
    chmod +x /home/$username/.local/share/pomodoro-lock/start-pomodoro.sh
    chmod +x /home/$username/.local/share/pomodoro-lock/configure-pomodoro.py
    
    # Create desktop shortcut
    mkdir -p /home/$username/.local/share/applications
    cat > /home/$username/.local/share/applications/pomodoro-lock.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Pomodoro Lock
Comment=Multi-display Pomodoro timer with screen overlay
Exec=pomodoro-configure
Icon=appointment
Terminal=false
Categories=Utility;Productivity;
Keywords=pomodoro;timer;productivity;focus;
EOF
    
    chown $username:$username /home/$username/.local/share/applications/pomodoro-lock.desktop
    
    # Enable and start service
    systemctl enable pomodoro-lock@$username.service
    systemctl start pomodoro-lock@$username.service
    
    print_success "Added Pomodoro Lock service for user: $username"
}

# Function to remove user
remove_user() {
    local username=$1
    
    if [ -z "$username" ]; then
        print_error "Username is required"
        exit 1
    fi
    
    print_status "Removing Pomodoro Lock service for user: $username"
    
    # Stop and disable service
    systemctl stop pomodoro-lock@$username.service 2>/dev/null || true
    systemctl disable pomodoro-lock@$username.service 2>/dev/null || true
    
    # Remove service file
    rm -f /etc/systemd/system/pomodoro-lock@$username.service
    
    # Remove user directories (optional - ask first)
    printf "Remove user directories for %s? (y/N): " "$username"
    read -r REPLY
    if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
        rm -rf /home/$username/.local/share/pomodoro-lock
        rm -rf /home/$username/.config/pomodoro-lock
        rm -f /home/$username/.local/share/applications/pomodoro-lock.desktop
        print_success "Removed user directories for: $username"
    else
        print_warning "User directories preserved for: $username"
    fi
    
    print_success "Removed Pomodoro Lock service for user: $username"
}

# Function to list users
list_users() {
    print_status "Users with Pomodoro Lock service:"
    echo ""
    
    # Find all service files
    for service_file in /etc/systemd/system/pomodoro-lock@*.service; do
        if [ -f "$service_file" ]; then
            username=$(basename "$service_file" | sed 's/pomodoro-lock@\(.*\)\.service/\1/')
            status=$(systemctl is-active pomodoro-lock@$username.service 2>/dev/null || echo "unknown")
            enabled=$(systemctl is-enabled pomodoro-lock@$username.service 2>/dev/null || echo "unknown")
            
            echo "• $username (Status: $status, Enabled: $enabled)"
        fi
    done
    
    if [ ! -f /etc/systemd/system/pomodoro-lock@*.service ]; then
        print_warning "No users found with Pomodoro Lock service"
    fi
}

# Function to check service status
check_status() {
    local username=$1
    
    if [ -z "$username" ]; then
        print_error "Username is required"
        exit 1
    fi
    
    print_status "Service status for user: $username"
    echo ""
    systemctl status pomodoro-lock@$username.service
}

# Function to start service
start_service() {
    local username=$1
    
    if [ -z "$username" ]; then
        print_error "Username is required"
        exit 1
    fi
    
    print_status "Starting service for user: $username"
    systemctl start pomodoro-lock@$username.service
    print_success "Started service for user: $username"
}

# Function to stop service
stop_service() {
    local username=$1
    
    if [ -z "$username" ]; then
        print_error "Username is required"
        exit 1
    fi
    
    print_status "Stopping service for user: $username"
    systemctl stop pomodoro-lock@$username.service
    print_success "Stopped service for user: $username"
}

# Function to restart service
restart_service() {
    local username=$1
    
    if [ -z "$username" ]; then
        print_error "Username is required"
        exit 1
    fi
    
    print_status "Restarting service for user: $username"
    systemctl restart pomodoro-lock@$username.service
    print_success "Restarted service for user: $username"
}

# Function to show logs
show_logs() {
    local username=$1
    
    if [ -z "$username" ]; then
        print_error "Username is required"
        exit 1
    fi
    
    print_status "Showing logs for user: $username"
    echo "Press Ctrl+C to exit"
    echo ""
    journalctl -u pomodoro-lock@$username.service -f
}

# Main script logic
case "${1:-}" in
    "add")
        add_user "$2"
        ;;
    "remove")
        remove_user "$2"
        ;;
    "list")
        list_users
        ;;
    "status")
        check_status "$2"
        ;;
    "start")
        start_service "$2"
        ;;
    "stop")
        stop_service "$2"
        ;;
    "restart")
        restart_service "$2"
        ;;
    "logs")
        show_logs "$2"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac 