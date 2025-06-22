#!/usr/bin/env python3
"""
Pomodoro Lock Service - Core Timer Logic

This service manages the Pomodoro timer, configuration, notifications, and overlays.
It communicates with UI clients via status files.
"""

import os
import time
import json
import signal
import subprocess
import logging
import threading
from pathlib import Path
from datetime import datetime, timedelta
import gi
gi.require_version('Notify', '0.7')
gi.require_version('Gtk', '3.0')
from gi.repository import Notify, Gtk, GLib, Gdk
import psutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.local/share/pomodoro-lock/pomodoro-service.log')),
        logging.StreamHandler()
    ]
)

class UserActivityMonitor:
    def __init__(self, inactivity_threshold_minutes=10):
        self.inactivity_threshold = inactivity_threshold_minutes * 60
        self.last_activity = time.time()
        self.is_active = True
        self.monitoring = False

    def start_monitoring(self):
        """Start monitoring user activity"""
        if self.monitoring:
            return

        logging.info("User activity monitoring started (audio only)")
        self.monitoring = True
        self.last_activity = time.time()

        # Start activity monitoring in a separate thread
        self.monitor_thread = threading.Thread(target=self._monitor_activity, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring user activity"""
        logging.info("User activity monitoring stopped")
        self.monitoring = False

    def _monitor_activity(self):
        """Monitor user activity using audio checks"""
        while self.monitoring:
            # Check audio activity as the primary method
            audio_active = self._check_audio_activity()
            if audio_active:
                self.last_activity = time.time()
                if not self.is_active:
                    self.is_active = True
                    logging.debug("Activity detected: audio playing")

            time.sleep(1) # Small delay to avoid busy-waiting

    def _check_audio_activity(self):
        """Check if there's active audio playback"""
        try:
            audio_processes = [
                'pulseaudio', 'pipewire', 'pavucontrol', 'pactl',
                'ffplay', 'mpv', 'vlc', 'spotify', 'firefox', 'chrome',
                'chromium', 'brave', 'opera', 'safari', 'audacious',
                'rhythmbox', 'clementine', 'amarok', 'banshee'
            ]

            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    if proc_info['name'] in audio_processes:
                        if proc_info['name'] in ['pulseaudio', 'pipewire']:
                            result = subprocess.run(['pactl', 'list', 'short', 'sinks'],
                                                     capture_output=True, text=True, timeout=2)
                            if result.returncode == 0 and result.stdout.strip():
                                return True
                        else:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            try:
                result = subprocess.run(['pactl', 'list', 'short', 'sink-inputs'],
                                     capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and result.stdout.strip():
                    return True
            except:
                pass

            try:
                result = subprocess.run(['amixer', 'get', 'Master'],
                                     capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and '[on]' in result.stdout:
                    return True
            except:
                pass

            return False

        except Exception as e:
            logging.error(f"Error checking audio activity: {e}")
            return False

    def check_inactivity(self):
        """Check if user has been inactive for the threshold period"""
        current_time = time.time()
        inactive_time = current_time - self.last_activity

        if inactive_time >= self.inactivity_threshold:
            if self.is_active:
                self.is_active = False
                logging.info(f"User inactive for {inactive_time/60:.1f} minutes - pausing timer")
            return False
        else:
            if not self.is_active:
                self.is_active = True
                logging.info(f"User activity resumed after {inactive_time/60:.1f} minutes")
            return True

    def get_inactive_time(self):
        """Get the time since last activity in seconds"""
        return time.time() - self.last_activity

class FullScreenOverlay(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.fullscreen()
        
        # Create event box for mouse events
        self.event_box = Gtk.EventBox()
        self.add(self.event_box)
        
        # Create a box with background color using CSS
        self.box = Gtk.Box()
        self.box.set_margin_start(50)
        self.box.set_margin_end(50)
        self.box.set_margin_top(50)
        self.box.set_margin_bottom(50)
        
        # Apply CSS styling
        css_provider = Gtk.CssProvider()
        css = """
        .overlay-box {
            background-color: rgba(0, 0, 0, 0.9);
            border-radius: 20px;
        }
        """
        css_provider.load_from_data(css.encode())
        style_context = self.box.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        style_context.add_class("overlay-box")
        
        self.event_box.add(self.box)
        
        # Create label for timer
        self.label = Gtk.Label()
        self.label.set_markup("<span size='xx-large' weight='bold' foreground='white'>Break Time!</span>")
        self.box.pack_start(self.label, True, True, 0)
        
        # Connect mouse events
        self.event_box.connect("button-press-event", self.on_button_press)
        self.event_box.connect("button-release-event", self.on_button_release)
        self.event_box.connect("motion-notify-event", self.on_motion)
        
        # Enable motion events
        self.event_box.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                                 Gdk.EventMask.BUTTON_RELEASE_MASK |
                                 Gdk.EventMask.POINTER_MOTION_MASK)

    def on_button_press(self, widget, event):
        return True

    def on_button_release(self, widget, event):
        return True

    def on_motion(self, widget, event):
        return True

    def update_timer(self, seconds):
        """Update the timer display"""
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        time_str = f"{minutes:02d}:{remaining_seconds:02d}"
        self.label.set_markup(f"<span size='xx-large' weight='bold' foreground='white'>Break Time! {time_str}</span>")

class MultiDisplayOverlay:
    def __init__(self):
        self.overlays = []
        self.create_overlays()

    def create_overlays(self):
        """Create overlays for all connected displays"""
        display = Gdk.Display.get_default()
        if display:
            n_monitors = display.get_n_monitors()
            logging.info(f"Creating overlays for {n_monitors} monitors")
            
            for i in range(n_monitors):
                monitor = display.get_monitor(i)
                geometry = monitor.get_geometry()
                
                overlay = FullScreenOverlay()
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

class PomodoroService:
    def __init__(self):
        # Setup paths
        self.user_dir = os.path.expanduser('~/.local/share/pomodoro-lock')
        self.status_file = os.path.join(self.user_dir, 'status.json')
        self.config_file = os.path.join(self.user_dir, 'config/config.json')
        self.ui_status_file = os.path.join(self.user_dir, 'ui_status.json')
        
        # Ensure directories exist
        os.makedirs(self.user_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Load configuration
        self.load_config()
        
        # Initialize timer state
        self.work_time = self.config['work_time_minutes'] * 60
        self.break_time = self.config['break_time_minutes'] * 60
        self.notification_time = self.config['notification_time_minutes'] * 60
        self.inactivity_threshold = self.config['inactivity_threshold_minutes'] * 60
        
        self.state = 'work'
        self.is_paused = False
        self.end_time = None  # To store the calculated end time
        self.remaining_seconds = self.work_time
        self.notification_sent = False
        self.total_pause_time = 0
        
        # Initialize GTK and notifications
        Notify.init("Pomodoro Lock Service")
        
        # Initialize overlays
        self.overlay = None
        
        # Initialize and start activity monitoring
        self.activity_monitor = UserActivityMonitor(self.config['inactivity_threshold_minutes'])
        self.activity_monitor.start_monitoring()
        
        # Write initial status
        self.write_status()
        
        # Start timer
        GLib.timeout_add_seconds(1, self.tick)

    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "work_time_minutes": 25,
            "break_time_minutes": 5,
            "notification_time_minutes": 2,
            "inactivity_threshold_minutes": 10
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = {**default_config, **json.load(f)}
        else:
            self.config = default_config
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)

    def write_status(self):
        """Write current status to file for UI clients"""
        status = {
            'state': self.state,
            'remaining': self.remaining_seconds,
            'is_paused': self.is_paused,
            'total_pause_time': self.total_pause_time,
            'work_time': self.work_time,
            'break_time': self.break_time,
            'timestamp': time.time()
        }
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logging.error(f"Error writing status file: {e}")

    def send_notification(self, message):
        """Send desktop notification"""
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

    def start_timer(self, duration_seconds):
        """Starts a timer for a given duration."""
        self.end_time = datetime.now() + timedelta(seconds=duration_seconds)
        self.remaining_seconds = duration_seconds
        self.is_paused = False

    def toggle_pause(self):
        """Toggles the pause state of the timer."""
        self.is_paused = not self.is_paused
        if self.is_paused:
            # When pausing, store the remaining seconds
            self.remaining_seconds = self.get_remaining_seconds()
            self.end_time = None
            logging.info("Timer paused.")
        else:
            # When unpausing, calculate a new end_time
            self.start_timer(self.remaining_seconds)
            logging.info("Timer resumed.")
        self.write_status()

    def get_remaining_seconds(self):
        """Calculates remaining seconds from the end_time."""
        if self.is_paused or not self.end_time:
            return self.remaining_seconds
        
        remaining = (self.end_time - datetime.now()).total_seconds()
        return max(0, int(remaining))

    def tick(self):
        """The main timer loop, executed every second."""
        # Check if the UI is active and providing its own countdown
        ui_is_active = os.path.exists(self.ui_status_file)
        
        if ui_is_active:
            try:
                with open(self.ui_status_file, 'r') as f:
                    ui_status = json.load(f)
                self.remaining_seconds = ui_status.get('remaining', self.remaining_seconds)
            except (json.JSONDecodeError, FileNotFoundError):
                # If file is deleted mid-read or is corrupt, fallback to service timer
                ui_is_active = False
        
        # Only run the service-side countdown if the UI is not active
        if not ui_is_active and not self.is_paused:
            self.remaining_seconds = self.get_remaining_seconds()

        # Activity check and state transitions are always handled by the service
        if not self.is_paused:
            if self.activity_monitor:
                self.activity_monitor.check_inactivity()
                if not self.activity_monitor.is_active:
                    self.toggle_pause()
                    return

            if self.remaining_seconds <= 0:
                if self.state == 'work':
                    self.start_break()
                elif self.state == 'break':
                    self.end_break()

        self.write_status()

    def start_break(self):
        """Handles the transition from work to break."""
        self.state = 'break'
        self.send_notification(f"Time for a {self.config['break_time_minutes']} minute break!")
        self.start_timer(self.break_time)
        self.overlay.show_all()
        self.overlay.update_timer(self.remaining_seconds)
        logging.info("Work session finished, starting break.")

    def end_break(self):
        """Handles the transition from break back to work."""
        self.state = 'work'
        self.send_notification("Break's over! Time to get back to work.")
        self.start_timer(self.work_time)
        self.overlay.hide_all()
        logging.info("Break finished, starting new work session.")

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'activity_monitor'):
            self.activity_monitor.stop_monitoring()
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy_all()
        # Clean up status file
        try:
            if os.path.exists(self.status_file):
                os.remove(self.status_file)
        except Exception as e:
            logging.error(f"Error cleaning up status file: {e}")

    def run(self):
        """Main service loop."""
        logging.info("Pomodoro Service started.")
        self.start_timer(self.config['work_time_minutes'] * 60)
        
        while not self.shutdown_event.is_set():
            loop_start_time = time.monotonic()
            
            self.tick()
            
            # Calculate sleep time to ensure the loop runs precisely every second
            elapsed = time.monotonic() - loop_start_time
            sleep_time = max(0, 1.0 - elapsed)
            time.sleep(sleep_time)

        self.cleanup()

def main():
    service = PomodoroService()
    
    def signal_handler(signum, frame):
        logging.info("Received shutdown signal")
        service.cleanup()
        Gtk.main_quit()
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    Gtk.main()

if __name__ == "__main__":
    main() 