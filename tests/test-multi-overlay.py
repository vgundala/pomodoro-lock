#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

class FullScreenOverlay(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        # Don't automatically fullscreen - we'll control this manually
        
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
        self.message_label.set_markup("<span size='x-large' foreground='white'>TEST - Multi-Display Overlay</span>")
        self.box.pack_start(self.message_label, True, True, 0)
        
        # Add monitor info label
        self.monitor_label = Gtk.Label()
        self.monitor_label.set_markup("<span size='large' foreground='white'>Monitor: Unknown</span>")
        self.box.pack_start(self.monitor_label, True, True, 0)
        
        self.show_all()
    
    def update_timer(self, seconds):
        self.timer_label.set_markup(f"<span size='xx-large' weight='bold' foreground='white'>{seconds}</span>")
    
    def set_monitor_info(self, monitor_id, geometry):
        self.monitor_label.set_markup(f"<span size='large' foreground='white'>Monitor {monitor_id}: {geometry.width}x{geometry.height}</span>")

class MultiDisplayOverlay:
    def __init__(self):
        self.overlays = []
        self.create_overlays()
    
    def create_overlays(self):
        """Create overlays for all available displays"""
        display = Gdk.Display.get_default()
        if display:
            n_monitors = display.get_n_monitors()
            print(f"Found {n_monitors} monitor(s)")
            for i in range(n_monitors):
                overlay = FullScreenOverlay()
                # Get monitor geometry
                monitor = display.get_monitor(i)
                geometry = monitor.get_geometry()
                
                # Set window to cover the specific monitor
                overlay.unfullscreen()  # Remove fullscreen first
                overlay.move(geometry.x, geometry.y)
                overlay.resize(geometry.width, geometry.height)
                overlay.set_default_size(geometry.width, geometry.height)
                overlay.set_monitor_info(i, geometry)
                
                self.overlays.append(overlay)
                print(f"Created overlay for monitor {i}: {geometry.width}x{geometry.height} at ({geometry.x}, {geometry.y})")
        else:
            # Fallback to single overlay
            overlay = FullScreenOverlay()
            self.overlays.append(overlay)
            print("No display found, created single overlay")
    
    def show_all(self):
        """Show all overlays"""
        for overlay in self.overlays:
            overlay.show_all()
    
    def hide_all(self):
        """Hide all overlays"""
        for overlay in self.overlays:
            overlay.hide()
    
    def update_timer(self, seconds):
        """Update timer on all overlays"""
        for overlay in self.overlays:
            overlay.update_timer(seconds)
    
    def destroy_all(self):
        """Destroy all overlays"""
        for overlay in self.overlays:
            overlay.destroy()
        self.overlays.clear()

def test_multi_overlay():
    """Test multi-display overlay functionality"""
    print("Testing multi-display overlay...")
    print("You should see overlays on all your connected displays")
    print("Each overlay will show a 30-second countdown")
    
    try:
        overlay = MultiDisplayOverlay()
        overlay.show_all()
        print("✓ Multi-display overlay created successfully")
        
        # Update timer every second for 30 seconds
        def update_timer():
            nonlocal overlay
            current_time = int(overlay.overlays[0].timer_label.get_text())
            if current_time > 0:
                overlay.update_timer(current_time - 1)
                print(f"Timer: {current_time} seconds remaining")
                return True
            else:
                print("✓ Multi-overlay test completed - closing overlays")
                overlay.destroy_all()
                Gtk.main_quit()
                return False
        
        GLib.timeout_add_seconds(1, update_timer)
        Gtk.main()
        print("✓ Multi-display overlay test completed successfully")
        return True
    except Exception as e:
        print(f"✗ Multi-display overlay failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting multi-display overlay test...")
    print("=" * 50)
    overlay_ok = test_multi_overlay()
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Multi-Display Overlay: {'✓ PASS' if overlay_ok else '✗ FAIL'}") 