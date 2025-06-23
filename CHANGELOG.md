# Changelog

**Copyright © 2024 Vinay Gundala (vg@ivdata.dev)**

All notable changes to Pomodoro Lock will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Standalone UI Architecture**
  - Consolidated service and UI into single standalone application
  - Removed redundant `pomodoro-service.py` file
  - Integrated screen overlay functionality directly into UI
  - Added single instance protection with file locking
  - Simplified architecture with single process design

- **Enhanced Installation Process**
  - `make install` now automatically enables autostart service
  - New `make install-and-start` target for explicit installation with auto-start
  - Enhanced start script with robust environment variable handling
  - Better error handling and fallback mechanisms for service startup

- **Improved Service Management**
  - New make commands for service management: `make start`, `make stop`, `make restart`, `make status`, `make logs`
  - Improved system service user management with make commands
  - Better troubleshooting and debugging capabilities

- **Documentation Updates**
  - Updated README.md with new standalone UI architecture
  - Enhanced detailed documentation with improved service management instructions
  - Added troubleshooting section for common service issues
  - Updated configuration management documentation

### Changed
- **Architecture**: Moved from service/UI split to standalone UI design
- **Installation Behavior**: `make install` now enables autostart service automatically
- **Service Configuration**: Updated to run UI directly instead of separate service
- **Start Script**: Enhanced robustness with multiple fallback strategies for environment variables
- **Documentation**: Streamlined installation and service management instructions using make commands

### Removed
- **Redundant Code**: Removed `pomodoro-service.py` file
- **Service Communication**: Removed service/UI communication code
- **Unused Methods**: Removed `detect_desktop_environment` and `stop_service_and_exit` methods
- **Unused Imports**: Removed unused `time` import from UI

### Fixed
- **Service Startup Issues**: Resolved problems with service exiting immediately after installation
- **Environment Variables**: Fixed issues with DBUS_SESSION_BUS_ADDRESS and XDG_RUNTIME_DIR detection
- **Systemd Configuration**: Removed deprecated `%R` specifier that was causing warnings

### Technical Improvements
- **Start Script Robustness**: Added multiple fallback methods for environment variable detection
- **Error Handling**: Improved error handling in installation and startup processes
- **Service Reliability**: Enhanced service startup reliability across different desktop environments
- **Code Cleanup**: Removed duplicate overlay classes and redundant functionality

## [1.1.0] - 2024-12-19

### Added
- **Improved Installation Process**
  - `make install` now automatically starts the service after installation
  - New `make install-and-start` target for explicit installation with auto-start
  - Enhanced start script with robust environment variable handling
  - Better error handling and fallback mechanisms for service startup

- **Enhanced Service Management**
  - New make commands for service management: `make start`, `make stop`, `make restart`, `make status`, `make logs`
  - Improved system service user management with make commands
  - Better troubleshooting and debugging capabilities

- **Documentation Updates**
  - Updated README.md with new installation options and make commands
  - Enhanced detailed documentation with improved service management instructions
  - Added troubleshooting section for common service issues
  - Updated configuration management documentation

### Changed
- **Installation Behavior**: `make install` now starts the service automatically instead of just enabling it
- **Service Configuration**: Fixed deprecated systemd specifiers and improved environment variable handling
- **Start Script**: Enhanced robustness with multiple fallback strategies for environment variables
- **Documentation**: Streamlined installation and service management instructions using make commands

### Fixed
- **Service Startup Issues**: Resolved problems with service exiting immediately after installation
- **Environment Variables**: Fixed issues with DBUS_SESSION_BUS_ADDRESS and XDG_RUNTIME_DIR detection
- **Systemd Configuration**: Removed deprecated `%R` specifier that was causing warnings

### Technical Improvements
- **Start Script Robustness**: Added multiple fallback methods for environment variable detection
- **Error Handling**: Improved error handling in installation and startup processes
- **Service Reliability**: Enhanced service startup reliability across different desktop environments

### Added
- Comprehensive project organization and structure
- Debian packaging support
- Python packaging support
- Makefile with development commands
- Detailed documentation and guides
- Copyright information and licensing

## [1.0.0] - 2024-12-19

### Added
- **Core Functionality**
  - Multi-display Pomodoro timer with screen overlay
  - Configurable work and break periods
  - Visual countdown timer with drag-and-drop functionality
  - Desktop notifications before break periods
  - Inactivity detection and timer reset
  - Systemd service integration for automatic startup

- **Technical Features**
  - Full-screen overlays on all connected displays
  - Cross-desktop compatibility (GNOME, KDE, XFCE)
  - JSON-based configuration system
  - Comprehensive logging for debugging
  - User activity monitoring (mouse/keyboard)
  - Screen overlay instead of system locks for better compatibility

- **Configuration System**
  - Interactive configuration script
  - Preset configurations (standard, long, short)
  - JSON configuration file with validation
  - Runtime configuration updates

- **Testing Framework**
  - Individual component tests (notifications, overlays, timer)
  - Multi-display overlay tests
  - Complete workflow tests
  - Manual testing scripts

- **Installation System**
  - Desktop installer with environment detection
  - Command-line installer for headless systems
  - Automatic dependency installation
  - User-specific installation paths

- **Documentation**
  - Comprehensive README with quick start guide
  - Detailed documentation in docs/
  - Installation and configuration guides
  - Troubleshooting section
  - Contributing guidelines

### Technical Details
- **Language**: Python 3.6+
- **GUI Framework**: GTK3
- **Dependencies**: python3-gi, python3-psutil, python3-xlib, python3-notify2
- **Service**: Systemd user service
- **Configuration**: JSON format
- **Logging**: File and console output

### Architecture
- **CountdownTimer**: GTK window for work period timer
- **FullScreenOverlay**: GTK window for break period overlay
- **MultiDisplayOverlay**: Manages overlays across multiple displays
- **PomodoroLock**: Main application logic and state management

### Security Features
- Runs as user service (no root privileges required)
- Proper file permissions and security settings
- Isolated from system processes
- User-specific configuration and logs

---

## Version History

### Version 1.0.0
- **Release Date**: December 19, 2024
- **Author**: Vinay Gundala (vg@ivdata.dev)
- **License**: MIT License
- **Status**: Initial release

### Key Features in 1.0.0
1. **Multi-Display Support**: Full-screen overlays on all connected monitors
2. **Visual Timer**: Draggable countdown timer in bottom-left corner
3. **Notifications**: Desktop notifications before break periods
4. **Inactivity Detection**: Resets timer if user is inactive for too long
5. **Configuration**: JSON-based configuration with easy management
6. **Systemd Service**: Runs as a user service, starts automatically on login
7. **Cross-Desktop**: Works with GNOME, KDE, XFCE, and other desktop environments
8. **Packaging Ready**: Supports both pip and Debian packaging

### Installation Methods
- **Source**: Direct installation from source code
- **Python Package**: pip install (development/testing)
- **Debian Package**: .deb package (end users)
- **Manual**: Step-by-step installation guide

### Supported Platforms
- **Operating Systems**: Ubuntu, Debian, and derivatives
- **Desktop Environments**: GNOME, KDE, XFCE, MATE, Cinnamon
- **Python Versions**: 3.6, 3.7, 3.8, 3.9, 3.10, 3.11
- **Architectures**: x86_64, arm64 (where Python dependencies are available)

---

## Contributing to the Changelog

When adding new entries to the changelog, please follow these guidelines:

1. **Use the existing format** and structure
2. **Group changes** by type (Added, Changed, Deprecated, Removed, Fixed, Security)
3. **Use clear, concise language** that users can understand
4. **Include version numbers** and release dates
5. **Link to issues** or pull requests when relevant

### Change Types
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

---

## Contact Information

- **Author**: Vinay Gundala
- **Email**: [vg@ivdata.dev](mailto:vg@ivdata.dev)
- **GitHub**: [@vgundala](https://github.com/vgundala)
- **Project**: [pomodoro-lock](https://github.com/vgundala/pomodoro-lock)

For more information about this project, see the [README.md](README.md) and [docs/README.md](docs/README.md) files.

## Architecture Diagram
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