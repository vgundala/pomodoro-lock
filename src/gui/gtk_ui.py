"""
GTK-based GUI implementation for Linux
"""

import os
import logging
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, GLib, Gdk

class TimerWindow(Gtk.Window):
    """GTK-based timer window for Linux"""
    
    def __init__(self, on_close=None, on_power=None):
        Gtk.Window.__init__(self)
        self.on_close = on_close
        self.on_power = on_power
        
        self.set_title("Pomodoro Lock")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_default_size(350, 120)
        
        # Move to left bottom
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() if display else display.get_monitor(0)
        geometry = monitor.get_geometry()
        x = geometry.x
        y = geometry.y + geometry.height - 120  # 120 is window height
        self.move(x, y)
        
        # Create event box for mouse events
        self.event_box = Gtk.EventBox()
        self.add(self.event_box)
        
        # Create a box with background color using CSS
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
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
        .timer-box.paused {
            background-color: rgba(255, 165, 0, 0.8);
        }
        .timer-box.break {
            background-color: rgba(220, 20, 60, 0.8);
        }
        .corner-button {
            background-color: transparent;
            border: none;
            outline: none;
            color: white;
            font-weight: bold;
            font-size: 16px;
            padding: 0;
            margin: 0;
            box-shadow: none;
        }
        .corner-button:hover {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
            border: none;
            outline: none;
            box-shadow: none;
        }
        .corner-button:focus {
            border: none;
            outline: none;
            box-shadow: none;
        }
        .corner-button:active {
            border: none;
            outline: none;
            box-shadow: none;
        }
        .corner-button:selected {
            border: none;
            outline: none;
            box-shadow: none;
        }
        .close-button {
            color: #ff6b6b;
        }
        .power-button {
            color: #ffa726;
        }
        """
        css_provider.load_from_data(css.encode())
        style_context = self.box.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        style_context.add_class("timer-box")
        
        self.event_box.add(self.box)
        
        # Create overlay for corner buttons
        self.overlay = Gtk.Overlay()
        self.box.pack_start(self.overlay, True, True, 0)
        
        # Timer label (centered)
        self.label = Gtk.Label()
        self.label.set_markup("<span size='x-large' weight='bold' foreground='white'>00:00</span>")
        self.label.set_halign(Gtk.Align.CENTER)
        self.label.set_valign(Gtk.Align.CENTER)
        self.overlay.add_overlay(self.label)
        
        # Close button (X) - top-left corner
        self.close_button = Gtk.Button(label="✕")
        self.close_button.set_size_request(25, 25)
        self.close_button.set_halign(Gtk.Align.START)
        self.close_button.set_valign(Gtk.Align.START)
        self.close_button.set_margin_start(5)
        self.close_button.set_margin_top(5)
        
        close_style = self.close_button.get_style_context()
        close_style.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        close_style.add_class("corner-button")
        close_style.add_class("close-button")
        self.close_button.connect("clicked", self._on_close_clicked)
        self.overlay.add_overlay(self.close_button)
        
        # Power button (stop service) - bottom-left corner
        self.power_button = Gtk.Button(label="⏻")
        self.power_button.set_size_request(25, 25)
        self.power_button.set_halign(Gtk.Align.START)
        self.power_button.set_valign(Gtk.Align.END)
        self.power_button.set_margin_start(5)
        self.power_button.set_margin_bottom(5)
        
        power_style = self.power_button.get_style_context()
        power_style.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        power_style.add_class("corner-button")
        power_style.add_class("power-button")
        self.power_button.connect("clicked", self._on_power_clicked)
        self.overlay.add_overlay(self.power_button)
        
        # Connect mouse events for dragging
        self.event_box.connect("button-press-event", self._on_button_press)
        self.event_box.connect("button-release-event", self._on_button_release)
        self.event_box.connect("motion-notify-event", self._on_motion)
        
        # Enable motion events
        self.event_box.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                                 Gdk.EventMask.BUTTON_RELEASE_MASK |
                                 Gdk.EventMask.POINTER_MOTION_MASK)

        # Mouse drag variables
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Add state tracking to prevent CSS changes on every tick
        self.current_state_key = None
    
    def _on_button_press(self, widget, event):
        if event.button == 1:  # Left click
            self.dragging = True
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
        return True

    def _on_button_release(self, widget, event):
        if event.button == 1:  # Left click
            self.dragging = False
        return True

    def _on_motion(self, widget, event):
        if self.dragging:
            # Calculate new position
            new_x = self.get_position()[0] + (event.x_root - self.drag_start_x)
            new_y = self.get_position()[1] + (event.y_root - self.drag_start_y)
            
            # Update drag start position
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
            
            # Move window
            self.move(new_x, new_y)
        return True
    
    def _on_close_clicked(self, widget):
        if self.on_close:
            self.on_close()
        else:
            self.hide()
    
    def _on_power_clicked(self, widget):
        if self.on_power:
            self.on_power()
    
    def update_timer(self, seconds, state='work', is_paused=False):
        """Update the timer display"""
        minutes = seconds // 60
        secs = seconds % 60
        time_str = f"{minutes:02d}:{secs:02d}"
        
        # Update label
        self.label.set_markup(f"<span size='x-large' weight='bold' foreground='white'>{time_str}</span>")
        
        # Update CSS classes based on state
        style_context = self.box.get_style_context()
        
        # Remove old state classes
        style_context.remove_class("paused")
        style_context.remove_class("break")
        
        # Add new state class
        if is_paused:
            style_context.add_class("paused")
        elif state == "break":
            style_context.add_class("break")
    
    def show_window(self):
        """Show the timer window"""
        self.show_all()
        self.present()
    
    def hide_window(self):
        """Hide the timer window"""
        self.hide()
    
    def destroy_window(self):
        """Destroy the timer window"""
        self.destroy()

class FullScreenOverlay(Gtk.Window):
    """GTK-based fullscreen overlay for Linux"""
    
    def __init__(self, screen_index=0):
        Gtk.Window.__init__(self)
        self.set_title("Pomodoro Lock - Break Time")
        self.set_decorated(False)
        self.fullscreen()
        self.set_keep_above(True)
        
        # Create main container
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.set_halign(Gtk.Align.CENTER)
        self.box.set_valign(Gtk.Align.CENTER)
        
        # Apply CSS styling
        css_provider = Gtk.CssProvider()
        css = """
        .break-overlay {
            background-color: rgba(220, 20, 60, 0.95);
            color: white;
        }
        .break-label {
            font-size: 48px;
            font-weight: bold;
            color: white;
            margin: 20px;
        }
        .timer-label {
            font-size: 72px;
            font-weight: bold;
            color: white;
            margin: 20px;
        }
        """
        css_provider.load_from_data(css.encode())
        style_context = self.box.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        style_context.add_class("break-overlay")
        
        self.add(self.box)
        
        # Break label
        self.break_label = Gtk.Label(label="Break Time!")
        self.break_label.set_halign(Gtk.Align.CENTER)
        break_style = self.break_label.get_style_context()
        break_style.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        break_style.add_class("break-label")
        self.box.pack_start(self.break_label, False, False, 0)
        
        # Timer label
        self.timer_label = Gtk.Label(label="00:00")
        self.timer_label.set_halign(Gtk.Align.CENTER)
        timer_style = self.timer_label.get_style_context()
        timer_style.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        timer_style.add_class("timer-label")
        self.box.pack_start(self.timer_label, False, False, 0)
    
    def update_timer(self, seconds):
        """Update the timer display"""
        minutes = seconds // 60
        secs = seconds % 60
        time_str = f"{minutes:02d}:{secs:02d}"
        self.timer_label.set_text(time_str)
    
    def show_overlay(self):
        """Show the overlay"""
        self.show_all()
        self.present()
    
    def hide_overlay(self):
        """Hide the overlay"""
        self.hide()
    
    def destroy_overlay(self):
        """Destroy the overlay"""
        self.destroy()

class MultiDisplayOverlay:
    """GTK-based multi-display overlay manager for Linux"""
    
    def __init__(self):
        self.overlays = []
        self.display = Gdk.Display.get_default()
    
    def create_overlays(self):
        """Create overlays for all connected displays"""
        if not self.display:
            return
        
        # Clear existing overlays
        self.destroy_all()
        
        # Create overlay for each monitor
        for i in range(self.display.get_n_monitors()):
            overlay = FullScreenOverlay(screen_index=i)
            self.overlays.append(overlay)
    
    def show_all(self):
        """Show all overlays"""
        for overlay in self.overlays:
            overlay.show_overlay()
    
    def hide_all(self):
        """Hide all overlays"""
        for overlay in self.overlays:
            overlay.hide_overlay()
    
    def update_timer(self, seconds):
        """Update timer on all overlays"""
        for overlay in self.overlays:
            overlay.update_timer(seconds)
    
    def destroy_all(self):
        """Destroy all overlays"""
        for overlay in self.overlays:
            overlay.destroy_overlay()
        self.overlays.clear() 