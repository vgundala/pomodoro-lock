#!/usr/bin/env python3
"""
Debug script to test activity detection in real-time
"""

import os
import time
import json
import logging
import threading
import psutil
import subprocess
import evdev
import select
from evdev import InputDevice, categorize, ecodes, list_devices

# Setup logging
# Get the root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Clear existing handlers (to avoid duplicate output if run multiple times)
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Add a StreamHandler to output to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Add a FileHandler for persistent logs (optional, but good for long tests)
# file_handler = logging.FileHandler(os.path.expanduser('~/.local/share/pomodoro-lock/evdev_debug.log'))
# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

class DebugActivityMonitor:
    def __init__(self, inactivity_threshold_minutes=1):
        self.inactivity_threshold = inactivity_threshold_minutes * 60
        self.last_activity = time.time()
        self.is_active = True
        self.monitoring = False
        self.devices = []
        self.polling_interval = 0.1  # Define polling_interval
        
    def start_monitoring(self):
        """Start monitoring user activity"""
        if self.monitoring:
            return
            
        logger.info("Debug activity monitoring started")
        self.monitoring = True
        self.last_activity = time.time()
        
        # Find and open input devices
        self._find_input_devices()

        if not self.devices:
            logger.error("No input devices found or accessible by evdev. Please check permissions.")
            logger.info("Try running with `sudo` or add your user to the 'input' group: `sudo usermod -a -G input $USER` (then log out and back in).")
            self.stop_monitoring()
            return

        # Start activity monitoring in a separate thread
        self.monitor_thread = threading.Thread(target=self._monitor_activity, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring user activity"""
        logger.info("Debug activity monitoring stopped")
        self.monitoring = False
        # Close evdev devices
        for dev in self.devices:
            try:
                dev.close()
            except Exception as e:
                logger.warning(f"Error closing device {dev.path}: {e}")
        self.devices.clear()

    def _find_input_devices(self):
        """Find all keyboard and mouse input devices using evdev"""
        self.devices = []
        devices_found = list_devices()
        for dev_path in devices_found:
            try:
                device = InputDevice(dev_path)
                # Check if it's a keyboard or mouse device
                if ecodes.EV_KEY in device.capabilities() and ecodes.KEY_SPACE in device.capabilities()[ecodes.EV_KEY]:
                    logger.info(f"Found keyboard device: {device.path} ({device.name})")
                    self.devices.append(device)
                elif ecodes.EV_REL in device.capabilities() and ecodes.REL_X in device.capabilities()[ecodes.EV_REL]:
                    logger.info(f"Found mouse device: {device.path} ({device.name})")
                    self.devices.append(device)
                else:
                    device.close() # Close devices that are not input devices
            except Exception as e:
                logger.debug(f"Could not open device {dev_path}: {e}")

    def _monitor_activity(self):
        """Monitor user activity using evdev input events and audio checks"""
        while self.monitoring:
            r, w, x = select.select(self.devices, [], [], self.polling_interval)
            if r: # Input events detected
                for dev in r:
                    try:
                        for event in dev.read():
                            # Log all evdev events for debugging
                            logger.debug(f"Evdev Event: device={dev.name}, type={categorize(event)._type}, code={categorize(event)._code}, value={event.value}")
                            
                            # Consider only key press/release and relative motion events as activity
                            if event.type == ecodes.EV_KEY and (event.value == 0 or event.value == 1): # Key press or release
                                self.last_activity = time.time()
                                if not self.is_active:
                                    self.is_active = True
                                    logger.debug(f"Activity detected: Keyboard event (device={dev.name})")
                            elif event.type == ecodes.EV_REL: # Relative movement (mouse)
                                # Add a small threshold for mouse movement to filter noise
                                if event.code == ecodes.REL_X or event.code == ecodes.REL_Y:
                                    if abs(event.value) > 0: # Any movement (was 10 pixels, let's try 0 for debug)
                                        self.last_activity = time.time()
                                        if not self.is_active:
                                            self.is_active = True
                                            logger.debug(f"Activity detected: Mouse movement (device={dev.name}, axis={event.code}, value={event.value})")
                    except OSError as e:
                        # Handle device disconnect or permission issues
                        logger.warning(f"Error reading from device {dev.path}: {e}. Removing device.")
                        self.devices.remove(dev)
                    except Exception as e:
                        logger.error(f"Unexpected error processing evdev event: {e}")

            # Check audio activity as a complementary method
            audio_active = self._check_audio_activity()
            if audio_active:
                self.last_activity = time.time()
                if not self.is_active:
                    self.is_active = True
                    logger.debug("Activity detected: audio playing")

            time.sleep(1) # Small delay to avoid busy-waiting, evdev select will handle actual blocking

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
            logger.error(f"Error checking audio activity: {e}")
            return False

    def check_inactivity(self):
        """Check if user has been inactive for the threshold period"""
        current_time = time.time()
        inactive_time = current_time - self.last_activity

        if inactive_time >= self.inactivity_threshold:
            if self.is_active:
                self.is_active = False
                logger.info(f"User inactive for {inactive_time/60:.1f} minutes - pausing timer")
            return False
        else:
            if not self.is_active:
                self.is_active = True
                logger.info(f"User activity resumed after {inactive_time/60:.1f} minutes")
            return True

    def get_inactive_time(self):
        """Get the time since last activity in seconds"""
        return time.time() - self.last_activity

def test_debug_monitor():
    """Test the debug activity monitor"""
    print("Debug Activity Monitor Test")
    print("=" * 50)
    
    monitor = DebugActivityMonitor(inactivity_threshold_minutes=1)
    monitor.start_monitoring()
    
    print("Debug monitor started. Testing for 2 minutes...")
    print("Move mouse, type, or play audio to test detection")
    print("Timer should pause after 1 minute of inactivity")
    print("-" * 50)
    
    start_time = time.time()
    while time.time() - start_time < 120:  # 2 minutes
        inactive_time = monitor.get_inactive_time()
        if monitor.check_inactivity():
            print(f"\r✅ ACTIVE - Last activity: {inactive_time:.1f}s ago", end="", flush=True)
        else:
            print(f"\r⏸️  INACTIVE - No activity for: {inactive_time:.1f}s", end="", flush=True)
        time.sleep(1)
    
    print("\nDebug monitor test completed")
    monitor.stop_monitoring()

if __name__ == "__main__":
    test_debug_monitor() 