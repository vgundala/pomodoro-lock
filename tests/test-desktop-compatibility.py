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
gi.require_version('GLib', '2.0')
from gi.repository import Gtk, GLib

# Try to import the newer libayatana-appindicator-glib first
try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3
    APPINDICATOR_NEW_API = True
    print("Using libayatana-appindicator-glib (new API)")
except ImportError:
    # Fallback to the older libayatana-appindicator
    try:
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3
        APPINDICATOR_NEW_API = False
        print("Using libayatana-appindicator (deprecated API)")
    except ImportError:
        print("No appindicator library available")
        APPINDICATOR_NEW_API = None

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

def test_appindicator3_compatibility():
    """Test AppIndicator3 compatibility across desktop environments"""
    print("🔍 Testing AppIndicator3 compatibility...")
    
    if APPINDICATOR_NEW_API is None:
        print("❌ No appindicator library available")
        return False
    
    desktop_env = detect_desktop_environment()
    print(f"✅ {desktop_env} detected - using AppIndicator3")
    
    try:
        if APPINDICATOR_NEW_API:
            # Test the new AyatanaAppIndicator3 API
            indicator = AyatanaAppIndicator3.Indicator.new(
                "pomodoro-lock-test",
                "pomodoro-lock",
                AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)
            
            # Create a simple menu
            menu = Gtk.Menu()
            test_item = Gtk.MenuItem(label="Test Item")
            menu.append(test_item)
            menu.show_all()
            indicator.set_menu(menu)
            
            # Clean up
            indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.PASSIVE)
        else:
            # Test the old AppIndicator3 API
            indicator = AppIndicator3.Indicator.new(
                "pomodoro-lock-test",
                "pomodoro-lock",
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            
            # Create a simple menu
            menu = Gtk.Menu()
            test_item = Gtk.MenuItem(label="Test Item")
            menu.append(test_item)
            menu.show_all()
            indicator.set_menu(menu)
            
            # Clean up
            indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
        
        print("✅ AppIndicator3 system tray icon created successfully")
        return True
        
    except Exception as e:
        print(f"❌ AppIndicator3 failed: {e}")
        return False

def test_gtk_compatibility():
    """Test basic GTK compatibility"""
    print("🔍 Testing GTK compatibility...")
    
    try:
        # Create a simple window
        window = Gtk.Window()
        window.set_title("GTK Compatibility Test")
        window.set_default_size(300, 200)
        window.connect("destroy", Gtk.main_quit)
        
        # Add a label
        label = Gtk.Label(label="GTK is working correctly!")
        window.add(label)
        
        # Show the window briefly
        window.show_all()
        
        # Schedule window destruction
        GLib.timeout_add(1000, window.destroy)
        
        print("✅ GTK compatibility test passed")
        return True
        
    except Exception as e:
        print(f"❌ GTK compatibility test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Desktop Environment Compatibility Test")
    print("=" * 50)
    
    # Detect desktop environment
    desktop_env = detect_desktop_environment()
    print(f"📋 Desktop Environment: {desktop_env}")
    
    # Test GTK compatibility
    gtk_ok = test_gtk_compatibility()
    
    # Test AppIndicator3 compatibility
    appindicator_ok = test_appindicator3_compatibility()
    
    # Print results
    print("\n📊 Test Results:")
    print("=" * 50)
    print(f"Desktop Environment: {desktop_env}")
    print(f"GTK Compatibility: {'✅ PASS' if gtk_ok else '❌ FAIL'}")
    print(f"AppIndicator3 Compatibility: {'✅ PASS' if appindicator_ok else '❌ FAIL'}")
    
    print("\n💡 Recommendations:")
    print("=" * 50)
    if appindicator_ok:
        print("   - System tray functionality should work correctly")
        if APPINDICATOR_NEW_API:
            print("   - Using modern libayatana-appindicator-glib")
        else:
            print("   - Using deprecated libayatana-appindicator (consider upgrading)")
    else:
        print("   - Install AppIndicator3 for system tray support")
        if APPINDICATOR_NEW_API is None:
            print("   - On Ubuntu/Debian: sudo apt-get install gir1.2-ayatanaappindicator3-0.1")
        else:
            print("   - On Ubuntu/Debian: sudo apt-get install gir1.2-appindicator3-0.1")
    
    if gtk_ok:
        print("   - GNOME detected: Using AppIndicator3")
    else:
        print("   - GTK issues detected - check GTK installation")
    
    # Start GTK main loop if tests passed
    if gtk_ok and appindicator_ok:
        print("\n🎉 All tests passed! Starting GTK main loop...")
        Gtk.main()
    else:
        print("\n⚠️  Some tests failed. Check the recommendations above.")

if __name__ == "__main__":
    main() 