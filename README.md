# Pomodoro Lock - Multi-Display Timer with Screen Overlay

A comprehensive Pomodoro timer application that helps you maintain focus during work sessions and enforces breaks with full-screen overlays across all connected displays.

**Copyright © 2024 Vinay Gundala (vg@ivdata.dev)**

## Quick Start

### Installation Options

#### Option 1: User Service (Recommended for single user)
```bash
# Clone the repository
git clone https://github.com/vgundala/pomodoro-lock.git
cd pomodoro-lock

# Check dependencies first (recommended)
make check-deps

# Smart installer (auto-selects best method)
make install

# Or install using desktop installer (legacy/desktop integration)
make install-desktop

# Or install without auto-start
make install-and-start
```

#### Option 2: System Service (For multiple users)
```bash
# Clone the repository
git clone https://github.com/vgundala/pomodoro-lock.git
cd pomodoro-lock

# Install as system service (requires sudo)
make install-system
```

#### Option 3: Debian Package
```bash
# Clone the repository
git clone https://github.com/vgundala/pomodoro-lock.git
cd pomodoro-lock

# Build Debian package
make package-deb

# Install the package
sudo dpkg -i ../pomodoro-lock_*.deb
```

**Note:** Some installation methods may require admin access to install system dependencies. If you don't have sudo privileges, contact your system administrator or use `make check-deps` to see what's available on your system.

### Using the Application

#### Starting the Application
```bash
# Start the UI (launches from Applications menu or command line)
pomodoro-lock

# Or start the service directly
pomodoro-lock service
```

#### UI Controls
- **Timer Window**: Draggable countdown timer in bottom-left corner
- **Close Button (✕)**: Minimizes the timer to system tray
- **Power Button (⏻)**: Stops the service and closes the application
- **System Tray**: Right-click for menu options (Show Timer, Stop Service, Quit)

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

#### User Service
```bash
# Start the service
make start

# Check status
make status

# View logs
make logs
```

#### System Service
```bash
# Check status for current user
systemctl status pomodoro-lock@$USER.service

# Add service for another user
make add-user USER=username

# List all users with service
make list-users
```

## Project Structure

```
pomodoro-lock/
├── src/                          # Source code
│   └── pomodoro-lock.py          # Main application
├── scripts/                      # Installation and utility scripts
│   ├── install.sh                # Command line installer (user service)
│   ├── install-desktop.sh        # Desktop installer (user service)
│   ├── install-system.sh         # System service installer
│   ├── manage-users.sh           # User management for system service
│   ├── start-pomodoro.sh         # Startup script
│   └── configure-pomodoro.py     # Configuration management
├── config/                       # Configuration files
│   ├── config.json               # Default configuration
│   ├── pomodoro-lock.service     # User service file
│   ├── pomodoro-lock-simple.service # Alternative user service
│   └── pomodoro-lock-system.service # System service file
├── tests/                        # Test scripts
│   ├── test-notification.py      # Notification tests
│   ├── test-overlay.py           # Overlay tests
│   ├── test-timer.py             # Timer tests
│   ├── test-multi-overlay.py     # Multi-display tests
│   ├── test-pomodoro-short.py    # Complete workflow tests
│   └── test-screen-lock.py       # Screen lock tests (legacy)
├── docs/                         # Documentation
│   └── README.md                 # Detailed documentation
├── debian/                       # Debian packaging files
├── README.md                     # This file (quick start)
├── Makefile                      # Build and development commands
├── CONTRIBUTING.md               # Contribution guidelines
└── LICENSE                       # MIT License
```

## Features

- ✅ **Multi-Display Support**: Full-screen overlays on all connected monitors
- ✅ **Visual Timer**: Draggable countdown timer in bottom-left corner
- ✅ **System Tray Integration**: Minimize to system tray with status display
- ✅ **Smart UI Controls**: Close button (✕) to minimize, Power button (⏻) to stop service
- ✅ **Single Instance**: Prevents multiple UI instances with graceful messaging
- ✅ **Notifications**: Desktop notifications before break periods
- ✅ **Configuration**: JSON-based configuration with easy management
- ✅ **Systemd Service**: Runs as user or system service, starts automatically on login
- ✅ **Cross-Desktop**: Works with GNOME, KDE, XFCE, and other desktop environments
- ✅ **Debian Packaging**: Ready for Debian/Ubuntu distribution
- ✅ **Multi-User Support**: System service can manage multiple users

## How It Works

1. **Work Period**: Shows countdown timer, sends notification before break
2. **Break Period**: Creates full-screen overlays on all displays with countdown
3. **Cycle**: Work → Break → Work → Break → (repeats indefinitely)

## Future Enhancements

- Re-implement robust user inactivity detection (e.g., using evdev for keyboard/mouse input or other screen activity monitoring methods).
- Add AppStream metadata support for better Linux desktop integration and app store distribution.

## Installation Methods

### User Service (Default)
- **Scope**: Single user
- **Permissions**: User-level
- **Location**: `~/.local/share/pomodoro-lock/`
- **Service**: `pomodoro-lock.service`
- **Management**: `systemctl --user` (for user service)

### System Service (Advanced)
- **Scope**: Multiple users
- **Permissions**: System-level (requires sudo)
- **Location**: `/usr/local/bin/` and `/etc/pomodoro-lock/`
- **Service**: `pomodoro-lock@username.service`
- **Management**: `systemctl` (with sudo)

### Debian Package
- **Scope**: System-wide installation
- **Permissions**: System-level
- **Location**: `/usr/bin/` and `/etc/pomodoro-lock/`
- **Service**: `pomodoro-lock.service`
- **Management**: Standard Debian package management

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