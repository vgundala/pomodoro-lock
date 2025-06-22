#!/usr/bin/env python3
"""
Pomodoro Lock UI - Timer Display Client

This UI component displays the timer and reads status from the service.
It's a lightweight client that doesn't manage timer logic.
"""

import os
import time
import json
import signal
import logging
import fcntl  # Import for file locking
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GLib, Gdk, AppIndicator3

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.local/share/pomodoro-lock/pomodoro-ui.log')),
        logging.StreamHandler()
    ]
)

class CountdownTimer(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_default_size(350, 120)
        
        # Move to left bottom
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() if display else display.get_monitor(0)
        geometry = monitor.get_geometry()
        x = geometry.x
        y = geometry.y + geometry.height - 120  # 120 is window height
        self.move(x, y)
        
        # Create event box for mouse events
        self.event_box = Gtk.EventBox()
        self.add(self.event_box)
        
        # Create a box with background color using CSS
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
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
        .timer-box.paused {
            background-color: rgba(255, 165, 0, 0.8);
        }
        .timer-box.break {
            background-color: rgba(220, 20, 60, 0.8);
        }
        .corner-button {
            background-color: transparent;
            border: none;
            color: white;
            font-weight: bold;
            font-size: 16px;
            padding: 0;
            margin: 0;
        }
        .corner-button:hover {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
        }
        .close-button {
            color: #ff6b6b;
        }
        .power-button {
            color: #ffa726;
        }
        """
        css_provider.load_from_data(css.encode())
        style_context = self.box.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        style_context.add_class("timer-box")
        
        self.event_box.add(self.box)
        
        # Create overlay for corner buttons
        self.overlay = Gtk.Overlay()
        self.box.pack_start(self.overlay, True, True, 0)
        
        # Timer label (centered)
        self.label = Gtk.Label()
        self.label.set_markup("<span size='x-large' weight='bold' foreground='white'>00:00</span>")
        self.label.set_halign(Gtk.Align.CENTER)
        self.label.set_valign(Gtk.Align.CENTER)
        self.overlay.add_overlay(self.label)
        
        # Close button (X) - top-left corner
        self.close_button = Gtk.Button(label="✕")
        self.close_button.set_size_request(25, 25)
        self.close_button.set_halign(Gtk.Align.START)
        self.close_button.set_valign(Gtk.Align.START)
        self.close_button.set_margin_start(5)
        self.close_button.set_margin_top(5)
        
        close_style = self.close_button.get_style_context()
        close_style.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        close_style.add_class("corner-button")
        close_style.add_class("close-button")
        self.close_button.connect("clicked", self.on_close_clicked)
        self.overlay.add_overlay(self.close_button)
        
        # Power button (stop service) - bottom-left corner
        self.power_button = Gtk.Button(label="⏻")
        self.power_button.set_size_request(25, 25)
        self.power_button.set_halign(Gtk.Align.START)
        self.power_button.set_valign(Gtk.Align.END)
        self.power_button.set_margin_start(5)
        self.power_button.set_margin_bottom(5)
        
        power_style = self.power_button.get_style_context()
        power_style.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        power_style.add_class("corner-button")
        power_style.add_class("power-button")
        self.power_button.connect("clicked", self.on_power_clicked)
        self.overlay.add_overlay(self.power_button)
        
        # Connect mouse events for dragging
        self.event_box.connect("button-press-event", self.on_button_press)
        self.event_box.connect("button-release-event", self.on_button_release)
        self.event_box.connect("motion-notify-event", self.on_motion)
        
        # Enable motion events
        self.event_box.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                                 Gdk.EventMask.BUTTON_RELEASE_MASK |
                                 Gdk.EventMask.POINTER_MOTION_MASK)

        # Mouse drag variables
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Add state tracking to prevent CSS changes on every tick
        self.current_state_key = None

    def on_button_press(self, widget, event):
        if event.button == 1:  # Left click
            self.dragging = True
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
        return True

    def on_button_release(self, widget, event):
        if event.button == 1:  # Left click
            self.dragging = False
        return True

    def on_motion(self, widget, event):
        if self.dragging:
            # Calculate new position
            new_x = self.get_position()[0] + (event.x_root - self.drag_start_x)
            new_y = self.get_position()[1] + (event.y_root - self.drag_start_y)
            
            # Update drag start position
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
            
            # Move window
            self.move(new_x, new_y)
        return True

    def on_close_clicked(self, widget):
        """Close button clicked - hide to system tray"""
        self.hide()
        if hasattr(self, 'parent'):
            self.parent.show_system_tray()

    def on_power_clicked(self, widget):
        """Power button clicked - stop service and exit"""
        if hasattr(self, 'parent'):
            self.parent.stop_service_and_exit()

    def update_timer(self, seconds, state='work', is_paused=False):
        """Update the timer display"""
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        time_str = f"{minutes:02d}:{remaining_seconds:02d}"
        
        # Determine the new state key and label markup
        if state == 'break':
            new_state_key = 'break'
            markup = f"<span size='x-large' weight='bold' foreground='white'>Break: {time_str}</span>"
        elif is_paused:
            new_state_key = 'paused'
            markup = f"<span size='x-large' weight='bold' foreground='white'>Paused: {time_str}</span>"
        else:
            new_state_key = 'work'
            markup = f"<span size='x-large' weight='bold' foreground='white'>{time_str}</span>"
            
        # Update label text every time for a smooth countdown
        self.label.set_markup(markup)

        # Only update CSS (which causes re-rendering) if the state has changed
        if new_state_key != self.current_state_key:
            style_context = self.box.get_style_context()
            
            # Remove all possible state classes to start fresh
            style_context.remove_class("paused")
            style_context.remove_class("break")
            
            # Add the correct class for the new state
            if new_state_key == 'break':
                style_context.add_class("break")
            elif new_state_key == 'paused':
                style_context.add_class("paused")

            self.current_state_key = new_state_key

class SystemTrayIcon:
    def __init__(self, parent):
        self.parent = parent
        self.indicator = None
        
        # Try to create system tray indicator
        try:
            self.indicator = AppIndicator3.Indicator.new(
                "pomodoro-lock",
                "pomodoro-lock",  # Use the custom icon name
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            
            # Create menu
            self.menu = Gtk.Menu()
            
            # Show timer item
            show_item = Gtk.MenuItem(label="Show Timer")
            show_item.connect("activate", self.on_show_timer)
            self.menu.append(show_item)
            
            # Separator
            separator = Gtk.SeparatorMenuItem()
            self.menu.append(separator)
            
            # Stop service item
            stop_item = Gtk.MenuItem(label="Stop Service")
            stop_item.connect("activate", self.on_stop_service)
            self.menu.append(stop_item)
            
            # Quit item
            quit_item = Gtk.MenuItem(label="Quit")
            quit_item.connect("activate", self.on_quit)
            self.menu.append(quit_item)
            
            self.menu.show_all()
            self.indicator.set_menu(self.menu)
            
            logging.info("System tray indicator created successfully")
            
        except Exception as e:
            logging.warning(f"Could not create system tray indicator: {e}")
            logging.info("System tray functionality will be limited")
            self.indicator = None

    def on_show_timer(self, widget):
        """Show the timer window"""
        self.parent.show_timer()

    def on_stop_service(self, widget):
        """Stop the service"""
        self.parent.stop_service_and_exit()

    def on_quit(self, widget):
        """Quit the application"""
        self.parent.quit_application()

    def update_status(self, state, remaining):
        """Update the system tray status"""
        if self.indicator:
            try:
                minutes = remaining // 60
                seconds = remaining % 60
                time_str = f"{minutes:02d}:{seconds:02d}"
                
                if state == 'break':
                    self.indicator.set_label(f"Break: {time_str}", "")
                else:
                    self.indicator.set_label(f"Work: {time_str}", "")
            except Exception as e:
                logging.warning(f"Error updating system tray status: {e}")

class PomodoroUI:
    def __init__(self):
        # Setup paths
        self.user_dir = os.path.expanduser('~/.local/share/pomodoro-lock')
        self.status_file = os.path.join(self.user_dir, 'status.json')
        self.lock_file = os.path.join(self.user_dir, 'ui.lock')
        self.lock_file_handle = None
        self.is_running = False
        self.ui_status_file = os.path.join(self.user_dir, 'ui_status.json')
        self.local_timer_active = False
        self.remaining_seconds = 0
        self.state = 'work'
        self.is_paused = False
        self.fallback_ui_active = False # Track if a fallback (notification/window) is shown

        # Attempt to acquire a lock to ensure single instance
        if not self.acquire_lock():
            self.show_already_running_dialog()
            return

        self.is_running = True

        # Initialize UI components
        self.timer = CountdownTimer()
        self.timer.parent = self
        self.timer.connect("destroy", self.on_timer_destroy)
        
        # Read the initial state from the service. Since local_timer_active is False,
        # this will unconditionally sync the time.
        self.read_service_status()
        
        # Now that we have the correct time, the UI can take over the countdown.
        self.local_timer_active = True
        
        # Initialize system tray based on desktop environment
        self.desktop_env = self.detect_desktop_environment()
        logging.info(f"Detected desktop environment: {self.desktop_env}")
        if self.desktop_env == 'XFCE':
            # Use fallback mechanisms for XFCE
            logging.info("Using fallback mechanisms for XFCE")
            self.system_tray = None
        else:
            # Try system tray for other environments
            self.system_tray = SystemTrayIcon(self)
        
        # Show timer initially
        self.timer.show_all()
        
        # Start the UI's internal, high-precision timer
        GLib.timeout_add_seconds(1, self.ui_tick)

    def acquire_lock(self):
        """
        Acquire an exclusive, non-blocking lock on the lock file.
        Returns True if the lock was acquired, False otherwise.
        """
        try:
            self.lock_file_handle = open(self.lock_file, 'w')
            fcntl.flock(self.lock_file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # Write PID for debugging purposes
            self.lock_file_handle.write(str(os.getpid()))
            self.lock_file_handle.flush()
            return True
        except (IOError, BlockingIOError):
            # Another instance is holding the lock
            if self.lock_file_handle:
                self.lock_file_handle.close()
            return False

    def detect_desktop_environment(self):
        """Detect the current desktop environment"""
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        session = os.environ.get('DESKTOP_SESSION', '').lower()
        
        if 'xfce' in desktop or 'xfce' in session:
            return 'XFCE'
        elif 'gnome' in desktop or 'gnome' in session:
            return 'GNOME'
        elif 'kde' in desktop or 'kde' in session:
            return 'KDE'
        elif 'mate' in desktop or 'mate' in session:
            return 'MATE'
        elif 'cinnamon' in desktop or 'cinnamon' in session:
            return 'Cinnamon'
        else:
            return 'Unknown'

    def show_already_running_dialog(self):
        """Show dialog that app is already running and then exit."""
        dialog = Gtk.MessageDialog(
            parent=None,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Pomodoro Lock is already running"
        )
        dialog.format_secondary_text("Check the system tray for the Pomodoro Lock icon.")
        dialog.run()
        dialog.destroy()

    def show_timer(self):
        """Show the timer window, destroy any fallbacks, and take control."""
        # Ensure any existing fallback UI is destroyed before showing the main timer.
        if hasattr(self, 'current_notification') and self.current_notification:
            self.current_notification.close()
            self.current_notification = None
        if hasattr(self, 'status_window') and self.status_window:
            self.status_window.destroy()
            self.status_window = None
        
        self.fallback_ui_active = False
        
        # Sync with the latest from the service, in case time passed while hidden.
        self.read_service_status()
        self.local_timer_active = True
        self.timer.show_all()
        self.timer.present()

    def show_system_tray(self):
        """Show the system tray icon or a single fallback UI."""
        # If a fallback is already active, do nothing.
        if self.fallback_ui_active:
            return

        if self.desktop_env == 'XFCE':
            self.show_minimized_notification()
            self.fallback_ui_active = True # Mark fallback as active
        elif self.system_tray and self.system_tray.indicator:
            self.system_tray.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        else:
            # Fallback for other environments without AppIndicator3 support
            self.show_minimized_notification()
            self.fallback_ui_active = True # Mark fallback as active

    def show_minimized_notification(self):
        """Show a persistent notification when minimized"""
        try:
            import notify2
            notify2.init("Pomodoro Lock")
            notification = notify2.Notification(
                "Pomodoro Lock", 
                "Timer is running in background. Click to restore.",
                "pomodoro-lock"
            )
            notification.set_timeout(0)  # Persistent notification
            notification.add_action("restore", "Restore", self.on_notification_restore)
            notification.add_action("stop", "Stop Service", self.on_notification_stop)
            notification.show()
            self.current_notification = notification
        except Exception as e:
            logging.warning(f"Could not show notification: {e}")
            # Create a small status window as last resort
            self.create_status_window()

    def on_notification_restore(self, notification, action):
        """Restore timer window from notification."""
        self.show_timer()
        # The notification is closed automatically, so we just need to update the flag.
        self.fallback_ui_active = False

    def on_notification_stop(self, notification, action):
        """Stop service from notification"""
        self.stop_service_and_exit()

    def create_status_window(self):
        """Create a single status window as a last resort fallback."""
        # If a status window somehow already exists, don't create another.
        if hasattr(self, 'status_window') and self.status_window:
            return

        self.status_window = Gtk.Window()
        self.status_window.set_decorated(False)
        self.status_window.set_keep_above(True)
        self.status_window.set_default_size(200, 60)
        self.status_window.set_resizable(False)
        
        # Position in top-right corner
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() if display else display.get_monitor(0)
        geometry = monitor.get_geometry()
        x = geometry.x + geometry.width - 200
        y = geometry.y
        self.status_window.move(x, y)
        
        # Create content
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        
        # Status label
        self.status_label = Gtk.Label(label="⏰ Pomodoro Running")
        self.status_label.set_margin_end(10)
        box.pack_start(self.status_label, True, True, 0)
        
        # Restore button
        restore_button = Gtk.Button(label="Show")
        restore_button.connect("clicked", lambda w: self.show_timer())
        box.pack_start(restore_button, False, False, 0)
        
        # Stop button
        stop_button = Gtk.Button(label="Stop")
        stop_button.connect("clicked", lambda w: self.stop_service_and_exit())
        box.pack_start(stop_button, False, False, 0)
        
        self.status_window.add(box)
        self.status_window.show_all()
        
        # Make it draggable
        self.status_window.connect("button-press-event", self.on_status_window_button_press)
        self.status_window.connect("button-release-event", self.on_status_window_button_release)
        self.status_window.connect("motion-notify-event", self.on_status_window_motion)
        self.status_window.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                                     Gdk.EventMask.BUTTON_RELEASE_MASK |
                                     Gdk.EventMask.POINTER_MOTION_MASK)

    def on_status_window_button_press(self, widget, event):
        if event.button == 1:  # Left click
            self.status_dragging = True
            self.status_drag_start_x = event.x_root
            self.status_drag_start_y = event.y_root
        return True

    def on_status_window_button_release(self, widget, event):
        if event.button == 1:  # Left click
            self.status_dragging = False
        return True

    def on_status_window_motion(self, widget, event):
        if hasattr(self, 'status_dragging') and self.status_dragging:
            new_x = self.status_window.get_position()[0] + (event.x_root - self.status_drag_start_x)
            new_y = self.status_window.get_position()[1] + (event.y_root - self.status_drag_start_y)
            self.status_drag_start_x = event.x_root
            self.status_drag_start_y = event.y_root
            self.status_window.move(new_x, new_y)
        return True

    def stop_service_and_exit(self):
        """Stop the service and exit"""
        try:
            os.system("systemctl --user stop pomodoro-lock.service")
            logging.info("Service stopped")
        except Exception as e:
            logging.error(f"Error stopping service: {e}")
        self.quit_application()

    def quit_application(self):
        """Quit the application, ensuring cleanup."""
        # Clean up the UI status file on quit
        if os.path.exists(self.ui_status_file):
            os.remove(self.ui_status_file)
        if self.lock_file_handle:
            try:
                fcntl.flock(self.lock_file_handle, fcntl.LOCK_UN)
                self.lock_file_handle.close()
            except Exception as e:
                logging.warning(f"Failed to release lock file: {e}")
        Gtk.main_quit()

    def on_timer_destroy(self, widget):
        """Called when the timer window is closed by the user."""
        self.local_timer_active = False
        # Clean up the UI status file so the service takes back full control
        if os.path.exists(self.ui_status_file):
            os.remove(self.ui_status_file)
        self.hide()
        self.show_system_tray()

    def ui_tick(self):
        """UI's internal timer tick. This is the new master countdown."""
        if self.local_timer_active and not self.is_paused:
            self.remaining_seconds -= 1

        # Update the visual timer display
        self.timer.update_timer(self.remaining_seconds, self.state, self.is_paused)
        
        # Continuously write status for the service to see
        self.write_ui_status()
        
        # Poll the main service to see if a state change has occurred (e.g., break started)
        self.read_service_status()

        return True # Keep the timer running

    def read_service_status(self):
        """Reads the main status file to sync state from the service."""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                
                new_state = status.get('state', self.state)
                new_remaining = status.get('remaining', self.remaining_seconds)
                
                # If the UI timer isn't the master, or if the service has forced
                # a state change (e.g., work -> break), sync the UI's state.
                if not self.local_timer_active or new_state != self.state:
                    self.state = new_state
                    self.remaining_seconds = new_remaining
                    if new_state != self.state:
                        logging.info(f"Service changed state to {self.state}. UI is syncing.")

                self.is_paused = status.get('is_paused', False)

        except (json.JSONDecodeError, FileNotFoundError) as e:
            logging.warning(f"Could not read service status, may be starting up: {e}")

    def write_ui_status(self):
        """Writes the UI's timer status for the service to consume."""
        if self.local_timer_active:
            with open(self.ui_status_file, 'w') as f:
                json.dump({'remaining': self.remaining_seconds}, f)

    def hide(self):
        """Hide the timer window"""
        self.timer.hide()

def main():
    """Initializes and runs the Pomodoro UI application."""
    # Configure logging
    log_file = os.path.expanduser('~/.local/share/pomodoro-lock/pomodoro-ui.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
    )

    Gtk.init(None)
    app = PomodoroUI()

    # Only run the main GTK loop if this is the primary instance
    if app.is_running:
        # Set up signal handling for graceful shutdown
        def signal_handler(signum, frame):
            logging.info("Received shutdown signal, quitting application.")
            app.quit_application()

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        Gtk.main()

if __name__ == "__main__":
    main() 