# Troubleshooting Guide

## System-Wide Installation Issues

### **Problem**: Installation fails with permission errors

**Error Message**:
```
Permission denied: /usr/share/pomodoro-lock
```

**Cause**: The install script needs sudo privileges to install system-wide.

**Solution**:
```bash
# Use sudo for system-wide installation
sudo ./scripts/install.sh
```

### **Problem**: Uninstall script fails to remove all files

**Error Message**:
```
Failed to remove service for user
```

**Cause**: Service files may be in use or have permission issues.

**Solution**:
```bash
# Stop all user services first
systemctl --user stop pomodoro-lock.service
systemctl --user disable pomodoro-lock.service

# Then run uninstall
sudo ./scripts/uninstall.sh

# Clean up any remaining systemd state
systemctl --user daemon-reload
systemctl --user reset-failed
```

---

## User Environment Auto-Setup Issues

### **Problem**: First run doesn't set up user environment

**Error Message**:
```
Failed to create user config directory
```

**Cause**: User doesn't have write permissions to their home directory.

**Solution**:
```bash
# Check home directory permissions
ls -la ~/

# Fix permissions if needed
chmod 755 ~/

# Try running again
pomodoro-lock
```

### **Problem**: Virtual environment creation fails

**Error Message**:
```
Failed to create virtual environment
```

**Cause**: Python venv module not available or disk space issues.

**Solution**:
```bash
# Install python3-venv if missing
sudo apt-get install python3-venv

# Check disk space
df -h

# Try manual setup
python3 -m venv ~/.local/share/pomodoro-lock/venv
```

---

## Single-Instance Enforcement Issues

### **Problem**: Multiple instances running despite single-instance protection

**Error Message**:
```
Pomodoro Lock is already running
```

**Cause**: Lock file not properly cleaned up from previous crash.

**Solution**:
```bash
# Remove stale lock file
rm -f ~/.local/share/pomodoro-lock/pomodoro-lock.pid

# Kill any remaining processes
pkill -f pomodoro-lock

# Start fresh
pomodoro-lock
```

### **Problem**: Lock file permission issues

**Error Message**:
```
Permission denied: .local/share/pomodoro-lock/pomodoro-lock.pid
```

**Cause**: Lock file owned by different user or wrong permissions.

**Solution**:
```bash
# Fix ownership
sudo chown -R $USER:$USER ~/.local/share/pomodoro-lock/

# Fix permissions
chmod 755 ~/.local/share/pomodoro-lock/
chmod 644 ~/.local/share/pomodoro-lock/pomodoro-lock.pid
```

---

## System Tray and Window Issues

### **Problem**: Tray icon doesn't appear

**Error Message**:
```
Failed to create system tray icon
```

**Cause**: Desktop environment doesn't support system tray or missing dependencies.

**Solution**:
```bash
# Install system tray dependencies
sudo apt-get install python3-gi gir1.2-appindicator3-0.1

# Check desktop environment support
echo $XDG_CURRENT_DESKTOP

# For XFCE, install additional packages
sudo apt-get install xfce4-appmenu-plugin
```

### **Problem**: Window doesn't restore from tray

**Error Message**:
```
Window restoration failed
```

**Cause**: Window manager issues or GTK problems.

**Solution**:
```bash
# Restart the application
pkill -f pomodoro-lock
pomodoro-lock

# Check GTK theme issues
export GTK_THEME=Adwaita
pomodoro-lock
```

### **Problem**: Dialog for second instance doesn't show

**Error Message**:
```
Dialog creation failed
```

**Cause**: GTK dialog dependencies missing or display issues.

**Solution**:
```bash
# Install GTK dependencies
sudo apt-get install python3-gi gir1.2-gtk-3.0

# Check display
echo $DISPLAY

# Try with different display
DISPLAY=:0 pomodoro-lock
```

---

## Systemd User Service Issues

### **Problem**: Service fails to start

**Error Message**:
```
Failed to start pomodoro-lock.service
```

**Cause**: Service file issues or user systemd not enabled.

**Solution**:
```bash
# Enable user systemd
systemctl --user enable --now

# Check service status
systemctl --user status pomodoro-lock.service

# View service logs
journalctl --user -u pomodoro-lock.service

# Reinstall service
pomodoro-lock  # This will recreate the service file
```

### **Problem**: Service doesn't autostart

**Error Message**:
```
Service not enabled for autostart
```

**Cause**: User systemd not properly configured or service not enabled.

**Solution**:
```bash
# Enable user systemd
loginctl enable-linger $USER

# Enable the service
systemctl --user enable pomodoro-lock.service

# Check if enabled
systemctl --user is-enabled pomodoro-lock.service
```

### **Problem**: Service file corruption

**Error Message**:
```
Invalid service file format
```

**Cause**: Service file was corrupted or has syntax errors.

**Solution**:
```bash
# Remove corrupted service file
rm ~/.config/systemd/user/pomodoro-lock.service

# Reload systemd
systemctl --user daemon-reload

# Run app to recreate service
pomodoro-lock
```

---

## Multi-User Environment Issues

### **Problem**: Service conflicts between users

**Error Message**:
```
Service already exists for different user
```

**Cause**: Service files from different users conflicting.

**Solution**:
```bash
# Each user should have their own service
# Check current user's service
systemctl --user status pomodoro-lock.service

# Ensure running as correct user
whoami
echo $USER
```

### **Problem**: Configuration conflicts

**Error Message**:
```
Configuration file access denied
```

**Cause**: Users trying to access each other's config files.

**Solution**:
```bash
# Each user has their own config
ls -la ~/.local/share/pomodoro-lock/config.json

# Fix permissions if needed
chmod 600 ~/.local/share/pomodoro-lock/config.json
```

---

## Configuration Issues

### **Problem**: Configuration changes don't take effect

**Error Message**:
```
Configuration not updated
```

**Cause**: Config file not writable or app not restarted.

**Solution**:
```bash
# Check config file permissions
ls -la ~/.local/share/pomodoro-lock/config.json

# Make sure it's writable
chmod 644 ~/.local/share/pomodoro-lock/config.json

# Restart the application
pkill -f pomodoro-lock
pomodoro-lock
```

### **Problem**: Configuration file corruption

**Error Message**:
```
Invalid JSON in configuration
```

**Cause**: Config file was corrupted or has syntax errors.

**Solution**:
```bash
# Backup corrupted config
cp ~/.local/share/pomodoro-lock/config.json ~/.local/share/pomodoro-lock/config.json.bak

# Remove corrupted config
rm ~/.local/share/pomodoro-lock/config.json

# Run app to recreate default config
pomodoro-lock
```

---

## Dependency Issues

### **Problem**: Missing Python dependencies

**Error Message**:
```
ModuleNotFoundError: No module named 'psutil'
```

**Cause**: Virtual environment not activated or dependencies not installed.

**Solution**:
```bash
# Activate virtual environment
source ~/.local/share/pomodoro-lock/venv/bin/activate

# Install dependencies
pip install -r /usr/share/pomodoro-lock/requirements-crossplatform.txt

# Or reinstall user environment
rm -rf ~/.local/share/pomodoro-lock/venv
pomodoro-lock  # This will recreate the venv
```

### **Problem**: System dependencies missing

**Error Message**:
```
GTK not available
```

**Cause**: GTK development libraries not installed.

**Solution**:
```bash
# Install GTK dependencies
sudo apt-get install python3-gi gir1.2-gtk-3.0 libgtk-3-dev

# Install notification dependencies
sudo apt-get install libnotify-bin python3-notify2
```

---

## Common Commands

### Debug Application
```bash
# Check if app is running
ps aux | grep pomodoro-lock

# Check lock file
cat ~/.local/share/pomodoro-lock/pomodoro-lock.pid

# View application logs
journalctl --user -f -u pomodoro-lock.service

# Check service status
systemctl --user status pomodoro-lock.service
```

### Reset User Environment
```bash
# Stop the application
pkill -f pomodoro-lock

# Remove user environment
rm -rf ~/.local/share/pomodoro-lock/

# Restart to recreate
pomodoro-lock
```

### Clean Installation
```bash
# Uninstall completely
sudo ./scripts/uninstall.sh

# Remove any remaining files
sudo rm -rf /usr/share/pomodoro-lock
sudo rm -f /usr/bin/pomodoro-lock
sudo rm -f /usr/bin/pomodoro-configure
sudo rm -f /usr/bin/pomodoro-service

# Reinstall
sudo ./scripts/install.sh
```

---

## Prevention Tips

1. **Always use sudo for install/uninstall** - System-wide installation requires root privileges
2. **Check user systemd** - Ensure user systemd is enabled before using services
3. **Monitor service logs** - Use `journalctl --user` to debug service issues
4. **Keep config files backed up** - Backup important configurations
5. **Test multi-user scenarios** - Verify isolation between users
6. **Check desktop environment compatibility** - Some DEs have limited tray support

---

## Resources

- [Systemd User Services](https://wiki.archlinux.org/title/Systemd/User)
- [GTK Documentation](https://docs.gtk.org/)
- [Python Virtual Environments](https://docs.python.org/3/library/venv.html)
- [Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/) 