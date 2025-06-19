#!/usr/bin/env python3

import json
import os
import sys

def load_config():
    """Load the current configuration"""
    config_path = os.path.expanduser('~/.local/share/pomodoro-lock/config/config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "work_time_minutes": 30,
            "break_time_minutes": 5,
            "notification_time_minutes": 2,
            "inactivity_threshold_minutes": 10
        }

def save_config(config):
    """Save the configuration to file"""
    config_path = os.path.expanduser('~/.local/share/pomodoro-lock/config/config.json')
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Configuration saved to: {config_path}")

def display_current_config(config):
    """Display the current configuration"""
    print("\nCurrent Configuration:")
    print("=" * 40)
    print(f"Work Time:           {config['work_time_minutes']} minutes")
    print(f"Break Time:          {config['break_time_minutes']} minutes")
    print(f"Notification Time:   {config['notification_time_minutes']} minutes before break")
    print(f"Inactivity Threshold: {config['inactivity_threshold_minutes']} minutes")
    print("=" * 40)

def get_user_input(prompt, current_value, min_value=1, max_value=120):
    """Get user input with validation"""
    while True:
        try:
            value = input(f"{prompt} (current: {current_value}): ").strip()
            if not value:  # User pressed Enter, keep current value
                return current_value
            
            value = int(value)
            if min_value <= value <= max_value:
                return value
            else:
                print(f"Please enter a value between {min_value} and {max_value}")
        except ValueError:
            print("Please enter a valid number")

def configure_interactive():
    """Interactive configuration"""
    config = load_config()
    
    print("Pomodoro Lock Configuration")
    print("=" * 40)
    display_current_config(config)
    
    print("\nEnter new values (press Enter to keep current value):")
    
    config['work_time_minutes'] = get_user_input(
        "Work time (minutes)", 
        config['work_time_minutes'], 
        1, 120
    )
    
    config['break_time_minutes'] = get_user_input(
        "Break time (minutes)", 
        config['break_time_minutes'], 
        1, 60
    )
    
    config['notification_time_minutes'] = get_user_input(
        "Notification time (minutes before break)", 
        config['notification_time_minutes'], 
        1, 10
    )
    
    config['inactivity_threshold_minutes'] = get_user_input(
        "Inactivity threshold (minutes)", 
        config['inactivity_threshold_minutes'], 
        1, 60
    )
    
    print("\nNew Configuration:")
    display_current_config(config)
    
    save = input("\nSave this configuration? (y/n): ").lower().strip()
    if save in ['y', 'yes']:
        save_config(config)
        print("Configuration saved successfully!")
    else:
        print("Configuration not saved.")

def configure_preset(preset_name):
    """Configure using preset values"""
    presets = {
        'standard': {
            "work_time_minutes": 25,
            "break_time_minutes": 5,
            "notification_time_minutes": 2,
            "inactivity_threshold_minutes": 10
        },
        'long': {
            "work_time_minutes": 45,
            "break_time_minutes": 15,
            "notification_time_minutes": 3,
            "inactivity_threshold_minutes": 15
        },
        'short': {
            "work_time_minutes": 15,
            "break_time_minutes": 3,
            "notification_time_minutes": 1,
            "inactivity_threshold_minutes": 5
        },
        'custom': {
            "work_time_minutes": 30,
            "break_time_minutes": 5,
            "notification_time_minutes": 2,
            "inactivity_threshold_minutes": 10
        }
    }
    
    if preset_name not in presets:
        print(f"Unknown preset: {preset_name}")
        print("Available presets: standard, long, short, custom")
        return
    
    config = presets[preset_name]
    print(f"\nApplying {preset_name} preset:")
    display_current_config(config)
    
    save = input("\nSave this configuration? (y/n): ").lower().strip()
    if save in ['y', 'yes']:
        save_config(config)
        print("Configuration saved successfully!")
    else:
        print("Configuration not saved.")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'show':
            config = load_config()
            display_current_config(config)
        elif command in ['standard', 'long', 'short', 'custom']:
            configure_preset(command)
        elif command == 'help':
            print("Pomodoro Lock Configuration Tool")
            print("=" * 40)
            print("Usage:")
            print("  python3 configure-pomodoro.py          # Interactive configuration")
            print("  python3 configure-pomodoro.py show     # Show current configuration")
            print("  python3 configure-pomodoro.py standard # Apply standard preset (25/5)")
            print("  python3 configure-pomodoro.py long     # Apply long preset (45/15)")
            print("  python3 configure-pomodoro.py short    # Apply short preset (15/3)")
            print("  python3 configure-pomodoro.py custom   # Apply custom preset (30/5)")
            print("  python3 configure-pomodoro.py help     # Show this help")
            print("\nPresets:")
            print("  standard: 25 min work, 5 min break")
            print("  long:     45 min work, 15 min break")
            print("  short:    15 min work, 3 min break")
            print("  custom:   30 min work, 5 min break")
        else:
            print(f"Unknown command: {command}")
            print("Run 'python3 configure-pomodoro.py help' for usage information")
    else:
        configure_interactive()

if __name__ == "__main__":
    main() 