# Pomodoro Lock

A Linux service that helps you maintain a healthy work-break balance by automatically locking your screen for breaks after a configurable work period.

## Features

- **Visible Countdown Timer**: Shows remaining work/break time in the bottom-left corner of your screen
- **Automatic Screen Lock**: Locks your screen when it's time for a break
- **Work-Break Cycle**: 
  - Work period: 30 minutes (configurable)
  - Break period: 5 minutes (configurable)
- **Inactivity Detection**: Resets work timer if no activity is detected for 10 minutes
- **Break Notifications**: Sends a notification 2 minutes before the break starts
- **Persistent Timer**: Timer window stays visible throughout work and break periods
- **User Service**: Runs automatically on login and restarts if it crashes

## Running as a Desktop App

If you prefer not to run Pomodoro Lock as a service, you can run it directly as a desktop application:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pomodoro-lock.git
   cd pomodoro-lock
   ```

2. Run the desktop installation script:
   ```bash
   ./install-desktop.sh
   ```

3. Run the application:
   - From your application launcher, search for "Pomodoro Lock"
   - Or run directly from terminal:
     ```bash
     python3 ~/.local/share/pomodoro-lock/bin/pomodoro-lock.py
     ```

**Note**: When running as a desktop app:
- The timer will only run while the application is open
- You'll need to start it manually each time
- It won't automatically restart if it crashes
- All other features (timer display, notifications, screen lock) work the same

## Configuration

The service is configured through a JSON file located at:
```
~/.local/share/pomodoro-lock/config/config.json
```

Default configuration:
```json
{
    "work_time_minutes": 30,
    "break_time_minutes": 5,
    "notification_time_minutes": 2,
    "inactivity_threshold_minutes": 10
}
```

## Service Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pomodoro-lock.git
   cd pomodoro-lock
   ```

2. Install the service:
   ```bash
   ./install.sh
   ```

3. Enable and start the service:
   ```bash
   systemctl --user enable pomodoro-lock.service
   systemctl --user start pomodoro-lock.service
   ```

## Usage

The service runs automatically in the background. You'll see:
- A countdown timer in the bottom-left corner
- Notifications before breaks
- Screen locks during breaks

### Managing the Service

Check status:
```bash
systemctl --user status pomodoro-lock.service
```

Restart the service:
```bash
systemctl --user restart pomodoro-lock.service
```

Stop the service:
```bash
systemctl --user stop pomodoro-lock.service
```

Start the service:
```bash
systemctl --user start pomodoro-lock.service
```

### Logs

View service logs:
```bash
journalctl --user -u pomodoro-lock.service
```

## How It Works

1. **Work Period**:
   - Timer counts down from configured work time
   - Monitors user activity
   - Sends notification before break
   - Locks screen when work time ends

2. **Break Period**:
   - Screen remains locked
   - Timer shows break countdown
   - Automatically unlocks when break ends

3. **Inactivity Handling**:
   - Monitors keyboard and mouse activity
   - Resets work timer if no activity detected
   - Logs inactivity events

## Requirements

- Linux system with systemd
- Python 3.x
- GTK 3
- Required Python packages:
  - gi (GTK bindings)
  - psutil
  - Xlib

## License

MIT License 