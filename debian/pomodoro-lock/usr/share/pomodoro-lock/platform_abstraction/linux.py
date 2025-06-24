"""
Linux-specific platform implementations for Pomodoro Lock
"""

import os
import sys
import json
import fcntl
import subprocess
import logging
import platform as platform_module
from pathlib import Path

# Check for Linux
if platform_module.system().lower() != "linux":
    raise ImportError("Linux platform module imported on non-Linux system")

# Optional dependencies
GTK_AVAILABLE = False
XLIB_AVAILABLE = False
NOTIFY2_AVAILABLE = False
APPINDICATOR_AVAILABLE = False

try:
    import gi
    gi.require_version('Notify', '0.7')
    gi.require_version('Gtk', '3.0')
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import Notify, Gtk, GLib, Gdk, AppIndicator3
    GTK_AVAILABLE = True
except ImportError:
    logging.warning("GTK3 not available - GUI features will be disabled")

try:
    from Xlib import display
    XLIB_AVAILABLE = True
except ImportError:
    logging.warning("python-xlib not available - screen detection will be limited")

try:
    import notify2
    NOTIFY2_AVAILABLE = True
except ImportError:
    logging.warning("notify2 not available - notifications will be disabled")

try:
    import gi
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3
    APPINDICATOR_AVAILABLE = True
except ImportError:
    logging.warning("AppIndicator3 not available - system tray will be disabled")

class NotificationManager:
    """Linux notification manager using notify2"""
    
    def __init__(self):
        self.initialized = False
        if NOTIFY2_AVAILABLE:
            try:
                notify2.init("Pomodoro Lock")
                self.initialized = True
            except Exception as e:
                logging.error(f"Failed to initialize notify2: {e}")
    
    def send_notification(self, title, message, urgency="normal"):
        """Send a desktop notification"""
        if not self.initialized:
            logging.warning("Notifications not available")
            return False
        
        try:
            notification = notify2.Notification(title, message)
            notification.set_urgency(urgency)
            notification.show()
            return True
        except Exception as e:
            logging.error(f"Failed to send notification: {e}")
            return False

class SystemTrayManager:
    """Linux system tray manager using AppIndicator3"""
    
    def __init__(self, parent):
        self.parent = parent
        self.indicator = None
        self.menu = None
        
        if not GTK_AVAILABLE:
            logging.warning("System tray not available (GTK missing)")
            return
        
        try:
            self._create_indicator()
        except Exception as e:
            logging.error(f"Failed to create system tray: {e}")
    
    def _create_indicator(self):
        """Create the system tray indicator"""
        self.indicator = AppIndicator3.Indicator.new(
            "pomodoro-lock",
            "pomodoro-lock",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Create menu
        self.menu = Gtk.Menu()
        
        # Show timer item
        show_item = Gtk.MenuItem(label="Show Timer")
        show_item.connect("activate", self._on_show_timer)
        self.menu.append(show_item)
        
        # Separator
        separator = Gtk.SeparatorMenuItem()
        self.menu.append(separator)
        
        # Quit item
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self._on_quit)
        self.menu.append(quit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
    
    def _on_show_timer(self, widget):
        """Show timer window"""
        if self.parent:
            self.parent.show_timer()
    
    def _on_quit(self, widget):
        """Quit application"""
        if self.parent:
            self.parent.quit_application()
    
    def update_status(self, state, remaining):
        """Update system tray status"""
        if not self.indicator:
            return
        
        # Update tooltip
        minutes = remaining // 60
        seconds = remaining % 60
        tooltip = f"Pomodoro Lock - {state.title()}: {minutes:02d}:{seconds:02d}"
        self.indicator.set_title(tooltip)
        
        # Update icon based on state
        if state == "work":
            self.indicator.set_icon("pomodoro-lock")
        elif state == "break":
            self.indicator.set_icon("pomodoro-lock-break")
        else:
            self.indicator.set_icon("pomodoro-lock-paused")

class ScreenManager:
    """Linux screen manager using Xlib"""
    
    def __init__(self):
        self.display = None
        if XLIB_AVAILABLE:
            try:
                self.display = display.Display()
            except Exception as e:
                logging.error(f"Failed to connect to X display: {e}")
    
    def get_screen_info(self):
        """Get information about connected screens"""
        if not self.display:
            return []
        
        try:
            screens = []
            for i in range(self.display.screen_count()):
                screen = self.display.screen(i)
                screens.append({
                    'width': screen.width_in_pixels,
                    'height': screen.height_in_pixels,
                    'x': 0,  # X11 doesn't provide screen position easily
                    'y': 0
                })
            return screens
        except Exception as e:
            logging.error(f"Failed to get screen info: {e}")
            return []
    
    def create_fullscreen_window(self, screen_index=0):
        """Create a fullscreen window on the specified screen"""
        if not GTK_AVAILABLE:
            return None
        
        try:
            window = Gtk.Window()
            window.set_decorated(False)
            window.fullscreen()
            
            # Move to specific screen if multiple monitors
            if self.display and self.display.screen_count() > 1:
                screen = self.display.screen(screen_index)
                window.move(0, 0)  # X11 handles multi-monitor positioning
            
            return window
        except Exception as e:
            logging.error(f"Failed to create fullscreen window: {e}")
            return None

class AutostartManager:
    """Linux autostart manager using systemd user services"""
    
    def __init__(self):
        self.service_name = "pomodoro-lock.service"
        self.service_path = Path.home() / ".config" / "systemd" / "user" / self.service_name
    
    def enable_autostart(self):
        """Enable autostart via systemd user service"""
        try:
            # Create systemd user directory
            service_dir = self.service_path.parent
            service_dir.mkdir(parents=True, exist_ok=True)
            
            # Create service file if it doesn't exist
            if not self.service_path.exists():
                service_content = f"""[Unit]
Description=Pomodoro Lock
After=graphical-session.target

[Service]
Type=simple
ExecStart={os.path.expanduser('~/.local/bin/pomodoro-lock')} ui
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical-session.target
"""
                self.service_path.write_text(service_content)
            
            # Enable the service
            subprocess.run([
                "systemctl", "--user", "daemon-reload"
            ], check=True)
            subprocess.run([
                "systemctl", "--user", "enable", self.service_name
            ], check=True)
            
            return True
        except Exception as e:
            logging.error(f"Failed to enable autostart: {e}")
            return False
    
    def disable_autostart(self):
        """Disable autostart"""
        try:
            subprocess.run([
                "systemctl", "--user", "disable", self.service_name
            ], check=True)
            return True
        except Exception as e:
            logging.error(f"Failed to disable autostart: {e}")
            return False
    
    def is_autostart_enabled(self):
        """Check if autostart is enabled"""
        try:
            result = subprocess.run([
                "systemctl", "--user", "is-enabled", self.service_name
            ], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

class FileLockManager:
    """Linux file lock manager using fcntl"""
    
    def __init__(self, lock_file_path):
        self.lock_file_path = Path(lock_file_path)
        self.lock_file = None
        self.lock_acquired = False
    
    def acquire_lock(self):
        """Acquire a file lock"""
        try:
            # Create lock file directory if it doesn't exist
            self.lock_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Open lock file
            self.lock_file = open(self.lock_file_path, 'w')
            
            # Try to acquire exclusive lock
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock_acquired = True
            
            # Write PID to lock file
            self.lock_file.write(str(os.getpid()))
            self.lock_file.flush()
            
            return True
        except (IOError, OSError) as e:
            if self.lock_file:
                self.lock_file.close()
                self.lock_file = None
            logging.error(f"Failed to acquire lock: {e}")
            return False
    
    def release_lock(self):
        """Release the file lock"""
        if self.lock_file and self.lock_acquired:
            try:
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                self.lock_file.close()
                self.lock_acquired = False
                
                # Remove lock file
                if self.lock_file_path.exists():
                    self.lock_file_path.unlink()
            except Exception as e:
                logging.error(f"Failed to release lock: {e}")
    
    def is_locked(self):
        """Check if another instance is running"""
        try:
            if not self.lock_file_path.exists():
                return False
            
            with open(self.lock_file_path, 'r') as f:
                pid_str = f.read().strip()
                if not pid_str:
                    return False
                
                pid = int(pid_str)
                
                # Check if process is still running
                try:
                    os.kill(pid, 0)  # Signal 0 just checks if process exists
                    return True
                except OSError:
                    # Process doesn't exist, clean up stale lock file
                    self.lock_file_path.unlink()
                    return False
        except Exception:
            return False 