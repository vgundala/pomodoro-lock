# Pomodoro Lock - Standalone UI Timer with Screen Overlay

A comprehensive Pomodoro timer application that helps you maintain focus during work sessions and enforces breaks with full-screen overlays across all connected displays.

**Copyright © 2024 Vinay Gundala (vg@ivdata.dev)**

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/vgundala/pomodoro-lock.git
cd pomodoro-lock

# Check dependencies first (recommended)
make check-deps

# Install with autostart enabled
make install

# Or install and start immediately
make install-and-start
```

### Using the Application

#### Starting the Application
```bash
# Start the UI (launches from Applications menu or command line)
pomodoro-lock

# Or start the UI directly
pomodoro-lock ui
```

#### UI Controls
- **Timer Window**: Draggable countdown timer with "Pomodoro Lock" title
- **Close Button (✕)**: Minimizes the timer to system tray
- **Power Button (⏻)**: Quits the application
- **System Tray**: Right-click for menu options (Show Timer, Quit)

#### Desktop Environment Compatibility
- **GNOME/KDE**: Full system tray support with AppIndicator3
- **XFCE**: Limited system tray support - uses persistent notifications or status window as fallback
- **Other**: Fallback to status window in top-right corner

#### Multiple Instances
- Only one UI instance can run at a time
- If you try to start another instance, you'll see a message: "Pomodoro Lock is already running"
- Check the system tray for the existing instance

### Configuration
```bash
# Interactive configuration
make configure

# Quick presets
make configure-standard  # 25/5
make configure-long      # 45/15
make configure-short     # 15/3
```

### Service Management

```bash
# Start the UI
make start

# Stop the UI
make stop

# Check status
make status

# View logs
make logs

# Restart the UI
make restart
```

## Project Structure

```
pomodoro-lock/
├── src/                          # Source code
│   └── pomodoro-ui.py            # Standalone UI application
├── scripts/                      # Installation and utility scripts
│   ├── install.sh                # Command line installer
│   ├── configure-pomodoro.py     # Configuration management
│   └── start-pomodoro.sh         # Robust startup script with environment handling
├── config/                       # Configuration files
│   ├── config.json               # Default configuration
│   └── pomodoro-lock.service     # Systemd service for autostart
├── tests/                        # Test scripts
│   ├── test-notification.py      # Notification tests
│   ├── test-overlay.py           # Overlay tests
│   ├── test-timer.py             # Timer tests
│   ├── test-multi-overlay.py     # Multi-display tests
│   ├── test-pomodoro-short.py    # Complete workflow tests
│   └── test-system-tray.py       # System tray tests
├── docs/                         # Documentation
│   └── README.md                 # Detailed documentation
├── debian/                       # Debian packaging files
├── README.md                     # This file (quick start)
├── Makefile                      # Build and development commands
├── CONTRIBUTING.md               # Contribution guidelines
└── LICENSE                       # MIT License
```

## Features

- ✅ **Standalone UI**: Complete timer application with integrated overlays
- ✅ **Multi-Display Support**: Full-screen overlays on all connected monitors
- ✅ **Visual Timer**: Draggable countdown timer with "Pomodoro Lock" title
- ✅ **System Tray Integration**: Minimize to system tray with status display
- ✅ **Smart UI Controls**: Close button (✕) to minimize, Power button (⏻) to quit
- ✅ **Single Instance Protection**: Prevents multiple UI instances with graceful messaging
- ✅ **Notifications**: Desktop notifications before break periods
- ✅ **Configuration**: JSON-based configuration with easy management
- ✅ **Systemd Autostart**: Runs automatically on login via systemd user service
- ✅ **Cross-Desktop**: Works with GNOME, KDE, XFCE, and other desktop environments
- ✅ **Debian Packaging**: Ready for Debian/Ubuntu distribution

## How It Works

1. **Work Period**: Shows countdown timer, sends notification before break
2. **Break Period**: Creates full-screen overlays on all displays with countdown
3. **Cycle**: Work → Break → Work → Break → (repeats indefinitely)

## Architecture
### Architecture Diagram
┌─────────────────────────────────────────────────────────────┐
│                    Standalone UI                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Timer Window  │  │  System Tray    │  │   Overlays  │ │
│  │  (Draggable)    │  │  (AppIndicator) │  │ (Multi-Display) │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Single Process (pomodoro-ui.py)            │ │
│  │  • Timer Logic • Notifications • File Locking • Cleanup │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Systemd Service │
                    │  (Autostart)     │
                    └─────────────────┘ 

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

## Future Enhancements

- Re-implement robust user inactivity detection (e.g., using evdev for keyboard/mouse input or other screen activity monitoring methods).
- Add AppStream metadata support for better Linux desktop integration and app store distribution.

## Documentation

For detailed documentation, installation instructions, configuration options, and troubleshooting, see:
- [Detailed Documentation](docs/README.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

## Testing

Run individual component tests:
```bash
# Test notifications
python3 tests/test-notification.py

# Test overlay functionality
python3 tests/test-overlay.py

# Test timer widget
python3 tests/test-timer.py

# Test multi-display overlay
python3 tests/test-multi-overlay.py

# Test complete workflow
python3 tests/test-pomodoro-short.py
```