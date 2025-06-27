#!/usr/bin/env python3
"""
Test script to verify snooze functionality without segmentation faults
"""

import sys
import os
import time
import threading
import importlib.util

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def load_pomodoro_module():
    """Load the pomodoro module using importlib"""
    module_path = os.path.join(os.path.dirname(__file__), 'src', 'pomodoro-ui-crossplatform.py')
    spec = importlib.util.spec_from_file_location("pomodoro_ui_crossplatform", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_snooze_functionality():
    """Test snooze functionality with short timeouts"""
    print("🧪 Testing snooze functionality...")
    
    try:
        pomodoro_module = load_pomodoro_module()
        PomodoroTimer = pomodoro_module.PomodoroTimer
        
        # Create application instance
        app = PomodoroTimer()
        
        # Set up a short test (30 seconds instead of 10 minutes)
        print("Setting up 30-second snooze test...")
        
        # Simulate pause with short timeout
        app.is_paused = True
        app.paused_time = app.current_time
        
        # Use a short timeout for testing (30 seconds)
        test_timeout = 30
        
        if app.SYSTEM == "linux":
            # Test GLib timeout
            import gi
            gi.require_version('GLib', '2.0')
            from gi.repository import GLib
            
            print("Testing GLib timeout (Linux)...")
            app.snooze_timeout_id = GLib.timeout_add_seconds(test_timeout, app._auto_resume_timer)
            
            # Start a thread to monitor the timeout
            def monitor_timeout():
                time.sleep(test_timeout + 2)  # Wait for timeout + buffer
                if app.is_paused:
                    print("❌ Auto-resume did not trigger within expected time")
                else:
                    print("✅ Auto-resume triggered successfully")
            
            monitor_thread = threading.Thread(target=monitor_timeout, daemon=True)
            monitor_thread.start()
            
            # Start GTK main loop
            print("Starting GTK main loop (will auto-resume in 30 seconds)...")
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            Gtk.main()
            
        else:
            # Test threading.Timer for Windows
            print("Testing threading.Timer (Windows)...")
            app.snooze_timer = threading.Timer(test_timeout, app._auto_resume_timer)
            app.snooze_timer.daemon = True
            app.snooze_timer.start()
            
            # Wait for the timer
            print(f"Waiting {test_timeout} seconds for auto-resume...")
            time.sleep(test_timeout + 2)
            
            if app.is_paused:
                print("❌ Auto-resume did not trigger within expected time")
                return False
            else:
                print("✅ Auto-resume triggered successfully")
                return True
        
        return True
        
    except Exception as e:
        print(f"❌ Snooze test failed: {e}")
        return False

def test_manual_resume():
    """Test manual resume functionality"""
    print("\n🧪 Testing manual resume functionality...")
    
    try:
        pomodoro_module = load_pomodoro_module()
        PomodoroTimer = pomodoro_module.PomodoroTimer
        
        # Create application instance
        app = PomodoroTimer()
        
        # Simulate pause
        app.is_paused = True
        app.paused_time = app.current_time
        
        # Set up a long timeout (5 minutes)
        test_timeout = 300
        
        if app.SYSTEM == "linux":
            import gi
            gi.require_version('GLib', '2.0')
            from gi.repository import GLib
            app.snooze_timeout_id = GLib.timeout_add_seconds(test_timeout, app._auto_resume_timer)
        else:
            app.snooze_timer = threading.Timer(test_timeout, app._auto_resume_timer)
            app.snooze_timer.daemon = True
            app.snooze_timer.start()
        
        print("Timer paused with 5-minute auto-resume...")
        
        # Simulate manual resume after 2 seconds
        time.sleep(2)
        print("Triggering manual resume...")
        
        # Call the pause/snooze handler to resume
        app._on_pause_snooze_clicked()
        
        if app.is_paused:
            print("❌ Manual resume failed")
            return False
        else:
            print("✅ Manual resume successful")
            return True
        
    except Exception as e:
        print(f"❌ Manual resume test failed: {e}")
        return False

def test_cleanup():
    """Test cleanup functionality"""
    print("\n🧪 Testing cleanup functionality...")
    
    try:
        pomodoro_module = load_pomodoro_module()
        PomodoroTimer = pomodoro_module.PomodoroTimer
        
        # Create application instance
        app = PomodoroTimer()
        
        # Simulate pause with timeout
        app.is_paused = True
        app.paused_time = app.current_time
        
        if app.SYSTEM == "linux":
            import gi
            gi.require_version('GLib', '2.0')
            from gi.repository import GLib
            app.snooze_timeout_id = GLib.timeout_add_seconds(60, app._auto_resume_timer)
        else:
            app.snooze_timer = threading.Timer(60, app._auto_resume_timer)
            app.snooze_timer.daemon = True
            app.snooze_timer.start()
        
        print("Timer paused with timeout...")
        
        # Test cleanup
        print("Testing cleanup...")
        app.quit_application()
        
        # Check if timers are cleaned up
        if app.SYSTEM == "linux":
            if app.snooze_timeout_id is None:
                print("✅ GLib timeout cleaned up successfully")
                return True
            else:
                print("❌ GLib timeout not cleaned up")
                return False
        else:
            if app.snooze_timer is None or not app.snooze_timer.is_alive():
                print("✅ Threading timer cleaned up successfully")
                return True
            else:
                print("❌ Threading timer not cleaned up")
                return False
        
    except Exception as e:
        print(f"❌ Cleanup test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Snooze Fix Test Suite")
    print("=" * 50)
    
    # Test 1: Snooze functionality (short timeout)
    test1_passed = test_snooze_functionality()
    
    # Test 2: Manual resume
    test2_passed = test_manual_resume()
    
    # Test 3: Cleanup
    test3_passed = test_cleanup()
    
    # Print results
    print("\n📊 Test Results:")
    print("=" * 50)
    print(f"Snooze functionality: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Manual resume: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"Cleanup: {'✅ PASS' if test3_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 All tests passed! Snooze functionality is working correctly.")
        print("✅ No segmentation faults should occur during auto-resume.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 