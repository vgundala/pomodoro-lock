# Pomodoro Lock Makefile - Service-Based Architecture

.PHONY: help install install-and-start test test-all clean uninstall configure package-deb

# Default target
help:
	@echo "Pomodoro Lock - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  make install          - Install using new service-based architecture"
	@echo "  make install-and-start - Install and automatically start the service"
	@echo ""
	@echo "Dependency Management:"
	@echo "  make check-deps       - Check system dependencies and provide guidance"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-notification - Test notifications"
	@echo "  make test-overlay     - Test overlay functionality"
	@echo "  make test-timer       - Test timer widget"
	@echo "  make test-multi       - Test multi-display overlay"
	@echo "  make test-workflow    - Test complete workflow (1min work, 30sec break)"
	@echo "  make test-quick       - Quick test for packaging (1 minute 30 seconds overlay test)"
	@echo "  make test-system-tray - Test system tray functionality"
	@echo "  make test-compatibility - Test desktop environment compatibility"
	@echo ""
	@echo "Configuration:"
	@echo "  make configure        - Interactive configuration"
	@echo "  make configure-show   - Show current configuration"
	@echo "  make configure-standard - Apply standard preset (25/5)"
	@echo "  make configure-long   - Apply long preset (45/15)"
	@echo "  make configure-short  - Apply short preset (15/3)"
	@echo ""
	@echo "Service Management:"
	@echo "  make start            - Start the user service"
	@echo "  make stop             - Stop the user service"
	@echo "  make restart          - Restart the user service"
	@echo "  make status           - Check user service status"
	@echo "  make logs             - View user service logs"
	@echo ""
	@echo "Packaging:"
	@echo "  make package-deb      - Build Debian package (.deb)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            - Clean up temporary files"
	@echo "  make uninstall        - Uninstall the user service"

# Installation
install:
	@echo "Installing Pomodoro Lock (Service-Based Architecture)..."
	@chmod +x scripts/install.sh
	@./scripts/install.sh

install-and-start:
	@echo "Installing Pomodoro Lock (Service-Based Architecture) and starting it..."
	@chmod +x scripts/install.sh
	@./scripts/install.sh
	@echo "Starting service..."
	@systemctl --user start pomodoro-lock.service
	@echo "Service started successfully!"

check-deps:
	@echo "Checking Pomodoro Lock dependencies..."
	@chmod +x scripts/check-dependencies.sh
	@./scripts/check-dependencies.sh

# Testing
test: test-notification test-overlay test-timer test-multi test-workflow test-system-tray test-compatibility
	@echo "All tests completed!"

test-notification:
	@echo "Testing notifications..."
	@python3 tests/test-notification.py

test-overlay:
	@echo "Testing overlay functionality..."
	@python3 tests/test-overlay.py

test-timer:
	@echo "Testing timer widget..."
	@python3 tests/test-timer.py

test-multi:
	@echo "Testing multi-display overlay..."
	@python3 tests/test-multi-overlay.py

test-workflow:
	@echo "Testing complete workflow (using short times: 1min work, 30sec break)..."
	@python3 tests/test-pomodoro-short.py

test-quick:
	@echo "Quick test for packaging (1 minute 30 seconds overlay test)..."
	@python3 tests/test-pomodoro.py

test-system-tray:
	@echo "Testing system tray functionality..."
	@python3 test-system-tray.py

test-compatibility:
	@echo "Testing desktop environment compatibility..."
	@python3 tests/test-desktop-compatibility.py

# Configuration
configure:
	@echo "Interactive configuration..."
	@python3 scripts/configure-pomodoro.py

configure-show:
	@echo "Current configuration:"
	@python3 scripts/configure-pomodoro.py show

configure-standard:
	@echo "Applying standard preset (25/5)..."
	@echo "y" | python3 scripts/configure-pomodoro.py standard

configure-long:
	@echo "Applying long preset (45/15)..."
	@echo "y" | python3 scripts/configure-pomodoro.py long

configure-short:
	@echo "Applying short preset (15/3)..."
	@echo "y" | python3 scripts/configure-pomodoro.py short

# Service Management
start:
	@echo "Starting Pomodoro Lock service..."
	@systemctl --user start pomodoro-lock.service

stop:
	@echo "Stopping Pomodoro Lock service..."
	@systemctl --user stop pomodoro-lock.service

restart:
	@echo "Restarting Pomodoro Lock service..."
	@systemctl --user restart pomodoro-lock.service

status:
	@echo "Service status:"
	@systemctl --user status pomodoro-lock.service

logs:
	@echo "Service logs (press Ctrl+C to exit):"
	@journalctl --user -u pomodoro-lock.service -f

# Packaging
package-deb:
	@echo "Building Debian package..."
	@dpkg-buildpackage -b -us -uc
	@echo "Debian package built in parent directory"

# Maintenance
clean:
	@echo "Cleaning up temporary files..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.log" -delete
	@rm -rf build/ dist/ *.egg-info/
	@rm -f ../pomodoro-lock_*.deb ../pomodoro-lock_*.changes ../pomodoro-lock_*.dsc

uninstall:
	@chmod +x scripts/uninstall.sh
	@./scripts/uninstall.sh 