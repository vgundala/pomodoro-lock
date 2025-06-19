#!/usr/bin/env python3

import os
import time
import json
import signal
import subprocess
import logging
from pathlib import Path
from datetime import datetime, timedelta
import gi
gi.require_version('Notify', '0.7')
gi.require_version('Gtk', '3.0')
from gi.repository import Notify, Gtk, GLib, Gdk
import psutil
import Xlib
from Xlib import X, display
from Xlib.ext import record
from Xlib.protocol import rq

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class CountdownTimer(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_default_size(300, 100)
        # Move to left bottom
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() if display else display.get_monitor(0)
        geometry = monitor.get_geometry()
        x = geometry.x
        y = geometry.y + geometry.height - 100  # 100 is window height
        self.move(x, y)
        
        # Create event box for mouse events
        self.event_box = Gtk.EventBox()
        self.add(self.event_box)
        
        # Create a box with background color using CSS
        self.box = Gtk.Box()
        self.box.set_margin_start(20)
        self.box.set_margin_end(20)
        self.box.set_margin_top(20)
        self.box.set_margin_bottom(20)
        
        # Apply CSS styling
        css_provider = Gtk.CssProvider()
        css = """
        .timer-box {
            background-color: rgba(51, 51, 51, 0.8);
            border-radius: 10px;
        }
        .timer-box:hover {
            background-color: rgba(61, 61, 61, 0.8);
        }
        """
        css_provider.load_from_data(css.encode())
        style_context = self.box.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        style_context.add_class("timer-box")
        
        self.event_box.add(self.box)
        
        self.label = Gtk.Label()
        self.label.set_markup("<span size='x-large' weight='bold' foreground='white'>00:00</span>")
        self.box.pack_start(self.label, True, True, 0)
        
        # Connect mouse events
        self.event_box.connect("button-press-event", self.on_button_press)
        self.event_box.connect("button-release-event", self.on_button_release)
        self.event_box.connect("motion-notify-event", self.on_motion)
        
        # Enable motion events
        self.event_box.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                                Gdk.EventMask.BUTTON_RELEASE_MASK |
                                Gdk.EventMask.POINTER_MOTION_MASK)
        
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.show_all()
    
    def on_button_press(self, widget, event):
        if event.button == 1:  # Left mouse button
            self.dragging = True
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
            return True
        return False
    
    def on_button_release(self, widget, event):
        if event.button == 1:  # Left mouse button
            self.dragging = False
            return True
        return False
    
    def on_motion(self, widget, event):
        if self.dragging:
            x, y = self.get_position()
            new_x = x + (event.x_root - self.drag_start_x)
            new_y = y + (event.x_root - self.drag_start_y)
            self.move(new_x, new_y)
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
            return True
        return False

    def update_timer(self, seconds, mode='work'):
        minutes, secs = divmod(seconds, 60)
        color = 'white' if mode == 'work' else 'orange'
        self.label.set_markup(f"<span size='x-large' weight='bold' foreground='{color}'>{minutes:02d}:{secs:02d}</span>")

class FullScreenOverlay(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        # Don't automatically fullscreen - we'll control this manually
        
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
        self.timer_label.set_markup("<span size='xx-large' weight='bold' foreground='white'>00:00</span>")
        self.box.pack_start(self.timer_label, True, True, 0)
        
        # Add message label
        self.message_label = Gtk.Label()
        self.message_label.set_markup("<span size='x-large' foreground='white'>Break Time - Screen Locked</span>")
        self.box.pack_start(self.message_label, True, True, 0)
        
        self.show_all()
    
    def update_timer(self, seconds):
        minutes, secs = divmod(seconds, 60)
        self.timer_label.set_markup(f"<span size='xx-large' weight='bold' foreground='white'>{minutes:02d}:{secs:02d}</span>")

class MultiDisplayOverlay:
    def __init__(self):
        self.overlays = []
        self.create_overlays()
    
    def create_overlays(self):
        """Create overlays for all available displays"""
        display = Gdk.Display.get_default()
        if display:
            n_monitors = display.get_n_monitors()
            logging.info(f"Found {n_monitors} monitor(s)")
            for i in range(n_monitors):
                overlay = FullScreenOverlay()
                # Get monitor geometry
                monitor = display.get_monitor(i)
                geometry = monitor.get_geometry()
                
                # Set window to cover the specific monitor
                overlay.unfullscreen()  # Remove fullscreen first
                overlay.move(geometry.x, geometry.y)
                overlay.resize(geometry.width, geometry.height)
                overlay.set_default_size(geometry.width, geometry.height)
                
                self.overlays.append(overlay)
                logging.info(f"Created overlay for monitor {i}: {geometry.width}x{geometry.height} at ({geometry.x}, {geometry.y})")
        else:
            # Fallback to single overlay
            overlay = FullScreenOverlay()
            self.overlays.append(overlay)
            logging.info("No display found, created single overlay")
    
    def show_all(self):
        """Show all overlays"""
        for overlay in self.overlays:
            overlay.show_all()
    
    def hide_all(self):
        """Hide all overlays"""
        for overlay in self.overlays:
            overlay.hide()
    
    def update_timer(self, seconds):
        """Update timer on all overlays"""
        for overlay in self.overlays:
            overlay.update_timer(seconds)
    
    def destroy_all(self):
        """Destroy all overlays"""
        for overlay in self.overlays:
            overlay.destroy()
        self.overlays.clear()

class PomodoroLock:
    def __init__(self):
        # Load config from file
        self.config_path = os.path.expanduser('~/.local/share/pomodoro-lock/config/config.json')
        self.load_config()
        
        # Use config values (convert to seconds for testing)
        self.work_time = self.config['work_time_minutes'] * 60
        self.break_time = self.config['break_time_minutes'] * 60
        self.notification_time = self.config['notification_time_minutes'] * 60
        self.inactivity_threshold = self.config['inactivity_threshold_minutes'] * 60
        
        self.state = 'work'
        self.remaining = self.work_time
        self.notification_sent = False
        self.last_activity = time.time()
        
        Notify.init("Pomodoro Lock")
        self.timer = CountdownTimer()
        self.overlay = None
        self.timer.update_timer(self.remaining, mode='work')
        self.timer.show_all()
        GLib.timeout_add_seconds(1, self.tick)

    def load_config(self):
        default_config = {
            "work_time_minutes": 30,
            "break_time_minutes": 5,
            "notification_time_minutes": 2,
            "inactivity_threshold_minutes": 10
        }
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = {**default_config, **json.load(f)}
        else:
            self.config = default_config
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)

    def check_user_activity(self):
        # Simplified activity check for testing
        current_time = time.time()
        if (current_time - self.last_activity) > self.inactivity_threshold:
            logging.info("Inactivity detected, resetting timer")
            self.remaining = self.work_time
            self.notification_sent = False
            self.state = 'work'
            self.timer.update_timer(self.remaining, mode='work')
            return False
        return True

    def send_notification(self, message):
        try:
            notification = Notify.Notification.new(
                "Pomodoro Lock",
                message,
                "dialog-information"
            )
            notification.show()
            logging.info(f"Notification sent: {message}")
        except Exception as e:
            logging.error(f"Failed to send notification: {e}")

    def start_break(self):
        """Start break period with overlay on all displays"""
        try:
            logging.info("Starting break period with overlay on all displays")
            if not self.overlay:
                self.overlay = MultiDisplayOverlay()
            self.overlay.show_all()
            logging.info("Overlay created and shown on all displays")
        except Exception as e:
            logging.error(f"Error creating overlay: {e}")

    def end_break(self):
        """End break period and hide overlays"""
        try:
            logging.info("Ending break period")
            if self.overlay:
                self.overlay.hide_all()
                self.overlay.destroy_all()
                self.overlay = None
            logging.info("Overlays hidden and destroyed")
        except Exception as e:
            logging.error(f"Error hiding overlays: {e}")

    def tick(self):
        if self.state == 'work':
            if self.check_user_activity():
                self.remaining -= 1
                self.timer.update_timer(self.remaining, mode='work')
                # Notify before break
                if self.remaining == self.notification_time and not self.notification_sent:
                    logging.info("Sending break notification")
                    self.send_notification(
                        f"Break coming in {self.notification_time} seconds. "
                        f"You will be locked out for {self.break_time} seconds."
                    )
                    self.notification_sent = True
                if self.remaining <= 0:
                    logging.info("Work period ended, starting break")
                    self.start_break()
                    self.state = 'break'
                    self.remaining = self.break_time
                    self.notification_sent = False
                    if self.overlay:
                        self.overlay.update_timer(self.remaining)
        else:  # break state
            self.remaining -= 1
            if self.overlay:
                self.overlay.update_timer(self.remaining)
            if self.remaining <= 0:
                logging.info("Break period ended, starting work")
                self.end_break()
                self.state = 'work'
                self.remaining = self.work_time
                self.notification_sent = False
                self.timer.update_timer(self.remaining, mode='work')
        return True

def main():
    pomodoro = PomodoroLock()
    Gtk.main()

if __name__ == "__main__":
    main() 