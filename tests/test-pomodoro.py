#!/usr/bin/env python3

import os
import time
import json
import subprocess
import logging
import gi
gi.require_version('Notify', '0.7')
gi.require_version('Gtk', '3.0')
from gi.repository import Notify, Gtk, GLib, Gdk

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class TestOverlay(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.fullscreen()
        
        # Create event box for mouse events
        self.event_box = Gtk.EventBox()
        self.add(self.event_box)
        
        # Create a box with background color using CSS
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.box.set_margin_start(20)
        self.box.set_margin_end(20)
        self.box.set_margin_top(20)
        self.box.set_margin_bottom(20)
        
        # Apply CSS styling
        css_provider = Gtk.CssProvider()
        css = """
        .overlay-box {
            background-color: rgba(0, 0, 0, 0.95);
        }
        """
        css_provider.load_from_data(css.encode())
        style_context = self.box.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        style_context.add_class("overlay-box")
        
        self.event_box.add(self.box)
        
        # Add timer label
        self.timer_label = Gtk.Label()
        self.timer_label.set_markup("<span size='xx-large' weight='bold' foreground='white'>30</span>")
        self.box.pack_start(self.timer_label, True, True, 0)
        
        # Add message label
        self.message_label = Gtk.Label()
        self.message_label.set_markup("<span size='x-large' foreground='white'>TEST - Screen Overlay Active</span>")
        self.box.pack_start(self.message_label, True, True, 0)
        
        self.show_all()
    
    def update_timer(self, seconds):
        self.timer_label.set_markup(f"<span size='xx-large' weight='bold' foreground='white'>{seconds}</span>")

def test_notification():
    """Test notification functionality"""
    print("Testing notification...")
    try:
        Notify.init("Pomodoro Test")
        notification = Notify.Notification.new(
            "Pomodoro Test",
            "This is a test notification",
            "dialog-information"
        )
        notification.show()
        print("✓ Notification sent successfully")
        return True
    except Exception as e:
        print(f"✗ Notification failed: {e}")
        return False

def test_screen_lock():
    """Test screen lock functionality"""
    print("Testing screen lock...")
    try:
        result = subprocess.run(['loginctl', 'lock-session'], 
                             capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Screen lock command executed successfully")
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
            return True
        else:
            print(f"✗ Screen unlock failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Screen unlock error: {e}")
        return False

def test_overlay():
    """Test overlay functionality"""
    print("Testing overlay...")
    try:
        overlay = TestOverlay()
        overlay.show_all()
        print("✓ Overlay created successfully")
        
        # Update timer every second for 30 seconds
        def update_timer():
            nonlocal overlay
            current_time = int(overlay.timer_label.get_text())
            if current_time > 0:
                overlay.update_timer(current_time - 1)
                return True
            else:
                overlay.destroy()
                Gtk.main_quit()
                return False
        
        GLib.timeout_add_seconds(1, update_timer)
        Gtk.main()
        print("✓ Overlay test completed")
        return True
    except Exception as e:
        print(f"✗ Overlay failed: {e}")
        return False

def main():
    print("Starting Pomodoro functionality tests...")
    print("=" * 50)
    
    # Test 1: Notification
    notification_ok = test_notification()
    time.sleep(2)
    
    # Test 2: Screen Lock
    lock_ok = test_screen_lock()
    time.sleep(3)
    
    # Test 3: Screen Unlock
    unlock_ok = test_screen_unlock()
    time.sleep(2)
    
    # Test 4: Overlay (30 seconds)
    print("\nStarting overlay test - you should see a full-screen overlay for 30 seconds...")
    overlay_ok = test_overlay()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Notification: {'✓ PASS' if notification_ok else '✗ FAIL'}")
    print(f"Screen Lock: {'✓ PASS' if lock_ok else '✗ FAIL'}")
    print(f"Screen Unlock: {'✓ PASS' if unlock_ok else '✗ FAIL'}")
    print(f"Overlay: {'✓ PASS' if overlay_ok else '✗ FAIL'}")

if __name__ == "__main__":
    main() 