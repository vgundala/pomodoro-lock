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
        logging.FileHandler(os.path.expanduser('~/.local/share/pomodoro-lock/pomodoro.log')),
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
        screen = Gdk.Screen.get_default()
        monitor = screen.get_primary_monitor() if hasattr(screen, 'get_primary_monitor') else 0
        geometry = screen.get_monitor_geometry(monitor)
        x = geometry.x
        y = geometry.y + geometry.height - 100  # 100 is window height
        self.move(x, y)
        self.box = Gtk.Box()
        self.box.set_margin_start(20)
        self.box.set_margin_end(20)
        self.box.set_margin_top(20)
        self.box.set_margin_bottom(20)
        self.add(self.box)
        self.label = Gtk.Label()
        self.label.set_markup("<span size='x-large' weight='bold' foreground='white'>00:00</span>")
        self.box.pack_start(self.label, True, True, 0)
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.2, 0.2, 0.2, 0.8))
        self.show_all()
    def update_timer(self, seconds, mode='work'):
        minutes, secs = divmod(seconds, 60)
        color = 'white' if mode == 'work' else 'orange'
        self.label.set_markup(f"<span size='x-large' weight='bold' foreground='{color}'>{minutes:02d}:{secs:02d}</span>")

class PomodoroLock:
    def __init__(self):
        self.config_path = os.path.expanduser('~/.local/share/pomodoro-lock/config/config.json')
        self.load_config()
        self.last_activity = time.time()
        self.work_time = self.config['work_time_minutes'] * 60
        self.break_time = self.config['break_time_minutes'] * 60
        self.notification_time = self.config['notification_time_minutes'] * 60
        self.inactivity_threshold = self.config['inactivity_threshold_minutes'] * 60
        self.state = 'work'  # or 'break'
        self.remaining = self.work_time
        self.notification_sent = False
        Notify.init("Pomodoro Lock")
        self.timer = CountdownTimer()
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
        # Check keyboard and mouse activity
        d = display.Display()
        root = d.screen().root
        current_time = time.time()
        # Check if any sound is playing
        sound_active = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] in ['pulseaudio', 'pipewire']:
                    sound_active = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        # If there's been no activity for the threshold time, reset work time
        if (current_time - self.last_activity) > self.inactivity_threshold:
            elapsed_time = (current_time - self.last_activity) / 60
            logging.info("Inactivity detected for more than %d minutes. Elapsed time: %.2f minutes. Resetting work timer.", self.config['inactivity_threshold_minutes'], elapsed_time)
            self.remaining = self.work_time
            self.notification_sent = False
            self.state = 'work'
            self.timer.update_timer(self.remaining, mode='work')
            return False
        return True

    def send_notification(self, message):
        notification = Notify.Notification.new(
            "Pomodoro Lock",
            message,
            "dialog-information"
        )
        notification.show()

    def lock_screen(self):
        logging.info("Locking screen for break")
        subprocess.run(['loginctl', 'lock-session'])

    def unlock_screen(self):
        logging.info("Unlocking screen after break")
        subprocess.run(['loginctl', 'unlock-session'])

    def tick(self):
        if self.state == 'work':
            if self.check_user_activity():
                self.remaining -= 1
                self.timer.update_timer(self.remaining, mode='work')
                # Notify before break
                if self.remaining == self.notification_time and not self.notification_sent:
                    self.send_notification(
                        f"Break coming in {self.config['notification_time_minutes']} minutes. "
                        f"You will be locked out for {self.config['break_time_minutes']} minutes."
                    )
                    self.notification_sent = True
                if self.remaining <= 0:
                    self.lock_screen()
                    self.state = 'break'
                    self.remaining = self.break_time
                    self.timer.update_timer(self.remaining, mode='break')
            else:
                self.remaining = self.work_time
                self.notification_sent = False
                self.timer.update_timer(self.remaining, mode='work')
        elif self.state == 'break':
            self.remaining -= 1
            self.timer.update_timer(self.remaining, mode='break')
            if self.remaining <= 0:
                self.unlock_screen()
                self.state = 'work'
                self.remaining = self.work_time
                self.notification_sent = False
                self.timer.update_timer(self.remaining, mode='work')
        return True  # Continue the timeout

def main():
    pomodoro = PomodoroLock()
    def signal_handler(signum, frame):
        logging.info("Received shutdown signal")
        Gtk.main_quit()
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    Gtk.main()

if __name__ == "__main__":
    main() 