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
    
    def __init__(self, on_close=None, on_power=None, on_pause_snooze=None):
        Gtk.Window.__init__(self)
        self.on_close = on_close
        self.on_power = on_power
        self.on_pause_snooze = on_pause_snooze
        
        self.set_title("Pomodoro Lock")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_default_size(350, 120)
        
        # Set window hints to ensure proper z-order
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL)
        self.set_accept_focus(True)
        
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
        .pause-button {
            color: #4ecdc4;
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
        try:
            self.label.set_markup("<span size='x-large' weight='bold' foreground='white'>00:00</span>")
        except Exception as e:
            # Fallback to simple text if markup fails
            self.label.set_text("00:00")
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
        
        # Add tooltip for close button
        self.close_button.set_tooltip_text("Close to tray")
        
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
        
        # Add tooltip for power button
        self.power_button.set_tooltip_text("Quit Pomodoro Lock")
        
        power_style = self.power_button.get_style_context()
        power_style.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        power_style.add_class("corner-button")
        power_style.add_class("power-button")
        self.power_button.connect("clicked", self._on_power_clicked)
        self.overlay.add_overlay(self.power_button)
        
        # Pause/Snooze button (⏸) - top-right corner
        self.pause_snooze_button = Gtk.Button(label="⏸")
        self.pause_snooze_button.set_size_request(25, 25)
        self.pause_snooze_button.set_halign(Gtk.Align.END)
        self.pause_snooze_button.set_valign(Gtk.Align.START)
        self.pause_snooze_button.set_margin_end(5)
        self.pause_snooze_button.set_margin_top(5)
        
        # Add tooltip for pause/snooze button
        self.pause_snooze_button.set_tooltip_text("Pause and auto-resume in 10 minutes")
        
        pause_style = self.pause_snooze_button.get_style_context()
        pause_style.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        pause_style.add_class("corner-button")
        pause_style.add_class("pause-button")
        self.pause_snooze_button.connect("clicked", self._on_pause_snooze_clicked)
        self.overlay.add_overlay(self.pause_snooze_button)
        
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
    
    def _on_pause_snooze_clicked(self, widget):
        if self.on_pause_snooze:
            self.on_pause_snooze()
    
    def update_timer(self, seconds, state='work', is_paused=False):
        """Update the timer display"""
        try:
            minutes = seconds // 60
            secs = seconds % 60
            time_str = f"{minutes:02d}:{secs:02d}"
            
            # Ensure proper UTF-8 encoding and escape any special characters
            safe_time_str = time_str.encode('utf-8', errors='ignore').decode('utf-8')
            
            # Update label with proper markup escaping
            markup = f"<span size='x-large' weight='bold' foreground='white'>{safe_time_str}</span>"
            self.label.set_markup(markup)
            
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
            
            # Update pause/snooze button appearance
            self._update_pause_button(is_paused)
            
        except Exception as e:
            # Fallback to simple text if markup fails
            try:
                minutes = seconds // 60
                secs = seconds % 60
                time_str = f"{minutes:02d}:{secs:02d}"
                self.label.set_text(time_str)
            except Exception as fallback_error:
                # Last resort - set a safe default
                self.label.set_text("00:00")
    
    def _update_pause_button(self, is_paused):
        """Update the pause/snooze button appearance based on timer state"""
        try:
            if is_paused:
                # Show play icon when paused
                self.pause_snooze_button.set_label("▶")
                self.pause_snooze_button.set_tooltip_text("Resume timer")
            else:
                # Show pause icon when running
                self.pause_snooze_button.set_label("⏸")
                self.pause_snooze_button.set_tooltip_text("Pause and auto-resume in 10 minutes")
        except Exception as e:
            # Fallback if button update fails
            pass
    
    def show_window(self):
        """Show the timer window"""
        self.show_all()
        self.present()
    
    def hide_window(self):
        """Hide the timer window"""
        self.hide()
    
    def destroy_window(self):
        """Destroy the timer window with enhanced error handling"""
        try:
            # First hide the window to stop any active operations
            self.hide_window()
            
            # Small delay to allow GTK to process the hide operation
            import time
            time.sleep(0.01)
            
            # Disconnect any signals to prevent callbacks during destruction
            try:
                # Disconnect button signals
                self.close_button.disconnect_by_func(self._on_close_clicked)
                self.power_button.disconnect_by_func(self._on_power_clicked)
                self.pause_snooze_button.disconnect_by_func(self._on_pause_snooze_clicked)
                
                # Disconnect event box signals
                self.event_box.disconnect_by_func(self._on_button_press)
                self.event_box.disconnect_by_func(self._on_button_release)
                self.event_box.disconnect_by_func(self._on_motion)
            except Exception as e:
                # Ignore errors if no signals are connected
                pass
            
            # Now destroy the window
            self.destroy()
            
        except RecursionError as e:
            print(f"Recursion error in destroy_window: {e}")
            # Fallback to basic destroy
            try:
                self.destroy()
            except Exception as fallback_error:
                print(f"Fallback destroy also failed: {fallback_error}")
        except Exception as e:
            print(f"Error in destroy_window: {e}")
            # Try to force destroy
            try:
                self.destroy()
            except Exception as force_error:
                print(f"Force destroy also failed: {force_error}")
    
    def lower_window(self):
        """Lower the window to ensure overlay is on top"""
        try:
            # Use the correct GTK method
            self.get_window().lower()
        except RecursionError as e:
            print(f"Recursion error in lower_window: {e}")
            # Fallback - just hide the window
            self.hide()
        except Exception as e:
            print(f"Error in lower_window: {e}")
    
    def raise_window(self):
        """Raise the window back to normal level"""
        try:
            # Use the correct GTK method
            self.get_window().raise_()
        except RecursionError as e:
            print(f"Recursion error in raise_window: {e}")
            # Fallback - just show the window
            self.show_all()
        except Exception as e:
            print(f"Error in raise_window: {e}")
    
    def lower(self):
        """Lower the window (alias for lower_window)"""
        self.lower_window()
    
    def raise_(self):
        """Raise the window (alias for raise_window)"""
        self.raise_window()

class FullScreenOverlay(Gtk.Window):
    """GTK-based fullscreen overlay for Linux"""
    
    def __init__(self, monitor_index=0):
        Gtk.Window.__init__(self)
        self.set_title("Pomodoro Lock - Break Time")
        self.set_decorated(False)
        self.set_keep_above(True)
        
        # Store monitor index
        self.monitor_index = monitor_index
        
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
        self.break_label = Gtk.Label()
        try:
            self.break_label.set_text("Break Time!")
        except Exception as e:
            # Fallback to simple text if markup fails
            self.break_label.set_text("Break Time!")
        self.break_label.set_halign(Gtk.Align.CENTER)
        break_style = self.break_label.get_style_context()
        break_style.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        break_style.add_class("break-label")
        self.box.pack_start(self.break_label, False, False, 0)
        
        # Timer label
        self.timer_label = Gtk.Label()
        try:
            self.timer_label.set_text("00:00")
        except Exception as e:
            # Fallback to safe default
            self.timer_label.set_text("00:00")
        self.timer_label.set_halign(Gtk.Align.CENTER)
        timer_style = self.timer_label.get_style_context()
        timer_style.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        timer_style.add_class("timer-label")
        self.box.pack_start(self.timer_label, False, False, 0)
    
    def update_timer(self, seconds):
        """Update the timer display"""
        try:
            minutes = seconds // 60
            secs = seconds % 60
            time_str = f"{minutes:02d}:{secs:02d}"
            
            # Ensure proper UTF-8 encoding
            safe_time_str = time_str.encode('utf-8', errors='ignore').decode('utf-8')
            self.timer_label.set_text(safe_time_str)
        except Exception as e:
            # Fallback to simple text if setting fails
            try:
                minutes = seconds // 60
                secs = seconds % 60
                time_str = f"{minutes:02d}:{secs:02d}"
                self.timer_label.set_text(time_str)
            except Exception as fallback_error:
                # Last resort - set a safe default
                self.timer_label.set_text("00:00")
    
    def show_overlay(self):
        """Show the overlay on the specified monitor"""
        try:
            # Set window hints to ensure it's always on top
            self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
            self.set_keep_above(True)
            self.set_accept_focus(False)
            
            # Get the display and monitor
            display = Gdk.Display.get_default()
            if display and self.monitor_index < display.get_n_monitors():
                monitor = display.get_monitor(self.monitor_index)
                geometry = monitor.get_geometry()
                
                # Move window to the monitor and make it fullscreen
                self.move(geometry.x, geometry.y)
                self.resize(geometry.width, geometry.height)
                self.fullscreen_on_monitor(display, self.monitor_index)
            
            # Ensure window is shown and raised to top
            self.show_all()
            self.present()
            # Use the correct GTK method to avoid recursion
            try:
                self.get_window().raise_()
            except Exception as e:
                print(f"Error raising overlay window: {e}")
            
            # Force the window to stay on top
            self.set_keep_above(True)
            
        except RecursionError as e:
            # Handle recursion error specifically
            print(f"Recursion error in show_overlay: {e}")
            # Fallback to basic show without raise
            self.show_all()
            self.present()
        except Exception as e:
            # Fallback to regular fullscreen if monitor-specific positioning fails
            try:
                self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
                self.set_keep_above(True)
                self.set_accept_focus(False)
                self.fullscreen()
                self.show_all()
                self.present()
                # Use the correct GTK method to avoid recursion
                try:
                    self.get_window().raise_()
                except Exception as e:
                    print(f"Error raising overlay window: {e}")
            except Exception as fallback_error:
                print(f"Fallback show_overlay also failed: {fallback_error}")
                # Last resort - just show the window
                self.show_all()
    
    def hide_overlay(self):
        """Hide the overlay"""
        self.hide()
    
    def destroy_overlay(self):
        """Destroy the overlay with enhanced error handling"""
        try:
            # First hide the overlay to stop any active operations
            self.hide_overlay()
            
            # Small delay to allow GTK to process the hide operation
            import time
            time.sleep(0.01)
            
            # Disconnect any signals to prevent callbacks during destruction
            try:
                # Disconnect all signals from this window
                self.disconnect_by_func(self._on_key_press)
            except Exception as e:
                # Ignore errors if no signals are connected
                pass
            
            # Now destroy the window
            self.destroy()
            
        except RecursionError as e:
            print(f"Recursion error in destroy_overlay: {e}")
            # Fallback to basic destroy
            try:
                self.destroy()
            except Exception as fallback_error:
                print(f"Fallback destroy also failed: {fallback_error}")
        except Exception as e:
            print(f"Error in destroy_overlay: {e}")
            # Try to force destroy
            try:
                self.destroy()
            except Exception as force_error:
                print(f"Force destroy also failed: {force_error}")
    
    def raise_(self):
        """Raise the overlay (alias for raise_window)"""
        try:
            # Use the correct GTK method name
            self.get_window().raise_()
        except Exception as e:
            print(f"Error in FullScreenOverlay.raise_(): {e}")
            # Fallback to just showing the window
            self.show_all()

class MultiDisplayOverlay:
    """GTK-based multi-display overlay manager for Linux"""
    
    def __init__(self):
        self.overlays = []
        self.display = Gdk.Display.get_default()
    
    def create_overlays(self):
        """Create overlays for all connected displays"""
        try:
            if not self.display:
                print("No display available")
                return
            
            # Clear existing overlays
            self.destroy_all()
            
            # Get number of monitors
            n_monitors = self.display.get_n_monitors()
            print(f"Creating overlays for {n_monitors} monitors")
            
            # Create overlay for each monitor
            for i in range(n_monitors):
                try:
                    print(f"Creating overlay for monitor {i}")
                    overlay = FullScreenOverlay(monitor_index=i)
                    self.overlays.append(overlay)
                except Exception as e:
                    # Log error but continue with other monitors
                    print(f"Failed to create overlay for monitor {i}: {e}")
            
            print(f"Successfully created {len(self.overlays)} overlays")
        except Exception as e:
            print(f"Error creating overlays: {e}")
    
    def show_all(self):
        """Show all overlays"""
        print(f"Showing {len(self.overlays)} overlays")
        for i, overlay in enumerate(self.overlays):
            try:
                print(f"Showing overlay {i}")
                overlay.show_overlay()
            except RecursionError as e:
                print(f"Recursion error showing overlay {i}: {e}")
                # Skip this overlay to prevent infinite recursion
                continue
            except Exception as e:
                print(f"Failed to show overlay {i}: {e}")
    
    def hide_all(self):
        """Hide all overlays"""
        print(f"Hiding {len(self.overlays)} overlays")
        for i, overlay in enumerate(self.overlays):
            try:
                print(f"Hiding overlay {i}")
                overlay.hide_overlay()
            except RecursionError as e:
                print(f"Recursion error hiding overlay {i}: {e}")
                # Skip this overlay to prevent infinite recursion
                continue
            except Exception as e:
                print(f"Failed to hide overlay {i}: {e}")
    
    def update_timer(self, seconds):
        """Update timer on all overlays"""
        for i, overlay in enumerate(self.overlays):
            try:
                overlay.update_timer(seconds)
            except RecursionError as e:
                print(f"Recursion error updating overlay {i} timer: {e}")
                # Skip this overlay to prevent infinite recursion
                continue
            except Exception as e:
                print(f"Failed to update overlay {i} timer: {e}")
    
    def destroy_all(self):
        """Destroy all overlays with enhanced error handling"""
        print(f"Destroying {len(self.overlays)} overlays")
        
        # Create a copy of the list to avoid modification during iteration
        overlays_to_destroy = list(self.overlays)
        self.overlays.clear()  # Clear the list immediately to prevent further access
        
        for i, overlay in enumerate(overlays_to_destroy):
            if overlay is None:
                continue
                
            try:
                print(f"Destroying overlay {i}")
                
                # First hide the overlay to prevent any active operations
                try:
                    overlay.hide_overlay()
                except Exception as hide_error:
                    print(f"Error hiding overlay {i} before destroy: {hide_error}")
                
                # Small delay to allow GTK to process the hide operation
                import time
                time.sleep(0.01)
                
                # Now destroy the overlay
                overlay.destroy_overlay()
                
            except RecursionError as e:
                print(f"Recursion error destroying overlay {i}: {e}")
                # Force destroy by setting overlay to None
                overlays_to_destroy[i] = None
                continue
            except Exception as e:
                print(f"Failed to destroy overlay {i}: {e}")
                # Try to force destroy the window
                try:
                    if hasattr(overlay, 'destroy') and overlay.destroy:
                        overlay.destroy()
                except Exception as force_error:
                    print(f"Force destroy also failed for overlay {i}: {force_error}")
        
        # Final cleanup - ensure the list is empty
        self.overlays.clear()
        print("Overlay destruction completed") 