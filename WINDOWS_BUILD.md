# Windows Build Guide

This document explains how to build the Windows executable for Pomodoro Lock using PyInstaller.

## Prerequisites

### Required Software
- **Python 3.11+** (recommended)
- **PyInstaller** (`pip install pyinstaller`)
- **Windows 10/11** (for building and testing)

### Python Dependencies
Install the required Python packages:
```bash
pip install -r requirements-crossplatform.txt
pip install pyinstaller
```

### Windows-Specific Dependencies
The following packages are required for Windows functionality:
```bash
pip install win10toast pystray pillow pywin32
```

## Build Process

### 1. Basic Build
```bash
# Navigate to the project directory
cd pomodoro-lock

# Build using the spec file
pyinstaller pomodoro-lock.spec
```

### 2. Build Options
```bash
# Build with debug information
pyinstaller --debug=all pomodoro-lock.spec

# Build without UPX compression (larger file, faster startup)
pyinstaller --upx-dir="" pomodoro-lock.spec

# Build with console window (for debugging)
pyinstaller --console pomodoro-lock.spec
```

### 3. Output Location
The built executable will be in:
```
dist/pomodoro-lock.exe
```

## PyInstaller Configuration

### Spec File Overview
The `pomodoro-lock.spec` file contains:

1. **Platform Detection**: Automatically detects Windows vs Linux
2. **Hidden Imports**: Includes all required modules
3. **Data Files**: Platform-specific data files
4. **Executable Settings**: GUI mode, icon, compression

### Key Configuration Options

#### Hidden Imports (Windows)
```python
hidden_imports = [
    'psutil',           # Process management
    'win10toast',       # Windows 10 notifications
    'pystray',          # System tray
    'PIL',              # Image processing
    'win32api',         # Windows API
    'win32con',         # Windows constants
    'win32gui',         # Windows GUI
    'win32process',     # Windows process management
]
```

#### Executable Settings
```python
exe = EXE(
    # ... other settings ...
    console=False,      # GUI application (no console window)
    icon='pomodoro-lock-24.png',  # Application icon
    upx=True,           # Enable UPX compression
)
```

## Testing the Build

### 1. Basic Testing
```bash
# Run the executable
./dist/pomodoro-lock.exe
```

### 2. Feature Testing
Test the following Windows-specific features:
- **System Tray**: Right-click the tray icon
- **Notifications**: Windows 10 toast notifications
- **Window Management**: Minimize/restore from tray
- **Single Instance**: Try running multiple instances

### 3. Compatibility Testing
Test on:
- Windows 10 (recommended)
- Windows 11
- Different screen resolutions
- Different DPI settings

## Troubleshooting

### Common Build Issues

#### 1. Missing Dependencies
**Error**: `ModuleNotFoundError: No module named 'win10toast'`

**Solution**:
```bash
pip install win10toast pystray pillow pywin32
```

#### 2. PyInstaller Not Found
**Error**: `'pyinstaller' is not recognized`

**Solution**:
```bash
pip install pyinstaller
# Or use Python module syntax
python -m PyInstaller pomodoro-lock.spec
```

#### 3. Icon File Missing
**Error**: `Icon file not found`

**Solution**:
```bash
# Ensure icon file exists
ls pomodoro-lock-24.png

# Or remove icon from spec file
# icon=None
```

#### 4. Large Executable Size
**Problem**: Executable is very large (>100MB)

**Solutions**:
```bash
# Use UPX compression (default)
pyinstaller pomodoro-lock.spec

# Exclude unnecessary modules
# Edit spec file to add excludes=['unused_module']
```

### Runtime Issues

#### 1. Tray Icon Not Appearing
**Problem**: System tray icon doesn't show

**Solutions**:
- Check Windows notification settings
- Ensure pystray is properly installed
- Test with different Windows versions

#### 2. Notifications Not Working
**Problem**: Windows toast notifications don't appear

**Solutions**:
- Check Windows notification permissions
- Ensure win10toast is installed
- Test notification settings in Windows

#### 3. Permission Errors
**Problem**: Access denied errors

**Solutions**:
- Run as administrator if needed
- Check file permissions
- Ensure antivirus isn't blocking

## Distribution

### 1. Single Executable
The built `pomodoro-lock.exe` is a standalone executable that includes:
- Python interpreter
- All required libraries
- Application code
- Icons and resources

### 2. Installation Package
For distribution, consider creating an installer:
- **NSIS**: Create Windows installer
- **Inno Setup**: Alternative installer
- **Microsoft Store**: For Windows Store distribution

### 3. GitHub Actions
The Windows executable is automatically built by GitHub Actions:
- Triggered by version tags (`v1.3.7`)
- Built on Windows runners
- Included in GitHub releases

## Build Scripts

### Automated Build Script
Create a `build-windows.bat` script:
```batch
@echo off
echo Building Windows executable...
pyinstaller pomodoro-lock.spec
echo Build complete: dist/pomodoro-lock.exe
pause
```

### PowerShell Script
Create a `build-windows.ps1` script:
```powershell
Write-Host "Building Windows executable..."
pyinstaller pomodoro-lock.spec
if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful: dist/pomodoro-lock.exe"
} else {
    Write-Host "Build failed!"
}
```

## Performance Optimization

### 1. Reduce Executable Size
```bash
# Use UPX compression
pyinstaller --upx-dir=/path/to/upx pomodoro-lock.spec

# Exclude unnecessary modules
# Edit spec file to add excludes
```

### 2. Improve Startup Time
```bash
# Disable UPX compression (larger but faster startup)
pyinstaller --upx-dir="" pomodoro-lock.spec

# Use --onefile for single executable
pyinstaller --onefile pomodoro-lock.spec
```

### 3. Debug Builds
```bash
# Include debug information
pyinstaller --debug=all pomodoro-lock.spec

# Enable console for debugging
pyinstaller --console pomodoro-lock.spec
```

## Best Practices

1. **Test on Clean Systems**: Test the executable on fresh Windows installations
2. **Version Compatibility**: Test on multiple Windows versions
3. **Dependency Management**: Keep dependencies minimal and up-to-date
4. **Error Handling**: Include proper error handling in the application
5. **User Experience**: Ensure the app works well with Windows UI guidelines

## Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [Windows API Documentation](https://docs.microsoft.com/en-us/windows/win32/)
- [PyWin32 Documentation](https://github.com/mhammond/pywin32)
- [PyStray Documentation](https://github.com/moses-palmer/pystray)
- [Win10Toast Documentation](https://github.com/jithurjacob/Windows-10-Toast-Notifications) 