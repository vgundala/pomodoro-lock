#!/usr/bin/env python3

import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify
import time

def test_notification():
    """Test notification functionality"""
    print("Testing notification...")
    try:
        Notify.init("Pomodoro Test")
        notification = Notify.Notification.new(
            "Pomodoro Test",
            "This is a test notification - if you see this, notifications work!",
            "dialog-information"
        )
        notification.show()
        print("✓ Notification sent successfully")
        print("You should see a notification popup on your screen")
        time.sleep(3)
        return True
    except Exception as e:
        print(f"✗ Notification failed: {e}")
        return False

if __name__ == "__main__":
    test_notification() 