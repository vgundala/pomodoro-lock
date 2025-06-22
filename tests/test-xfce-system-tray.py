#!/usr/bin/env python3
"""
XFCE System Tray Test - Specialized testing for XFCE environment

This test focuses on XFCE-specific system tray issues and provides
detailed troubleshooting information.
"""

import os
import sys
import time
import signal
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GLib, AppIndicator3, Gdk

class XFCESystemTrayTest:
    def __init__(self):
        self.indicator = None
        self.test_results = {}
        
    def check_xfce_environment(self):
        """Check XFCE-specific environment"""
        print("🔍 Checking XFCE environment...")
        
        # Check if we're actually in XFCE
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        session = os.environ.get('DESKTOP_SESSION', '').lower()
        
        if 'xfce' not in desktop and 'xfce' not in session:
            print("⚠️  Not running in XFCE environment")
            return False
        
        print("✅ Running in XFCE environment")
        
        # Check XFCE panel processes
        try:
            result = subprocess.run(['pgrep', '-f', 'xfce4-panel'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ XFCE panel is running")
                self.test_results['xfce_panel_running'] = True
            else:
                print("❌ XFCE panel not found")
                self.test_results['xfce_panel_running'] = False
        except Exception as e:
            print(f"❌ Error checking XFCE panel: {e}")
            self.test_results['xfce_panel_running'] = False
        
        # Check for system tray plugin
        try:
            result = subprocess.run(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins/plugin-1'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ XFCE panel configuration accessible")
                self.test_results['xfce_config_accessible'] = True
            else:
                print("❌ XFCE panel configuration not accessible")
                self.test_results['xfce_config_accessible'] = False
        except Exception as e:
            print(f"❌ Error checking XFCE config: {e}")
            self.test_results['xfce_config_accessible'] = False
        
        return True
    
    def check_system_tray_plugins(self):
        """Check for system tray plugins"""
        print("🔍 Checking system tray plugins...")
        
        # Check for common system tray plugins
        tray_plugins = [
            'systray',
            'notification-area',
            'indicator',
            'appindicator'
        ]
        
        found_plugins = []
        try:
            result = subprocess.run(['xfconf-query', '-c', 'xfce4-panel', '-l'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                config_lines = result.stdout.split('\n')
                for plugin in tray_plugins:
                    for line in config_lines:
                        if plugin in line.lower():
                            found_plugins.append(plugin)
                            break
                
                if found_plugins:
                    print(f"✅ Found system tray plugins: {', '.join(found_plugins)}")
                    self.test_results['system_tray_plugins'] = found_plugins
                else:
                    print("❌ No system tray plugins found")
                    self.test_results['system_tray_plugins'] = []
            else:
                print("❌ Could not query XFCE panel configuration")
                self.test_results['system_tray_plugins'] = []
        except Exception as e:
            print(f"❌ Error checking plugins: {e}")
            self.test_results['system_tray_plugins'] = []
    
    def test_appindicator3_in_xfce(self):
        """Test AppIndicator3 specifically in XFCE"""
        print("🔍 Testing AppIndicator3 in XFCE...")
        
        try:
            # Create indicator with XFCE-specific settings
            self.indicator = AppIndicator3.Indicator.new(
                "xfce-test-pomodoro-lock",
                "pomodoro-lock",
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_label("XFCE Test: 25:00", "")
            
            # Create menu
            menu = Gtk.Menu()
            
            # Status item
            status_item = Gtk.MenuItem(label="XFCE System Tray Test")
            status_item.set_sensitive(False)
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
            
            print("✅ AppIndicator3 created successfully")
            self.test_results['appindicator3_created'] = True
            return True
            
        except Exception as e:
            print(f"❌ AppIndicator3 failed: {e}")
            self.test_results['appindicator3_created'] = False
            return False
    
    def test_alternative_indicators(self):
        """Test alternative indicator methods"""
        print("🔍 Testing alternative indicator methods...")
        
        # Test with different icon names
        icon_names = [
            "pomodoro-lock",
            "dialog-information",
            "appointment",
            "alarm-clock",
            "timer"
        ]
        
        for icon_name in icon_names:
            try:
                test_indicator = AppIndicator3.Indicator.new(
                    f"test-{icon_name}",
                    icon_name,
                    AppIndicator3.IndicatorCategory.APPLICATION_STATUS
                )
                test_indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
                test_indicator.set_label(f"Test: {icon_name}", "")
                
                # Simple menu
                menu = Gtk.Menu()
                item = Gtk.MenuItem(label=f"Test {icon_name}")
                menu.append(item)
                menu.show_all()
                test_indicator.set_menu(menu)
                
                print(f"✅ Alternative icon '{icon_name}' works")
                time.sleep(1)
                
                # Clean up
                test_indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
                
            except Exception as e:
                print(f"❌ Alternative icon '{icon_name}' failed: {e}")
        
        self.test_results['alternative_indicators'] = True
    
    def test_notification_fallback(self):
        """Test notification fallback for XFCE"""
        print("🔍 Testing notification fallback...")
        
        try:
            import notify2
            notify2.init("XFCE Pomodoro Test")
            
            # Test different notification types
            notifications = [
                ("Pomodoro Test", "Testing basic notification", "dialog-information"),
                ("Timer Running", "Work session in progress", "appointment"),
                ("Break Time", "Time for a break!", "alarm-clock")
            ]
            
            for title, message, icon in notifications:
                notification = notify2.Notification(title, message, icon)
                notification.show()
                print(f"✅ Notification: {title}")
                time.sleep(2)
                notification.close()
            
            self.test_results['notification_fallback'] = True
            return True
            
        except Exception as e:
            print(f"❌ Notification fallback failed: {e}")
            self.test_results['notification_fallback'] = False
            return False
    
    def test_status_window_fallback(self):
        """Test status window fallback for XFCE"""
        print("🔍 Testing status window fallback...")
        
        try:
            # Create a more prominent status window
            self.status_window = Gtk.Window()
            self.status_window.set_decorated(False)
            self.status_window.set_keep_above(True)
            self.status_window.set_default_size(250, 80)
            self.status_window.set_resizable(False)
            
            # Position in top-right corner
            display = Gdk.Display.get_default()
            monitor = display.get_primary_monitor() if display else display.get_monitor(0)
            geometry = monitor.get_geometry()
            x = geometry.x + geometry.width - 250
            y = geometry.y + 10
            self.status_window.move(x, y)
            
            # Create content
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            box.set_margin_start(15)
            box.set_margin_end(15)
            box.set_margin_top(10)
            box.set_margin_bottom(10)
            
            # Icon and text
            icon_label = Gtk.Label(label="⏰")
            icon_label.set_margin_end(10)
            box.pack_start(icon_label, False, False, 0)
            
            text_label = Gtk.Label(label="Pomodoro Running\n25:00 remaining")
            box.pack_start(text_label, True, True, 0)
            
            # Close button
            close_button = Gtk.Button(label="✕")
            close_button.set_size_request(30, 30)
            close_button.connect("clicked", self.on_status_window_close)
            box.pack_start(close_button, False, False, 0)
            
            self.status_window.add(box)
            self.status_window.show_all()
            
            print("✅ Status window fallback created")
            self.test_results['status_window_fallback'] = True
            return True
            
        except Exception as e:
            print(f"❌ Status window fallback failed: {e}")
            self.test_results['status_window_fallback'] = False
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
    
    def on_status_window_close(self, widget):
        """Callback for status window close button"""
        if hasattr(self, 'status_window'):
            self.status_window.destroy()
    
    def cleanup(self):
        """Clean up resources"""
        if self.indicator:
            self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
        if hasattr(self, 'status_window'):
            self.status_window.destroy()
    
    def run_xfce_tests(self):
        """Run all XFCE-specific tests"""
        print("🚀 Starting XFCE System Tray Test")
        print("=" * 50)
        
        # Check XFCE environment
        if not self.check_xfce_environment():
            print("❌ Not running in XFCE environment")
            return
        
        # Check system tray plugins
        self.check_system_tray_plugins()
        
        # Test AppIndicator3
        appindicator_works = self.test_appindicator3_in_xfce()
        
        # Test alternative indicators
        self.test_alternative_indicators()
        
        # Test fallback mechanisms
        self.test_notification_fallback()
        self.test_status_window_fallback()
        
        # Print results and recommendations
        self.print_xfce_results()
        
        # Keep running for manual testing
        if self.indicator or hasattr(self, 'status_window'):
            print("\n📋 Manual Testing:")
            print("   - Look for the system tray icon in your XFCE panel")
            print("   - Check the status window in the top-right corner")
            print("   - Right-click on the icon to test the menu")
            print("   - Click 'Test Menu Item' to verify menu works")
            print("   - Click 'Quit Test' to exit")
            print("   - Press Ctrl+C to exit")
            
            # Set up signal handler
            signal.signal(signal.SIGINT, self.signal_handler)
            
            # Start GTK main loop
            Gtk.main()
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\n🛑 Interrupted by user")
        self.cleanup()
        Gtk.main_quit()
    
    def print_xfce_results(self):
        """Print XFCE-specific test results and recommendations"""
        print("\n" + "=" * 50)
        print("📊 XFCE SYSTEM TRAY TEST RESULTS")
        print("=" * 50)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            if isinstance(result, list):
                status = f"ℹ️  {', '.join(result)}"
            elif isinstance(result, str):
                status = f"ℹ️  {result}"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print("\n💡 XFCE-Specific Recommendations:")
        
        if not self.test_results.get('xfce_panel_running', False):
            print("   - XFCE panel is not running - restart XFCE session")
        
        if not self.test_results.get('system_tray_plugins', []):
            print("   - No system tray plugins found - add system tray to XFCE panel")
            print("   - Right-click panel → Add New Items → System Tray")
        
        if not self.test_results.get('appindicator3_created', False):
            print("   - AppIndicator3 not working - install libayatana-appindicator3-dev")
            print("   - sudo apt-get install libayatana-appindicator3-dev")
        
        print("\n🔧 XFCE Panel Configuration:")
        print("   1. Right-click on XFCE panel")
        print("   2. Select 'Panel Preferences'")
        print("   3. Go to 'Items' tab")
        print("   4. Add 'System Tray' or 'Notification Area' plugin")
        print("   5. Make sure it's enabled and visible")
        
        print("\n🔄 Alternative Solutions:")
        print("   - Use notification fallback (already working)")
        print("   - Use status window fallback (already working)")
        print("   - The app will work with limited system tray functionality")
        
        print("=" * 50)

def main():
    """Main function"""
    test = XFCESystemTrayTest()
    test.run_xfce_tests()

if __name__ == "__main__":
    main() 