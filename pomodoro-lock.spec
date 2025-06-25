# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the current directory
current_dir = Path.cwd()

# Define the main script
main_script = current_dir / 'src' / 'pomodoro-ui-crossplatform.py'

# Define the icon
icon_file = current_dir / 'pomodoro-lock-24.png'

# Platform-specific settings
is_windows = sys.platform.startswith('win')

# Define the analysis
a = Analysis(
    [str(main_script)],
    pathex=[str(current_dir)],
    binaries=[],
    datas=[],
    hiddenimports=[
        # Core modules
        'psutil',
        'json',
        'threading',
        'logging',
        'time',
        'signal',
        'pathlib',
        
        # Platform abstraction
        'platform_abstraction',
        'platform_abstraction.linux',
        'platform_abstraction.windows',
        'platform_abstraction.__init__',
        
        # GUI modules
        'gui',
        'gui.gtk_ui',
        'gui.tkinter_ui',
        'gui.__init__',
        
        # Windows-specific imports
        'win10toast' if is_windows else None,
        'pystray' if is_windows else None,
        'PIL' if is_windows else None,
        'win32api' if is_windows else None,
        'win32con' if is_windows else None,
        'win32gui' if is_windows else None,
        'win32process' if is_windows else None,
        
        # Linux-specific imports (these are usually system packages)
        'gi' if not is_windows else None,
        'gi.repository' if not is_windows else None,
        'gi.repository.Gtk' if not is_windows else None,
        'gi.repository.GLib' if not is_windows else None,
        'gi.repository.Notify' if not is_windows else None,
        'gi.repository.AppIndicator3' if not is_windows else None,
        'Xlib' if not is_windows else None,
        'Xlib.display' if not is_windows else None,
        'Xlib.ext.randr' if not is_windows else None,
        'notify2' if not is_windows else None,
    ],
    hookspath=[str(current_dir / 'hooks')],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove None values from hiddenimports
a.hiddenimports = [imp for imp in a.hiddenimports if imp is not None]

# Platform-specific data files
if is_windows:
    # Windows-specific data files
    a.datas += [
        # Add any Windows-specific data files here
    ]
else:
    # Linux-specific data files
    a.datas += [
        # Add any Linux-specific data files here
    ]

# Define the PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Define the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pomodoro-lock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_file) if icon_file.exists() else None,
) 