#!/usr/bin/env python3
"""
Simple visible system tray test
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3
import time

def main():
    print("Creating a very visible system tray icon...")
    
    # Create indicator with a very visible icon
    indicator = AppIndicator3.Indicator.new(
        "visible-test",
        "dialog-error",  # Use a bright red error icon
        AppIndicator3.IndicatorCategory.APPLICATION_STATUS
    )
    indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    indicator.set_label("VISIBLE TEST", "")  # Very visible label
    
    # Create menu
    menu = Gtk.Menu()
    
    # Very visible menu item
    item = Gtk.MenuItem(label="CLICK ME - VISIBLE TEST")
    item.connect("activate", lambda w: print("Menu clicked!"))
    menu.append(item)
    
    # Quit item
    quit_item = Gtk.MenuItem(label="Quit")
    quit_item.connect("activate", Gtk.main_quit)
    menu.append(quit_item)
    
    menu.show_all()
    indicator.set_menu(menu)
    
    print("✅ Bright red system tray icon created!")
    print("   Look for a red error icon with 'VISIBLE TEST' label")
    print("   Right-click to test menu")
    print("   Press Ctrl+C to exit")
    
    # Keep running
    Gtk.main()

if __name__ == "__main__":
    main() 