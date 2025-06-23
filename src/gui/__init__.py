"""
Cross-platform GUI abstraction layer for Pomodoro Lock
"""

import sys
import platform

# Detect platform
SYSTEM = platform.system().lower()

if SYSTEM == "linux":
    from .gtk_ui import (
        TimerWindow,
        FullScreenOverlay,
        MultiDisplayOverlay
    )
elif SYSTEM == "windows":
    from .tkinter_ui import (
        TimerWindow,
        FullScreenOverlay,
        MultiDisplayOverlay
    )
else:
    raise ImportError(f"Unsupported platform: {SYSTEM}")

__all__ = [
    'TimerWindow',
    'FullScreenOverlay',
    'MultiDisplayOverlay',
    'SYSTEM'
] 