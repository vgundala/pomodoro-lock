#!/bin/bash

# Exit on error
set -e

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run as root"
    exit 1
fi

# Get current user
CURRENT_USER=$(whoami)
USER_ID=$(id -u)

echo "Installing Pomodoro Lock for user: $CURRENT_USER (UID: $USER_ID)"
echo "This installation requires no sudo privileges!"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a Python module is available
python_module_exists() {
    python3 -c "import $1" >/dev/null 2>&1
}

# Create necessary directories
mkdir -p ~/.local/share/pomodoro-lock/{bin,config,scripts}
mkdir -p ~/.local/bin

# Check what's available for dependency installation
echo "Checking available installation methods..."

# Check if virtual environment is available
if command_exists python3 && python3 -m venv --help >/dev/null 2>&1; then
    VENV_AVAILABLE=true
    echo "✓ Python virtual environment available"
else
    VENV_AVAILABLE=false
    echo "✗ Python virtual environment not available"
fi

# Check if pipx is available
if command_exists pipx; then
    PIPX_AVAILABLE=true
    echo "✓ pipx available"
else
    PIPX_AVAILABLE=false
    echo "✗ pipx not available"
fi

# Check if pip is available
if command_exists pip3; then
    PIP_AVAILABLE=true
    echo "✓ pip3 available"
else
    PIP_AVAILABLE=false
    echo "✗ pip3 not available"
fi

# Check if system packages are already installed
echo "Checking for existing Python packages..."
EXISTING_PACKAGES=()
if python_module_exists gi; then
    EXISTING_PACKAGES+=("PyGObject")
    echo "✓ PyGObject already available"
fi
if python_module_exists psutil; then
    EXISTING_PACKAGES+=("psutil")
    echo "✓ psutil already available"
fi
if python_module_exists Xlib; then
    EXISTING_PACKAGES+=("python-xlib")
    echo "✓ python-xlib already available"
fi
if python_module_exists notify2; then
    EXISTING_PACKAGES+=("notify2")
    echo "✓ notify2 already available"
fi

# Determine installation method
INSTALL_METHOD=""
if [ "$VENV_AVAILABLE" = true ]; then
    INSTALL_METHOD="venv"
    echo "Using virtual environment installation method"
elif [ "$PIPX_AVAILABLE" = true ]; then
    INSTALL_METHOD="pipx"
    echo "Using pipx installation method"
elif [ "$PIP_AVAILABLE" = true ]; then
    INSTALL_METHOD="pip"
    echo "Using pip installation method"
elif [ ${#EXISTING_PACKAGES[@]} -eq 4 ]; then
    INSTALL_METHOD="existing"
    echo "All required packages already available"
else
    INSTALL_METHOD="manual"
    echo "Manual installation required"
fi

# Install dependencies based on available method
case $INSTALL_METHOD in
    "venv")
        echo "Creating virtual environment..."
        python3 -m venv ~/.local/share/pomodoro-lock/venv
        
        echo "Installing Python dependencies in virtual environment..."
        source ~/.local/share/pomodoro-lock/venv/bin/activate
        pip install psutil python-xlib notify2 PyGObject
        
        # Create convenience scripts that use the virtual environment
        echo "Creating convenience scripts..."
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
        
        # Update the start script to use the virtual environment
        echo "Updating start script to use virtual environment..."
        sed -i '1a source ~/.local/share/pomodoro-lock/venv/bin/activate' ~/.local/share/pomodoro-lock/start-pomodoro.sh
        ;;
        
    "pipx")
        echo "Installing dependencies via pipx..."
        pipx install psutil python-xlib notify2 PyGObject
        ;;
        
    "pip")
        echo "Installing dependencies via pip..."
        if python3 -m pip --version >/dev/null 2>&1; then
            python3 -m pip install --user --break-system-packages psutil python-xlib notify2 PyGObject
        else
            pip3 install --user --break-system-packages psutil python-xlib notify2 PyGObject
        fi
        ;;
        
    "existing")
        echo "All required packages already available, skipping dependency installation"
        ;;
        
    "manual")
        echo ""
        echo "❌ Installation cannot proceed!"
        echo ""
        echo "Your system doesn't have the necessary tools to install Python packages."
        echo "These are required dependencies that must be installed first:"
        echo ""
        echo "📦 Required Python packages:"
        echo "  - python3-gi (GTK3 bindings)"
        echo "  - python3-psutil (process utilities)"
        echo "  - python3-xlib (X11 bindings)"
        echo "  - python3-notify2 (notifications)"
        echo ""
        echo "🔧 Installation options:"
        echo ""
        echo "Option 1: Contact your system administrator"
        echo "  Ask them to install: sudo apt-get install python3-gi python3-psutil python3-xlib python3-notify2"
        echo "  Or: sudo apt-get install python3-pip python3-venv"
        echo ""
        echo "Option 2: Use alternative installation method"
        echo "  make install-user-robust  # Try automatic detection again"
        echo "  make install-user         # pip-based installation"
        echo "  make install              # Traditional installation (may require sudo)"
        echo ""
        echo "Option 3: Check what's available on your system"
        echo "  make check-deps"
        echo ""
        echo "After installing the required dependencies, run this installer again."
        echo ""
        exit 1
        ;;
esac

# Copy files to their locations
echo "Installing Pomodoro Lock..."
cp src/pomodoro-lock.py ~/.local/share/pomodoro-lock/bin/
chmod +x ~/.local/share/pomodoro-lock/bin/pomodoro-lock.py

# Copy startup script
cp scripts/start-pomodoro.sh ~/.local/share/pomodoro-lock/
chmod +x ~/.local/share/pomodoro-lock/start-pomodoro.sh

# Copy default config if it doesn't exist
if [ ! -f ~/.local/share/pomodoro-lock/config/config.json ]; then
    echo "Creating default configuration..."
    cp config/config.json ~/.local/share/pomodoro-lock/config/
fi

# Copy configuration script
cp scripts/configure-pomodoro.py ~/.local/share/pomodoro-lock/
chmod +x ~/.local/share/pomodoro-lock/configure-pomodoro.py

# Create convenience scripts if not already created by venv method
if [ "$INSTALL_METHOD" != "venv" ]; then
    echo "Creating convenience scripts..."
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
fi

# Choose service file based on environment
echo "Detecting desktop environment..."
if [ -n "$XDG_CURRENT_DESKTOP" ]; then
    echo "Desktop environment: $XDG_CURRENT_DESKTOP"
    SERVICE_FILE="config/pomodoro-lock.service"
else
    echo "No specific desktop environment detected, using simple service"
    SERVICE_FILE="config/pomodoro-lock-simple.service"
fi

# Install systemd service
echo "Installing systemd service: $SERVICE_FILE"
mkdir -p ~/.config/systemd/user/
cp "$SERVICE_FILE" ~/.config/systemd/user/pomodoro-lock.service

# Update the service file with correct user and paths
sed -i "s/User=vinay/User=$CURRENT_USER/g" ~/.config/systemd/user/pomodoro-lock.service
sed -i "s|/home/vinay|/home/$CURRENT_USER|g" ~/.config/systemd/user/pomodoro-lock.service
sed -i "s|/run/user/1000|/run/user/$USER_ID|g" ~/.config/systemd/user/pomodoro-lock.service

# Reload systemd and enable service
systemctl --user daemon-reload
systemctl --user enable pomodoro-lock.service

# Start the service automatically
echo "Starting Pomodoro Lock service..."
systemctl --user start pomodoro-lock.service

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Service Management Commands:"
echo "  Start service:     systemctl --user start pomodoro-lock.service"
echo "  Stop service:      systemctl --user stop pomodoro-lock.service"
echo "  Check status:      systemctl --user status pomodoro-lock.service"
echo "  View logs:         journalctl --user -u pomodoro-lock.service -f"
echo ""
echo "Convenience Commands:"
echo "  Run directly:      pomodoro-lock"
echo "  Configure:         pomodoro-configure"
echo ""
echo "Configuration:"
echo "  Config file:       ~/.local/share/pomodoro-lock/config/config.json"
echo "  Log file:          ~/.local/share/pomodoro-lock/pomodoro.log"

if [ "$INSTALL_METHOD" = "venv" ]; then
    echo "  Virtual env:       ~/.local/share/pomodoro-lock/venv/"
fi

echo ""
echo "The service is now running and will start automatically on login."
echo ""
echo "Note: If ~/.local/bin is not in your PATH, add it to your shell profile:"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\"" 