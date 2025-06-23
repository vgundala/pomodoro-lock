#!/usr/bin/env python3
"""
Test script for user activity detection functionality
Tests keyboard, mouse, and audio activity monitoring
"""

import os
import time
import json
import subprocess
import logging
import threading
import psutil
import gi
gi.require_version('Notify', '0.7')
gi.require_version('Gtk', '3.0')
from gi.repository import Notify, Gtk, GLib, Gdk
import Xlib
from Xlib import X, display

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class UserActivityMonitor:
    def __init__(self, inactivity_threshold_minutes=10):
        self.inactivity_threshold = inactivity_threshold_minutes * 60
        self.last_activity = time.time()
        self.is_active = True
        self.monitoring = False
        self.display = None
        self.last_pointer_pos = None
        
    def start_monitoring(self):
        """Start monitoring user activity"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.last_activity = time.time()
        
        # Start activity monitoring in a separate thread
        self.monitor_thread = threading.Thread(target=self._monitor_activity, daemon=True)
        self.monitor_thread.start()
        
        logging.info("User activity monitoring started")
        
    def stop_monitoring(self):
        """Stop monitoring user activity"""
        self.monitoring = False
        logging.info("User activity monitoring stopped")
        
    def _monitor_activity(self):
        """Monitor user activity using multiple methods"""
        try:
            self.display = display.Display()
            root = self.display.screen().root
        except Exception as e:
            logging.error(f"Failed to connect to X display: {e}")
            return
            
        while self.monitoring:
            try:
                # Method 1: Check mouse pointer position
                try:
                    pointer = root.query_pointer()
                    if pointer:
                        current_pos = (pointer.root_x, pointer.root_y)
                        if self.last_pointer_pos != current_pos:
                            self.last_pointer_pos = current_pos
                            self.last_activity = time.time()
                            if not self.is_active:
                                self.is_active = True
                                logging.info("Activity detected: mouse movement")
                except Exception as e:
                    pass
                
                # Method 2: Check for active windows (indicates user interaction)
                try:
                    active_window = self.display.get_input_focus()
                    if active_window:
                        self.last_activity = time.time()
                        if not self.is_active:
                            self.is_active = True
                            logging.info("Activity detected: active window")
                except Exception as e:
                    pass
                
                # Method 3: Check audio activity
                audio_active = self._check_audio_activity()
                if audio_active:
                    self.last_activity = time.time()
                    if not self.is_active:
                        self.is_active = True
                        logging.info("Activity detected: audio playing")
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                logging.error(f"Activity monitoring error: {e}")
                time.sleep(2)
                
    def _check_audio_activity(self):
        """Check if there's active audio playback"""
        try:
            # Method 1: Check for common audio processes
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
                        # For some processes, check if they're actually playing audio
                        if proc_info['name'] in ['pulseaudio', 'pipewire']:
                            # Check if there are active sinks/sources
                            try:
                                result = subprocess.run(['pactl', 'list', 'short', 'sinks'], 
                                                     capture_output=True, text=True, timeout=2)
                                if result.returncode == 0 and result.stdout.strip():
                                    return True
                            except:
                                pass
                        else:
                            return True
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Method 2: Check for active audio using pactl
            try:
                result = subprocess.run(['pactl', 'list', 'short', 'sink-inputs'], 
                                     capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and result.stdout.strip():
                    return True
            except:
                pass
                
            # Method 3: Check for active audio using amixer
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

class TestTimer:
    def __init__(self, duration_minutes=5, inactivity_threshold_minutes=2):
        self.duration = duration_minutes * 60
        self.remaining = self.duration
        self.inactivity_threshold = inactivity_threshold_minutes * 60
        self.is_paused = False
        self.pause_start_time = None
        self.total_pause_time = 0
        
        # Initialize activity monitor
        self.activity_monitor = UserActivityMonitor(inactivity_threshold_minutes)
        
    def start(self):
        """Start the timer with activity monitoring"""
        print(f"Starting timer for {self.duration/60} minutes")
        print(f"Inactivity threshold: {self.inactivity_threshold/60} minutes")
        print("Move mouse, type, or play audio to keep timer active")
        print("-" * 50)
        
        self.activity_monitor.start_monitoring()
        self.start_time = time.time()
        
        while self.remaining > 0:
            # Check user activity
            if not self.activity_monitor.check_inactivity():
                if not self.is_paused:
                    self.is_paused = True
                    self.pause_start_time = time.time()
                    print(f"⏸️  Timer PAUSED - User inactive for {self.activity_monitor.get_inactive_time()/60:.1f} minutes")
            else:
                if self.is_paused:
                    self.is_paused = False
                    if self.pause_start_time:
                        pause_duration = time.time() - self.pause_start_time
                        self.total_pause_time += pause_duration
                        self.pause_start_time = None
                        print(f"▶️  Timer RESUMED - Activity detected")
                
                # Only count down if not paused
                if not self.is_paused:
                    self.remaining -= 1
                    
            # Display status
            minutes, seconds = divmod(self.remaining, 60)
            status = "PAUSED" if self.is_paused else "RUNNING"
            print(f"\r⏱️  {minutes:02d}:{seconds:02d} - {status}", end="", flush=True)
            
            time.sleep(1)
            
        print(f"\n✅ Timer completed!")
        print(f"Total pause time: {self.total_pause_time/60:.1f} minutes")
        self.activity_monitor.stop_monitoring()

def test_activity_detection():
    """Test basic activity detection"""
    print("Testing activity detection...")
    
    monitor = UserActivityMonitor(inactivity_threshold_minutes=1)
    monitor.start_monitoring()
    
    print("Activity monitor started. Testing for 30 seconds...")
    print("Move mouse, type, or play audio to test detection")
    
    start_time = time.time()
    while time.time() - start_time < 30:
        if monitor.check_inactivity():
            print(f"\r✅ Active - Last activity: {monitor.get_inactive_time():.1f}s ago", end="", flush=True)
        else:
            print(f"\r⏸️  Inactive - No activity for: {monitor.get_inactive_time():.1f}s", end="", flush=True)
        time.sleep(1)
    
    print("\nActivity detection test completed")
    monitor.stop_monitoring()

def test_timer_with_activity():
    """Test timer with activity monitoring"""
    print("\nTesting timer with activity monitoring...")
    print("This will run for 2 minutes with 30-second inactivity threshold")
    print("Timer will pause when inactive and resume when activity is detected")
    
    timer = TestTimer(duration_minutes=2, inactivity_threshold_minutes=0.5)
    timer.start()

def test_audio_detection():
    """Test audio activity detection"""
    print("\nTesting audio activity detection...")
    
    monitor = UserActivityMonitor(inactivity_threshold_minutes=1)
    monitor.start_monitoring()
    
    print("Audio detection test - check if audio processes are detected")
    print("Start playing some audio (music, video, etc.) to test")
    print("Testing for 20 seconds...")
    
    start_time = time.time()
    while time.time() - start_time < 20:
        audio_active = monitor._check_audio_activity()
        status = "🎵 Audio detected" if audio_active else "🔇 No audio"
        print(f"\r{status} - Time: {time.time() - start_time:.0f}s", end="", flush=True)
        time.sleep(2)
    
    print("\nAudio detection test completed")
    monitor.stop_monitoring()

def test_keyboard_mouse_detection():
    """Test keyboard and mouse detection specifically"""
    print("\nTesting keyboard and mouse detection...")
    
    monitor = UserActivityMonitor(inactivity_threshold_minutes=1)
    monitor.start_monitoring()
    
    print("Move your mouse or type to test detection")
    print("Testing for 15 seconds...")
    
    start_time = time.time()
    while time.time() - start_time < 15:
        inactive_time = monitor.get_inactive_time()
        if inactive_time < 2:
            print(f"\r🖱️  Activity detected - Last activity: {inactive_time:.1f}s ago", end="", flush=True)
        else:
            print(f"\r⏸️  No recent activity - Inactive for: {inactive_time:.1f}s", end="", flush=True)
        time.sleep(1)
    
    print("\nKeyboard/mouse detection test completed")
    monitor.stop_monitoring()

def main():
    print("User Activity Detection Test Suite")
    print("=" * 50)
    
    # Test 1: Basic activity detection
    test_activity_detection()
    
    # Test 2: Audio detection
    test_audio_detection()
    
    # Test 3: Keyboard/mouse detection
    test_keyboard_mouse_detection()
    
    # Test 4: Timer with activity monitoring
    test_timer_with_activity()
    
    print("\n" + "=" * 50)
    print("All tests completed!")

if __name__ == "__main__":
    main() 