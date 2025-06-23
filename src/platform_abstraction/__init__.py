"""
Platform abstraction layer for Pomodoro Lock
Supports both Linux and Windows platforms
"""

import sys
import platform as platform_module

# Detect platform
SYSTEM = platform_module.system().lower()

if SYSTEM == "linux":
    from .linux import (
        NotificationManager,
        SystemTrayManager,
        ScreenManager,
        AutostartManager,
        FileLockManager
    )
elif SYSTEM == "windows":
    from .windows import (
        NotificationManager,
        SystemTrayManager,
        ScreenManager,
        AutostartManager,
        FileLockManager
    )
else:
    raise ImportError(f"Unsupported platform: {SYSTEM}")

__all__ = [
    'NotificationManager',
    'SystemTrayManager', 
    'ScreenManager',
    'AutostartManager',
    'FileLockManager',
    'SYSTEM'
] 