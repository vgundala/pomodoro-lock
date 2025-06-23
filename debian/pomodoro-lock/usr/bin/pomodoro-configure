#!/bin/bash
# Pomodoro Lock Configuration Script - Userspace Installation

set -e

# Get the installation directory
INSTALL_DIR="/usr/share/pomodoro-lock"
USER_DIR="$HOME/.local/share/pomodoro-lock"
CONFIG_FILE="$USER_DIR/config/config.json"

# Function to show current configuration
show_config() {
    if [ -f "$CONFIG_FILE" ]; then
        echo "Current configuration:"
        cat "$CONFIG_FILE" | python3 -m json.tool
    else
        echo "No configuration file found. Run the application first to create one."
    fi
}

# Function to apply preset configuration
apply_preset() {
    local preset="$1"
    local work_time
    local break_time
    
    case "$preset" in
        "standard")
            work_time=25
            break_time=5
            echo "Applying standard preset (25/5)..."
            ;;
        "long")
            work_time=45
            break_time=15
            echo "Applying long preset (45/15)..."
            ;;
        "short")
            work_time=15
            break_time=3
            echo "Applying short preset (15/3)..."
            ;;
        *)
            echo "Unknown preset: $preset"
            echo "Available presets: standard, long, short"
            exit 1
            ;;
    esac
    
    # Create config directory if it doesn't exist
    mkdir -p "$(dirname "$CONFIG_FILE")"
    
    # Create configuration file
    cat > "$CONFIG_FILE" << EOF
{
    "work_time_minutes": $work_time,
    "break_time_minutes": $break_time,
    "notification_time_minutes": 2,
    "inactivity_threshold_minutes": 10
}
EOF
    
    echo "Configuration updated successfully."
}

# Function to interactive configuration
interactive_config() {
    echo "Pomodoro Lock Configuration"
    echo "==========================="
    echo ""
    
    # Get current values or defaults
    if [ -f "$CONFIG_FILE" ]; then
        WORK_TIME=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['work_time_minutes'])")
        BREAK_TIME=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['break_time_minutes'])")
        NOTIFICATION_TIME=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['notification_time_minutes'])")
        INACTIVITY_THRESHOLD=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['inactivity_threshold_minutes'])")
    else
        WORK_TIME=25
        BREAK_TIME=5
        NOTIFICATION_TIME=2
        INACTIVITY_THRESHOLD=10
    fi
    
    echo "Current settings:"
    echo "  Work time: ${WORK_TIME} minutes"
    echo "  Break time: ${BREAK_TIME} minutes"
    echo "  Notification time: ${NOTIFICATION_TIME} minutes before break"
    echo "  Inactivity threshold: ${INACTIVITY_THRESHOLD} minutes"
    echo ""
    
    read -p "Work time in minutes [$WORK_TIME]: " new_work_time
    read -p "Break time in minutes [$BREAK_TIME]: " new_break_time
    read -p "Notification time in minutes [$NOTIFICATION_TIME]: " new_notification_time
    read -p "Inactivity threshold in minutes [$INACTIVITY_THRESHOLD]: " new_inactivity_threshold
    
    # Use new values or defaults
    WORK_TIME=${new_work_time:-$WORK_TIME}
    BREAK_TIME=${new_break_time:-$BREAK_TIME}
    NOTIFICATION_TIME=${new_notification_time:-$NOTIFICATION_TIME}
    INACTIVITY_THRESHOLD=${new_inactivity_threshold:-$INACTIVITY_THRESHOLD}
    
    # Create config directory if it doesn't exist
    mkdir -p "$(dirname "$CONFIG_FILE")"
    
    # Create configuration file
    cat > "$CONFIG_FILE" << EOF
{
    "work_time_minutes": $WORK_TIME,
    "break_time_minutes": $BREAK_TIME,
    "notification_time_minutes": $NOTIFICATION_TIME,
    "inactivity_threshold_minutes": $INACTIVITY_THRESHOLD
}
EOF
    
    echo ""
    echo "Configuration saved successfully!"
    echo "New settings:"
    echo "  Work time: ${WORK_TIME} minutes"
    echo "  Break time: ${BREAK_TIME} minutes"
    echo "  Notification time: ${NOTIFICATION_TIME} minutes before break"
    echo "  Inactivity threshold: ${INACTIVITY_THRESHOLD} minutes"
}

# Main execution
case "${1:-interactive}" in
    "show")
        show_config
        ;;
    "standard"|"long"|"short")
        apply_preset "$1"
        ;;
    "interactive")
        interactive_config
        ;;
    *)
        echo "Usage: $0 [show|standard|long|short|interactive]"
        echo ""
        echo "Commands:"
        echo "  show        - Show current configuration"
        echo "  standard    - Apply standard preset (25/5)"
        echo "  long        - Apply long preset (45/15)"
        echo "  short       - Apply short preset (15/3)"
        echo "  interactive - Interactive configuration (default)"
        exit 1
        ;;
esac 