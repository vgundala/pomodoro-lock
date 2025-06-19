#!/usr/bin/env python3

import subprocess
import time

def test_screen_lock():
    """Test screen lock functionality"""
    print("Testing screen lock...")
    try:
        result = subprocess.run(['loginctl', 'lock-session'], 
                             capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Screen lock command executed successfully")
            print("Your screen should be locked now")
            return True
        else:
            print(f"✗ Screen lock failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Screen lock error: {e}")
        return False

def test_screen_unlock():
    """Test screen unlock functionality"""
    print("Testing screen unlock...")
    try:
        result = subprocess.run(['loginctl', 'unlock-session'], 
                             capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Screen unlock command executed successfully")
            print("Your screen should be unlocked now")
            return True
        else:
            print(f"✗ Screen unlock failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Screen unlock error: {e}")
        return False

if __name__ == "__main__":
    print("Testing screen lock/unlock functionality...")
    print("=" * 50)
    
    # Test lock
    lock_ok = test_screen_lock()
    print("Waiting 5 seconds before unlocking...")
    time.sleep(5)
    
    # Test unlock
    unlock_ok = test_screen_unlock()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Screen Lock: {'✓ PASS' if lock_ok else '✗ FAIL'}")
    print(f"Screen Unlock: {'✓ PASS' if unlock_ok else '✗ FAIL'}") 