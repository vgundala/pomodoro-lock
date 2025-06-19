# System Service Installation Guide

**Copyright © 2024 Vinay Gundala (vg@ivdata.dev)**

This guide explains how to install and manage Pomodoro Lock as a system service for multiple users.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [User Management](#user-management)
4. [Service Management](#service-management)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Security Considerations](#security-considerations)

## Overview

The system service installation allows Pomodoro Lock to run for multiple users on the same system. Each user gets their own service instance with separate configuration and logs.

### Key Features
- **Multi-User Support**: Manage Pomodoro Lock for multiple users
- **System Integration**: Installs to system directories
- **Automatic Startup**: Services start automatically on user login
- **Centralized Management**: Admin can manage all users from one place
- **User Isolation**: Each user has separate configuration and logs

### Architecture
```
System Installation:
├── /usr/local/bin/pomodoro-lock.py          # Main application
├── /usr/local/share/pomodoro-lock/          # Scripts and resources
├── /etc/pomodoro-lock/                      # System configuration
├── /etc/systemd/system/pomodoro-lock@.service # Service template
└── /usr/local/share/applications/           # Desktop shortcuts

Per-User Installation:
├── /home/user/.local/share/pomodoro-lock/   # User-specific files
├── /home/user/.config/pomodoro-lock/        # User configuration
└── /home/user/.local/share/applications/    # User desktop shortcuts
```

## Installation

### Prerequisites
- Root access (sudo privileges)
- Ubuntu/Debian-based system
- Python 3.6+ and required dependencies

### Quick Installation
```bash
# Clone the repository
git clone https://github.com/vgundala/pomodoro-lock.git
cd pomodoro-lock

# Install as system service
sudo ./scripts/install-system.sh
```

### What Gets Installed
- **System Files**: `/usr/local/bin/`, `/usr/local/share/`, `/etc/pomodoro-lock/`
- **Service Files**: `/etc/systemd/system/pomodoro-lock@username.service`
- **User Files**: `~/.local/share/pomodoro-lock/`, `~/.config/pomodoro-lock/`
- **Desktop Shortcuts**: System-wide and user-specific
- **Commands**: `pomodoro-configure`, `pomodoro-start`

### Installation Verification
```bash
# Check if service is running for current user
systemctl status pomodoro-lock@$USER.service

# Check if commands are available
which pomodoro-configure
which pomodoro-start

# Check installation directories
ls -la /usr/local/bin/pomodoro-lock.py
ls -la /etc/pomodoro-lock/
```

## User Management

### Adding Users
```bash
# Add service for a specific user
sudo ./scripts/manage-users.sh add username

# Or using make
make add-user USER=username
```

### Removing Users
```bash
# Remove service for a specific user
sudo ./scripts/manage-users.sh remove username

# Or using make
make remove-user USER=username
```

### Listing Users
```bash
# List all users with Pomodoro Lock service
sudo ./scripts/manage-users.sh list

# Or using make
make list-users
```

### User Management Commands
```bash
# Full list of available commands
sudo ./scripts/manage-users.sh

# Examples
sudo ./scripts/manage-users.sh add john
sudo ./scripts/manage-users.sh remove jane
sudo ./scripts/manage-users.sh list
sudo ./scripts/manage-users.sh status john
sudo ./scripts/manage-users.sh start john
sudo ./scripts/manage-users.sh stop john
sudo ./scripts/manage-users.sh restart john
sudo ./scripts/manage-users.sh logs john
```

## Service Management

### Service Status
```bash
# Check status for current user
systemctl status pomodoro-lock@$USER.service

# Check status for specific user
systemctl status pomodoro-lock@username.service

# Check all pomodoro-lock services
systemctl list-units --type=service | grep pomodoro-lock
```

### Starting/Stopping Services
```bash
# For current user
systemctl start pomodoro-lock@$USER.service
systemctl stop pomodoro-lock@$USER.service
systemctl restart pomodoro-lock@$USER.service

# For specific user
systemctl start pomodoro-lock@username.service
systemctl stop pomodoro-lock@username.service
systemctl restart pomodoro-lock@username.service

# Using management script
sudo ./scripts/manage-users.sh start username
sudo ./scripts/manage-users.sh stop username
sudo ./scripts/manage-users.sh restart username
```

### Enabling/Disabling Services
```bash
# Enable service (start on boot)
systemctl enable pomodoro-lock@username.service

# Disable service (don't start on boot)
systemctl disable pomodoro-lock@username.service
```

### Viewing Logs
```bash
# View logs for current user
journalctl -u pomodoro-lock@$USER.service -f

# View logs for specific user
journalctl -u pomodoro-lock@username.service -f

# View recent logs
journalctl -u pomodoro-lock@username.service -n 50

# Using management script
sudo ./scripts/manage-users.sh logs username
```

## Configuration

### User Configuration
Each user has their own configuration file:
```bash
# User configuration location
~/.local/share/pomodoro-lock/config/config.json

# Edit configuration
nano ~/.local/share/pomodoro-lock/config/config.json

# Or use interactive configuration
pomodoro-configure
```

### System Configuration
System-wide configuration is stored in:
```bash
# System configuration location
/etc/pomodoro-lock/config.json

# Edit system configuration (requires sudo)
sudo nano /etc/pomodoro-lock/config.json
```

### Configuration Priority
1. User configuration (`~/.local/share/pomodoro-lock/config/config.json`)
2. System configuration (`/etc/pomodoro-lock/config.json`)
3. Default configuration (built into application)

### Configuration Management
```bash
# Interactive configuration for current user
pomodoro-configure

# Apply presets
pomodoro-configure standard  # 25/5
pomodoro-configure long      # 45/15
pomodoro-configure short     # 15/3

# Show current configuration
pomodoro-configure show
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check service status
systemctl status pomodoro-lock@username.service

# Check logs
journalctl -u pomodoro-lock@username.service -n 50

# Check if user has display access
echo $DISPLAY
xset q

# Check file permissions
ls -la /home/username/.local/share/pomodoro-lock/
```

#### Permission Issues
```bash
# Fix ownership
sudo chown -R username:username /home/username/.local/share/pomodoro-lock/
sudo chown -R username:username /home/username/.config/pomodoro-lock/

# Fix permissions
chmod +x /home/username/.local/share/pomodoro-lock/bin/pomodoro-lock.py
chmod +x /home/username/.local/share/pomodoro-lock/configure-pomodoro.py
```

#### Display Issues
```bash
# Check if user has X11 access
sudo -u username xset q

# Check if user is logged in graphically
who
w

# Restart service after user logs in
systemctl restart pomodoro-lock@username.service
```

### Debug Mode
```bash
# Stop the service
systemctl stop pomodoro-lock@username.service

# Run manually as the user
sudo -u username /usr/local/bin/pomodoro-lock.py
```

### Log Analysis
```bash
# View all pomodoro-lock logs
journalctl | grep pomodoro-lock

# View logs for specific time period
journalctl -u pomodoro-lock@username.service --since "1 hour ago"

# View logs with timestamps
journalctl -u pomodoro-lock@username.service -o short-iso
```

## Security Considerations

### Service Security
- **User Isolation**: Each service runs as the specific user
- **No Root Privileges**: Services don't run as root
- **File Permissions**: Proper ownership and permissions
- **System Protection**: Uses systemd security features

### Security Features
```ini
# From pomodoro-lock-system.service
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/%i/.local/share/pomodoro-lock
ReadWritePaths=/home/%i/.config/pomodoro-lock
```

### Best Practices
1. **Regular Updates**: Keep the application updated
2. **User Management**: Remove services for inactive users
3. **Log Monitoring**: Monitor logs for unusual activity
4. **Configuration**: Review user configurations regularly
5. **Access Control**: Limit who can manage services

### Uninstalling
```bash
# Remove service for specific user
sudo ./scripts/manage-users.sh remove username

# Remove system installation
sudo rm -rf /usr/local/bin/pomodoro-lock.py
sudo rm -rf /usr/local/share/pomodoro-lock
sudo rm -rf /etc/pomodoro-lock
sudo rm -f /usr/local/share/applications/pomodoro-lock.desktop
sudo rm -f /usr/local/bin/pomodoro-configure
sudo rm -f /usr/local/bin/pomodoro-start

# Remove all service files
sudo rm -f /etc/systemd/system/pomodoro-lock@*.service
sudo systemctl daemon-reload
```

## Advanced Usage

### Bulk User Management
```bash
# Add service for multiple users
for user in user1 user2 user3; do
    sudo ./scripts/manage-users.sh add $user
done

# Remove service for multiple users
for user in user1 user2 user3; do
    sudo ./scripts/manage-users.sh remove $user
done
```

### Custom Configuration
```bash
# Create custom configuration for specific user
sudo -u username mkdir -p /home/username/.local/share/pomodoro-lock/config/
sudo -u username nano /home/username/.local/share/pomodoro-lock/config/config.json
```

### Monitoring Scripts
```bash
# Monitor all services
watch "systemctl list-units --type=service | grep pomodoro-lock"

# Check service health
for service in /etc/systemd/system/pomodoro-lock@*.service; do
    username=$(basename $service | sed 's/pomodoro-lock@\(.*\)\.service/\1/')
    status=$(systemctl is-active pomodoro-lock@$username.service)
    echo "$username: $status"
done
```

---

For more information, see the main [README.md](README.md) and [docs/README.md](docs/README.md). 