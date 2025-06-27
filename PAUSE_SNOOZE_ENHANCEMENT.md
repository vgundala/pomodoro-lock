# Pause/Snooze Enhancement - Timer Window

## Overview
Added a pause/snooze button to the top-right corner of the timer window that allows users to pause the timer when they receive the 2-minute notification before the break overlay appears. The timer automatically resumes after 10 minutes, or users can manually resume it earlier.

## Problem Solved
When users receive the 2-minute notification before a break, they often need a few more minutes to finish their current task. The pause/snooze functionality provides a quick way to pause their work and automatically resume after 10 minutes, giving them time to complete their task without disrupting their workflow.

## Implementation Details

### 1. Button Design
- **Location**: Top-right corner of timer window
- **Icon**: ⏸ (pause) when running, ▶ (play) when paused
- **Color**: Teal (#4ecdc4) to distinguish from other buttons
- **Tooltip**: "Pause/Snooze for 10 minutes" / "Resume timer"

### 2. Functionality
- **When Timer is Running**:
  - Pauses the timer
  - Sets up auto-resume timer for 10 minutes
  - Sends notification: "Timer paused. Will resume in 10 minutes"
  - Changes button to play icon (▶)

- **When Timer is Paused**:
  - Manually resumes the timer from current state
  - Cancels any pending auto-resume timer
  - Sends notification: "Timer resumed!"
  - Changes button back to pause icon (⏸)

- **Auto-Resume**:
  - Automatically resumes timer after 10 minutes
  - Sends notification: "Timer resumed automatically!"
  - Resumes from the exact time when paused

### 3. Cross-Platform Support

#### Linux (GTK)
```python
# Button creation in TimerWindow.__init__()
self.pause_snooze_button = Gtk.Button(label="⏸")
self.pause_snooze_button.set_halign(Gtk.Align.END)
self.pause_snooze_button.set_valign(Gtk.Align.START)
self.pause_snooze_button.set_margin_end(5)
self.pause_snooze_button.set_margin_top(5)
```

#### Windows (Tkinter)
```python
# Button creation in TimerWindow.__init__()
self.pause_snooze_button = tk.Button(
    button_frame,
    text="⏸",
    fg='#4ecdc4',
    command=self._on_pause_snooze_clicked
)
self.pause_snooze_button.pack(side='right')
```

### 4. Integration with Main Application

#### Timer Window Constructor Update
```python
def __init__(self, on_close=None, on_power=None, on_pause_snooze=None):
    # Added on_pause_snooze callback parameter
```

#### Main Application Handler
```python
def _on_pause_snooze_clicked(self):
    """Handle pause/snooze button click"""
    try:
        if self.is_paused:
            # Manually resume timer
            self.is_paused = False
            # Cancel any pending auto-resume timer
            if self.snooze_timer and self.snooze_timer.is_alive():
                self.snooze_timer.cancel()
            # Send notification and update GUI
        else:
            # Pause timer and set up auto-resume after 10 minutes
            self.is_paused = True
            snooze_seconds = 10 * 60
            # Store current time when paused
            self.paused_time = self.current_time
            # Set up auto-resume timer
            self.snooze_timer = threading.Timer(snooze_seconds, self._auto_resume_timer)
            self.snooze_timer.daemon = True
            self.snooze_timer.start()
            # Send notification and update GUI
    except Exception as e:
        logging.error(f"Error in pause/snooze functionality: {e}")

def _auto_resume_timer(self):
    """Automatically resume the timer after snooze period"""
    try:
        if self.is_paused:
            self.is_paused = False
            # Send notification and update GUI
    except Exception as e:
        logging.error(f"Error in auto-resume functionality: {e}")
```

### 5. Visual Feedback

#### Button State Changes
- **Running State**: Shows ⏸ (pause icon)
- **Paused State**: Shows ▶ (play icon)
- **Tooltip Updates**: Reflects current action (pause/snooze vs resume)

#### Timer Window Styling
- **Paused State**: Timer window background changes to orange (#ffa500)
- **Work State**: Timer window background is dark gray (#333333)
- **Break State**: Timer window background is red (#dc143c)

## User Experience

### Workflow
1. User is working and timer is running
2. 2 minutes before break, notification appears: "Break starting in 2 minutes!"
3. User clicks pause/snooze button (⏸) in top-right corner
4. Timer pauses and sets up auto-resume for 10 minutes
5. Notification: "Timer paused. Will resume in 10 minutes"
6. Button changes to play icon (▶)
7. User can continue working or take a short break
8. After 10 minutes, timer automatically resumes
9. Notification: "Timer resumed automatically!"
10. Timer continues from where it was paused
11. **Alternative**: User can click play button (▶) anytime to manually resume early

### Benefits
- **Non-disruptive**: Quick one-click action
- **Flexible**: Can be used multiple times if needed
- **Visual Feedback**: Clear indication of timer state
- **Notification Integration**: Keeps user informed of actions
- **Cross-Platform**: Consistent experience on Linux and Windows

## Technical Implementation

### Files Modified
1. **`src/gui/gtk_ui.py`**: Linux GTK implementation (recursion protection, robust error handling, overlay recreation)
2. **`src/gui/tkinter_ui.py`**: Windows Tkinter implementation
3. **`src/pomodoro-ui-crossplatform.py`**: Main application integration (overlay recreation, error handling)
4. **`test-recursion-fix.py`**: Automated test for recursion and monitor change handling

### Key Methods Added/Updated
- `TimerWindow.raise_()` / `lower()`: Now use correct GTK methods and are protected against recursion
- `FullScreenOverlay.raise_()`: Now uses correct GTK method and is protected against recursion
- `MultiDisplayOverlay`: All methods have error handling for recursion and monitor changes
- `PomodoroTimer._recreate_overlays()`: Recreates overlays on monitor change or error

### Error Handling and Robustness
- All GUI operations are wrapped in try/except blocks
- RecursionError is specifically caught and handled
- Overlay recreation is triggered on error
- Application logs errors and continues running
- Automated test script verifies all fixes

## Testing

### Test Script
Created `test-pause-snooze.py` to verify:
- Button creation and positioning
- Button state changes (pause/play icons)
- Callback functionality
- Main application integration
- Cross-platform compatibility

### Test Cases
1. **Button Creation**: Verify button exists and is positioned correctly
2. **Initial State**: Button shows pause icon (⏸) when timer is running
3. **Pause Action**: Clicking button pauses timer and adds 10 minutes
4. **Paused State**: Button shows play icon (▶) when timer is paused
5. **Resume Action**: Clicking button resumes timer from current state
6. **Notifications**: Proper notifications are sent for pause/resume actions
7. **Visual Feedback**: Timer window styling changes appropriately

## Future Enhancements

### Potential Improvements
1. **Configurable Snooze Time**: Allow users to set custom snooze duration
2. **Multiple Snooze Options**: Quick buttons for 5, 10, 15 minutes
3. **Snooze History**: Track how often user snoozes
4. **Smart Snooze**: Learn user patterns and suggest optimal snooze times
5. **Snooze Limits**: Prevent infinite snoozing with maximum limits

### Configuration Options
```json
{
    "snooze_time_minutes": 10,
    "max_snooze_count": 3,
    "enable_smart_snooze": false,
    "snooze_notifications": true
}
```

## Conclusion

The pause/snooze enhancement provides a valuable user experience improvement by allowing users to quickly extend their work time when needed. The implementation is robust, cross-platform, and integrates seamlessly with the existing timer functionality.

The enhancement addresses a common user need while maintaining the simplicity and effectiveness of the Pomodoro technique. Users can now handle interruptions and task extensions without losing their focus or breaking their workflow. 