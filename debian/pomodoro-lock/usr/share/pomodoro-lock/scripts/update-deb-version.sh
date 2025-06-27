#!/bin/bash
# Usage: ./scripts/update-deb-version.sh [version]
# If [version] is not provided, uses latest git tag

set -e

if [ -n "$1" ]; then
    VERSION="$1"
else
    VERSION=$(git describe --tags --abbrev=0)
    VERSION="${VERSION#v}"  # Remove 'v' prefix if present
fi

echo "Updating Debian package version to $VERSION"

# Update control file
sed -i "s/^Version: .*/Version: $VERSION/" debian/pomodoro-lock/DEBIAN/control

# Update changelog (requires devscripts)
if command -v dch >/dev/null 2>&1; then
    (cd debian && dch --create --package pomodoro-lock --newversion "$VERSION-1" "Automated version bump to $VERSION")
else
    echo "Warning: 'dch' not found, skipping changelog update."
    echo "Install devscripts package to enable changelog updates:"
    echo "  sudo apt-get install devscripts"
fi

echo "Debian version updated to $VERSION" 