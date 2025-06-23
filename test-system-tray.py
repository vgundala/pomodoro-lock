#!/usr/bin/env python3
"""
Enhanced Test script for system tray functionality
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3
import os
import time
import signal

class SystemTrayTest:
    def __init__(self):
        self.indicator = None
        self.test_results = {}
        
    def test_desktop_environment(self):
        """Detect and report desktop environment"""
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
        elif 'ubuntu' in desktop or 'unity' in desktop:
            env = 'GNOME'
        else:
            env = 'OTHER'
        
        print(f"🔍 Desktop Environment: {env}")
        self.test_results['desktop_environment'] = env
        return env
    
    def test_appindicator3(self):
        """Test AppIndicator3 functionality using only the icon name 'pomodoro-lock'"""
        print("🔍 Testing AppIndicator3 support with icon name 'pomodoro-lock' only...")
        try:
            self.indicator = AppIndicator3.Indicator.new(
                "test-pomodoro-lock-unq",
                "pomodoro-lock",
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_label("Test: 25:00", "")
            # Create menu
            menu = Gtk.Menu()
            status_item = Gtk.MenuItem(label="Status: Testing")
            menu.append(status_item)
            separator = Gtk.SeparatorMenuItem()
            menu.append(separator)
            test_item = Gtk.MenuItem(label="Test Menu Item")
            test_item.connect("activate", self.on_test_click)
            menu.append(test_item)
            separator2 = Gtk.SeparatorMenuItem()
            menu.append(separator2)
            quit_item = Gtk.MenuItem(label="Quit Test")
            quit_item.connect("activate", self.on_quit)
            menu.append(quit_item)
            menu.show_all()
            self.indicator.set_menu(menu)
            print("✅ AppIndicator3 system tray icon created successfully with icon name 'pomodoro-lock'")
            self.test_results['appindicator3'] = True
            return True
        except Exception as e:
            print(f"❌ AppIndicator3 failed: {e}")
            self.test_results['appindicator3'] = False
            return False
    
    def test_status_updates(self):
        """Test status updates"""
        if not self.indicator:
            return False
            
        print("🔍 Testing status updates...")
        
        try:
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
    
    def on_test_click(self, widget):
        """Callback for test menu item"""
        print("✅ Menu item clicked successfully!")
        self.test_results['menu_interaction'] = True
    
    def on_quit(self, widget):
        """Callback for quit menu item"""
        print("🛑 Quit requested from menu")
        self.cleanup()
        Gtk.main_quit()
    
    def cleanup(self):
        """Clean up resources"""
        if self.indicator:
            self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
    
    def run_tests(self):
        """Run all tests"""
        print("🚀 Starting System Tray Functionality Test")
        print("=" * 50)
        # Test desktop environment
        env = self.test_desktop_environment()
        # Test AppIndicator3 only
        appindicator_works = self.test_appindicator3()
        # Test status updates if AppIndicator3 works
        if appindicator_works:
            self.test_status_updates()
        # Print results
        self.print_results()
        # Keep running for manual testing
        if self.indicator:
            print("\n📋 Manual Testing:")
            print("   - Look for the system tray icon in your panel")
            print("   - Right-click on the icon to test the menu")
            print("   - Click 'Test Menu Item' to verify menu works")
            print("   - Click 'Quit Test' to exit")
            print("   - Press Ctrl+C to exit")
            # Set up signal handler
            signal.signal(signal.SIGINT, self.signal_handler)
            # Start GTK main loop
            Gtk.main()
        else:
            print("❌ AppIndicator3 system tray icon could not be created. No fallback available.")
    
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
        if self.test_results.get('desktop_environment') == 'XFCE':
            print("   - XFCE has limited system tray support, fallback mechanisms will be used")
        print("=" * 50)

def main():
    """Main function"""
    test = SystemTrayTest()
    test.run_tests()

if __name__ == "__main__":
    main() 