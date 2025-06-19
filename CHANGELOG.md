# Changelog

**Copyright © 2024 Vinay Gundala (vg@ivdata.dev)**

All notable changes to Pomodoro Lock will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive project organization and structure
- Debian packaging support
- Python packaging support
- Makefile with development commands
- Detailed documentation and guides
- Copyright information and licensing

### Changed
- Reorganized project structure for better maintainability
- Updated all documentation with proper attribution
- Improved installation scripts for new directory structure

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