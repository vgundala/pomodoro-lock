# Packaging Guide for Pomodoro Lock

**Copyright © 2024 Vinay Gundala (vg@ivdata.dev)**

This guide explains how to package Pomodoro Lock for different distribution methods.

## Table of Contents

1. [Packaging Options](#packaging-options)
2. [Build Commands](#build-commands)
3. [Package Contents](#package-contents)
4. [Customization](#customization)
5. [Distribution](#distribution)
6. [Testing Packages](#testing-packages)
7. [Version Management](#version-management)
8. [Recommendations](#recommendations)

## 📦 **Packaging Options**

### **1. Python Package (pip) - ✅ Ready**

The project is already configured for pip packaging with `setup.py`.

#### **Build Python Package**
```bash
# Install build tools
pip install build wheel

# Build the package
make package-pip
# or manually:
python3 setup.py sdist bdist_wheel
```

#### **Install Python Package**
```bash
# Install in development mode
make install-pip
# or manually:
pip install -e .

# Install from built package
pip install dist/pomodoro-lock-1.0.0.tar.gz
```

#### **Publish to PyPI**
```bash
# Install twine
pip install twine

# Upload to PyPI
twine upload dist/*
```

**Advantages:**
- ✅ Already configured
- ✅ Easy for Python developers
- ✅ Can be published to PyPI
- ✅ Automatic dependency management

**Limitations:**
- System dependencies still need manual installation
- Service files need separate installation
- Not ideal for end users who want a "one-click" install

### **2. Debian Package (.deb) - 🔧 Ready**

The project includes complete Debian packaging configuration.

#### **Prerequisites**
```bash
# Install build dependencies
sudo apt-get install build-essential devscripts debhelper dh-python python3-all python3-setuptools
```

#### **Build Debian Package**
```bash
# Build the package
make package-deb
# or manually:
dpkg-buildpackage -b -us -uc
```

#### **Install Debian Package**
```bash
# Install the built package
sudo dpkg -i ../pomodoro-lock_1.0.0-1_all.deb

# Fix any dependency issues
sudo apt-get install -f
```

**Advantages:**
- ✅ Complete system integration
- ✅ Automatic dependency resolution
- ✅ Professional installation experience
- ✅ Can be distributed via repositories
- ✅ Includes desktop integration

**Features:**
- Installs to system directories
- Creates desktop application entry
- Sets up systemd service
- Handles user configuration
- Includes documentation

### **3. AppImage - 🔧 Could Be Added**

For cross-distribution compatibility.

#### **Requirements**
```bash
# Install AppImage tools
sudo apt-get install appimagetool
```

#### **Build AppImage**
```bash
# Create AppDir structure
mkdir -p AppDir/usr/{bin,lib,share}

# Copy application files
cp -r src/* AppDir/usr/lib/
cp scripts/* AppDir/usr/bin/
cp config/* AppDir/usr/share/

# Create AppImage
appimagetool AppDir pomodoro-lock-x86_64.AppImage
```

### **4. Snap Package - 🔧 Could Be Added**

For Ubuntu and other snap-enabled distributions.

#### **Create snapcraft.yaml**
```yaml
name: pomodoro-lock
version: '1.0.0'
summary: Multi-display Pomodoro timer
description: |
  A comprehensive Pomodoro timer application with screen overlay functionality.

grade: stable
confinement: strict

apps:
  pomodoro-lock:
    command: pomodoro-lock
    plugs: [desktop, desktop-legacy, x11, unity7]

parts:
  pomodoro-lock:
    source: .
    plugin: python
    python-version: python3
    requirements: requirements.txt
```

## 🛠️ **Build Commands**

### **Quick Build Commands**
```bash
# Python package
make package-pip

# Debian package
make package-deb

# Clean build artifacts
make clean
```

### **Development Installation**
```bash
# Install in development mode
make install-pip

# Run tests
make test

# Start service
make start
```

## 📋 **Package Contents**

### **Python Package**
- Source code (`src/`)
- Configuration files (`config/`)
- Scripts (`scripts/`)
- Documentation (`docs/`)
- Dependencies (`requirements.txt`)

### **Debian Package**
- **Binary files**: `/usr/bin/pomodoro-configure`, `/usr/bin/pomodoro-start`
- **Library files**: `/usr/lib/python3/dist-packages/`
- **Configuration**: `/etc/pomodoro-lock/`
- **Service files**: `/etc/systemd/user/`
- **Documentation**: `/usr/share/doc/pomodoro-lock/`
- **Desktop file**: `/usr/share/applications/pomodoro-lock.desktop`

## 🔧 **Customization**

### **Modify Package Information**
- **Python**: Edit `setup.py`
- **Debian**: Edit `debian/control`, `debian/changelog`

### **Add Dependencies**
- **Python**: Add to `requirements.txt`
- **Debian**: Add to `Depends:` in `debian/control`

### **Change Installation Paths**
- **Python**: Modify `setup.py` package_data
- **Debian**: Modify `debian/rules`

## 📤 **Distribution**

### **Python Package**
1. Build: `make package-pip`
2. Test: `pip install dist/pomodoro-lock-1.0.0.tar.gz`
3. Upload: `twine upload dist/*`

### **Debian Package**
1. Build: `make package-deb`
2. Test: `sudo dpkg -i ../pomodoro-lock_1.0.0-1_all.deb`
3. Upload to repository or distribute `.deb` file

### **Repository Distribution**
```bash
# Create repository structure
mkdir -p repo/conf/
mkdir -p repo/db/

# Add package to repository
reprepro -b repo includedeb stable ../pomodoro-lock_1.0.0-1_all.deb
```

## 🧪 **Testing Packages**

### **Test Python Package**
```bash
# Create virtual environment
python3 -m venv test_env
source test_env/bin/activate

# Install package
pip install dist/pomodoro-lock-1.0.0.tar.gz

# Test functionality
pomodoro-lock --help
```

### **Test Debian Package**
```bash
# Install in clean environment
sudo dpkg -i ../pomodoro-lock_1.0.0-1_all.deb

# Test installation
pomodoro-configure --help
systemctl --user status pomodoro-lock.service

# Uninstall
sudo dpkg -r pomodoro-lock
```

## 📝 **Version Management**

### **Update Version**
1. **Python**: Update `setup.py` version
2. **Debian**: Update `debian/changelog`
3. **Documentation**: Update version references

### **Release Process**
```bash
# Update version numbers
# Build packages
make package-pip
make package-deb

# Test packages
# Tag release
git tag v1.0.0

# Upload to distribution channels
```

## 🎯 **Recommendations**

### **For End Users**
- **Debian Package**: Best for Ubuntu/Debian users
- **AppImage**: Best for cross-distribution compatibility
- **Snap**: Best for Ubuntu users who prefer snaps

### **For Developers**
- **Python Package**: Best for development and testing
- **Source Code**: Best for customization and contribution

### **For Distribution**
- **Debian Package**: Best for Linux distributions
- **PyPI**: Best for Python ecosystem integration

## 📞 **Contact Information**

### **Package Maintainer**
- **Author**: Vinay Gundala
- **Email**: [vg@ivdata.dev](mailto:vg@ivdata.dev)
- **GitHub**: [@vgundala](https://github.com/vgundala)

### **Project Links**
- **Repository**: [pomodoro-lock](https://github.com/vgundala/pomodoro-lock)
- **Issues**: [GitHub Issues](https://github.com/vgundala/pomodoro-lock/issues)
- **Documentation**: [docs/README.md](docs/README.md)

---

**Note**: The Debian package provides the most complete user experience as it handles all system integration automatically, while the Python package is better for developers and testing. 