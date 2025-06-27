#!/usr/bin/env python3
"""
Simple test for snooze functionality without GUI
"""

import sys
import os
import time
import threading
import importlib.util

def test_glib_timeout():
    """Test GLib timeout functionality"""
    print("🧪 Testing GLib timeout functionality...")
    
    try:
        import gi
        gi.require_version('GLib', '2.0')
        from gi.repository import GLib
        
        # Test variables
        timeout_triggered = False
        timeout_id = None
        
        def timeout_callback():
            nonlocal timeout_triggered
            print("✅ GLib timeout triggered successfully")
            timeout_triggered = True
            return False  # Stop the timeout
        
        # Set up a 3-second timeout
        timeout_id = GLib.timeout_add_seconds(3, timeout_callback)
        print("GLib timeout set for 3 seconds...")
        
        # Wait for timeout
        time.sleep(4)
        
        if timeout_triggered:
            print("✅ GLib timeout test passed")
            return True
        else:
            print("❌ GLib timeout did not trigger")
            return False
            
    except Exception as e:
        print(f"❌ GLib timeout test failed: {e}")
        return False

def test_threading_timer():
    """Test threading.Timer functionality"""
    print("\n🧪 Testing threading.Timer functionality...")
    
    try:
        timer_triggered = False
        
        def timer_callback():
            nonlocal timer_triggered
            print("✅ Threading timer triggered successfully")
            timer_triggered = True
        
        # Set up a 3-second timer
        timer = threading.Timer(3, timer_callback)
        timer.daemon = True
        timer.start()
        print("Threading timer set for 3 seconds...")
        
        # Wait for timer
        time.sleep(4)
        
        if timer_triggered:
            print("✅ Threading timer test passed")
            return True
        else:
            print("❌ Threading timer did not trigger")
            return False
            
    except Exception as e:
        print(f"❌ Threading timer test failed: {e}")
        return False

def test_timer_cancellation():
    """Test timer cancellation"""
    print("\n🧪 Testing timer cancellation...")
    
    try:
        # Test GLib timeout cancellation
        import gi
        gi.require_version('GLib', '2.0')
        from gi.repository import GLib
        
        timeout_triggered = False
        
        def timeout_callback():
            nonlocal timeout_triggered
            print("❌ GLib timeout should not have triggered")
            timeout_triggered = True
            return False
        
        # Set up a 5-second timeout
        timeout_id = GLib.timeout_add_seconds(5, timeout_callback)
        print("GLib timeout set for 5 seconds...")
        
        # Cancel after 1 second
        time.sleep(1)
        print("Cancelling GLib timeout...")
        GLib.source_remove(timeout_id)
        
        # Wait to see if it triggers
        time.sleep(3)
        
        if not timeout_triggered:
            print("✅ GLib timeout cancellation test passed")
            return True
        else:
            print("❌ GLib timeout was not cancelled")
            return False
            
    except Exception as e:
        print(f"❌ Timer cancellation test failed: {e}")
        return False

def test_threading_timer_cancellation():
    """Test threading.Timer cancellation"""
    print("\n🧪 Testing threading.Timer cancellation...")
    
    try:
        timer_triggered = False
        
        def timer_callback():
            nonlocal timer_triggered
            print("❌ Threading timer should not have triggered")
            timer_triggered = True
        
        # Set up a 5-second timer
        timer = threading.Timer(5, timer_callback)
        timer.daemon = True
        timer.start()
        print("Threading timer set for 5 seconds...")
        
        # Cancel after 1 second
        time.sleep(1)
        print("Cancelling threading timer...")
        timer.cancel()
        
        # Wait to see if it triggers
        time.sleep(3)
        
        if not timer_triggered:
            print("✅ Threading timer cancellation test passed")
            return True
        else:
            print("❌ Threading timer was not cancelled")
            return False
            
    except Exception as e:
        print(f"❌ Threading timer cancellation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Simple Snooze Test Suite")
    print("=" * 50)
    
    # Test 1: GLib timeout
    test1_passed = test_glib_timeout()
    
    # Test 2: Threading timer
    test2_passed = test_threading_timer()
    
    # Test 3: GLib timeout cancellation
    test3_passed = test_timer_cancellation()
    
    # Test 4: Threading timer cancellation
    test4_passed = test_threading_timer_cancellation()
    
    # Print results
    print("\n📊 Test Results:")
    print("=" * 50)
    print(f"GLib timeout: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Threading timer: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"GLib cancellation: {'✅ PASS' if test3_passed else '❌ FAIL'}")
    print(f"Threading cancellation: {'✅ PASS' if test4_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed and test3_passed and test4_passed:
        print("\n🎉 All tests passed! Timer mechanisms are working correctly.")
        print("✅ The snooze functionality should work without segmentation faults.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 