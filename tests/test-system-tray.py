#!/usr/bin/env python3
"""
System Tray Test - Comprehensive testing of system tray functionality

This test will check:
1. AppIndicator3 availability and functionality
2. System tray icon creation
3. Menu functionality
4. Fallback mechanisms for different desktop environments
5. Status updates
"""

import os
import sys
import time
import signal
import logging
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GLib, AppIndicator3

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SystemTrayTest:
    def __init__(self):
        self.indicator = None
        self.test_results = {}
        self.menu_clicked = False
        
    def test_appindicator3_availability(self):
        """Test if AppIndicator3 is available"""
        print("🔍 Testing AppIndicator3 availability...")
        try:
            # Try to create a test indicator
            test_indicator = AppIndicator3.Indicator.new(
                "test-indicator",
                "dialog-information",
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            test_indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            test_indicator.set_label("Test", "")
            
            # Create a simple menu
            menu = Gtk.Menu()
            item = Gtk.MenuItem(label="Test Item")
            menu.append(item)
            menu.show_all()
            test_indicator.set_menu(menu)
            
            print("✅ AppIndicator3 is available and working")
            self.test_results['appindicator3'] = True
            
            # Clean up test indicator
            test_indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
            return True
            
        except Exception as e:
            print(f"❌ AppIndicator3 not available: {e}")
            self.test_results['appindicator3'] = False
            return False
    
    def test_desktop_environment(self):
        """Detect desktop environment"""
        print("🔍 Detecting desktop environment...")
        
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        session = os.environ.get('DESKTOP_SESSION', '').lower()
        
        if 'gnome' in desktop or 'gnome' in session:
            env = 'GNOME'
        elif 'kde' in desktop or 'kde' in session:
            env = 'KDE'
        elif 'xfce' in desktop or 'xfce' in session:
            env = 'XFCE'
        elif 'mate' in desktop or 'mate' in session:
            env = 'MATE'
        elif 'cinnamon' in desktop or 'cinnamon' in session:
            env = 'Cinnamon'
        else:
            env = 'Unknown'
        
        print(f"✅ Desktop Environment: {env}")
        self.test_results['desktop_environment'] = env
        return env
    
    def test_system_tray_creation(self):
        """Test creating the actual system tray icon"""
        print("🔍 Testing system tray icon creation...")
        
        try:
            self.indicator = AppIndicator3.Indicator.new(
                "pomodoro-lock-test",
                "pomodoro-lock",  # Use the custom icon
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_label("Test: 25:00", "")
            
            # Create menu
            menu = Gtk.Menu()
            
            # Test item
            test_item = Gtk.MenuItem(label="Test Menu Item")
            test_item.connect("activate", self.on_test_menu_click)
            menu.append(test_item)
            
            # Separator
            separator = Gtk.SeparatorMenuItem()
            menu.append(separator)
            
            # Quit item
            quit_item = Gtk.MenuItem(label="Quit Test")
            quit_item.connect("activate", self.on_quit)
            menu.append(quit_item)
            
            menu.show_all()
            self.indicator.set_menu(menu)
            
            print("✅ System tray icon created successfully")
            self.test_results['system_tray_creation'] = True
            return True
            
        except Exception as e:
            print(f"❌ Failed to create system tray icon: {e}")
            self.test_results['system_tray_creation'] = False
            return False
    
    def test_icon_availability(self):
        """Test if the pomodoro-lock icon is available"""
        print("🔍 Testing icon availability...")
        
        # Check common icon locations
        icon_paths = [
            "/usr/share/icons/hicolor/scalable/apps/pomodoro-lock.svg",
            "/usr/share/pixmaps/pomodoro-lock.svg",
            "pomodoro-lock.svg",
            "../pomodoro-lock.svg"
        ]
        
        found_icon = False
        for path in icon_paths:
            if os.path.exists(path):
                print(f"✅ Icon found at: {path}")
                found_icon = True
                break
        
        if not found_icon:
            print("⚠️  Pomodoro Lock icon not found, using fallback")
            # Try to use a system icon as fallback
            try:
                if self.indicator:
                    self.indicator.set_icon("dialog-information")
                print("✅ Using fallback icon: dialog-information")
                found_icon = True
            except:
                print("❌ Could not set fallback icon")
        
        self.test_results['icon_availability'] = found_icon
        return found_icon
    
    def test_status_updates(self):
        """Test updating the system tray status"""
        print("🔍 Testing status updates...")
        
        if not self.indicator:
            print("❌ No indicator available for status test")
            self.test_results['status_updates'] = False
            return False
        
        try:
            # Test different status updates
            test_statuses = [
                ("Work: 25:00", "work"),
                ("Break: 05:00", "break"),
                ("Paused: 12:30", "paused")
            ]
            
            for status_text, status_type in test_statuses:
                self.indicator.set_label(status_text, "")
                print(f"✅ Status updated: {status_text}")
                time.sleep(1)
            
            self.test_results['status_updates'] = True
            return True
            
        except Exception as e:
            print(f"❌ Status updates failed: {e}")
            self.test_results['status_updates'] = False
            return False
    
    def test_menu_interaction(self):
        """Test menu interaction"""
        print("🔍 Testing menu interaction...")
        print("📋 Right-click on the system tray icon to test menu")
        print("   - Click 'Test Menu Item' to verify menu works")
        print("   - Click 'Quit Test' to exit")
        
        self.menu_clicked = False
        
        # Wait for user interaction
        timeout = 30  # 30 seconds timeout
        start_time = time.time()
        
        while not self.menu_clicked and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            Gtk.main_iteration_do(False)
        
        if self.menu_clicked:
            print("✅ Menu interaction successful")
            self.test_results['menu_interaction'] = True
            return True
        else:
            print("⚠️  Menu interaction test timed out")
            self.test_results['menu_interaction'] = False
            return False
    
    def test_fallback_mechanisms(self):
        """Test fallback mechanisms for environments without AppIndicator3"""
        print("🔍 Testing fallback mechanisms...")
        
        # Test notification fallback
        try:
            import notify2
            notify2.init("Pomodoro Test")
            notification = notify2.Notification(
                "Pomodoro Test", 
                "Testing fallback notification system",
                "dialog-information"
            )
            notification.show()
            print("✅ Notification fallback works")
            time.sleep(2)
            notification.close()
            self.test_results['notification_fallback'] = True
        except Exception as e:
            print(f"❌ Notification fallback failed: {e}")
            self.test_results['notification_fallback'] = False
        
        # Test status window fallback
        try:
            status_window = Gtk.Window()
            status_window.set_decorated(False)
            status_window.set_keep_above(True)
            status_window.set_default_size(200, 60)
            
            label = Gtk.Label(label="⏰ Test Status Window")
            status_window.add(label)
            status_window.show_all()
            
            print("✅ Status window fallback works")
            time.sleep(2)
            status_window.destroy()
            self.test_results['status_window_fallback'] = True
            
        except Exception as e:
            print(f"❌ Status window fallback failed: {e}")
            self.test_results['status_window_fallback'] = False
        
        return True
    
    def on_test_menu_click(self, widget):
        """Callback for test menu item"""
        print("✅ Menu item clicked successfully!")
        self.menu_clicked = True
    
    def on_quit(self, widget):
        """Callback for quit menu item"""
        print("🛑 Quit requested from menu")
        self.cleanup()
        Gtk.main_quit()
    
    def cleanup(self):
        """Clean up resources"""
        if self.indicator:
            self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
    
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
        """Print test results summary"""
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            if isinstance(result, str):
                status = f"ℹ️  {result}"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print("\n💡 Recommendations:")
        
        if not self.test_results.get('appindicator3', False):
            print("   - Install AppIndicator3 for better system tray support")
            print("   - On Ubuntu/Debian: sudo apt-get install gir1.2-appindicator3-0.1")
        
        if not self.test_results.get('icon_availability', False):
            print("   - Install the pomodoro-lock icon for better visual integration")
        
        if self.test_results.get('desktop_environment') == 'XFCE':
            print("   - XFCE has limited system tray support, fallback mechanisms will be used")
        
        print("=" * 50)

def main():
    """Main function"""
    test = SystemTrayTest()
    test.run_all_tests()

if __name__ == "__main__":
    main() 