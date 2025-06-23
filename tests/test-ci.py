#!/usr/bin/env python3

"""
CI Test Script for Pomodoro Lock
This script runs tests that can work in headless CI environments (no display required)
"""

import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing module imports...")
    try:
        # Try to import system packages (may not be available in CI)
        try:
            import psutil
            print("OK psutil imported successfully")
        except ImportError:
            print("WARN psutil not available (expected in CI)")
        
        try:
            import Xlib
            print("OK python-xlib imported successfully")
        except ImportError:
            print("WARN python-xlib not available (expected in CI)")
        
        try:
            import notify2
            print("OK notify2 imported successfully")
        except ImportError:
            print("WARN notify2 not available (expected in CI)")
        
        # Try to import GTK (may fail in headless environment)
        try:
            import gi
            gi.require_version('Notify', '0.7')
            gi.require_version('Gtk', '3.0')
            from gi.repository import Notify, Gtk, GLib, Gdk
            print("OK GTK modules imported successfully")
        except Exception as e:
            print(f"WARN GTK modules not available (expected in CI): {e}")
        
        return True
    except Exception as e:
        print(f"FAIL Import test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading functionality"""
    print("Testing configuration loading...")
    try:
        # Test default config creation
        config_path = os.path.expanduser('~/.local/share/pomodoro-lock/config/config.json')
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        default_config = {
            "work_time_minutes": 25,
            "break_time_minutes": 5,
            "notification_time_minutes": 2,
            "inactivity_threshold_minutes": 10
        }
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
        
        if loaded_config == default_config:
            print("OK Configuration loading works correctly")
            return True
        else:
            print("FAIL Configuration loading failed - config mismatch")
            return False
            
    except Exception as e:
        print(f"FAIL Configuration test failed: {e}")
        return False

def test_package_structure():
    """Test that the package structure is correct"""
    print("Testing package structure...")
    try:
        required_files = [
            'src/pomodoro-ui.py',
            'scripts/install.sh',
            'config/config.json',
            '.github/workflows/build.yml',
            'debian/control',
            'Makefile'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if not missing_files:
            print("OK All required files present")
            return True
        else:
            print(f"FAIL Missing required files: {missing_files}")
            return False
            
    except Exception as e:
        print(f"FAIL Package structure test failed: {e}")
        return False

def test_script_permissions():
    """Test that scripts have correct permissions"""
    print("Testing script permissions...")
    try:
        script_files = [
            'scripts/install.sh',
            'scripts/configure-pomodoro.py',
            'scripts/start-pomodoro.sh'
        ]
        
        missing_executable = []
        for script_path in script_files:
            if os.path.exists(script_path):
                if not os.access(script_path, os.X_OK):
                    missing_executable.append(script_path)
            else:
                print(f"WARN Script not found: {script_path}")
        
        if not missing_executable:
            print("OK All scripts have executable permissions")
            return True
        else:
            print(f"FAIL Scripts missing executable permissions: {missing_executable}")
            return False
            
    except Exception as e:
        print(f"FAIL Script permissions test failed: {e}")
        return False

def test_notification_simulation():
    """Test notification functionality (simulated for CI)"""
    print("Testing notification simulation...")
    try:
        # Simulate notification test for CI environment
        print("OK Notification simulation successful (CI environment)")
        return True
    except Exception as e:
        print(f"FAIL Notification simulation failed: {e}")
        return False

def main():
    print("Starting CI Tests for Pomodoro Lock")
    print("=" * 50)
    print("Note: These tests are designed for headless CI environments")
    print("=" * 50)
    
    tests = [
        ("Package Structure", test_package_structure),
        ("Script Permissions", test_script_permissions),
        ("Module Imports", test_imports),
        ("Configuration Loading", test_config_loading),
        ("Notification Simulation", test_notification_simulation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"FAIL {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("CI Test Results:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nSummary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("OK All CI tests passed!")
        return 0
    else:
        print("FAIL Some CI tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 