#!/usr/bin/env python3
"""
Pomodoro Lock UI - Cross-Platform Timer Application

This is the main application that works on both Linux and Windows.
It uses platform-specific implementations through abstraction layers.
"""

import os
import json
import signal
import logging
import time
import threading
import sys
from pathlib import Path

# Import platform abstraction layers
from platform import (
    NotificationManager,
    SystemTrayManager,
    ScreenManager,
    AutostartManager,
    FileLockManager,
    SYSTEM
)

# Import cross-platform GUI
from gui import (
    TimerWindow,
    FullScreenOverlay,
    MultiDisplayOverlay,
    SYSTEM as GUI_SYSTEM
)

# Setup logging
def setup_logging():
    """Setup logging based on platform"""
    if SYSTEM == "linux":
        log_path = os.path.expanduser('~/.local/share/pomodoro-lock/pomodoro-ui.log')
    else:  # Windows
        log_path = os.path.expanduser('~/AppData/Local/pomodoro-lock/pomodoro-ui.log')
    
    # Ensure log directory exists
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )

class PomodoroTimer:
    """Cross-platform Pomodoro timer with platform-specific features"""
    
    def __init__(self):
        setup_logging()
        logging.info(f"Starting Pomodoro Lock on {SYSTEM}")
        
        # Setup paths
        self._setup_paths()
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize platform-specific components
        self._init_platform_components()
        
        # Initialize GUI components
        self._init_gui_components()
        
        # Timer state
        self.work_time = self.config.get('work_time_minutes', 25) * 60
        self.break_time = self.config.get('break_time_minutes', 5) * 60
        self.notification_time = self.config.get('notification_time_minutes', 2) * 60
        
        self.current_time = self.work_time
        self.is_work_session = True
        self.is_paused = False
        self.is_running = False
        
        # Threading
        self.timer_thread = None
        self.stop_event = threading.Event()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        # Acquire lock to prevent multiple instances
        if not self._acquire_lock():
            self._show_already_running_dialog()
            return
        
        # Start the application
        self.start()
    
    def _setup_paths(self):
        """Setup platform-specific paths"""
        if SYSTEM == "linux":
            self.config_dir = Path.home() / ".local" / "share" / "pomodoro-lock" / "config"
            self.lock_file = Path.home() / ".local" / "share" / "pomodoro-lock" / "pomodoro-ui.lock"
        else:  # Windows
            self.config_dir = Path.home() / "AppData" / "Local" / "pomodoro-lock" / "config"
            self.lock_file = Path.home() / "AppData" / "Local" / "pomodoro-lock" / "pomodoro-ui.lock"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self):
        """Load configuration from file"""
        config_file = self.config_dir / "config.json"
        
        default_config = {
            "work_time_minutes": 25,
            "break_time_minutes": 5,
            "notification_time_minutes": 2,
            "inactivity_threshold_minutes": 10
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logging.error(f"Failed to load config: {e}")
        
        # Create default config
        try:
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save default config: {e}")
        
        return default_config
    
    def _init_platform_components(self):
        """Initialize platform-specific components"""
        # Initialize notification manager
        self.notification_manager = NotificationManager()
        
        # Initialize system tray manager
        self.system_tray = SystemTrayManager(self)
        
        # Initialize screen manager
        self.screen_manager = ScreenManager()
        
        # Initialize autostart manager
        self.autostart_manager = AutostartManager()
        
        # Initialize file lock manager
        self.file_lock = FileLockManager(str(self.lock_file))
    
    def _init_gui_components(self):
        """Initialize GUI components"""
        # Create timer window
        self.timer_window = TimerWindow(
            on_close=self._on_timer_close,
            on_power=self._on_power_clicked
        )
        
        # Create multi-display overlay
        self.multi_overlay = MultiDisplayOverlay()
        
        # Hide timer window initially
        self.timer_window.hide_window()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logging.info("Received shutdown signal")
            self.quit_application()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if SYSTEM == "linux":
            signal.signal(signal.SIGHUP, signal_handler)
    
    def _acquire_lock(self):
        """Acquire file lock to prevent multiple instances"""
        return self.file_lock.acquire_lock()
    
    def _show_already_running_dialog(self):
        """Show dialog when another instance is running"""
        if SYSTEM == "linux":
            # Use GTK dialog
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            
            dialog = Gtk.MessageDialog(
                parent=None,
                flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Pomodoro Lock is already running"
            )
            dialog.run()
            dialog.destroy()
        else:
            # Use Tkinter dialog
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showinfo("Pomodoro Lock", "Pomodoro Lock is already running")
            root.destroy()
        
        sys.exit(1)
    
    def start(self):
        """Start the Pomodoro timer"""
        logging.info("Starting Pomodoro timer")
        self.is_running = True
        
        # Show system tray
        self._show_system_tray()
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
        
        # Start GUI event loop
        self._start_gui_loop()
    
    def _timer_loop(self):
        """Main timer loop"""
        while self.is_running and not self.stop_event.is_set():
            if not self.is_paused:
                if self.current_time > 0:
                    self.current_time -= 1
                    
                    # Check for notification time
                    if self.current_time == self.notification_time:
                        self._send_break_notification()
                    
                    # Check if session ended
                    if self.current_time == 0:
                        self._session_ended()
                
                # Update GUI
                self._update_gui()
            
            time.sleep(1)
    
    def _send_break_notification(self):
        """Send notification before break"""
        if self.is_work_session:
            self.notification_manager.send_notification(
                "Pomodoro Lock",
                f"Break starting in {self.notification_time // 60} minutes!",
                "normal"
            )
    
    def _session_ended(self):
        """Handle session end"""
        if self.is_work_session:
            # Work session ended, start break
            self._start_break()
        else:
            # Break ended, start work
            self._end_break()
    
    def _start_break(self):
        """Start break session"""
        logging.info("Starting break session")
        self.is_work_session = False
        self.current_time = self.break_time
        
        # Show break overlay
        self.multi_overlay.create_overlays()
        self.multi_overlay.show_all()
        
        # Send notification
        self.notification_manager.send_notification(
            "Pomodoro Lock",
            "Break time! Take a rest.",
            "high"
        )
        
        # Update system tray
        self._update_system_tray()
    
    def _end_break(self):
        """End break session"""
        logging.info("Ending break session")
        self.is_work_session = True
        self.current_time = self.work_time
        
        # Hide break overlay
        self.multi_overlay.hide_all()
        
        # Send notification
        self.notification_manager.send_notification(
            "Pomodoro Lock",
            "Break ended! Back to work.",
            "normal"
        )
        
        # Update system tray
        self._update_system_tray()
    
    def _update_gui(self):
        """Update GUI components"""
        try:
            # Update timer window
            if hasattr(self.timer_window, 'update_timer'):
                self.timer_window.update_timer(
                    self.current_time,
                    'break' if not self.is_work_session else 'work',
                    self.is_paused
                )
            
            # Update break overlay
            if not self.is_work_session:
                self.multi_overlay.update_timer(self.current_time)
            
            # Update system tray
            self._update_system_tray()
        except Exception as e:
            logging.error(f"Failed to update GUI: {e}")
    
    def _update_system_tray(self):
        """Update system tray status"""
        try:
            state = 'break' if not self.is_work_session else 'work'
            self.system_tray.update_status(state, self.current_time)
        except Exception as e:
            logging.error(f"Failed to update system tray: {e}")
    
    def _show_system_tray(self):
        """Show system tray icon"""
        # System tray is automatically shown when created
        pass
    
    def _start_gui_loop(self):
        """Start the GUI event loop"""
        if SYSTEM == "linux":
            # GTK main loop
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk, GLib
            
            # Add timer for GUI updates
            GLib.timeout_add(1000, self._gtk_update_callback)
            
            # Start GTK main loop
            Gtk.main()
        else:
            # Tkinter main loop
            import tkinter as tk
            
            # Create root window for Tkinter
            self.root = tk.Tk()
            self.root.withdraw()  # Hide root window
            
            # Add timer for GUI updates
            self._tkinter_update_callback()
            
            # Start Tkinter main loop
            self.root.mainloop()
    
    def _gtk_update_callback(self):
        """GTK timer callback for GUI updates"""
        if not self.is_running:
            Gtk.main_quit()
            return False
        
        self._update_gui()
        return True
    
    def _tkinter_update_callback(self):
        """Tkinter timer callback for GUI updates"""
        if not self.is_running:
            self.root.quit()
            return
        
        self._update_gui()
        self.root.after(1000, self._tkinter_update_callback)
    
    def show_timer(self):
        """Show the timer window"""
        self.timer_window.show_window()
    
    def _on_timer_close(self):
        """Handle timer window close"""
        self.timer_window.hide_window()
    
    def _on_power_clicked(self):
        """Handle power button click"""
        self.quit_application()
    
    def quit_application(self):
        """Quit the application"""
        logging.info("Quitting Pomodoro Lock")
        self.is_running = False
        self.stop_event.set()
        
        # Stop system tray
        if hasattr(self.system_tray, 'stop'):
            self.system_tray.stop()
        
        # Release lock
        self.file_lock.release_lock()
        
        # Destroy GUI components
        self.timer_window.destroy_window()
        self.multi_overlay.destroy_all()
        
        # Quit GUI loop
        if SYSTEM == "linux":
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            Gtk.main_quit()
        else:
            if hasattr(self, 'root'):
                self.root.quit()

def main():
    """Main entry point"""
    try:
        app = PomodoroTimer()
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
    except Exception as e:
        logging.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main() 