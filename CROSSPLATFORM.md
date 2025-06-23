# Cross-Platform Pomodoro Lock

This document explains the cross-platform architecture of Pomodoro Lock, which now supports both Linux and Windows.

## Architecture Overview

The application has been refactored to use a platform abstraction layer that provides:

- **Platform Detection**: Automatic detection of Linux vs Windows
- **Platform-Specific Implementations**: Separate implementations for each platform
- **Unified API**: Common interface regardless of platform
- **Graceful Fallbacks**: Features degrade gracefully when dependencies are missing

## Directory Structure

```
src/
├── platform/                 # Platform abstraction layer
│   ├── __init__.py          # Platform detection and imports
│   ├── linux.py             # Linux-specific implementations
│   └── windows.py           # Windows-specific implementations
├── gui/                     # Cross-platform GUI layer
│   ├── __init__.py          # GUI platform detection
│   ├── gtk_ui.py            # GTK-based GUI for Linux
│   └── tkinter_ui.py        # Tkinter-based GUI for Windows
├── pomodoro-ui.py           # Original Linux-only version
└── pomodoro-ui-crossplatform.py  # New cross-platform version
```

## Platform-Specific Features

### Linux Features
- **Notifications**: `notify2` for desktop notifications
- **System Tray**: `AppIndicator3` for system tray integration
- **GUI**: GTK3 with CSS styling
- **Screen Management**: Xlib for multi-monitor support
- **Autostart**: systemd user services
- **File Locking**: fcntl for process locking

### Windows Features
- **Notifications**: `win10toast` for Windows toast notifications
- **System Tray**: `pystray` for system tray integration
- **GUI**: Tkinter with native Windows styling
- **Screen Management**: win32api for monitor detection
- **Autostart**: Windows Registry
- **File Locking**: Windows file locking API

## Dependencies

### Linux Dependencies
```bash
# System packages
sudo apt-get install python3-gi python3-notify2 python3-xlib gir1.2-appindicator3-0.1

# Python packages
pip install psutil
```

### Windows Dependencies
```bash
# Python packages
pip install psutil win10toast pystray Pillow pywin32
```

## Usage

### Running the Cross-Platform Version

```bash
# Linux
python3 src/pomodoro-ui-crossplatform.py

# Windows
python src/pomodoro-ui-crossplatform.py
```

### Building Executables

#### Linux (Debian Package)
```bash
dpkg-buildpackage -b -us -uc
```

#### Windows (PyInstaller)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name pomodoro-lock --icon=pomodoro-lock-24.png src/pomodoro-ui-crossplatform.py
```

## Platform Abstraction Classes

### NotificationManager
- **Linux**: Uses `notify2` for desktop notifications
- **Windows**: Uses `win10toast` for toast notifications

### SystemTrayManager
- **Linux**: Uses `AppIndicator3` for system tray
- **Windows**: Uses `pystray` for system tray

### ScreenManager
- **Linux**: Uses Xlib for screen enumeration
- **Windows**: Uses win32api for monitor detection

### AutostartManager
- **Linux**: Uses systemd user services
- **Windows**: Uses Windows Registry

### FileLockManager
- **Linux**: Uses fcntl for file locking
- **Windows**: Uses Windows file locking API

## GUI Components

### TimerWindow
- **Linux**: GTK3 window with CSS styling
- **Windows**: Tkinter window with native styling

### FullScreenOverlay
- **Linux**: GTK3 fullscreen overlay
- **Windows**: Tkinter fullscreen overlay

### MultiDisplayOverlay
- **Linux**: Multi-monitor support via Xlib
- **Windows**: Basic multi-monitor support (can be enhanced)

## Configuration

The application uses platform-specific paths for configuration:

### Linux
- Config: `~/.local/share/pomodoro-lock/config/`
- Logs: `~/.local/share/pomodoro-lock/pomodoro-ui.log`
- Lock: `~/.local/share/pomodoro-lock/pomodoro-ui.lock`

### Windows
- Config: `~/AppData/Local/pomodoro-lock/config/`
- Logs: `~/AppData/Local/pomodoro-lock/pomodoro-ui.log`
- Lock: `~/AppData/Local/pomodoro-lock/pomodoro-ui.lock`

## Development

### Adding New Platform-Specific Features

1. **Add to platform abstraction**:
   ```python
   # In src/platform/__init__.py
   class NewFeatureManager:
       pass
   ```

2. **Implement for Linux**:
   ```python
   # In src/platform/linux.py
   class NewFeatureManager:
       def __init__(self):
           # Linux-specific implementation
           pass
   ```

3. **Implement for Windows**:
   ```python
   # In src/platform/windows.py
   class NewFeatureManager:
       def __init__(self):
           # Windows-specific implementation
           pass
   ```

### Testing Cross-Platform Features

```python
# Test platform detection
from platform import SYSTEM
print(f"Running on: {SYSTEM}")

# Test feature availability
from platform import NotificationManager
notifier = NotificationManager()
print(f"Notifications available: {notifier.initialized}")
```

## GitHub Actions

The GitHub Actions workflow now builds for both platforms:

- **Linux**: Builds Debian package (`.deb`)
- **Windows**: Builds executable (`.exe`)
- **Release**: Creates GitHub release with both artifacts

## Migration from Linux-Only Version

The original `pomodoro-ui.py` remains unchanged for backward compatibility. To migrate to the cross-platform version:

1. **Update imports** in your code to use the platform abstraction
2. **Replace direct GTK calls** with the GUI abstraction layer
3. **Update dependency management** to include cross-platform requirements
4. **Test on both platforms** to ensure compatibility

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Install platform-specific dependencies
2. **GUI Not Working**: Check if GUI libraries are available
3. **Notifications Not Working**: Verify notification system is properly configured
4. **System Tray Not Showing**: Check system tray permissions

### Platform-Specific Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check platform detection
from platform import SYSTEM
print(f"Detected platform: {SYSTEM}")

# Test individual components
from platform import NotificationManager, SystemTrayManager
notifier = NotificationManager()
tray = SystemTrayManager(None)
```

## Future Enhancements

- **macOS Support**: Add macOS platform implementation
- **Enhanced Multi-Monitor**: Improve Windows multi-monitor support
- **Better Windows GUI**: Consider PyQt or wxPython for richer Windows GUI
- **Mobile Support**: Add mobile platform support
- **Web Interface**: Add web-based interface option 