# Pomodoro Lock

## Overview
Pomodoro Lock is a cross-platform, single-instance Pomodoro timer with a tray icon, multi-display support, and systemd user service integration. It is designed for robust, multi-user, system-wide installation and easy use.

> **⚠️ Note: Windows version is currently not stable and may have issues. Linux version is fully stable and recommended for production use.**

---

## Key Features (as of v1.3.7+)
- **System-wide installation** to `/usr/share/pomodoro-lock` and `/usr/bin/`
- **User environment auto-setup**: Each user's config, venv, and service are set up automatically on first launch
- **Single-instance enforcement**: Only one instance per user; launching again shows a dialog and exits
- **Tray-based UI**: Timer window can be closed to tray and restored by clicking the tray icon
- **Modern GTK/Tkinter UI**: Consistent look and feel on Linux and Windows
- **Multi-display support**: Break overlays automatically appear on all connected monitors
- **Fullscreen break overlays**: Always-on-top overlays that cover all displays during breaks
- **Systemd user service**: Managed per-user, not system-wide
- **Robust install/uninstall scripts**: Clean up all system and user files, services, and icons
- **No manual user setup required**: No more copying files or running setup scripts per user
- **Enhanced error handling**: Robust UTF-8 encoding safety and thread-safe GUI updates

---

## Installation

### Debian Package
- Install with `sudo dpkg -i pomodoro-lock.deb`
- Uninstall with `sudo dpkg -r pomodoro-lock`

### Manual Installation
- Run `sudo ./scripts/install.sh` to install system-wide
- Run `sudo ./scripts/uninstall.sh` to remove all files and services

---

## Usage
- Run `pomodoro-lock` to start or bring up the timer window
- If the window is closed, click the Pomodoro Lock tray icon to restore it
- Only one instance per user is allowed; a dialog will inform you if already running
- Use `pomodoro-configure` to change timer settings
- Use `pomodoro-service` to manage the user service (start/stop/status/logs)
- During breaks, fullscreen overlays will appear on all connected displays

---

## Multi-Display Support
- **Automatic detection**: The application automatically detects all connected monitors
- **Fullscreen overlays**: Break overlays cover each monitor completely
- **Always on top**: Overlays appear above all other windows and applications
- **Synchronized timers**: All overlays show the same countdown timer
- **Proper z-order**: Timer window is automatically lowered during breaks to ensure overlay visibility

---

## Service Management
- The app installs a per-user systemd service on first launch
- Service is managed with `systemctl --user` or the `pomodoro-service` script
- Uninstall scripts now fully clean up service files and systemd state

---

## What's New (since last docs update)
- **System-wide install** replaces user-space copying
- **Auto-setup** for each user on first run (no manual setup)
- **Single-instance logic**: Only one instance, always brings up the window or shows a tray message
- **Tray icon**: Always available; click to restore window
- **Dialog for second instance**: Now instructs user to use the tray icon
- **No more SIGUSR1 or IPC**: Simpler, more robust logic
- **Install/uninstall scripts**: Now handle all users, system files, and systemd state
- **Obsolete service files and user setup scripts removed**
- **All documentation and help messages updated for new workflow**
- **Multi-display overlay support**: Break overlays now appear on all connected monitors
- **Enhanced error handling**: Fixed UTF-8 encoding issues and added thread-safe GUI updates
- **Improved z-order management**: Timer window automatically adjusts position relative to overlays

---

## Troubleshooting
- If you see a warning about the service after uninstall, run `systemctl --user daemon-reload && systemctl --user reset-failed`
- If the timer window does not appear, click the tray icon
- For multi-user systems, each user can run `pomodoro-lock` and get their own isolated environment
- If overlays don't appear on all monitors, check that your display manager supports multi-monitor fullscreen windows

---

## Contributing
See `CONTRIBUTING.md` for guidelines.

## License
See `LICENSE` for details. 