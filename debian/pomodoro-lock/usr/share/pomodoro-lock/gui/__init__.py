"""
Cross-platform GUI abstraction layer for Pomodoro Lock
"""

import sys
import platform as platform_module

# Detect platform
SYSTEM = platform_module.system().lower()

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