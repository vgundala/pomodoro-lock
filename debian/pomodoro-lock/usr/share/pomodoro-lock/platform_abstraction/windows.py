"""
Windows-specific platform implementations for Pomodoro Lock
"""

import os
import sys
import logging
import platform as platform_module
from pathlib import Path

# Check for Windows
if platform_module.system().lower() != "windows":
    raise ImportError("Windows platform module imported on non-Windows system")

# Optional dependencies
TKINTER_AVAILABLE = True
WIN32_AVAILABLE = False
TOAST_AVAILABLE = False
PYSTRAY_AVAILABLE = False

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    TKINTER_AVAILABLE = False
    logging.warning("Tkinter not available")

try:
    import win32api
    import win32con
    import win32gui
    import winreg
    WIN32_AVAILABLE = True
except ImportError:
    logging.warning("pywin32 not available - some features will be limited")

try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    logging.warning("win10toast not available - notifications will be disabled")

try:
    import pystray
    from PIL import Image
    PYSTRAY_AVAILABLE = True
except ImportError:
    logging.warning("pystray/PIL not available - system tray will be disabled")

class NotificationManager:
    """Windows notification manager using win10toast"""
    
    def __init__(self):
        self.toaster = None
        if TOAST_AVAILABLE:
            try:
                self.toaster = ToastNotifier()
            except Exception as e:
                logging.error(f"Failed to initialize toast notifier: {e}")
    
    def send_notification(self, title, message, urgency="normal"):
        """Send a Windows toast notification"""
        if not self.toaster:
            logging.warning("Notifications not available")
            return False
        
        try:
            # Convert urgency to Windows toast duration
            duration = 5 if urgency == "low" else 10 if urgency == "normal" else 15
            
            self.toaster.show_toast(
                title,
                message,
                duration=duration,
                threaded=True
            )
            return True
        except Exception as e:
            logging.error(f"Failed to send notification: {e}")
            return False

class SystemTrayManager:
    """Windows system tray manager using pystray"""
    
    def __init__(self, parent):
        self.parent = parent
        self.icon = None
        self.menu = None
        
        if not PYSTRAY_AVAILABLE:
            logging.warning("System tray not available (pystray missing)")
            return
        
        try:
            self._create_icon()
        except Exception as e:
            logging.error(f"Failed to create system tray: {e}")
    
    def _create_icon(self):
        """Create the system tray icon"""
        # Create a simple icon (you can replace this with a proper icon file)
        icon_image = self._create_default_icon()
        
        # Create menu
        self.menu = pystray.Menu(
            pystray.MenuItem("Show Timer", self._on_show_timer),
            pystray.MenuItem("Quit", self._on_quit)
        )
        
        # Create icon
        self.icon = pystray.Icon(
            "pomodoro-lock",
            icon_image,
            "Pomodoro Lock",
            self.menu
        )
        
        # Start the icon in a separate thread
        self.icon.run_detached()
    
    def _create_default_icon(self):
        """Create a default icon if no icon file is available"""
        try:
            # Try to load icon from file
            icon_path = Path(__file__).parent.parent.parent / "pomodoro-lock-24.png"
            if icon_path.exists():
                return Image.open(icon_path)
        except Exception:
            pass
        
        # Create a simple colored square as fallback
        img = Image.new('RGB', (64, 64), color='red')
        return img
    
    def _on_show_timer(self, icon, item):
        """Show timer window"""
        if self.parent:
            self.parent.show_timer()
    
    def _on_quit(self, icon, item):
        """Quit application"""
        if self.parent:
            self.parent.quit_application()
        if self.icon:
            self.icon.stop()
    
    def update_status(self, state, remaining):
        """Update system tray status"""
        if not self.icon:
            return
        
        # Update tooltip
        minutes = remaining // 60
        seconds = remaining % 60
        tooltip = f"Pomodoro Lock - {state.title()}: {minutes:02d}:{seconds:02d}"
        self.icon.title = tooltip
        
        # Update icon based on state (simplified - you can add different icons)
        if state == "work":
            # Use default icon
            pass
        elif state == "break":
            # Could change icon color or use different icon
            pass
        else:
            # Paused state
            pass
    
    def stop(self):
        """Stop the system tray icon"""
        if self.icon:
            self.icon.stop()

class ScreenManager:
    """Windows screen manager using win32gui"""
    
    def __init__(self):
        self.screens = []
        if WIN32_AVAILABLE:
            self._enumerate_screens()
    
    def _enumerate_screens(self):
        """Enumerate connected screens"""
        try:
            # Get primary monitor
            primary_monitor = win32api.GetSystemMetrics(win32con.SM_CXSCREEN), win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            self.screens.append({
                'width': primary_monitor[0],
                'height': primary_monitor[1],
                'x': 0,
                'y': 0
            })
            
            # Get virtual screen (all monitors combined)
            virtual_screen = (
                win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN),
                win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN),
                win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN),
                win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            )
            
            # If virtual screen is larger than primary, we have multiple monitors
            if virtual_screen[2] > primary_monitor[0] or virtual_screen[3] > primary_monitor[1]:
                # Add secondary monitor info (simplified)
                self.screens.append({
                    'width': virtual_screen[2] - primary_monitor[0],
                    'height': virtual_screen[3],
                    'x': primary_monitor[0],
                    'y': 0
                })
        except Exception as e:
            logging.error(f"Failed to enumerate screens: {e}")
    
    def get_screen_info(self):
        """Get information about connected screens"""
        return self.screens
    
    def create_fullscreen_window(self, screen_index=0):
        """Create a fullscreen window on the specified screen"""
        if not TKINTER_AVAILABLE:
            return None
        
        try:
            window = tk.Tk()
            window.title("Pomodoro Lock")
            window.attributes('-fullscreen', True)
            window.attributes('-topmost', True)
            
            # Move to specific screen if multiple monitors
            if screen_index < len(self.screens):
                screen = self.screens[screen_index]
                window.geometry(f"{screen['width']}x{screen['height']}+{screen['x']}+{screen['y']}")
            
            return window
        except Exception as e:
            logging.error(f"Failed to create fullscreen window: {e}")
            return None

class AutostartManager:
    """Windows autostart manager using registry"""
    
    def __init__(self):
        self.app_name = "Pomodoro Lock"
        self.registry_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def enable_autostart(self):
        """Enable autostart via Windows registry"""
        try:
            # Get the path to the executable
            exe_path = self._get_executable_path()
            if not exe_path:
                return False
            
            # Open registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_WRITE)
            
            # Set the value
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, f'"{exe_path}"')
            
            # Close the key
            winreg.CloseKey(key)
            
            return True
        except Exception as e:
            logging.error(f"Failed to enable autostart: {e}")
            return False
    
    def disable_autostart(self):
        """Disable autostart"""
        try:
            # Open registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_WRITE)
            
            # Delete the value
            winreg.DeleteValue(key, self.app_name)
            
            # Close the key
            winreg.CloseKey(key)
            
            return True
        except Exception as e:
            logging.error(f"Failed to disable autostart: {e}")
            return False
    
    def is_autostart_enabled(self):
        """Check if autostart is enabled"""
        try:
            # Open registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_READ)
            
            # Try to read the value
            try:
                winreg.QueryValueEx(key, self.app_name)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False
    
    def _get_executable_path(self):
        """Get the path to the executable"""
        # This should be updated to point to the actual executable
        # For now, return a placeholder
        return os.path.expanduser("~\\AppData\\Local\\Programs\\pomodoro-lock\\pomodoro-lock.exe")

class FileLockManager:
    """Windows file lock manager using file locking"""
    
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
            
            # Try to acquire exclusive lock (Windows file locking)
            import msvcrt
            msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
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
                import msvcrt
                msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)
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