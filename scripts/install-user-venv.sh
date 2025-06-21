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
echo "This installation uses a virtual environment (no sudo required)!"

# Create necessary directories
mkdir -p ~/.local/share/pomodoro-lock/{bin,config,scripts,venv}
mkdir -p ~/.local/bin

# Create virtual environment
echo "Creating virtual environment..."
if python3 -m venv --help >/dev/null 2>&1; then
    python3 -m venv ~/.local/share/pomodoro-lock/venv
else
    echo ""
    echo "❌ Installation cannot proceed!"
    echo ""
    echo "Python virtual environment support is not available on your system."
    echo "This is required for isolated installation without sudo privileges."
    echo ""
    echo "📦 Required system package:"
    echo "  - python3-venv (Python virtual environment support)"
    echo ""
    echo "🔧 Resolution options:"
    echo ""
    echo "Option 1: Contact your system administrator"
    echo "  Ask them to install: sudo apt-get install python3-venv"
    echo ""
    echo "Option 2: Use alternative installation method"
    echo "  make install-user-robust  # Automatic detection and installation"
    echo "  make install-user         # pip-based installation"
    echo "  make install              # Traditional installation (may require sudo)"
    echo ""
    echo "Option 3: Check what's available on your system"
    echo "  make check-deps"
    echo ""
    echo "After python3-venv is installed, run this installer again."
    echo ""
    exit 1
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies in virtual environment..."
source ~/.local/share/pomodoro-lock/venv/bin/activate
pip install psutil python-xlib notify2 PyGObject

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

# Create convenience scripts in ~/.local/bin that use the virtual environment
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

echo "Installation complete!"
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
echo "  Virtual env:       ~/.local/share/pomodoro-lock/venv/"
echo ""
echo "The service is now running and will start automatically on login."
echo ""
echo "Note: If ~/.local/bin is not in your PATH, add it to your shell profile:"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\"" 