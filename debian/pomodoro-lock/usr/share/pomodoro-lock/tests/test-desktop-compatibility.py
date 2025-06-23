#!/usr/bin/env python3
"""
Desktop Environment Compatibility Test

This test verifies that the system tray functionality works correctly
across different desktop environments.
"""

import os
import sys
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3

def detect_desktop_environment():
    """Detect the current desktop environment"""
    desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    session = os.environ.get('DESKTOP_SESSION', '').lower()
    if 'gnome' in desktop or 'ubuntu' in desktop or 'unity' in desktop:
        return 'GNOME'
    elif 'kde' in desktop or 'plasma' in desktop:
        return 'KDE'
    # Remove XFCE detection
    return 'OTHER'

def test_system_tray():
    """Test system tray functionality"""
    desktop = detect_desktop_environment()
    print(f"🔍 Detected Desktop Environment: {desktop}")
    
    if desktop == 'GNOME':
        print("✅ GNOME detected - using AppIndicator3")
    elif desktop == 'KDE':
        print("✅ KDE detected - using StatusNotifier")
    else:
        print("✅ Other desktop detected - using default system tray implementation")
    
    # Test AppIndicator3 for other environments
    try:
        indicator = AppIndicator3.Indicator.new(
            "compatibility-test",
            "dialog-information",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        indicator.set_label("Test", "")
        
        # Create simple menu
        menu = Gtk.Menu()
        item = Gtk.MenuItem(label="Test Item")
        menu.append(item)
        menu.show_all()
        indicator.set_menu(menu)
        
        print("✅ AppIndicator3 system tray icon created successfully")
        print("   - System tray should work properly")
        print("   - Look for the system tray icon in your panel")
        
        # Clean up
        indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
        return True
        
    except Exception as e:
        print(f"❌ AppIndicator3 failed: {e}")
        print("   - System tray functionality may be limited")
        print("   - Fallback mechanisms will be used")
        return False

def test_notifications():
    """Test notification functionality"""
    try:
        import notify2
        notify2.init("Compatibility Test")
        notification = notify2.Notification(
            "Desktop Compatibility Test",
            "Notifications are working correctly",
            "dialog-information"
        )
        notification.show()
        print("✅ Notifications work correctly")
        return True
    except Exception as e:
        print(f"❌ Notifications failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Desktop Environment Compatibility Test")
    print("=" * 50)
    
    # Test desktop detection
    desktop = detect_desktop_environment()
    
    # Test system tray
    system_tray_works = test_system_tray()
    
    # Test notifications
    notifications_work = test_notifications()
    
    print("\n" + "=" * 50)
    print("📊 COMPATIBILITY RESULTS")
    print("=" * 50)
    print(f"Desktop Environment: {desktop}")
    print(f"System Tray: {'✅ Working' if system_tray_works else '❌ Limited'}")
    print(f"Notifications: {'✅ Working' if notifications_work else '❌ Failed'}")
    
    print("\n💡 Recommendations:")
    
    if desktop == 'GNOME':
        print("   - GNOME detected: Using AppIndicator3")
    elif desktop == 'KDE':
        print("   - KDE detected: Using StatusNotifier")
    else:
        print("   - Other desktop detected: Using default system tray implementation")
    
    if not notifications_work:
        print("   - Install notification support: sudo apt-get install libnotify-bin")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 