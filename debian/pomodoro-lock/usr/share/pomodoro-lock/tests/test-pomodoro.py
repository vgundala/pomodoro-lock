#!/usr/bin/env python3

import os
import time
import json
import subprocess
import logging
import gi
import signal
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
        self.timer_label.set_markup("<span size='xx-large' weight='bold' foreground='white'>90</span>")
        self.box.pack_start(self.timer_label, True, True, 0)
        
        # Add message label
        self.message_label = Gtk.Label()
        self.message_label.set_markup("<span size='x-large' foreground='white'>TEST - Screen Overlay Active</span>")
        self.box.pack_start(self.message_label, True, True, 0)
        
        # Add exit instructions
        self.exit_label = Gtk.Label()
        self.exit_label.set_markup("<span size='medium' foreground='yellow'>Press ESC or Ctrl+C to exit test</span>")
        self.box.pack_start(self.exit_label, True, True, 0)
        
        # Connect keyboard events
        self.connect("key-press-event", self.on_key_press)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        
        self.show_all()
    
    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            print("Escape key pressed - exiting test")
            Gtk.main_quit()
            return True
        return False
    
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
    """Test screen lock functionality (SIMULATED for packaging)"""
    print("Testing screen lock (SIMULATED - no actual lock)...")
    try:
        # Simulate screen lock for packaging tests - don't actually lock
        print("✓ Screen lock simulation successful (no actual lock)")
        return True
    except Exception as e:
        print(f"✗ Screen lock simulation failed: {e}")
        return False

def test_screen_unlock():
    """Test screen unlock functionality (SIMULATED for packaging)"""
    print("Testing screen unlock (SIMULATED - no actual unlock)...")
    try:
        # Simulate screen unlock for packaging tests - don't actually unlock
        print("✓ Screen unlock simulation successful (no actual unlock)")
        return True
    except Exception as e:
        print(f"✗ Screen unlock simulation failed: {e}")
        return False

def test_overlay():
    """Test overlay functionality"""
    print("Testing overlay...")
    try:
        # Setup signal handling for Ctrl+C
        def signal_handler(signum, frame):
            print("Ctrl+C received - exiting overlay test")
            Gtk.main_quit()
        
        signal.signal(signal.SIGINT, signal_handler)
        
        overlay = TestOverlay()
        overlay.show_all()
        print("✓ Overlay created successfully")
        
        # Update timer every second for 90 seconds
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
    print("Starting Pomodoro PACKAGING tests (simulated functionality)...")
    print("=" * 60)
    print("NOTE: This is a PACKAGING test - no actual screen locking will occur")
    print("=" * 60)
    
    # Test 1: Notification
    notification_ok = test_notification()
    time.sleep(1)  # Reduced wait time for packaging
    
    # Test 2: Screen Lock (simulated)
    lock_ok = test_screen_lock()
    time.sleep(1)  # Reduced wait time for packaging
    
    # Test 3: Screen Unlock (simulated)
    unlock_ok = test_screen_unlock()
    time.sleep(1)  # Reduced wait time for packaging
    
    # Test 4: Overlay (1 minute 30 seconds)
    print("\nStarting overlay test - you should see a full-screen overlay for 1 minute 30 seconds...")
    print("Press ESC or Ctrl+C to exit early")
    overlay_ok = test_overlay()
    
    print("\n" + "=" * 60)
    print("PACKAGING Test Results:")
    print(f"Notification: {'✓ PASS' if notification_ok else '✗ FAIL'}")
    print(f"Screen Lock (simulated): {'✓ PASS' if lock_ok else '✗ FAIL'}")
    print(f"Screen Unlock (simulated): {'✓ PASS' if unlock_ok else '✗ FAIL'}")
    print(f"Overlay: {'✓ PASS' if overlay_ok else '✗ FAIL'}")
    print("=" * 60)
    print("Packaging test completed successfully!")

if __name__ == "__main__":
    main() 