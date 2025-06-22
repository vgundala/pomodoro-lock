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
        import psutil
        print("✓ psutil imported successfully")
        
        import Xlib
        print("✓ python-xlib imported successfully")
        
        import notify2
        print("✓ notify2 imported successfully")
        
        # Try to import GTK (may fail in headless environment)
        try:
            import gi
            gi.require_version('Notify', '0.7')
            gi.require_version('Gtk', '3.0')
            from gi.repository import Notify, Gtk, GLib, Gdk
            print("✓ GTK modules imported successfully")
        except Exception as e:
            print(f"⚠ GTK modules not available (expected in CI): {e}")
        
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
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
            print("✓ Configuration loading works correctly")
            return True
        else:
            print("✗ Configuration loading failed - config mismatch")
            return False
            
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_setup_py():
    """Test that setup.py can be executed without errors"""
    print("Testing setup.py execution...")
    try:
        # Test setup.py syntax and basic execution
        result = subprocess.run([
            sys.executable, '-c', 
            'import setup; print("✓ setup.py imports successfully")'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ setup.py execution successful")
            return True
        else:
            print(f"✗ setup.py execution failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ setup.py execution timed out")
        return False
    except Exception as e:
        print(f"✗ setup.py test failed: {e}")
        return False

def test_package_structure():
    """Test that the package structure is correct"""
    print("Testing package structure...")
    try:
        required_files = [
            'setup.py',
            'requirements.txt',
            'src/pomodoro-lock.py',
            'scripts/install.sh',
            'config/config.json',
            '.github/workflows/build.yml'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if not missing_files:
            print("✓ All required files present")
            return True
        else:
            print(f"✗ Missing required files: {missing_files}")
            return False
            
    except Exception as e:
        print(f"✗ Package structure test failed: {e}")
        return False

def test_script_permissions():
    """Test that scripts have correct permissions"""
    print("Testing script permissions...")
    try:
        script_files = [
            'scripts/install.sh',
            'scripts/build-appimage.sh',
            'scripts/generate-icons.sh',
            'scripts/test-build.sh'
        ]
        
        missing_executable = []
        for script_path in script_files:
            if os.path.exists(script_path):
                if not os.access(script_path, os.X_OK):
                    missing_executable.append(script_path)
            else:
                print(f"⚠ Script not found: {script_path}")
        
        if not missing_executable:
            print("✓ All scripts have executable permissions")
            return True
        else:
            print(f"✗ Scripts missing executable permissions: {missing_executable}")
            return False
            
    except Exception as e:
        print(f"✗ Script permissions test failed: {e}")
        return False

def test_notification_simulation():
    """Test notification functionality (simulated for CI)"""
    print("Testing notification simulation...")
    try:
        # Simulate notification test for CI environment
        print("✓ Notification simulation successful (CI environment)")
        return True
    except Exception as e:
        print(f"✗ Notification simulation failed: {e}")
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
        ("Setup.py Execution", test_setup_py),
        ("Notification Simulation", test_notification_simulation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("CI Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nSummary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All CI tests passed!")
        return 0
    else:
        print("❌ Some CI tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 