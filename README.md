# Pomodoro Lock

A robust, cross-platform Pomodoro timer with system tray integration, multi-display support, and per-user systemd service. Designed for system-wide installation, single-instance enforcement, and seamless user experience.

> **⚠️ Note: Windows version is currently not stable and may have issues. Linux version is fully stable and recommended for production use.**

## Highlights
- System-wide install to `/usr/share/pomodoro-lock` and `/usr/bin/`
- Per-user config and venv auto-setup on first run
- Single instance per user; launching again shows a dialog and exits
- Tray icon for restoring the timer window
- Modern GTK/Tkinter UI with multi-display support
- Fullscreen break overlays on all connected monitors
- Per-user systemd service, managed automatically
- Install/uninstall scripts clean up all files and services
- Robust error handling and UTF-8 encoding safety

## Install
- `sudo ./scripts/install.sh` or use the Debian package
- Uninstall with `sudo ./scripts/uninstall.sh` or `sudo dpkg -r pomodoro-lock`

## Usage
- Run `pomodoro-lock` to start or bring up the timer window
- Click the tray icon to restore the window if closed
- Use `pomodoro-configure` for settings
- Use `pomodoro-service` to manage the user service
- Break overlays automatically appear on all connected displays

## See `docs/README.md` for full details.

## 🚀 Quick Start

### Linux Installation

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

### Windows Installation

> **⚠️ Warning: Windows version is not stable and may have issues. Use at your own risk.**

```bash
# Clone the repository
git clone https://github.com/vgundala/pomodoro-lock.git
cd pomodoro-lock

# Install Python dependencies
pip install -r requirements-crossplatform.txt

# Run the application
python src/pomodoro-ui-crossplatform.py

# Or build executable
pip install pyinstaller
pyinstaller --onefile --windowed --name pomodoro-lock --icon=pomodoro-lock-24.png src/pomodoro-ui-crossplatform.py
```

### Using the Application

#### Starting the Application

**Linux:**
```bash
# Start the UI (launches from Applications menu or command line)
pomodoro-lock

# Or start the UI directly
pomodoro-lock ui
```

**Windows:**
```bash
# Run Python version
python src/pomodoro-ui-crossplatform.py

# Or run executable
pomodoro-lock.exe
```

#### UI Controls
- **Timer Window**: Draggable countdown timer with "Pomodoro Lock" title
- **Close Button (✕)**: Minimizes the timer to system tray
- **Power Button (⏻)**: Quits the application
- **System Tray**: Right-click for menu options (Show Timer, Quit)

#### Desktop Environment Compatibility

**Linux:**
- **GNOME/KDE**: Full system tray support with AppIndicator3
- **XFCE**: Limited system tray support - uses persistent notifications or status window as fallback
- **Other**: Fallback to status window in top-right corner

**Windows:**
- **Windows 10/11**: Full system tray support with pystray
- **Windows 7/8**: Basic system tray support
- **All versions**: Toast notifications and fullscreen overlays

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

**Linux:**
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

**Windows:**
```bash
# Enable autostart (adds to Windows Registry)
python -c "from src.platform import AutostartManager; AutostartManager().enable_autostart()"

# Disable autostart
python -c "from src.platform import AutostartManager; AutostartManager().disable_autostart()"
```

## 📁 Project Structure

```
pomodoro-lock/
├── src/                          # Source code
│   ├── pomodoro-ui.py            # Original Linux-only UI application
│   ├── pomodoro-ui-crossplatform.py  # Cross-platform UI application
│   ├── platform/                 # Platform abstraction layer
│   │   ├── __init__.py          # Platform detection and imports
│   │   ├── linux.py             # Linux-specific implementations
│   │   └── windows.py           # Windows-specific implementations
│   └── gui/                     # Cross-platform GUI layer
│       ├── __init__.py          # GUI platform detection
│       ├── gtk_ui.py            # GTK-based GUI for Linux
│       └── tkinter_ui.py        # Tkinter-based GUI for Windows
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
├── requirements-crossplatform.txt # Cross-platform dependencies
├── CROSSPLATFORM.md              # Cross-platform architecture guide
├── CONTRIBUTING.md               # Contribution guidelines
└── LICENSE                       # MIT License
```