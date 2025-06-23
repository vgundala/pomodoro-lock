# Pomodoro Lock - Cross-Platform Timer with Screen Overlay

A comprehensive Pomodoro timer application that helps you maintain focus during work sessions and enforces breaks with full-screen overlays across all connected displays. **Now supports both Linux and Windows!**

**Copyright © 2024 Vinay Gundala (vg@ivdata.dev)**

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

## ✨ Features

### Core Features (Both Platforms)
- ✅ **Standalone UI**: Complete timer application with integrated overlays
- ✅ **Multi-Display Support**: Full-screen overlays on all connected monitors
- ✅ **Visual Timer**: Draggable countdown timer with "Pomodoro Lock" title
- ✅ **System Tray Integration**: Minimize to system tray with status display
- ✅ **Smart UI Controls**: Close button (✕) to minimize, Power button (⏻) to quit
- ✅ **Single Instance Protection**: Prevents multiple UI instances with graceful messaging
- ✅ **Notifications**: Desktop notifications before break periods
- ✅ **Configuration**: JSON-based configuration with easy management
- ✅ **Autostart**: Runs automatically on login
- ✅ **Cross-Platform**: Works on Linux and Windows

### Linux-Specific Features
- ✅ **Systemd Autostart**: Runs automatically on login via systemd user service
- ✅ **Cross-Desktop**: Works with GNOME, KDE, XFCE, and other desktop environments
- ✅ **Debian Packaging**: Ready for Debian/Ubuntu distribution
- ✅ **GTK3 GUI**: Native Linux look and feel with CSS styling
- ✅ **notify2**: Desktop notifications
- ✅ **AppIndicator3**: System tray integration

### Windows-Specific Features
- ✅ **Windows Registry Autostart**: Runs automatically on login via Windows Registry
- ✅ **Windows Toast Notifications**: Modern Windows 10/11 toast notifications
- ✅ **pystray System Tray**: Native Windows system tray integration
- ✅ **Tkinter GUI**: Native Windows look and feel
- ✅ **Windows File Locking**: Reliable process locking
- ✅ **High DPI Support**: Scales properly on high-resolution displays

## 🔧 How It Works

1. **Work Period**: Shows countdown timer, sends notification before break
2. **Break Period**: Creates full-screen overlays on all displays with countdown
3. **Cycle**: Work → Break → Work → Break → (repeats indefinitely)

## 🏗️ Architecture

### Cross-Platform Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Cross-Platform UI                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Timer Window  │  │  System Tray    │  │   Overlays  │ │
│  │  (Platform UI)  │  │  (Platform API) │  │ (Multi-Display) │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Platform Abstraction Layer                 │ │
│  │  • Linux: GTK3, notify2, AppIndicator3, systemd        │ │
│  │  • Windows: Tkinter, win10toast, pystray, Registry     │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Platform-Specific │
                    │  Autostart & Services │
                    └─────────────────┘ 
```

### Platform Detection
The application automatically detects the platform and uses the appropriate implementations:

- **Linux**: Uses GTK3, notify2, AppIndicator3, systemd
- **Windows**: Uses Tkinter, win10toast, pystray, Windows Registry

### Standalone UI Design
- **Single Process**: UI handles all functionality (timer, overlays, notifications)
- **Platform Services**: Manages autostart and process lifecycle
- **File Locking**: Prevents multiple instances using platform-specific file locks
- **Clean Exit**: Proper cleanup on quit (overlays, lock files, etc.)

## 📦 Distribution

### Linux Distribution
- **Debian Package**: `dpkg-buildpackage -b -us -uc`
- **System Integration**: Full systemd service integration
- **Package Manager**: Ready for Debian/Ubuntu repositories

### Windows Distribution
- **Executable**: `pyinstaller --onefile --windowed`
- **Installer**: Can be packaged with NSIS or Inno Setup
- **Microsoft Store**: Ready for Windows Store submission

### GitHub Actions
- **Automated Builds**: Builds both Linux (.deb) and Windows (.exe) packages
- **Release Automation**: Creates GitHub releases with both artifacts
- **CI/CD**: Automated testing and packaging

## 🔮 Future Enhancements

- **macOS Support**: Add macOS platform implementation
- **Enhanced Multi-Monitor**: Improve Windows multi-monitor support
- **Better Windows GUI**: Consider PyQt or wxPython for richer Windows GUI
- **Mobile Support**: Add mobile platform support
- **Web Interface**: Add web-based interface option
- **Re-implement robust user inactivity detection** (e.g., using evdev for keyboard/mouse input or other screen activity monitoring methods)
- **Add AppStream metadata support** for better Linux desktop integration and app store distribution

## 📚 Documentation

For detailed documentation, installation instructions, configuration options, and troubleshooting, see:
- [Detailed Documentation](docs/README.md)
- [Cross-Platform Architecture Guide](CROSSPLATFORM.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

## 🧪 Testing

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

# Test cross-platform features
python3 -c "from src.platform import SYSTEM; print(f'Platform: {SYSTEM}')"
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.