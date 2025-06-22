# Troubleshooting Guide

## Externally-Managed-Environment Issues

### **Problem**: Modern Python installations prevent direct pip installs

**Error Message**:
```
ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory: '/usr/lib/python3.13/site-packages/pomodoro_lock-1.0.0-py3.13.egg-info'
error: externally-managed-environment
```

**Cause**: Modern Python installations (especially Ubuntu 22.04+, Debian 12+) have externally-managed-environment protection that prevents direct pip installs to system directories.

### **Solution**: Use the User-Friendly Installer

**✅ Recommended Solution**:
```bash
# Build and install with automatic handling
make package-pip
make install-pip-user
```

This installer automatically:
- Creates an isolated virtual environment
- Installs system dependencies (GTK bindings, etc.)
- Sets up desktop integration
- Creates a launcher script
- Handles all the complexity automatically

### **Alternative Solutions**

**For Developers (Manual Virtual Environment)**:
```bash
# Create virtual environment
python3 -m venv pomodoro-env
source pomodoro-env/bin/activate

# Install system dependencies
sudo apt-get install python3-gi python3-notify2

# Install the package
pip install dist/pomodoro_lock-1.0.0-py3-none-any.whl
```

**For System Administrators**:
```bash
# Disable externally-managed-environment (not recommended)
sudo mkdir -p /usr/lib/python3.13/site-packages
sudo touch /usr/lib/python3.13/site-packages/pomodoro_lock-1.0.0-py3.13.egg-info
```

### **Why This Happens**

Modern Python installations use PEP 668 to prevent conflicts between system package managers and pip. This is a security and stability feature, not a bug.

### **Best Practices**

1. **Always use `make install-pip-user`** for end-user installations
2. **Use virtual environments** for development
3. **Don't disable externally-managed-environment** unless absolutely necessary
4. **Consider using system packages** (Debian packages) for system-wide installations

## AppImage Build Issues

### 1. AppStream Validation Errors

**Problem**: AppImage build fails with AppStream validation errors:
```
✘ Validation failed: errors: 1, warnings: 1, infos: 1
run_external: subprocess exited with status 3Failed to validate AppStream information with appstreamcli
```

**Causes**:
- Invalid license format in `appdata.xml`
- Missing or incorrectly formatted developer information
- Invalid categories in desktop file
- Trailing spaces or invalid characters in metadata files

**Solutions**:

#### Option A: Fix AppStream Metadata (Recommended for Distribution)
1. **Update license format** in `AppDir/pomodoro-lock.appdata.xml`:
   ```xml
   <project_license>GPL-3.0-or-later</project_license>
   ```

2. **Add proper developer information**:
   ```xml
   <developer>
     <id>your-username</id>
     <name>Your Name</name>
   </developer>
   ```

3. **Use valid AppStream categories**:
   ```xml
   <categories>
     <category>Utility</category>
     <category>Office</category>
   </categories>
   ```

4. **Clean up desktop file** - remove trailing spaces and invalid characters

#### Option B: Bypass AppStream Validation (Quick Fix)
1. **Comment out appdata.xml copying** in `scripts/build-appimage.sh`:
   ```bash
   # cp AppDir/pomodoro-lock.appdata.xml "$BUILD_DIR/AppDir/usr/share/metainfo/"
   ```

2. **Use --no-appstream flag** (if supported):
   ```bash
   "$APPIMAGETOOL" --no-appstream "$BUILD_DIR/AppDir" "$APPIMAGE_NAME"
   ```

### 2. Icon Issues

**Problem**: Missing icon files or wrong icon format

**Solutions**:
1. **Ensure SVG icon exists** at `AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.svg`
2. **Copy SVG to AppDir root** for appimagetool:
   ```bash
   cp AppDir/usr/share/icons/hicolor/256x256/apps/pomodoro-lock.svg "$BUILD_DIR/AppDir/pomodoro-lock.svg"
   ```
3. **Remove PNG generation** if only using SVG icons

### 3. Desktop File Validation Errors

**Problem**: Desktop file has invalid format or characters

**Common Issues**:
- Trailing spaces after values
- Invalid boolean values (should be `true`/`false`, not `True`/`False`)
- Invalid categories
- Missing required fields

**Solution**: Clean desktop file format:
```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Pomodoro Lock
Comment=Multi-display Pomodoro timer with screen overlay
Exec=pomodoro-lock
Icon=pomodoro-lock
Terminal=false
Categories=Utility;Office;
Keywords=pomodoro;timer;productivity;focus;
```

### 4. AppImage Tool Execution Errors

**Problem**: 
```
[appimagelauncher-binfmt-bypass/interpreter] ERROR: execv(...) failed
```

**Causes**:
- Invalid command line arguments
- Corrupted appimagetool download
- Permission issues

**Solutions**:
1. **Check appimagetool help**:
   ```bash
   ./build-appimage/appimagetool --help
   ```

2. **Re-download appimagetool**:
   ```bash
   rm build-appimage/appimagetool
   # Re-run build to download fresh copy
   ```

3. **Verify file permissions**:
   ```bash
   chmod +x build-appimage/appimagetool
   ```

### 5. Dependency Issues

**Problem**: Missing system dependencies for PyGObject

**Solution**: Install required packages:
```bash
sudo apt-get install -y libcairo2-dev pkg-config libgirepository-2.0-dev gir1.2-gtk-3.0
```

### 6. Python Package Installation Issues

**Problem**: Python dependencies fail to install

**Solutions**:
1. **Use virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --target="$BUILD_DIR/AppDir/usr/lib/python3/dist-packages" psutil python-xlib notify2 PyGObject
   ```

2. **Check Python version compatibility**:
   ```bash
   python3 --version
   ```

## Build Process Checklist

### Before Building
- [ ] SVG icon exists and is valid
- [ ] Desktop file is properly formatted
- [ ] System dependencies are installed
- [ ] Python environment is ready

### During Build
- [ ] Check for AppStream validation errors
- [ ] Verify icon copying to AppDir root
- [ ] Confirm Python packages install successfully
- [ ] Monitor appimagetool execution

### After Build
- [ ] Test AppImage execution
- [ ] Verify icon appears correctly
- [ ] Check desktop integration
- [ ] Test on different systems if possible

## Common Commands

### Debug AppImage Build
```bash
# Check appimagetool version and options
./build-appimage/appimagetool --help

# Validate appdata.xml manually
appstreamcli validate AppDir/pomodoro-lock.appdata.xml

# Check desktop file syntax
desktop-file-validate AppDir/pomodoro-lock.desktop

# List AppImage contents
./build-appimage/appimagetool -l Pomodoro_Lock-1.0.0-x86_64.AppImage
```

### Clean Build
```bash
# Remove build artifacts
rm -rf build-appimage/
rm -f Pomodoro_Lock-*.AppImage

# Rebuild from scratch
make package-appimage
```

## Prevention Tips

1. **Use consistent icon formats** - Stick to SVG for scalability
2. **Validate metadata early** - Test appdata.xml and desktop files before building
3. **Keep dependencies minimal** - Only include necessary Python packages
4. **Test on clean systems** - Verify AppImage works on fresh installations
5. **Document changes** - Keep track of what fixes work for future reference

## Resources

- [AppImage Documentation](https://docs.appimage.org/)
- [AppStream Specification](https://www.freedesktop.org/software/appstream/docs/)
- [Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html)
- [AppImageKit Repository](https://github.com/AppImage/AppImageKit) 