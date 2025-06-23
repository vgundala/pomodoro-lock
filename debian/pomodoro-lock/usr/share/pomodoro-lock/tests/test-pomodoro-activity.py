#!/usr/bin/env python3
"""
Test script to verify pomodoro timer pausing functionality
"""

import os
import sys
import time
import subprocess
import signal
import json

def test_pomodoro_activity():
    """Test the pomodoro application with activity detection"""
    print("Testing Pomodoro Activity Detection")
    print("=" * 50)
    
    # Start the pomodoro application
    print("Starting pomodoro application...")
    process = subprocess.Popen(
        [sys.executable, 'src/pomodoro-ui.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait a moment for the app to start
        time.sleep(3)
        
        print("✓ Pomodoro application started")
        print("\nTest Instructions:")
        print("1. You should see a timer window in the bottom-left corner")
        print("2. The timer should be running (white text)")
        print("3. Stay inactive for 1 minute (configured inactivity threshold)")
        print("4. The timer should pause and turn yellow")
        print("5. Move your mouse or type to resume the timer")
        print("6. The timer should resume and turn white again")
        print("\nPress Ctrl+C to stop the test")
        
        # Monitor the process
        while process.poll() is None:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nStopping pomodoro application...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("✓ Pomodoro application stopped")
        
    except Exception as e:
        print(f"Error during test: {e}")
        process.terminate()
        
    print("\nTest completed!")

def test_config_inactivity():
    """Test the inactivity threshold configuration"""
    print("\nTesting Inactivity Configuration")
    print("=" * 50)
    
    # Use the project's config file
    config_path = 'config/config.json'
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"Current inactivity threshold: {config.get('inactivity_threshold_minutes', 'Not set')} minutes")
        print(f"Work time: {config.get('work_time_minutes', 'Not set')} minutes")
        print(f"Break time: {config.get('break_time_minutes', 'Not set')} minutes")
        
        # Test with a shorter inactivity threshold for testing
        test_config = config.copy()
        test_config['inactivity_threshold_minutes'] = 1  # 1 minute for testing
        test_config['work_time_minutes'] = 5  # 5 minutes for testing
        test_config['break_time_minutes'] = 2  # 2 minutes for testing
        test_config['notification_time_minutes'] = 1  # 1 minute for testing
        
        print(f"\nSetting test configuration:")
        print(f"- Inactivity threshold: 1 minute")
        print(f"- Work time: 5 minutes")
        print(f"- Break time: 2 minutes")
        print(f"- Notification time: 1 minute")
        
        # Save test config
        with open(config_path, 'w') as f:
            json.dump(test_config, f, indent=4)
            
        print("✓ Test configuration saved")
        print("Now run the pomodoro app to test with 1-minute inactivity threshold")
        
    else:
        print("No configuration file found. Creating default config...")
        default_config = {
            "work_time_minutes": 5,
            "break_time_minutes": 2,
            "notification_time_minutes": 1,
            "inactivity_threshold_minutes": 1
        }
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
            
        print("✓ Default configuration created with 1-minute inactivity threshold")

def main():
    print("Pomodoro Activity Detection Test Suite")
    print("=" * 60)
    
    # Test 1: Configuration
    test_config_inactivity()
    
    # Test 2: Application
    print("\n" + "=" * 60)
    test_pomodoro_activity()
    
    print("\n" + "=" * 60)
    print("All tests completed!")

if __name__ == "__main__":
    main() 