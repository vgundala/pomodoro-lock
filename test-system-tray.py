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
        else:
            env = 'Unknown'
        
        print(f"🔍 Desktop Environment: {env}")
        self.test_results['desktop_environment'] = env
        return env
    
    def test_appindicator3(self):
        """Test AppIndicator3 functionality"""
        print("🔍 Testing AppIndicator3 support...")
        
        try:
            # Create system tray indicator
            self.indicator = AppIndicator3.Indicator.new(
                "test-pomodoro-lock",
                "pomodoro-lock",
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_label("Test: 25:00", "")
            
            # Create menu
            menu = Gtk.Menu()
            
            # Status item
            status_item = Gtk.MenuItem(label="Status: Testing")
            menu.append(status_item)
            
            # Separator
            separator = Gtk.SeparatorMenuItem()
            menu.append(separator)
            
            # Test item
            test_item = Gtk.MenuItem(label="Test Menu Item")
            test_item.connect("activate", self.on_test_click)
            menu.append(test_item)
            
            # Separator
            separator2 = Gtk.SeparatorMenuItem()
            menu.append(separator2)
            
            # Quit item
            quit_item = Gtk.MenuItem(label="Quit Test")
            quit_item.connect("activate", self.on_quit)
            menu.append(quit_item)
            
            menu.show_all()
            self.indicator.set_menu(menu)
            
            print("✅ AppIndicator3 system tray icon created successfully")
            self.test_results['appindicator3'] = True
            return True
            
        except Exception as e:
            print(f"❌ AppIndicator3 failed: {e}")
            self.test_results['appindicator3'] = False
            return False
    
    def test_icon_availability(self):
        """Test if the pomodoro-lock icon is available"""
        print("🔍 Testing icon availability...")
        
        icon_paths = [
            "pomodoro-lock.svg",
            "../pomodoro-lock.svg",
            "/usr/share/icons/hicolor/scalable/apps/pomodoro-lock.svg",
            "/usr/share/pixmaps/pomodoro-lock.svg"
        ]
        
        found_icon = False
        for path in icon_paths:
            if os.path.exists(path):
                print(f"✅ Icon found at: {path}")
                found_icon = True
                break
        
        if not found_icon:
            print("⚠️  Pomodoro Lock icon not found, using fallback")
            if self.indicator:
                self.indicator.set_icon("dialog-information")
                print("✅ Using fallback icon: dialog-information")
                found_icon = True
        
        self.test_results['icon_availability'] = found_icon
        return found_icon
    
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
    
    def test_fallback_mechanisms(self):
        """Test fallback mechanisms"""
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
        
        # Test AppIndicator3
        appindicator_works = self.test_appindicator3()
        
        # Test icon availability
        self.test_icon_availability()
        
        # Test status updates if AppIndicator3 works
        if appindicator_works:
            self.test_status_updates()
        
        # Test fallback mechanisms
        self.test_fallback_mechanisms()
        
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
            # Create fallback window
            self.create_fallback_window()
    
    def create_fallback_window(self):
        """Create fallback window when system tray fails"""
        print("\n📋 Creating fallback test window...")
        
        window = Gtk.Window(title="Pomodoro Lock System Tray Test")
        window.set_default_size(400, 300)
        window.connect("destroy", Gtk.main_quit)
        
        # Create content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        
        # Title
        title_label = Gtk.Label()
        title_label.set_markup("<span size='large' weight='bold'>System Tray Test Results</span>")
        box.pack_start(title_label, False, False, 10)
        
        # Results
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            if isinstance(result, str):
                status = f"ℹ️  {result}"
            
            result_label = Gtk.Label(label=f"{test_name.replace('_', ' ').title()}: {status}")
            result_label.set_halign(Gtk.Align.START)
            box.pack_start(result_label, False, False, 5)
        
        # Recommendations
        recommendations = Gtk.Label()
        recommendations.set_markup("\n<span weight='bold'>Recommendations:</span>")
        recommendations.set_halign(Gtk.Align.START)
        box.pack_start(recommendations, False, False, 10)
        
        if not self.test_results.get('appindicator3', False):
            rec1 = Gtk.Label(label="• Install AppIndicator3: sudo apt-get install gir1.2-appindicator3-0.1")
            rec1.set_halign(Gtk.Align.START)
            box.pack_start(rec1, False, False, 5)
        
        if self.test_results.get('desktop_environment') == 'XFCE':
            rec2 = Gtk.Label(label="• XFCE has limited system tray support - fallback mechanisms will be used")
            rec2.set_halign(Gtk.Align.START)
            box.pack_start(rec2, False, False, 5)
        
        # Close button
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", Gtk.main_quit)
        box.pack_start(close_button, False, False, 20)
        
        window.add(box)
        window.show_all()
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
    test.run_tests()

if __name__ == "__main__":
    main() 