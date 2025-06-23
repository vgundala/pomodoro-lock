#!/usr/bin/env python3
"""
Pomodoro Lock UI - Timer Display Client

This UI component displays the timer and reads status from the service.
It's a lightweight client that doesn't manage timer logic.
"""

import os
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
        self.set_title("Pomodoro Lock")
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
            outline: none;
            color: white;
            font-weight: bold;
            font-size: 16px;
            padding: 0;
            margin: 0;
            box-shadow: none;
        }
        .corner-button:hover {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
            border: none;
            outline: none;
            box-shadow: none;
        }
        .corner-button:focus {
            border: none;
            outline: none;
            box-shadow: none;
        }
        .corner-button:active {
            border: none;
            outline: none;
            box-shadow: none;
        }
        .corner-button:selected {
            border: none;
            outline: none;
            box-shadow: none;
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
        """Power button clicked - quit application"""
        if hasattr(self, 'parent'):
            self.parent.quit_application()

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

class SystemTrayIcon:
    def __init__(self, parent):
        self.parent = parent
        self.indicator = None
        
        try:
            # Use the application's own icon name
            self.indicator = AppIndicator3.Indicator.new(
                "pomodoro-lock",
                "pomodoro-lock",  # This now refers to the installed icon
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            
            # Set tooltip to show "Pomodoro Lock" when hovered
            self.indicator.set_title("Pomodoro Lock")
            
            # Create a more intuitive menu
            self.menu = Gtk.Menu()
            
            # Show timer item
            show_item = Gtk.MenuItem(label="Show Timer")
            show_item.connect("activate", self.on_show_timer)
            self.menu.append(show_item)
            
            # Separator
            separator = Gtk.SeparatorMenuItem()
            self.menu.append(separator)
            
            # A single, clear Quit option
            quit_item = Gtk.MenuItem(label="Quit Pomodoro Lock")
            quit_item.connect("activate", self.on_quit)
            self.menu.append(quit_item)
            
            self.menu.show_all()
            self.indicator.set_menu(self.menu)
            
            logging.info("System tray icon created successfully")
            
        except Exception as e:
            logging.warning(f"Could not create system tray indicator: {e}")
            self.indicator = None

    def on_show_timer(self, widget):
        """Show the timer window."""
        self.parent.show_timer()

    def on_quit(self, widget):
        """Quits the entire application."""
        logging.info("Quit clicked: Exiting application.")
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
        self.lock_file = os.path.join(self.user_dir, 'ui.lock')
        self.lock_file_handle = None
        self.is_running = False
        
        # Load config
        self.config_file = os.path.join(self.user_dir, 'config/config.json')
        self.config = self.load_config()

        # Initialize timer state
        self.remaining_seconds = self.config.get('work_time_minutes', 30) * 60
        self.state = 'work'
        self.is_paused = False

        # Attempt to acquire a lock to ensure single instance
        if not self.acquire_lock():
            self.show_already_running_dialog()
            return

        self.is_running = True

        # Initialize UI components
        self.timer = CountdownTimer()
        self.timer.parent = self
        self.timer.connect("destroy", self.on_timer_destroy)
        
        # Initialize system tray
        self.system_tray = SystemTrayIcon(self)
        
        # Initialize overlay for break periods
        self.overlay = None
        
        # Show timer initially
        self.timer.show_all()
        
        # Start the UI's internal timer
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
        """Shows the timer window."""
        self.timer.show_all()
        self.timer.present()

    def show_system_tray(self):
        """Shows the system tray icon."""
        if self.system_tray and self.system_tray.indicator:
            self.system_tray.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        else:
            logging.error("System tray icon could not be created or shown.")

    def quit_application(self):
        """Quit the application, ensuring cleanup."""
        # Clean up overlay if it exists
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy_all()
        
        if self.lock_file_handle:
            try:
                fcntl.flock(self.lock_file_handle, fcntl.LOCK_UN)
                self.lock_file_handle.close()
            except Exception as e:
                logging.warning(f"Failed to release lock file: {e}")
        Gtk.main_quit()

    def on_timer_destroy(self, widget):
        """Called when the timer window is closed by the user. Hides to tray."""
        self.hide()
        self.show_system_tray()

    def ui_tick(self):
        """UI's internal timer tick. This is the new master countdown."""
        if not self.is_paused:
            self.remaining_seconds -= 1

        # Update the visual timer display
        self.timer.update_timer(self.remaining_seconds, self.state, self.is_paused)
        
        # Check if work period ended and start break overlay
        if self.state == 'work' and self.remaining_seconds <= 0:
            logging.info("Work period ended, starting break overlay")
            self.start_break()
            self.state = 'break'
            self.remaining_seconds = self.config.get('break_time_minutes', 5) * 60
            if self.overlay:
                self.overlay.update_timer(self.remaining_seconds)
        elif self.state == 'break':
            # Update overlay timer during break
            if self.overlay:
                self.overlay.update_timer(self.remaining_seconds)
            
            # Check if break period ended
            if self.remaining_seconds <= 0:
                logging.info("Break period ended, starting work")
                self.end_break()
                self.state = 'work'
                self.remaining_seconds = self.config.get('work_time_minutes', 30) * 60
                self.timer.update_timer(self.remaining_seconds, self.state, self.is_paused)
        
        return True # Keep the timer running

    def hide(self):
        """Hide the timer window"""
        self.timer.hide()

    def load_config(self):
        default_config = {
            "work_time_minutes": 30,
            "break_time_minutes": 5,
            "notification_time_minutes": 2,
            "inactivity_threshold_minutes": 1
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                return {**default_config, **user_config}
            except Exception as e:
                logging.warning(f"Failed to load config, using defaults: {e}")
                return default_config
        else:
            return default_config

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