"""
Tkinter-based GUI implementation for Windows
"""

import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox

class TimerWindow(tk.Toplevel):
    """Tkinter-based timer window for Windows"""
    
    def __init__(self, parent=None, on_close=None, on_power=None, on_pause_snooze=None):
        super().__init__(parent)
        self.on_close = on_close
        self.on_power = on_power
        self.on_pause_snooze = on_pause_snooze
        
        self.title("Pomodoro Lock")
        self.overrideredirect(True)  # Remove window decorations
        self.attributes('-topmost', True)
        self.geometry("350x120")
        
        # Position window at bottom-left
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = 0
        y = screen_height - 120
        self.geometry(f"350x120+{x}+{y}")
        
        # Configure window styling
        self.configure(bg='#333333')
        
        # Create main frame
        self.main_frame = tk.Frame(self, bg='#333333', relief='flat', bd=0)
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Timer label
        self.timer_label = tk.Label(
            self.main_frame,
            text="00:00",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#333333'
        )
        self.timer_label.pack(expand=True)
        
        # Button frame
        button_frame = tk.Frame(self.main_frame, bg='#333333')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Close button (X)
        self.close_button = tk.Button(
            button_frame,
            text="✕",
            font=('Arial', 12, 'bold'),
            fg='#ff6b6b',
            bg='#333333',
            bd=0,
            relief='flat',
            command=self._on_close_clicked,
            width=3,
            height=1
        )
        self.close_button.pack(side='left')
        
        # Add tooltip for close button
        self._create_tooltip(self.close_button, "Close to tray")
        
        # Power button
        self.power_button = tk.Button(
            button_frame,
            text="⏻",
            font=('Arial', 12, 'bold'),
            fg='#ffa726',
            bg='#333333',
            bd=0,
            relief='flat',
            command=self._on_power_clicked,
            width=3,
            height=1
        )
        self.power_button.pack(side='left', padx=(5, 0))
        
        # Add tooltip for power button
        self._create_tooltip(self.power_button, "Quit Pomodoro Lock")
        
        # Pause/Snooze button
        self.pause_snooze_button = tk.Button(
            button_frame,
            text="⏸",
            font=('Arial', 12, 'bold'),
            fg='#4ecdc4',
            bg='#333333',
            bd=0,
            relief='flat',
            command=self._on_pause_snooze_clicked,
            width=3,
            height=1
        )
        self.pause_snooze_button.pack(side='right')
        
        # Add tooltip for pause/snooze button
        self._create_tooltip(self.pause_snooze_button, "Pause and auto-resume in 10 minutes")
        
        # Bind mouse events for dragging
        self.bind('<Button-1>', self._on_button_press)
        self.bind('<B1-Motion>', self._on_motion)
        self.bind('<ButtonRelease-1>', self._on_button_release)
        
        # Mouse drag variables
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # State tracking
        self.current_state = 'work'
        self.is_paused = False
    
    def _create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, 
                           justify='left',
                           background="#ffffe0", 
                           relief='solid', 
                           borderwidth=1,
                           font=("Arial", "8", "normal"))
            label.pack()
            
            def hide_tooltip(event):
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', hide_tooltip)
            tooltip.bind('<Leave>', hide_tooltip)
        
        widget.bind('<Enter>', show_tooltip)
    
    def _on_button_press(self, event):
        """Handle mouse button press for dragging"""
        self.dragging = True
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
    
    def _on_motion(self, event):
        """Handle mouse motion for dragging"""
        if self.dragging:
            new_x = self.winfo_x() + (event.x_root - self.drag_start_x)
            new_y = self.winfo_y() + (event.y_root - self.drag_start_y)
            self.geometry(f"+{new_x}+{new_y}")
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
    
    def _on_button_release(self, event):
        """Handle mouse button release"""
        self.dragging = False
    
    def _on_close_clicked(self):
        """Handle close button click"""
        if self.on_close:
            self.on_close()
        else:
            self.withdraw()
    
    def _on_power_clicked(self):
        """Handle power button click"""
        if self.on_power:
            self.on_power()
    
    def _on_pause_snooze_clicked(self):
        """Handle pause/snooze button click"""
        if self.on_pause_snooze:
            self.on_pause_snooze()
    
    def update_timer(self, seconds, state='work', is_paused=False):
        """Update the timer display"""
        minutes = seconds // 60
        secs = seconds % 60
        time_str = f"{minutes:02d}:{secs:02d}"
        
        # Update label
        self.timer_label.config(text=time_str)
        
        # Update colors based on state
        if is_paused:
            self._set_paused_style()
        elif state == "break":
            self._set_break_style()
        else:
            self._set_work_style()
        
        # Update pause/snooze button appearance
        self._update_pause_button(is_paused)
    
    def _update_pause_button(self, is_paused):
        """Update the pause/snooze button appearance based on timer state"""
        try:
            if is_paused:
                # Show play icon when paused
                self.pause_snooze_button.config(text="▶")
                self._create_tooltip(self.pause_snooze_button, "Resume timer")
            else:
                # Show pause icon when running
                self.pause_snooze_button.config(text="⏸")
                self._create_tooltip(self.pause_snooze_button, "Pause and auto-resume in 10 minutes")
        except Exception as e:
            # Fallback if button update fails
            pass
    
    def _set_work_style(self):
        """Set work state styling"""
        if self.current_state != 'work' or self.is_paused:
            self.configure(bg='#333333')
            self.main_frame.configure(bg='#333333')
            self.timer_label.configure(bg='#333333')
            self.close_button.configure(bg='#333333')
            self.power_button.configure(bg='#333333')
            self.pause_snooze_button.configure(bg='#333333')
            self.current_state = 'work'
            self.is_paused = False
    
    def _set_paused_style(self):
        """Set paused state styling"""
        if not self.is_paused:
            self.configure(bg='#ffa500')
            self.main_frame.configure(bg='#ffa500')
            self.timer_label.configure(bg='#ffa500')
            self.close_button.configure(bg='#ffa500')
            self.power_button.configure(bg='#ffa500')
            self.pause_snooze_button.configure(bg='#ffa500')
            self.is_paused = True
    
    def _set_break_style(self):
        """Set break state styling"""
        if self.current_state != 'break' or self.is_paused:
            self.configure(bg='#dc143c')
            self.main_frame.configure(bg='#dc143c')
            self.timer_label.configure(bg='#dc143c')
            self.close_button.configure(bg='#dc143c')
            self.power_button.configure(bg='#dc143c')
            self.pause_snooze_button.configure(bg='#dc143c')
            self.current_state = 'break'
            self.is_paused = False
    
    def show_window(self):
        """Show the timer window"""
        self.deiconify()
        self.lift()
        self.focus_force()
    
    def hide_window(self):
        """Hide the timer window"""
        self.withdraw()
    
    def destroy_window(self):
        """Destroy the timer window"""
        self.destroy()

class FullScreenOverlay(tk.Toplevel):
    """Tkinter-based fullscreen overlay for Windows"""
    
    def __init__(self, parent=None, screen_index=0):
        super().__init__(parent)
        self.title("Pomodoro Lock - Break Time")
        self.overrideredirect(True)
        self.attributes('-fullscreen', True)
        self.attributes('-topmost', True)
        
        # Configure window styling
        self.configure(bg='#dc143c')
        
        # Create main frame
        self.main_frame = tk.Frame(self, bg='#dc143c')
        self.main_frame.pack(fill='both', expand=True)
        
        # Center content
        center_frame = tk.Frame(self.main_frame, bg='#dc143c')
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Break label
        self.break_label = tk.Label(
            center_frame,
            text="Break Time!",
            font=('Arial', 48, 'bold'),
            fg='white',
            bg='#dc143c'
        )
        self.break_label.pack(pady=20)
        
        # Timer label
        self.timer_label = tk.Label(
            center_frame,
            text="00:00",
            font=('Arial', 72, 'bold'),
            fg='white',
            bg='#dc143c'
        )
        self.timer_label.pack(pady=20)
    
    def update_timer(self, seconds):
        """Update the timer display"""
        minutes = seconds // 60
        secs = seconds % 60
        time_str = f"{minutes:02d}:{secs:02d}"
        self.timer_label.config(text=time_str)
    
    def show_overlay(self):
        """Show the overlay"""
        self.deiconify()
        self.lift()
        self.focus_force()
    
    def hide_overlay(self):
        """Hide the overlay"""
        self.withdraw()
    
    def destroy_overlay(self):
        """Destroy the overlay"""
        self.destroy()

class MultiDisplayOverlay:
    """Tkinter-based multi-display overlay manager for Windows"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.overlays = []
        self._enumerate_screens()
    
    def _enumerate_screens(self):
        """Enumerate connected screens"""
        # For now, create one overlay for the primary screen
        # In a full implementation, you'd use win32api to detect multiple monitors
        pass
    
    def create_overlays(self):
        """Create overlays for all connected displays"""
        # Clear existing overlays
        self.destroy_all()
        
        # Create overlay for primary screen
        overlay = FullScreenOverlay(parent=self.parent)
        self.overlays.append(overlay)
        
        # TODO: Add support for multiple monitors using win32api
    
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