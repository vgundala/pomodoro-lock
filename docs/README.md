# Pomodoro Lock - Detailed Documentation

**Copyright © 2024 Vinay Gundala (vg@ivdata.dev)**

A comprehensive Pomodoro timer application that helps you maintain focus during work sessions and enforces breaks with full-screen overlays across all connected displays.

## Table of Contents

1. [Features](#features)
2. [How It Works](#how-it-works)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Service Management](#service-management)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [File Structure](#file-structure)
9. [Technical Details](#technical-details)
10. [Support](#support)

## Features

### ✅ Core Functionality
- **Work-Break Cycle**: Configurable work sessions followed by break periods
- **Multi-Display Support**: Full-screen overlays on all connected monitors
- **Visual Timer**: Draggable countdown timer with "Pomodoro Lock" title
- **Notifications**: Desktop notifications before break periods
- **Configuration**: JSON-based configuration for customizing timers

### ✅ Technical Features
- **Standalone UI**: Complete timer application with integrated overlays
- **Screen Overlay**: Full-screen black overlays with countdown timers
- **Systemd Autostart**: Runs automatically on login via systemd user service
- **Cross-Desktop**: Works with GNOME, KDE, XFCE, and other desktop environments
- **Single Instance Protection**: Prevents multiple UI instances with file locking
- **Logging**: Comprehensive logging for debugging and monitoring
- **Security**: Proper user permissions and security settings
- **Packaging**: Supports both pip and Debian packaging

## How It Works

### Work Period (configurable, default: 30 minutes)
1. Shows a small, draggable timer with "Pomodoro Lock" title
2. Counts down from work time (configurable)
3. Sends notification 2 minutes before break
4. Can be minimized to system tray

### Break Period (configurable, default: 5 minutes)
1. Creates full-screen overlays on ALL connected displays
2. Shows countdown timer on each overlay
3. Prevents user interaction with other applications
4. Automatically ends after break time
5. Returns to work mode

### Cycle
- Work → Break → Work → Break → (repeats indefinitely)

## Architecture

### Standalone UI Design
- **Single Process**: UI handles all functionality (timer, overlays, notifications)
- **Systemd Service**: Manages autostart and process lifecycle
- **File Locking**: Prevents multiple instances using exclusive file locks
- **Clean Exit**: Proper cleanup on quit (overlays, lock files, etc.)

### Service Lifecycle
- **Installation**: `make install` copies files and enables autostart
- **Autostart**: Service starts automatically on login
- **Manual Control**: Start/stop via systemctl or make commands
- **Quit Handling**: UI quits cleanly, service restarts on next login

## Installation

### Prerequisites
- Ubuntu/Debian-based system
- Python 3.6+
- GTK3 desktop environment
- User account (not root)

### Quick Installation

```bash
# Clone or download the repository
git clone https://github.com/vgundala/pomodoro-lock.git
cd pomodoro-lock

# Check dependencies first (recommended)
make check-deps

# Install with autostart enabled
make install

# Or install and start immediately
make install-and-start
```

### Manual Installation

1. **Install Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-gi python3-psutil python3-xlib python3-notify2
   ```

2. **Create Directories**
   ```bash
   mkdir -p ~/.local/share/pomodoro-lock/{bin,config,scripts}
   ```

3. **Copy Files**
   ```bash
   cp src/pomodoro-ui.py ~/.local/share/pomodoro-lock/bin/
   cp scripts/start-pomodoro.sh ~/.local/share/pomodoro-lock/
   chmod +x ~/.local/share/pomodoro-lock/bin/pomodoro-ui.py
   chmod +x ~/.local/share/pomodoro-lock/start-pomodoro.sh
   ```

4. **Install Systemd Service**
   ```bash
   cp config/pomodoro-lock.service ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable pomodoro-lock.service
   ```

## Configuration

### Configuration File
Location: `~/.local/share/pomodoro-lock/config/config.json`

```json
{
    "work_time_minutes": 30,
    "break_time_minutes": 5,
    "notification_time_minutes": 2,
    "inactivity_threshold_minutes": 10
}
```

### Settings Explained
- **work_time_minutes**: Duration of work sessions (default: 30)
- **break_time_minutes**: Duration of break sessions (default: 5)
- **notification_time_minutes**: Minutes before break to send notification (default: 2)
- **inactivity_threshold_minutes**: Minutes of inactivity before resetting timer (default: 10)

### Configuration Management

#### Using Make Commands (Recommended)
```bash
# Interactive configuration
make configure

# Quick presets
make configure-standard  # Apply standard preset (25/5)
make configure-long      # Apply long session preset (45/15)
make configure-short     # Apply short session preset (15/3)

# Show current configuration
make configure-show
```

#### Interactive Configuration
```bash
# Run interactive configuration
python3 ~/.local/share/pomodoro-lock/configure-pomodoro.py

# Or from the project directory
python3 scripts/configure-pomodoro.py
```

#### Quick Presets
```bash
# Apply standard Pomodoro preset (25/5)
python3 scripts/configure-pomodoro.py standard

# Apply long session preset (45/15)
python3 scripts/configure-pomodoro.py long

# Apply short session preset (15/3)
python3 scripts/configure-pomodoro.py short

# Apply custom preset (30/5)
python3 scripts/configure-pomodoro.py custom
```

#### View Current Configuration
```bash
# Show current settings
python3 scripts/configure-pomodoro.py show
```

#### Manual Configuration
You can also edit the configuration file directly:
```bash
nano ~/.local/share/pomodoro-lock/config/config.json
```

**Note**: After changing the configuration, restart the UI:
```bash
make restart
```

## Service Management

### Using Make Commands (Recommended)
```bash
# Start/Stop/Restart
make start
make stop
make restart

# Check status and logs
make status
make logs
```

### Using Systemctl Commands (Alternative)
```bash
# Start the service
systemctl --user start pomodoro-lock.service

# Stop the service
systemctl --user stop pomodoro-lock.service

# Restart the service
systemctl --user restart pomodoro-lock.service
```

### Check Status
```bash
# Using make (recommended)
make status

# Using systemctl
systemctl --user status pomodoro-lock.service

# View real-time logs
make logs

# Or using journalctl
journalctl --user -u pomodoro-lock.service -f

# View recent logs
journalctl --user -u pomodoro-lock.service -n 50
```

### Enable/Disable Auto-Start
```bash
# Enable auto-start on login
systemctl --user enable pomodoro-lock.service

# Disable auto-start
systemctl --user disable pomodoro-lock.service
```

### Installation Behavior

#### New Installation Process (make install)
The `make install` command now automatically:
1. Installs all necessary files
2. Enables the systemd service for auto-start on login
3. **Starts the service immediately** (new behavior)

This means the Pomodoro Lock will be running right after installation without requiring manual intervention.

#### Manual Service Control
If you prefer to start the service manually after installation:
```bash
# Install without auto-start
make install-and-start

# Or install and then manually control
make install
make start    # Start when ready
make stop     # Stop when needed
```

## Testing

### Using Make Commands (Recommended)
```bash
# Run all tests
make test

# Run individual tests
make test-notification
make test-overlay
make test-timer
make test-multi
make test-workflow
```

### Individual Component Tests
The repository includes test scripts for each component:

```bash
# Test notifications
python3 tests/test-notification.py

# Test screen lock/unlock (legacy)
python3 tests/test-screen-lock.py

# Test overlay functionality
python3 tests/test-overlay.py

# Test timer widget
python3 tests/test-timer.py

# Test multi-display overlay
python3 tests/test-multi-overlay.py

# Test complete workflow (short timers)
python3 tests/test-pomodoro-short.py
```

### Manual Testing
```bash
# Test the startup script directly
~/.local/share/pomodoro-lock/start-pomodoro.sh

# Test the main script directly
python3 ~/.local/share/pomodoro-lock/bin/pomodoro-ui.py
```

## Troubleshooting

### Common Issues

#### Service Won't Start
1. Check service status: `make status` or `systemctl --user status pomodoro-lock.service`
2. View logs: `make logs` or `journalctl --user -u pomodoro-lock.service -f`
3. Ensure display is ready: `xset q`
4. Check file permissions: `ls -la ~/.local/share/pomodoro-lock/`
5. Try restarting: `make restart`

#### Service Exits Immediately
1. Check if the service is configured correctly: `make status`
2. View recent logs: `journalctl --user -u pomodoro-lock.service -n 20`
3. Verify environment variables are set correctly
4. Check if the start script has proper permissions: `ls -la ~/.local/share/pomodoro-lock/start-pomodoro.sh`

#### Overlay Not Appearing
1. Check if multiple displays are detected
2. Verify GTK environment variables
3. Check if any other full-screen applications are running
4. Try running the test overlay: `python3 tests/test-multi-overlay.py`

#### Timer Not Visible
1. Check if the timer window is behind other windows
2. Look in the bottom-left corner of your primary display
3. Try dragging the timer to a different position
4. Check if the service is running: `make status`

### Log Files
- **Service Logs**: `journalctl --user -u pomodoro-lock.service`
- **Application Logs**: `~/.local/share/pomodoro-lock/pomodoro.log`

### Debug Mode
To run with verbose logging:
```bash
# Stop the service
systemctl --user stop pomodoro-lock.service

# Run manually with debug output
python3 ~/.local/share/pomodoro-lock/bin/pomodoro-ui.py
```

## File Structure

### Project Directory
```
pomodoro-lock/
├── src/                          # Source code
│   └── pomodoro-ui.py          # Main application
├── scripts/                      # Installation and utility scripts
│   ├── install.sh                # Command line installer
│   ├── install-desktop.sh        # Desktop installer
│   ├── start-pomodoro.sh         # Startup script
│   └── configure-pomodoro.py     # Configuration management
├── config/                       # Configuration files
│   ├── config.json               # Default configuration
│   ├── pomodoro-lock.service     # Systemd service file
│   └── pomodoro-lock-simple.service # Alternative service
├── tests/                        # Test scripts
│   ├── test-notification.py      # Notification tests
│   ├── test-overlay.py           # Overlay tests
│   ├── test-timer.py             # Timer tests
│   ├── test-multi-overlay.py     # Multi-display tests
│   ├── test-pomodoro-short.py    # Complete workflow tests
│   └── test-screen-lock.py       # Screen lock tests (legacy)
├── debian/                       # Debian packaging files
├── docs/                         # Documentation
│   └── README.md                 # This file
├── README.md                     # Quick start guide
├── Makefile                      # Build and development commands
├── setup.py                      # Python package configuration
├── requirements.txt              # Python dependencies
├── PACKAGING.md                  # Packaging guide
├── CONTRIBUTING.md               # Contribution guidelines
└── LICENSE                       # MIT License
```

### Installed Files
```
~/.local/share/pomodoro-lock/
├── bin/
│   └── pomodoro-ui.py          # Installed application
├── config/
│   └── config.json               # Configuration file
├── scripts/                      # Additional scripts
├── start-pomodoro.sh             # Startup script
├── configure-pomodoro.py         # Configuration management script
└── pomodoro.log                  # Application logs

~/.config/systemd/user/
└── pomodoro-lock.service         # Systemd service file
```

## Technical Details

### Dependencies
- **python3-gi**: GTK3 bindings for Python
- **python3-psutil**: Process and system utilities
- **python3-xlib**: X11 library bindings
- **python3-notify2**: Desktop notifications

### Architecture
- **Standalone UI**: Complete timer application with integrated overlays
- **Screen Overlay**: Full-screen black overlays with countdown timers
- **Systemd Autostart**: Runs automatically on login via systemd user service
- **Cross-Desktop**: Works with GNOME, KDE, XFCE, and other desktop environments
- **Single Instance Protection**: Prevents multiple UI instances with file locking
- **Logging**: Comprehensive logging for debugging and monitoring
- **Security**: Proper user permissions and security settings

### Security
- Runs as user service (not system service)
- No root privileges required
- Proper file permissions
- Isolated from system processes

## Support

### Getting Help
If you encounter issues or have questions:

1. **Check Documentation**: Review this file and the main README
2. **Run Tests**: Use the test scripts to verify functionality
3. **Check Logs**: Review service and application logs
4. **Search Issues**: Check existing GitHub issues
5. **Create Issue**: Report bugs or request features

### Contact Information
- **Author**: Vinay Gundala (vg@ivdata.dev)
- **GitHub**: [@vgundala](https://github.com/vgundala)
- **Project**: [pomodoro-lock](https://github.com/vgundala/pomodoro-lock)
- **Issues**: [GitHub Issues](https://github.com/vgundala/pomodoro-lock/issues)

### Contributing
Contributions are welcome! Please read [CONTRIBUTING.md](../CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Note**: This application uses screen overlays instead of system screen locks for better compatibility across different desktop environments and to ensure the timer remains visible during break periods. 