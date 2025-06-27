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

# Import platform abstraction layers with explicit imports to avoid circular issues
import platform as platform_module
SYSTEM = platform_module.system().lower()

if SYSTEM == "linux":
    from platform_abstraction.linux import (
        NotificationManager,
        SystemTrayManager,
        ScreenManager,
        AutostartManager,
        FileLockManager
    )
elif SYSTEM == "windows":
    from platform_abstraction.windows import (
        NotificationManager,
        SystemTrayManager,
        ScreenManager,
        AutostartManager,
        FileLockManager
    )
else:
    raise ImportError(f"Unsupported platform: {SYSTEM}")

# Import cross-platform GUI
if SYSTEM == "linux":
    from gui.gtk_ui import (
        TimerWindow,
        FullScreenOverlay,
        MultiDisplayOverlay
    )
elif SYSTEM == "windows":
    from gui.tkinter_ui import (
        TimerWindow,
        FullScreenOverlay,
        MultiDisplayOverlay
    )
else:
    raise ImportError(f"Unsupported platform: {SYSTEM}")

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
        
        # Initialize platform-specific components (but NOT tray yet)
        self.notification_manager = NotificationManager()
        self.screen_manager = ScreenManager()
        self.autostart_manager = AutostartManager()
        self.file_lock = FileLockManager(str(self.lock_file))
        
        # Timer state
        self.work_time = self.config.get('work_time_minutes', 25) * 60
        self.break_time = self.config.get('break_time_minutes', 5) * 60
        self.notification_time = self.config.get('notification_time_minutes', 2) * 60
        self.current_time = self.work_time
        self.is_work_session = True
        self.is_paused = False
        self.is_running = False
        self.timer_thread = None
        self.stop_event = threading.Event()
        
        # Snooze functionality
        self.snooze_timer = None
        self.paused_time = None
        
        # Setup signal handlers (no SIGUSR1)
        self._setup_signal_handlers()
        
        # Acquire lock to prevent multiple instances
        if not self._acquire_lock():
            self._show_already_running_dialog()
            return
        
        # Only now, after lock is acquired, create tray and GUI
        self._init_gui_components()
        
        try:
            self.system_tray = SystemTrayManager(self)
            logging.info("System tray initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize system tray: {e}")
            # Continue without system tray
            self.system_tray = None
        
        # Always show the timer window on startup
        self.timer_window.show_window()
        
        # Check and enable systemd service on first launch
        self._check_and_enable_service()
        
        # Start the application
        self.start()
    
    def _setup_paths(self):
        """Setup platform-specific paths"""
        if SYSTEM == "linux":
            self.config_dir = Path.home() / ".local" / "share" / "pomodoro-lock" / "config"
            self.lock_file = Path.home() / ".local" / "share" / "pomodoro-lock" / "pomodoro-ui.lock"
            self.service_enabled_file = Path.home() / ".local" / "share" / "pomodoro-lock" / ".service-enabled"
        else:  # Windows
            self.config_dir = Path.home() / "AppData" / "Local" / "pomodoro-lock" / "config"
            self.lock_file = Path.home() / "AppData" / "Local" / "pomodoro-lock" / "pomodoro-ui.lock"
            self.service_enabled_file = Path.home() / "AppData" / "Local" / "pomodoro-lock" / ".service-enabled"
        
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
    
    def _init_gui_components(self):
        """Initialize GUI components"""
        try:
            # Create timer window
            self.timer_window = TimerWindow(
                on_close=self._on_timer_close,
                on_power=self._on_power_clicked,
                on_pause_snooze=self._on_pause_snooze_clicked
            )
            
            # Create multi-display overlay
            self.multi_overlay = MultiDisplayOverlay()
            
            # Hide timer window initially
            self.timer_window.hide_window()
            
            logging.info("GUI components initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize GUI components: {e}")
            # Don't re-raise - try to continue without GUI
            raise
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logging.info(f"Received signal {signum}, shutting down gracefully")
            self.quit_application()
        
        # Set up GLib assertion failure handler for Linux
        if SYSTEM == "linux":
            try:
                import gi
                gi.require_version('GLib', '2.0')
                from gi.repository import GLib
                
                # Set up assertion failure handler
                def glib_assertion_handler(log_domain, log_level, message):
                    if "g_hash_table_remove_node" in message or "assertion failed" in message:
                        logging.warning(f"GLib assertion caught: {message}")
                        # Don't abort, just log the warning
                        return True
                    return False
                
                # Install the assertion handler
                GLib.log_set_handler(None, GLib.LogLevelFlags.LEVEL_WARNING, glib_assertion_handler)
                logging.info("GLib assertion failure handler installed")
                
            except Exception as e:
                logging.warning(f"Could not install GLib assertion handler: {e}")
        
        # Set up system signal handlers
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _acquire_lock(self):
        """Acquire file lock to prevent multiple instances"""
        return self.file_lock.acquire_lock()
    
    def _show_already_running_dialog(self):
        """Show dialog when another instance is running and exit"""
        if SYSTEM == "linux":
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            dialog = Gtk.MessageDialog(
                parent=None,
                message_type=Gtk.MessageType.INFO,
                modal=True,
                destroy_with_parent=True,
                text="Pomodoro Lock is already running"
            )
            dialog.format_secondary_text(
                "The timer is already running. Only one instance is allowed.\n\n"
                "To show the timer window, click the Pomodoro Lock icon in your system tray."
            )
            dialog.add_buttons(
                "OK", Gtk.ResponseType.OK
            )
            dialog.run()
            dialog.destroy()
        else:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(
                "Pomodoro Lock", 
                "Pomodoro Lock is already running. Only one instance is allowed.\n\n"
                "To show the timer window, click the Pomodoro Lock icon in your system tray."
            )
            root.destroy()
        sys.exit(0)
    
    def start(self):
        """Start the Pomodoro timer"""
        logging.info("Starting Pomodoro timer")
        self.is_running = True
        
        # Show system tray (now safe, only one instance)
        self._show_system_tray()
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
        
        # Start GUI event loop
        self._start_gui_loop()
    
    def _timer_loop(self):
        """Main timer loop"""
        logging.info("Starting timer loop")
        while self.is_running and not self.stop_event.is_set():
            try:
                if not self.is_paused:
                    if self.current_time > 0:
                        self.current_time -= 1
                        
                        # Check for notification time
                        if self.current_time == self.notification_time:
                            self._send_break_notification()
                        
                        # Check if session ended
                        if self.current_time == 0:
                            self._session_ended()
                    
                    # Note: GUI updates are handled by the main thread callbacks
                    # (_gtk_update_callback or _tkinter_update_callback)
                    # This prevents race conditions and memory corruption
                
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error in timer loop: {e}")
                # Continue the timer loop even if there's an error
                # Don't quit the application due to timer errors
                time.sleep(1)
        
        logging.info("Timer loop ended")
    
    def _send_break_notification(self):
        """Send notification before break"""
        if self.is_work_session:
            self.notification_manager.send_notification(
                "Pomodoro Lock",
                f"Break starting in {self.notification_time // 60} minutes!",
                "normal",
                timeout=8  # 8 seconds for break warning
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
        try:
            logging.info("Starting break session")
            self.is_work_session = False
            self.current_time = self.break_time
            
            # Lower timer window to ensure overlay is on top
            try:
                self.timer_window.lower_window()
            except Exception as e:
                logging.error(f"Failed to lower timer window: {e}")
            
            # Show break overlay
            try:
                self.multi_overlay.create_overlays()
                self.multi_overlay.show_all()
            except Exception as e:
                logging.error(f"Failed to show break overlay: {e}")
            
            # Send notification
            try:
                self.notification_manager.send_notification(
                    "Pomodoro Lock",
                    "Break time! Take a rest.",
                    "high",
                    timeout=5  # 5 seconds for break start notification
                )
            except Exception as e:
                logging.error(f"Failed to send break notification: {e}")
            
            # Update system tray
            self._update_system_tray()
        except Exception as e:
            logging.error(f"Error starting break session: {e}")
    
    def _end_break(self):
        """End break session"""
        try:
            logging.info("Ending break session")
            self.is_work_session = True
            self.current_time = self.work_time
            
            # Hide break overlay
            try:
                self.multi_overlay.hide_all()
            except Exception as e:
                logging.error(f"Failed to hide break overlay: {e}")
            
            # Raise timer window back to normal level
            try:
                self.timer_window.raise_window()
            except Exception as e:
                logging.error(f"Failed to raise timer window: {e}")
            
            # Send notification
            try:
                self.notification_manager.send_notification(
                    "Pomodoro Lock",
                    "Break ended! Back to work.",
                    "normal",
                    timeout=6  # 6 seconds for break end notification
                )
            except Exception as e:
                logging.error(f"Failed to send break end notification: {e}")
            
            # Update system tray
            self._update_system_tray()
        except Exception as e:
            logging.error(f"Error ending break session: {e}")
    
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
            
            # Update break overlay only if not in work session and not paused
            if not self.is_work_session and not self.is_paused:
                try:
                    self.multi_overlay.update_timer(self.current_time)
                except RecursionError as e:
                    logging.error(f"Recursion error in overlay update: {e}")
                    # Force cleanup and recreate overlays
                    self._recreate_overlays()
                except Exception as e:
                    logging.error(f"Failed to update break overlay: {e}")
            
            # Update system tray
            self._update_system_tray()
        except Exception as e:
            logging.error(f"Failed to update GUI: {e}")
            # Don't re-raise - just log and continue
    
    def _recreate_overlays(self):
        """Recreate overlays to handle monitor sleep/wake scenarios"""
        try:
            logging.info("Recreating overlays due to monitor changes")
            self.multi_overlay.destroy_all()
            time.sleep(0.1)  # Small delay to ensure cleanup
            self.multi_overlay.create_overlays()
            if not self.is_work_session:
                self.multi_overlay.show_all()
        except Exception as e:
            logging.error(f"Failed to recreate overlays: {e}")
    
    def _update_system_tray(self):
        """Update system tray status"""
        try:
            if self.system_tray is None:
                return  # System tray not available
            
            state = 'break' if not self.is_work_session else 'work'
            self.system_tray.update_status(state, self.current_time)
        except Exception as e:
            logging.error(f"Failed to update system tray: {e}")
            # Don't re-raise - just log and continue
    
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
        try:
            if not self.is_running:
                logging.info("Stopping GTK main loop")
                Gtk.main_quit()
                return False
            
            self._update_gui()
            return True
        except Exception as e:
            logging.error(f"Error in GTK update callback: {e}")
            # Continue the timer even if GUI update fails
            # Don't quit the application due to GUI errors
            return True
    
    def _tkinter_update_callback(self):
        """Tkinter timer callback for GUI updates"""
        try:
            if not self.is_running:
                self.root.quit()
                return
            
            self._update_gui()
            self.root.after(1000, self._tkinter_update_callback)
        except Exception as e:
            logging.error(f"Error in Tkinter update callback: {e}")
            # Continue the timer even if GUI update fails
            if self.is_running:
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
    
    def _on_pause_snooze_clicked(self):
        """Handle pause/snooze button click"""
        try:
            if self.is_paused:
                # If already paused, resume the timer immediately
                self.is_paused = False
                logging.info("Timer resumed manually")
                self.notification_manager.send_notification(
                    "Pomodoro Lock",
                    "Timer resumed!",
                    "normal",
                    timeout=5  # 5 seconds for resume notification
                )
            else:
                # Pause the timer and set up auto-resume after 10 minutes
                self.is_paused = True
                snooze_seconds = 10 * 60  # 10 minutes
                
                # Store the original time when paused
                self.paused_time = self.current_time
                
                # Set up auto-resume timer
                self.snooze_timer = threading.Timer(snooze_seconds, self._auto_resume_timer)
                self.snooze_timer.daemon = True
                self.snooze_timer.start()
                
                logging.info(f"Timer paused and will auto-resume in {snooze_seconds // 60} minutes")
                self.notification_manager.send_notification(
                    "Pomodoro Lock",
                    f"Timer paused. Will resume in {snooze_seconds // 60} minutes",
                    "normal",
                    timeout=10  # 10 seconds for pause notification
                )
            
            # Update GUI to reflect the new state
            self._update_gui()
            
        except Exception as e:
            logging.error(f"Error in pause/snooze functionality: {e}")
    
    def _auto_resume_timer(self):
        """Automatically resume the timer after snooze period"""
        try:
            if self.is_paused:
                self.is_paused = False
                logging.info("Timer auto-resumed after snooze period")
                self.notification_manager.send_notification(
                    "Pomodoro Lock",
                    "Timer resumed automatically!",
                    "normal",
                    timeout=5  # 5 seconds for auto-resume notification
                )
                
                # Update GUI to reflect the new state
                self._update_gui()
                
        except Exception as e:
            logging.error(f"Error in auto-resume functionality: {e}")
    
    def quit_application(self):
        """Quit the application with enhanced cleanup"""
        logging.info("Quitting Pomodoro Lock")
        self.is_running = False
        self.stop_event.set()
        
        # Cancel any active snooze timer
        if self.snooze_timer and self.snooze_timer.is_alive():
            try:
                self.snooze_timer.cancel()
                logging.info("Cancelled active snooze timer")
            except Exception as e:
                logging.error(f"Error cancelling snooze timer: {e}")
        
        # Stop system tray
        if self.system_tray is not None and hasattr(self.system_tray, 'stop'):
            try:
                self.system_tray.stop()
            except Exception as e:
                logging.error(f"Error stopping system tray: {e}")
        
        # Release lock
        try:
            self.file_lock.release_lock()
        except Exception as e:
            logging.error(f"Error releasing lock: {e}")
        
        # Destroy GUI components with enhanced error handling
        try:
            logging.info("Destroying GUI components...")
            
            # First destroy overlays to prevent any active operations
            if hasattr(self, 'multi_overlay') and self.multi_overlay:
                try:
                    self.multi_overlay.destroy_all()
                    logging.info("Overlays destroyed successfully")
                except Exception as e:
                    logging.error(f"Error destroying overlays: {e}")
            
            # Small delay to allow GTK to process overlay destruction
            import time
            time.sleep(0.05)
            
            # Then destroy timer window
            if hasattr(self, 'timer_window') and self.timer_window:
                try:
                    self.timer_window.destroy_window()
                    logging.info("Timer window destroyed successfully")
                except Exception as e:
                    logging.error(f"Error destroying timer window: {e}")
            
            # Additional delay before quitting GUI loop
            time.sleep(0.05)
            
        except Exception as e:
            logging.error(f"Error during GUI cleanup: {e}")
        
        # Quit GUI loop with error handling
        try:
            if SYSTEM == "linux":
                import gi
                gi.require_version('Gtk', '3.0')
                from gi.repository import Gtk
                Gtk.main_quit()
                logging.info("GTK main loop quit successfully")
            else:
                if hasattr(self, 'root'):
                    self.root.quit()
                    logging.info("Tkinter main loop quit successfully")
        except Exception as e:
            logging.error(f"Error quitting GUI loop: {e}")
            # Force exit if GUI quit fails
            import sys
            sys.exit(0)
    
    def _check_and_enable_service(self):
        """Check if systemd service is enabled, and enable it if not"""
        if SYSTEM != "linux":
            return  # Only for Linux
        
        # Check if we've already tried to enable the service
        if self.service_enabled_file.exists():
            return
        
        try:
            import subprocess
            import shutil
            
            # Check if systemctl is available
            if not shutil.which("systemctl"):
                logging.info("systemctl not available, skipping service enablement")
                return
            
            # Check if service is already enabled
            result = subprocess.run(
                ["systemctl", "--user", "is-enabled", "pomodoro-lock.service"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and "enabled" in result.stdout:
                logging.info("Service already enabled")
                # Mark as enabled to skip future checks
                self.service_enabled_file.touch()
                return
            
            # Try to enable the service
            logging.info("Enabling systemd service for autostart...")
            result = subprocess.run(
                ["systemctl", "--user", "enable", "pomodoro-lock.service"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logging.info("✅ Service enabled successfully for autostart")
                # Mark as enabled to skip future checks
                self.service_enabled_file.touch()
            else:
                logging.warning(f"Failed to enable service: {result.stderr}")
                # Still mark as attempted to avoid repeated failures
                self.service_enabled_file.touch()
                
        except subprocess.TimeoutExpired:
            logging.warning("Timeout while enabling service")
            self.service_enabled_file.touch()
        except Exception as e:
            logging.error(f"Error enabling service: {e}")
            self.service_enabled_file.touch()

def main():
    """Main entry point"""
    try:
        logging.info("Starting Pomodoro Lock application")
        app = PomodoroTimer()
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
    except Exception as e:
        logging.error(f"Application error: {e}")
        # Don't re-raise the exception to prevent unexpected quits
        # Just log the error and exit gracefully
        return 1
    return 0

if __name__ == "__main__":
    main() 