# Pomodoro Lock Makefile

.PHONY: help install install-desktop install-system test test-all clean uninstall configure package-pip package-deb

# Default target
help:
	@echo "Pomodoro Lock - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  make install          - Install using command line installer (user service)"
	@echo "  make install-desktop  - Install using desktop installer (user service, recommended)"
	@echo "  make install-system   - Install as system service (requires sudo)"
	@echo ""
	@echo "User Management (System Service):"
	@echo "  make add-user USER=username    - Add service for a user"
	@echo "  make remove-user USER=username - Remove service for a user"
	@echo "  make list-users               - List all users with service"
	@echo "  make user-status USER=username - Check service status for user"
	@echo "  make user-start USER=username  - Start service for user"
	@echo "  make user-stop USER=username   - Stop service for user"
	@echo "  make user-restart USER=username - Restart service for user"
	@echo "  make user-logs USER=username   - Show logs for user"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-notification - Test notifications"
	@echo "  make test-overlay     - Test overlay functionality"
	@echo "  make test-timer       - Test timer widget"
	@echo "  make test-multi       - Test multi-display overlay"
	@echo "  make test-workflow    - Test complete workflow"
	@echo ""
	@echo "Configuration:"
	@echo "  make configure        - Interactive configuration"
	@echo "  make configure-show   - Show current configuration"
	@echo "  make configure-standard - Apply standard preset (25/5)"
	@echo "  make configure-long   - Apply long preset (45/15)"
	@echo "  make configure-short  - Apply short preset (15/3)"
	@echo ""
	@echo "Service Management (User Service):"
	@echo "  make start            - Start the user service"
	@echo "  make stop             - Stop the user service"
	@echo "  make restart          - Restart the user service"
	@echo "  make status           - Check user service status"
	@echo "  make logs             - View user service logs"
	@echo ""
	@echo "Packaging:"
	@echo "  make package-pip      - Build Python package (pip)"
	@echo "  make package-deb      - Build Debian package (.deb)"
	@echo "  make install-pip      - Install Python package in development mode"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            - Clean up temporary files"
	@echo "  make uninstall        - Uninstall the user service"

# Installation
install:
	@echo "Installing Pomodoro Lock (User Service)..."
	@chmod +x scripts/install.sh
	@./scripts/install.sh

install-desktop:
	@echo "Installing Pomodoro Lock (Desktop - User Service)..."
	@chmod +x scripts/install-desktop.sh
	@./scripts/install-desktop.sh

install-system:
	@echo "Installing Pomodoro Lock (System Service)..."
	@chmod +x scripts/install-system.sh
	@sudo ./scripts/install-system.sh

# User Management (System Service)
add-user:
	@if [ -z "$(USER)" ]; then \
		echo "Error: USER parameter is required. Example: make add-user USER=john"; \
		exit 1; \
	fi
	@echo "Adding Pomodoro Lock service for user: $(USER)"
	@chmod +x scripts/manage-users.sh
	@sudo ./scripts/manage-users.sh add $(USER)

remove-user:
	@if [ -z "$(USER)" ]; then \
		echo "Error: USER parameter is required. Example: make remove-user USER=john"; \
		exit 1; \
	fi
	@echo "Removing Pomodoro Lock service for user: $(USER)"
	@chmod +x scripts/manage-users.sh
	@sudo ./scripts/manage-users.sh remove $(USER)

list-users:
	@echo "Listing users with Pomodoro Lock service..."
	@chmod +x scripts/manage-users.sh
	@sudo ./scripts/manage-users.sh list

user-status:
	@if [ -z "$(USER)" ]; then \
		echo "Error: USER parameter is required. Example: make user-status USER=john"; \
		exit 1; \
	fi
	@echo "Checking service status for user: $(USER)"
	@chmod +x scripts/manage-users.sh
	@sudo ./scripts/manage-users.sh status $(USER)

user-start:
	@if [ -z "$(USER)" ]; then \
		echo "Error: USER parameter is required. Example: make user-start USER=john"; \
		exit 1; \
	fi
	@echo "Starting service for user: $(USER)"
	@chmod +x scripts/manage-users.sh
	@sudo ./scripts/manage-users.sh start $(USER)

user-stop:
	@if [ -z "$(USER)" ]; then \
		echo "Error: USER parameter is required. Example: make user-stop USER=john"; \
		exit 1; \
	fi
	@echo "Stopping service for user: $(USER)"
	@chmod +x scripts/manage-users.sh
	@sudo ./scripts/manage-users.sh stop $(USER)

user-restart:
	@if [ -z "$(USER)" ]; then \
		echo "Error: USER parameter is required. Example: make user-restart USER=john"; \
		exit 1; \
	fi
	@echo "Restarting service for user: $(USER)"
	@chmod +x scripts/manage-users.sh
	@sudo ./scripts/manage-users.sh restart $(USER)

user-logs:
	@if [ -z "$(USER)" ]; then \
		echo "Error: USER parameter is required. Example: make user-logs USER=john"; \
		exit 1; \
	fi
	@echo "Showing logs for user: $(USER)"
	@chmod +x scripts/manage-users.sh
	@sudo ./scripts/manage-users.sh logs $(USER)

# Testing
test: test-notification test-overlay test-timer test-multi test-workflow
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
	@echo "Testing complete workflow..."
	@python3 tests/test-pomodoro-short.py

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

# Service Management (User Service)
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
package-pip:
	@echo "Building Python package..."
	@python3 setup.py sdist bdist_wheel
	@echo "Package built in dist/ directory"

package-deb:
	@echo "Building Debian package..."
	@dpkg-buildpackage -b -us -uc
	@echo "Debian package built in parent directory"

install-pip:
	@echo "Installing Python package in development mode..."
	@pip install -e .

# Maintenance
clean:
	@echo "Cleaning up temporary files..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.log" -delete
	@rm -rf build/ dist/ *.egg-info/
	@rm -f ../pomodoro-lock_*.deb ../pomodoro-lock_*.changes ../pomodoro-lock_*.dsc

uninstall:
	@echo "Uninstalling Pomodoro Lock..."
	@systemctl --user stop pomodoro-lock.service 2>/dev/null || true
	@systemctl --user disable pomodoro-lock.service 2>/dev/null || true
	@rm -f ~/.config/systemd/user/pomodoro-lock.service
	@systemctl --user daemon-reload
	@echo "Service uninstalled. To remove all files, run:"
	@echo "  rm -rf ~/.local/share/pomodoro-lock" 