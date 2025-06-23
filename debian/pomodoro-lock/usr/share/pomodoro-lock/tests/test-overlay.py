#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

class TestOverlay(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.fullscreen()
        
        # Create event box for mouse events
        self.event_box = Gtk.EventBox()
        self.add(self.event_box)
        
        # Create a box with background color using CSS
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.box.set_margin_start(20)
        self.box.set_margin_end(20)
        self.box.set_margin_top(20)
        self.box.set_margin_bottom(20)
        
        # Apply CSS styling
        css_provider = Gtk.CssProvider()
        css = """
        .overlay-box {
            background-color: rgba(0, 0, 0, 0.95);
        }
        """
        css_provider.load_from_data(css.encode())
        style_context = self.box.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        style_context.add_class("overlay-box")
        
        self.event_box.add(self.box)
        
        # Add timer label
        self.timer_label = Gtk.Label()
        self.timer_label.set_markup("<span size='xx-large' weight='bold' foreground='white'>30</span>")
        self.box.pack_start(self.timer_label, True, True, 0)
        
        # Add message label
        self.message_label = Gtk.Label()
        self.message_label.set_markup("<span size='x-large' foreground='white'>TEST - Screen Overlay Active</span>")
        self.box.pack_start(self.message_label, True, True, 0)
        
        # Add instruction label
        self.instruction_label = Gtk.Label()
        self.instruction_label.set_markup("<span size='large' foreground='white'>This overlay will disappear in 30 seconds</span>")
        self.box.pack_start(self.instruction_label, True, True, 0)
        
        self.show_all()
    
    def update_timer(self, seconds):
        self.timer_label.set_markup(f"<span size='xx-large' weight='bold' foreground='white'>{seconds}</span>")

def test_overlay():
    """Test overlay functionality"""
    print("Testing overlay...")
    print("You should see a full-screen black overlay with a 30-second countdown")
    print("The overlay should cover your entire screen and stay on top")
    
    try:
        overlay = TestOverlay()
        overlay.show_all()
        print("✓ Overlay created successfully")
        
        # Update timer every second for 30 seconds
        def update_timer():
            nonlocal overlay
            current_time = int(overlay.timer_label.get_text())
            if current_time > 0:
                overlay.update_timer(current_time - 1)
                print(f"Timer: {current_time} seconds remaining")
                return True
            else:
                print("✓ Overlay test completed - closing overlay")
                overlay.destroy()
                Gtk.main_quit()
                return False
        
        GLib.timeout_add_seconds(1, update_timer)
        Gtk.main()
        print("✓ Overlay test completed successfully")
        return True
    except Exception as e:
        print(f"✗ Overlay failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting overlay test...")
    print("=" * 50)
    overlay_ok = test_overlay()
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Overlay: {'✓ PASS' if overlay_ok else '✗ FAIL'}") 