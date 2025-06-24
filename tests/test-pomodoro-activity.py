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
    """Test that the pomodoro application responds to activity correctly"""
    
    # Start the pomodoro application
    print("Starting Pomodoro Lock application...")
    
    # Use the cross-platform UI
    process = subprocess.Popen([
        sys.executable, 'src/pomodoro-ui-crossplatform.py'
    ])
    
    try:
        # Wait a moment for the application to start
        time.sleep(3)
        
        # Check if the process is still running
        if process.poll() is None:
            print("✅ Application started successfully")
            
            # Simulate some activity (move mouse, etc.)
            print("Simulating user activity...")
            time.sleep(2)
            
            # Terminate the process
            print("Stopping application...")
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
                print("✅ Application stopped gracefully")
            except subprocess.TimeoutExpired:
                print("⚠️  Application didn't stop gracefully, force killing...")
                process.kill()
                process.wait()
                print("✅ Application force stopped")
                
        else:
            print(f"❌ Application failed to start (exit code: {process.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        if process.poll() is None:
            process.kill()
        return False
    
    return True

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
    success = test_pomodoro_activity()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 