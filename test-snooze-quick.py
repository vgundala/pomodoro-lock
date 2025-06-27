#!/usr/bin/env python3
"""
Quick test for 5-minute timer with 2-minute pause
"""

import sys
import os
import time
import threading
import importlib.util

# Add src to path for platform_abstraction imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def load_pomodoro_module():
    """Load the pomodoro module using importlib"""
    module_path = os.path.join(os.path.dirname(__file__), 'src', 'pomodoro-ui-crossplatform.py')
    spec = importlib.util.spec_from_file_location("pomodoro_ui_crossplatform", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_5min_timer_2min_pause():
    """Test 5-minute timer with 2-minute pause"""
    print("🧪 Testing 5-minute timer with 2-minute pause...")
    
    try:
        pomodoro_module = load_pomodoro_module()
        PomodoroTimer = pomodoro_module.PomodoroTimer
        
        # Create application instance
        app = PomodoroTimer()
        
        # Set up 5-minute work session
        app.work_time = 5 * 60  # 5 minutes
        app.current_time = app.work_time
        app.is_work_session = True
        app.is_running = True
        
        print(f"Timer set to {app.work_time // 60} minutes")
        print(f"Current time: {app.current_time // 60}:{app.current_time % 60:02d}")
        
        # Simulate 3 minutes of work (2 minutes remaining)
        work_elapsed = 3 * 60
        app.current_time = app.work_time - work_elapsed
        
        print(f"After 3 minutes of work: {app.current_time // 60}:{app.current_time % 60:02d}")
        
        # Now pause for 2 minutes
        print("\n⏸ Pausing timer for 2 minutes...")
        app.is_paused = True
        app.paused_time = app.current_time
        
        # Set up 2-minute auto-resume (instead of 10 minutes for testing)
        snooze_seconds = 2 * 60  # 2 minutes for testing
        
        if app.SYSTEM == "linux":
            # Use GLib timeout for Linux
            import gi
            gi.require_version('GLib', '2.0')
            from gi.repository import GLib
            app.snooze_timeout_id = GLib.timeout_add_seconds(snooze_seconds, app._auto_resume_timer)
            app.snooze_timer = None
        else:
            # Use threading.Timer for Windows
            app.snooze_timer = threading.Timer(snooze_seconds, app._auto_resume_timer)
            app.snooze_timer.daemon = True
            app.snooze_timer.start()
            app.snooze_timeout_id = None
        
        print(f"Auto-resume set for {snooze_seconds // 60} minutes")
        print(f"Paused time: {app.paused_time // 60}:{app.paused_time % 60:02d}")
        
        # Wait for auto-resume
        print(f"Waiting {snooze_seconds // 60} minutes for auto-resume...")
        time.sleep(snooze_seconds + 1)  # Wait for timeout + buffer
        
        # Check if auto-resume worked
        if app.is_paused:
            print("❌ Timer is still paused - auto-resume failed")
            return False
        else:
            print("✅ Timer auto-resumed successfully")
            print(f"Resumed time: {app.current_time // 60}:{app.current_time % 60:02d}")
            return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_manual_resume_early():
    """Test manual resume before auto-resume"""
    print("\n🧪 Testing manual resume before auto-resume...")
    
    try:
        pomodoro_module = load_pomodoro_module()
        PomodoroTimer = pomodoro_module.PomodoroTimer
        
        # Create application instance
        app = PomodoroTimer()
        
        # Set up 5-minute work session
        app.work_time = 5 * 60
        app.current_time = app.work_time
        app.is_work_session = True
        app.is_running = True
        
        # Simulate 3 minutes of work
        work_elapsed = 3 * 60
        app.current_time = app.work_time - work_elapsed
        
        # Pause for 2 minutes
        print("Pausing timer for 2 minutes...")
        app.is_paused = True
        app.paused_time = app.current_time
        
        # Set up 2-minute auto-resume
        snooze_seconds = 2 * 60
        
        if app.SYSTEM == "linux":
            import gi
            gi.require_version('GLib', '2.0')
            from gi.repository import GLib
            app.snooze_timeout_id = GLib.timeout_add_seconds(snooze_seconds, app._auto_resume_timer)
            app.snooze_timer = None
        else:
            app.snooze_timer = threading.Timer(snooze_seconds, app._auto_resume_timer)
            app.snooze_timer.daemon = True
            app.snooze_timer.start()
            app.snooze_timeout_id = None
        
        # Wait 30 seconds then manually resume
        print("Waiting 30 seconds then manually resuming...")
        time.sleep(30)
        
        # Manually resume
        print("Manually resuming timer...")
        app._on_pause_snooze_clicked()
        
        if app.is_paused:
            print("❌ Manual resume failed")
            return False
        else:
            print("✅ Manual resume successful")
            print(f"Resumed time: {app.current_time // 60}:{app.current_time % 60:02d}")
            return True
        
    except Exception as e:
        print(f"❌ Manual resume test failed: {e}")
        return False

def main():
    """Run the tests"""
    print("🚀 5-Minute Timer with 2-Minute Pause Test")
    print("=" * 50)
    
    # Test 1: Auto-resume after 2 minutes
    test1_passed = test_5min_timer_2min_pause()
    
    # Test 2: Manual resume before auto-resume
    test2_passed = test_manual_resume_early()
    
    # Print results
    print("\n📊 Test Results:")
    print("=" * 50)
    print(f"Auto-resume after 2 minutes: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Manual resume before auto-resume: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Snooze functionality is working correctly.")
        print("✅ No segmentation faults should occur during auto-resume.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 