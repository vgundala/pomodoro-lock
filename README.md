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

# Install as user service
./scripts/install-desktop.sh
```

#### Option 2: System Service (For multiple users)
```bash
# Clone the repository
git clone https://github.com/vgundala/pomodoro-lock.git
cd pomodoro-lock

# Install as system service (requires sudo)
sudo ./scripts/install-system.sh
```

### Configuration
```bash
# Interactive configuration
pomodoro-configure

# Quick presets
pomodoro-configure standard
```

### Service Management

#### User Service
```bash
# Start the service
systemctl --user start pomodoro-lock.service

# Check status
systemctl --user status pomodoro-lock.service
```

#### System Service
```bash
# Check status for current user
systemctl status pomodoro-lock@$USER.service

# Add service for another user
sudo ./scripts/manage-users.sh add username

# List all users with service
sudo ./scripts/manage-users.sh list
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
├── setup.py                      # Python package configuration
├── requirements.txt              # Python dependencies
├── PACKAGING.md                  # Packaging guide
├── CONTRIBUTING.md               # Contribution guidelines
└── LICENSE                       # MIT License
```

## Features

- ✅ **Multi-Display Support**: Full-screen overlays on all connected monitors
- ✅ **Visual Timer**: Draggable countdown timer in bottom-left corner
- ✅ **Notifications**: Desktop notifications before break periods
- ✅ **Inactivity Detection**: Resets timer if user is inactive for too long
- ✅ **Configuration**: JSON-based configuration with easy management
- ✅ **Systemd Service**: Runs as user or system service, starts automatically on login
- ✅ **Cross-Desktop**: Works with GNOME, KDE, XFCE, and other desktop environments
- ✅ **Packaging Ready**: Supports both pip and Debian packaging
- ✅ **Multi-User Support**: System service can manage multiple users

## How It Works

1. **Work Period**: Shows countdown timer, sends notification before break
2. **Break Period**: Creates full-screen overlays on all displays with countdown
3. **Cycle**: Work → Break → Work → Break → (repeats indefinitely)

## Installation Methods

### User Service (Default)
- **Scope**: Single user
- **Permissions**: User-level
- **Location**: `~/.local/share/pomodoro-lock/`
- **Service**: `pomodoro-lock.service`
- **Management**: `systemctl --user`

### System Service (Advanced)
- **Scope**: Multiple users
- **Permissions**: System-level (requires sudo)
- **Location**: `/usr/local/bin/` and `/etc/pomodoro-lock/`
- **Service**: `pomodoro-lock@username.service`
- **Management**: `systemctl` (with sudo)

## Documentation

For detailed documentation, installation instructions, configuration options, and troubleshooting, see:
- [Detailed Documentation](docs/README.md)
- [Packaging Guide](PACKAGING.md)
- [Contributing Guidelines](CONTRIBUTING.md)

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

## Configuration

### Quick Configuration
```bash
# Interactive configuration
pomodoro-configure

# Apply presets
pomodoro-configure standard  # 25/5
pomodoro-configure long      # 45/15
pomodoro-configure short     # 15/3
```

### Manual Configuration
Edit the configuration file directly:
```bash
# User service
nano ~/.local/share/pomodoro-lock/config/config.json

# System service
sudo nano /etc/pomodoro-lock/config.json
```

## Service Management

### User Service
```bash
# Start/Stop/Restart
systemctl --user start pomodoro-lock.service
systemctl --user stop pomodoro-lock.service
systemctl --user restart pomodoro-lock.service

# Check status and logs
systemctl --user status pomodoro-lock.service
journalctl --user -u pomodoro-lock.service -f
```

### System Service
```bash
# Check status for current user
systemctl status pomodoro-lock@$USER.service

# Add service for a user
sudo ./scripts/manage-users.sh add username

# Remove service for a user
sudo ./scripts/manage-users.sh remove username

# List all users with service
sudo ./scripts/manage-users.sh list

# Manage service for specific user
sudo ./scripts/manage-users.sh start username
sudo ./scripts/manage-users.sh stop username
sudo ./scripts/manage-users.sh restart username
sudo ./scripts/manage-users.sh logs username
```

## Packaging

This project supports multiple packaging formats:

### Python Package (pip)
```bash
make package-pip
pip install dist/pomodoro-lock-1.0.0.tar.gz
```

### Debian Package (.deb)
```bash
make package-deb
sudo dpkg -i ../pomodoro-lock_1.0.0-1_all.deb
```

For detailed packaging information, see [PACKAGING.md](PACKAGING.md).

## Requirements

- Ubuntu/Debian-based system
- Python 3.6+
- GTK3 desktop environment
- User account (not root for user service)
- Root access (for system service installation)

## Development

### Quick Development Setup
```bash
# Install in development mode
make install-pip

# Run tests
make test

# Start service
make start
```

### Available Make Commands
```bash
make help                    # Show all available commands
make install-desktop         # Install as user service
make install-system          # Install as system service
make configure               # Interactive configuration
make test                    # Run all tests
make package-pip             # Build Python package
make package-deb             # Build Debian package

# System service user management
make add-user USER=username    # Add service for user
make remove-user USER=username # Remove service for user
make list-users               # List all users with service
make user-status USER=username # Check service status for user
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Vinay Gundala** - [vg@ivdata.dev](mailto:vg@ivdata.dev)

- GitHub: [@vgundala](https://github.com/vgundala)
- Project: [pomodoro-lock](https://github.com/vgundala/pomodoro-lock)

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Support

If you encounter any issues or have questions:

1. Check the [detailed documentation](docs/README.md)
2. Review the [troubleshooting section](docs/README.md#troubleshooting)
3. Run the test scripts to verify functionality
4. Create an issue on [GitHub](https://github.com/vgundala/pomodoro-lock/issues)

---

**Note**: This application uses screen overlays instead of system screen locks for better compatibility across different desktop environments and to ensure the timer remains visible during break periods. 