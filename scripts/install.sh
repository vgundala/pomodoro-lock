#!/bin/bash

# Pomodoro Lock - Smart Installer
# Automatically chooses the best installation method for your system
# Copyright © 2024 Vinay Gundala (vg@ivdata.dev)

set -e

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run as root"
    exit 1
fi

# Get current user
CURRENT_USER=$(whoami)
USER_ID=$(id -u)

echo "🚀 Pomodoro Lock - Smart Installer"
echo "=================================="
echo "User: $CURRENT_USER (UID: $USER_ID)"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a Python module is available
python_module_exists() {
    python3 -c "import $1" >/dev/null 2>&1
}

# Check what's available on the system
echo "🔍 Analyzing system capabilities..."

VENV_AVAILABLE=false
PIP_AVAILABLE=false
EXISTING_COUNT=0

# Check virtual environment support
if python3 -m venv --help >/dev/null 2>&1; then
    VENV_AVAILABLE=true
    echo "✅ Virtual environment support available"
else
    echo "❌ Virtual environment support not available"
fi

# Check pip availability
if python3 -m pip --version >/dev/null 2>&1; then
    PIP_AVAILABLE=true
    echo "✅ pip available"
elif command_exists pip3; then
    PIP_AVAILABLE=true
    echo "✅ pip3 available"
else
    echo "❌ pip not available"
fi

# Check existing packages
echo ""
echo "📦 Checking existing packages..."
if python_module_exists gi; then
    echo "✅ PyGObject (gi): Available"
    EXISTING_COUNT=$(expr $EXISTING_COUNT + 1)
else
    echo "❌ PyGObject (gi): Not found"
fi

if python_module_exists psutil; then
    echo "✅ psutil: Available"
    EXISTING_COUNT=$(expr $EXISTING_COUNT + 1)
else
    echo "❌ psutil: Not found"
fi

if python_module_exists Xlib; then
    echo "✅ python-xlib: Available"
    EXISTING_COUNT=$(expr $EXISTING_COUNT + 1)
else
    echo "❌ python-xlib: Not found"
fi

if python_module_exists notify2; then
    echo "✅ notify2: Available"
    EXISTING_COUNT=$(expr $EXISTING_COUNT + 1)
else
    echo "❌ notify2: Not found"
fi

# Determine installation strategy
echo ""
echo "🎯 Installation Strategy:"

if [ $EXISTING_COUNT -eq 4 ]; then
    echo "✅ All packages available - proceeding with direct installation"
    INSTALL_STRATEGY="existing"
elif [ "$VENV_AVAILABLE" = true ]; then
    echo "✅ Using virtual environment (recommended for isolation)"
    INSTALL_STRATEGY="venv"
elif [ "$PIP_AVAILABLE" = true ]; then
    echo "⚠️  Using pip (may require --break-system-packages)"
    INSTALL_STRATEGY="pip"
else
    echo "❌ No suitable installation method found"
    echo ""
    echo "Your system doesn't have the necessary tools to install Python packages."
    echo "Please contact your system administrator to install:"
    echo "  sudo apt-get install python3-pip python3-venv"
    echo ""
    echo "Or try the robust installer:"
    echo "  make install-user-robust"
    echo ""
    exit 1
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p ~/.local/share/pomodoro-lock/{bin,config,scripts}
mkdir -p ~/.local/bin

# Install dependencies based on strategy
case $INSTALL_STRATEGY in
    "venv")
        echo ""
        echo "🐍 Creating virtual environment..."
        python3 -m venv ~/.local/share/pomodoro-lock/venv
        
        echo "📦 Installing packages in virtual environment..."
        source ~/.local/share/pomodoro-lock/venv/bin/activate
        pip install psutil python-xlib notify2 PyGObject
        
        # Create convenience scripts
        echo "🔧 Creating convenience scripts..."
        cat > ~/.local/bin/pomodoro-lock << 'EOF'
#!/bin/bash
source ~/.local/share/pomodoro-lock/venv/bin/activate
exec python3 ~/.local/share/pomodoro-lock/bin/pomodoro-lock.py "$@"
EOF

        cat > ~/.local/bin/pomodoro-configure << 'EOF'
#!/bin/bash
source ~/.local/share/pomodoro-lock/venv/bin/activate
exec python3 ~/.local/share/pomodoro-lock/configure-pomodoro.py "$@"
EOF

        chmod +x ~/.local/bin/pomodoro-lock
        chmod +x ~/.local/bin/pomodoro-configure
        
        # Update start script to use venv
        echo "📝 Updating start script..."
        sed -i '1a source ~/.local/share/pomodoro-lock/venv/bin/activate' ~/.local/share/pomodoro-lock/start-pomodoro.sh
        ;;
        
    "pip")
        echo ""
        echo "📦 Installing packages via pip..."
        if python3 -m pip --version >/dev/null 2>&1; then
            python3 -m pip install --user --break-system-packages psutil python-xlib notify2 PyGObject
        else
            pip3 install --user --break-system-packages psutil python-xlib notify2 PyGObject
        fi
        
        # Create convenience scripts
        echo "🔧 Creating convenience scripts..."
        cat > ~/.local/bin/pomodoro-lock << 'EOF'
#!/bin/bash
exec python3 ~/.local/share/pomodoro-lock/bin/pomodoro-lock.py "$@"
EOF

        cat > ~/.local/bin/pomodoro-configure << 'EOF'
#!/bin/bash
exec python3 ~/.local/share/pomodoro-lock/configure-pomodoro.py "$@"
EOF

        chmod +x ~/.local/bin/pomodoro-lock
        chmod +x ~/.local/bin/pomodoro-configure
        ;;
        
    "existing")
        echo ""
        echo "✅ All packages already available, skipping dependency installation"
        
        # Create convenience scripts
        echo "🔧 Creating convenience scripts..."
        cat > ~/.local/bin/pomodoro-lock << 'EOF'
#!/bin/bash
exec python3 ~/.local/share/pomodoro-lock/bin/pomodoro-lock.py "$@"
EOF

        cat > ~/.local/bin/pomodoro-configure << 'EOF'
#!/bin/bash
exec python3 ~/.local/share/pomodoro-lock/configure-pomodoro.py "$@"
EOF

        chmod +x ~/.local/bin/pomodoro-lock
        chmod +x ~/.local/bin/pomodoro-configure
        ;;
esac

# Copy application files
echo ""
echo "📋 Installing application files..."
cp src/pomodoro-lock.py ~/.local/share/pomodoro-lock/bin/
chmod +x ~/.local/share/pomodoro-lock/bin/pomodoro-lock.py

cp scripts/start-pomodoro.sh ~/.local/share/pomodoro-lock/
chmod +x ~/.local/share/pomodoro-lock/start-pomodoro.sh

if [ ! -f ~/.local/share/pomodoro-lock/config/config.json ]; then
    echo "📄 Creating default configuration..."
    cp config/config.json ~/.local/share/pomodoro-lock/config/
fi

cp scripts/configure-pomodoro.py ~/.local/share/pomodoro-lock/
chmod +x ~/.local/share/pomodoro-lock/configure-pomodoro.py

# Choose service file based on environment
echo ""
echo "🔧 Installing systemd service..."
mkdir -p ~/.config/systemd/user/

if [ -n "$XDG_CURRENT_DESKTOP" ]; then
    echo "Desktop environment: $XDG_CURRENT_DESKTOP"
    SERVICE_FILE="config/pomodoro-lock.service"
else
    echo "No specific desktop environment detected, using simple service"
    SERVICE_FILE="config/pomodoro-lock-simple.service"
fi

cp "$SERVICE_FILE" ~/.config/systemd/user/pomodoro-lock.service

# Update service file paths
sed -i "s/User=vinay/User=$CURRENT_USER/g" ~/.config/systemd/user/pomodoro-lock.service
sed -i "s|/home/vinay|/home/$CURRENT_USER|g" ~/.config/systemd/user/pomodoro-lock.service
sed -i "s|/run/user/1000|/run/user/$USER_ID|g" ~/.config/systemd/user/pomodoro-lock.service

# Enable and start service
systemctl --user daemon-reload
systemctl --user enable pomodoro-lock.service

echo ""
echo "🚀 Starting service..."
systemctl --user start pomodoro-lock.service

# Final output
echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "✅ Pomodoro Lock has been installed successfully!"
echo ""
echo "📋 Service Management:"
echo "  Start:   systemctl --user start pomodoro-lock.service"
echo "  Stop:    systemctl --user stop pomodoro-lock.service"
echo "  Status:  systemctl --user status pomodoro-lock.service"
echo "  Logs:    journalctl --user -u pomodoro-lock.service -f"
echo ""
echo "🔧 Convenience Commands:"
echo "  Run:     pomodoro-lock"
echo "  Config:  pomodoro-configure"
echo ""
echo "📁 Files:"
echo "  Config:  ~/.local/share/pomodoro-lock/config/config.json"
echo "  Logs:    ~/.local/share/pomodoro-lock/pomodoro.log"

if [ "$INSTALL_STRATEGY" = "venv" ]; then
    echo "  Venv:   ~/.local/share/pomodoro-lock/venv/"
fi

echo ""
echo "⚠️  Important Notes:"
if [ "$INSTALL_STRATEGY" = "pip" ]; then
    echo "  - Packages were installed with --break-system-packages"
    echo "  - This may conflict with system packages"
fi

echo "  - Add ~/.local/bin to your PATH if not already there:"
echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "🌐 The service will start automatically on login."
echo ""
echo "❓ Need help? Check: https://github.com/vgundala/pomodoro-lock#readme" 