#!/usr/bin/env python3
"""
System Tray Functionality Test

This test verifies:
1. AppIndicator3 availability and functionality
2. System tray icon creation and display
3. Menu interaction and callbacks
4. Status updates and icon changes
5. Fallback mechanisms for different desktop environments
"""

import os
import sys
import signal
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

class SystemTrayTest:
    """System tray functionality test class"""
    
    def __init__(self):
        self.indicator = None
        self.test_results = {
            'desktop_environment': False,
            'appindicator3': False,
            'icon_availability': False,
            'system_tray_creation': False,
            'status_updates': False,
            'menu_interaction': False,
            'fallback_mechanisms': False
        }
    
    def test_desktop_environment(self):
        """Test desktop environment detection"""
        print("🔍 Testing desktop environment...")
        
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        session = os.environ.get('DESKTOP_SESSION', '').lower()
        
        if 'gnome' in desktop or 'ubuntu' in desktop or 'unity' in desktop:
            print("✅ GNOME detected - using AppIndicator3")
            self.test_results['desktop_environment'] = True
            return 'GNOME'
        elif 'kde' in desktop or 'plasma' in desktop:
            print("✅ KDE detected - using AppIndicator3")
            self.test_results['desktop_environment'] = True
            return 'KDE'
        else:
            print("⚠️  Unknown desktop environment - testing AppIndicator3 anyway")
            return 'OTHER'
    
    def test_appindicator3_availability(self):
        """Test if AppIndicator3 is available"""
        print("🔍 Testing AppIndicator3 availability...")
        
        if APPINDICATOR_NEW_API is None:
            print("❌ No appindicator library available")
            self.test_results['appindicator3'] = False
            return False
        
        try:
            if APPINDICATOR_NEW_API:
                # Test the new AyatanaAppIndicator3 API
                test_indicator = AyatanaAppIndicator3.Indicator.new(
                    "test-indicator",
                    "pomodoro-lock",
                    AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS
                )
                test_indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)
                test_indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.PASSIVE)
            else:
                # Test the old AppIndicator3 API
                test_indicator = AppIndicator3.Indicator.new(
                    "test-indicator",
                    "pomodoro-lock",
                    AppIndicator3.IndicatorCategory.APPLICATION_STATUS
                )
                test_indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
                test_indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
            
            print("✅ AppIndicator3 is available and working")
            self.test_results['appindicator3'] = True
            return True
            
        except Exception as e:
            print(f"❌ AppIndicator3 not available: {e}")
            self.test_results['appindicator3'] = False
            return False
    
    def test_icon_availability(self):
        """Test if the application icon is available"""
        print("🔍 Testing icon availability...")
        
        icon_paths = [
            "/usr/share/icons/hicolor/scalable/apps/pomodoro-lock.svg",
            "/usr/share/pixmaps/pomodoro-lock.svg",
            "pomodoro-lock.svg",
            "src/pomodoro-lock.svg"
        ]
        
        for path in icon_paths:
            if os.path.exists(path):
                print(f"✅ Icon found at: {path}")
                self.test_results['icon_availability'] = True
                return True
        
        print("⚠️  Icon not found in standard locations")
        self.test_results['icon_availability'] = False
        return False
    
    def test_system_tray_creation(self):
        """Test system tray indicator creation"""
        print("🔍 Testing system tray creation...")
        
        try:
            if APPINDICATOR_NEW_API:
                self.indicator = AyatanaAppIndicator3.Indicator.new(
                    "pomodoro-lock-test",
                    "pomodoro-lock",
                    AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS
                )
                self.indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)
            else:
                self.indicator = AppIndicator3.Indicator.new(
                    "pomodoro-lock-test",
                    "pomodoro-lock",
                    AppIndicator3.IndicatorCategory.APPLICATION_STATUS
                )
                self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            
            print("✅ System tray indicator created successfully")
            self.test_results['system_tray_creation'] = True
            return True
            
        except Exception as e:
            print(f"❌ Failed to create system tray: {e}")
            self.test_results['system_tray_creation'] = False
            return False
    
    def test_status_updates(self):
        """Test system tray status updates"""
        print("🔍 Testing status updates...")
        
        if not self.indicator:
            print("❌ No indicator available for status updates")
            return False
        
        try:
            # Test tooltip updates
            self.indicator.set_title("Pomodoro Lock - Work: 25:00")
            self.indicator.set_title("Pomodoro Lock - Break: 05:00")
            
            # Test icon changes
            self.indicator.set_icon("pomodoro-lock")
            self.indicator.set_icon("pomodoro-lock-break")
            
            print("✅ Status updates working correctly")
            self.test_results['status_updates'] = True
            return True
            
        except Exception as e:
            print(f"❌ Status updates failed: {e}")
            self.test_results['status_updates'] = False
            return False
    
    def test_menu_interaction(self):
        """Test menu interaction"""
        print("🔍 Testing menu interaction...")
        
        if not self.indicator:
            print("❌ No indicator available for menu testing")
            return False
        
        try:
            # Create a test menu
            menu = Gtk.Menu()
            
            # Test item
            test_item = Gtk.MenuItem(label="Test Item")
            test_item.connect("activate", self._on_test_menu_click)
            menu.append(test_item)
            
            # Quit item
            quit_item = Gtk.MenuItem(label="Quit Test")
            quit_item.connect("activate", self._on_quit_test)
            menu.append(quit_item)
            
            menu.show_all()
            self.indicator.set_menu(menu)
            
            print("✅ Menu created and attached successfully")
            self.test_results['menu_interaction'] = True
            return True
            
        except Exception as e:
            print(f"❌ Menu interaction failed: {e}")
            self.test_results['menu_interaction'] = False
            return False
    
    def _on_test_menu_click(self, widget):
        """Handle test menu item click"""
        print("✅ Menu item clicked successfully")
    
    def _on_quit_test(self, widget):
        """Handle quit menu item click"""
        print("🛑 Quit requested from menu")
        self.cleanup()
        Gtk.main_quit()
    
    def test_fallback_mechanisms(self):
        """Test fallback mechanisms for environments without AppIndicator3"""
        print("🔍 Testing fallback mechanisms...")
        
        # Test if we can create a simple GTK window as fallback
        try:
            fallback_window = Gtk.Window()
            fallback_window.set_title("Fallback Window")
            fallback_window.set_default_size(200, 100)
            fallback_window.connect("destroy", Gtk.main_quit)
            fallback_window.show_all()
            
            # Close the window immediately
            fallback_window.destroy()
            
            print("✅ Fallback mechanisms available")
            self.test_results['fallback_mechanisms'] = True
            return True
            
        except Exception as e:
            print(f"❌ Fallback mechanisms failed: {e}")
            self.test_results['fallback_mechanisms'] = False
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.indicator:
            try:
                if APPINDICATOR_NEW_API:
                    self.indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.PASSIVE)
                else:
                    self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
            except Exception as e:
                print(f"Error during cleanup: {e}")
    
    def run_all_tests(self):
        """Run all system tray tests"""
        print("🚀 Starting System Tray Functionality Test")
        print("=" * 50)
        
        # Test desktop environment
        env = self.test_desktop_environment()
        
        # Test AppIndicator3 availability
        appindicator_available = self.test_appindicator3_availability()
        
        # Test icon availability
        self.test_icon_availability()
        
        # Test system tray creation
        if appindicator_available:
            self.test_system_tray_creation()
            self.test_status_updates()
            self.test_menu_interaction()
        else:
            print("⚠️  Skipping AppIndicator3 tests (not available)")
        
        # Test fallback mechanisms
        self.test_fallback_mechanisms()
        
        # Print results
        self.print_results()
        
        # Keep the indicator visible for manual testing
        if self.indicator:
            print("\n📋 Manual Testing:")
            print("   - The system tray icon should be visible")
            print("   - Right-click to test the menu")
            print("   - Click 'Quit Test' to exit")
            
            # Set up signal handler for clean exit
            signal.signal(signal.SIGINT, self.signal_handler)
            
            # Start GTK main loop
            Gtk.main()
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\n🛑 Interrupted by user")
        self.cleanup()
        Gtk.main_quit()
    
    def print_results(self):
        """Print test results"""
        print("\n📊 Test Results:")
        print("=" * 50)
        
        for test_name, passed in self.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print("\n💡 Recommendations:")
        print("=" * 50)
        
        if not self.test_results.get('appindicator3', False):
            print("   - Install AppIndicator3 for better system tray support")
            if APPINDICATOR_NEW_API is None:
                print("   - On Ubuntu/Debian: sudo apt-get install gir1.2-ayatanaappindicator3-0.1")
            else:
                print("   - On Ubuntu/Debian: sudo apt-get install gir1.2-appindicator3-0.1")
        
        if not self.test_results.get('icon_availability', False):
            print("   - Ensure pomodoro-lock.svg icon is installed")
            print("   - Icon should be in /usr/share/icons/hicolor/scalable/apps/")

if __name__ == "__main__":
    test = SystemTrayTest()
    test.run_all_tests() 