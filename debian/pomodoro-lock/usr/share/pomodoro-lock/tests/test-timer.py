#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

class TestTimer(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_default_size(300, 100)
        # Move to left bottom
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() if display else display.get_monitor(0)
        geometry = monitor.get_geometry()
        x = geometry.x
        y = geometry.y + geometry.height - 100  # 100 is window height
        self.move(x, y)
        
        # Create event box for mouse events
        self.event_box = Gtk.EventBox()
        self.add(self.event_box)
        
        # Create a box with background color using CSS
        self.box = Gtk.Box()
        self.box.set_margin_start(20)
        self.box.set_margin_end(20)
        self.box.set_margin_top(20)
        self.box.set_margin_bottom(20)
        
        # Apply CSS styling
        css_provider = Gtk.CssProvider()
        css = """
        .timer-box {
            background-color: rgba(51, 51, 51, 0.8);
            border-radius: 10px;
        }
        .timer-box:hover {
            background-color: rgba(61, 61, 61, 0.8);
        }
        """
        css_provider.load_from_data(css.encode())
        style_context = self.box.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        style_context.add_class("timer-box")
        
        self.event_box.add(self.box)
        
        self.label = Gtk.Label()
        self.label.set_markup("<span size='x-large' weight='bold' foreground='white'>30</span>")
        self.box.pack_start(self.label, True, True, 0)
        
        # Connect mouse events
        self.event_box.connect("button-press-event", self.on_button_press)
        self.event_box.connect("button-release-event", self.on_button_release)
        self.event_box.connect("motion-notify-event", self.on_motion)
        
        # Enable motion events
        self.event_box.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                                Gdk.EventMask.BUTTON_RELEASE_MASK |
                                Gdk.EventMask.POINTER_MOTION_MASK)
        
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.show_all()
    
    def on_button_press(self, widget, event):
        if event.button == 1:  # Left mouse button
            self.dragging = True
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
            return True
        return False
    
    def on_button_release(self, widget, event):
        if event.button == 1:  # Left mouse button
            self.dragging = False
            return True
        return False
    
    def on_motion(self, widget, event):
        if self.dragging:
            x, y = self.get_position()
            new_x = x + (event.x_root - self.drag_start_x)
            new_y = y + (event.x_root - self.drag_start_y)
            self.move(new_x, new_y)
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
            return True
        return False

    def update_timer(self, seconds, mode='work'):
        minutes, secs = divmod(seconds, 60)
        color = 'white' if mode == 'work' else 'orange'
        self.label.set_markup(f"<span size='x-large' weight='bold' foreground='{color}'>{minutes:02d}:{secs:02d}</span>")

def test_timer():
    """Test timer functionality"""
    print("Testing timer...")
    print("You should see a small timer window in the bottom-left corner")
    print("The timer will count down from 30 seconds to 0")
    
    try:
        timer = TestTimer()
        timer.show_all()
        print("✓ Timer created successfully")
        
        # Track timer value separately
        current_time = 30
        
        # Test work mode (30 seconds)
        def update_timer():
            nonlocal timer, current_time
            if current_time > 0:
                timer.update_timer(current_time, mode='work')
                print(f"Work Timer: {current_time} seconds remaining")
                current_time -= 1
                return True
            else:
                print("✓ Work timer completed, switching to break mode")
                # Switch to break mode (10 seconds)
                current_time = 10
                
                def update_break_timer():
                    nonlocal timer, current_time
                    if current_time > 0:
                        timer.update_timer(current_time, mode='break')
                        print(f"Break Timer: {current_time} seconds remaining")
                        current_time -= 1
                        return True
                    else:
                        print("✓ Break timer completed")
                        timer.destroy()
                        Gtk.main_quit()
                        return False
                
                GLib.timeout_add_seconds(1, update_break_timer)
                return False
        
        GLib.timeout_add_seconds(1, update_timer)
        Gtk.main()
        print("✓ Timer test completed successfully")
        return True
    except Exception as e:
        print(f"✗ Timer failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting timer test...")
    print("=" * 50)
    timer_ok = test_timer()
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Timer: {'✓ PASS' if timer_ok else '✗ FAIL'}") 