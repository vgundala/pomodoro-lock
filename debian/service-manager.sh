#!/bin/bash
# Pomodoro Lock Service Manager

set -e

# Function to show usage
show_usage() {
    echo "Pomodoro Lock Service Manager"
    echo "============================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     - Start the service"
    echo "  stop      - Stop the service"
    echo "  restart   - Restart the service"
    echo "  status    - Show service status"
    echo "  enable    - Enable service to start on login"
    echo "  disable   - Disable service from starting on login"
    echo "  logs      - Show service logs"
    echo "  ui        - Start UI client"
    echo "  help      - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 start   # Start the service"
    echo "  $0 ui      # Start UI client"
    echo "  $0 status  # Check service status"
    echo "  $0 logs    # View service logs"
}

# Function to check if service is running
is_service_running() {
    systemctl --user is-active --quiet pomodoro-lock.service
}

# Function to start service
start_service() {
    echo "Starting Pomodoro Lock service..."
    systemctl --user start pomodoro-lock.service
    if is_service_running; then
        echo "✓ Service started successfully"
    else
        echo "✗ Failed to start service"
        exit 1
    fi
}

# Function to stop service
stop_service() {
    echo "Stopping Pomodoro Lock service..."
    systemctl --user stop pomodoro-lock.service
    echo "✓ Service stopped"
}

# Function to restart service
restart_service() {
    echo "Restarting Pomodoro Lock service..."
    systemctl --user restart pomodoro-lock.service
    if is_service_running; then
        echo "✓ Service restarted successfully"
    else
        echo "✗ Failed to restart service"
        exit 1
    fi
}

# Function to show status
show_status() {
    echo "Pomodoro Lock Service Status:"
    echo "============================="
    systemctl --user status pomodoro-lock.service --no-pager
}

# Function to enable service
enable_service() {
    echo "Enabling Pomodoro Lock service..."
    systemctl --user enable pomodoro-lock.service
    echo "✓ Service enabled (will start on login)"
}

# Function to disable service
disable_service() {
    echo "Disabling Pomodoro Lock service..."
    systemctl --user disable pomodoro-lock.service
    echo "✓ Service disabled (will not start on login)"
}

# Function to show logs
show_logs() {
    echo "Pomodoro Lock Service Logs:"
    echo "==========================="
    journalctl --user -u pomodoro-lock.service -f
}

# Function to start UI
start_ui() {
    echo "Starting Pomodoro Lock UI..."
    exec pomodoro-lock ui
}

# Main execution
case "${1:-help}" in
    "start")
        start_service
        ;;
    "stop")
        stop_service
        ;;
    "restart")
        restart_service
        ;;
    "status")
        show_status
        ;;
    "enable")
        enable_service
        ;;
    "disable")
        disable_service
        ;;
    "logs")
        show_logs
        ;;
    "ui")
        start_ui
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac 