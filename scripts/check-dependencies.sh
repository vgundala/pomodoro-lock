#!/bin/bash

# Dependency checker for Pomodoro Lock
# This script checks what's available and provides installation guidance

echo "🔍 Checking Pomodoro Lock dependencies..."
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a Python module is available
python_module_exists() {
    python3 -c "import $1" >/dev/null 2>&1
}

# Check Python availability
echo "📋 System Requirements:"
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "✓ Python3: $PYTHON_VERSION"
else
    echo "✗ Python3: Not found"
    echo "   Install with: sudo apt-get install python3"
    PYTHON_MISSING=true
fi

# Check package managers
echo ""
echo "📦 Package Managers:"
if command_exists pip3; then
    echo "✓ pip3: Available"
    PIP3_AVAILABLE=true
else
    echo "✗ pip3: Not found"
    PIP3_AVAILABLE=false
fi

if command_exists python3 && python3 -m pip --version >/dev/null 2>&1; then
    echo "✓ python3 -m pip: Available"
    PYTHON_PIP_AVAILABLE=true
else
    echo "✗ python3 -m pip: Not found"
    PYTHON_PIP_AVAILABLE=false
fi

if command_exists pipx; then
    echo "✓ pipx: Available"
    PIPX_AVAILABLE=true
else
    echo "✗ pipx: Not found"
    PIPX_AVAILABLE=false
fi

# Check virtual environment support
echo ""
echo "🐍 Virtual Environment Support:"
if command_exists python3 && python3 -m venv --help >/dev/null 2>&1; then
    echo "✓ python3 -m venv: Available"
    VENV_AVAILABLE=true
else
    echo "✗ python3 -m venv: Not found"
    echo "   Install with: sudo apt-get install python3-venv"
    VENV_AVAILABLE=false
fi

# Check existing Python packages
echo ""
echo "📚 Required Python Packages:"
MISSING_PACKAGES=()

if python_module_exists gi; then
    echo "✓ PyGObject (gi): Available"
else
    echo "✗ PyGObject (gi): Not found"
    MISSING_PACKAGES+=("PyGObject")
fi

if python_module_exists psutil; then
    echo "✓ psutil: Available"
else
    echo "✗ psutil: Not found"
    MISSING_PACKAGES+=("psutil")
fi

if python_module_exists Xlib; then
    echo "✓ python-xlib: Available"
else
    echo "✗ python-xlib: Not found"
    MISSING_PACKAGES+=("python-xlib")
fi

if python_module_exists notify2; then
    echo "✓ notify2: Available"
else
    echo "✗ notify2: Not found"
    MISSING_PACKAGES+=("notify2")
fi

# Determine installation method
echo ""
echo "🎯 Recommended Installation Method:"

if [ "$PYTHON_MISSING" = true ]; then
    echo "❌ Python3 is required but not installed."
    echo "   Please install Python3 first:"
    echo "   sudo apt-get install python3"
    exit 1
fi

if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
    echo "✅ All required packages are already available!"
    echo "   You can proceed with installation."
    RECOMMENDED_METHOD="existing"
elif [ "$VENV_AVAILABLE" = true ]; then
    echo "✅ Virtual Environment (Recommended)"
    echo "   Use: make install-user-venv"
    echo "   This creates an isolated environment with all dependencies."
    RECOMMENDED_METHOD="venv"
elif [ "$PIPX_AVAILABLE" = true ]; then
    echo "✅ pipx (Alternative)"
    echo "   Use: make install-user"
    echo "   This installs packages in isolated environments."
    RECOMMENDED_METHOD="pipx"
elif [ "$PYTHON_PIP_AVAILABLE" = true ] || [ "$PIP3_AVAILABLE" = true ]; then
    echo "⚠️  pip (Use with caution)"
    echo "   Use: make install-user"
    echo "   This may conflict with system packages."
    RECOMMENDED_METHOD="pip"
else
    echo "❌ No package manager available"
    echo "   Manual installation required."
    RECOMMENDED_METHOD="manual"
fi

# Provide installation instructions
echo ""
echo "📖 Installation Instructions:"

case $RECOMMENDED_METHOD in
    "existing")
        echo "All dependencies are available. You can install with:"
        echo "  make install"
        ;;
    "venv")
        echo "Install using virtual environment (recommended):"
        echo "  make install-user-venv"
        ;;
    "pipx")
        echo "Install using pipx:"
        echo "  make install-user"
        ;;
    "pip")
        echo "Install using pip:"
        echo "  make install-user"
        echo ""
        echo "Note: This may require --break-system-packages flag."
        ;;
    "manual")
        echo "Manual installation required. Install these packages first:"
        echo ""
        echo "Option 1: Contact your system administrator"
        echo "  Ask them to install: sudo apt-get install python3-gi python3-psutil python3-xlib python3-notify2"
        echo "  Or: sudo apt-get install python3-pip python3-venv"
        echo ""
        echo "Option 2: Install system packages (requires sudo)"
        echo "  sudo apt-get update"
        echo "  sudo apt-get install python3-gi python3-psutil python3-xlib python3-notify2"
        echo ""
        echo "Option 3: Install python3-venv for virtual environment (requires sudo)"
        echo "  sudo apt-get install python3-venv"
        echo ""
        echo "Then run installation:"
        echo "  make install-user-venv"
        ;;
esac

echo ""
echo "🔧 Alternative Installation Methods:"
echo "  make install-user-robust  - Automatic detection and installation"
echo "  make install              - Traditional installation (may require sudo for deps)"
echo "  make install-system       - System-wide installation (requires sudo)"

echo ""
echo "❓ Need help? Check the documentation:"
echo "  https://github.com/vgundala/pomodoro-lock#readme" 