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

# Platform-specific hidden imports
if is_windows:
    hidden_imports = [
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
        'win10toast',
        'pystray',
        'PIL',
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
    ]
else:
    hidden_imports = [
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
        
        # Linux-specific imports (these are usually system packages)
        'gi',
        'gi.repository',
        'gi.repository.Gtk',
        'gi.repository.GLib',
        'gi.repository.Notify',
        'gi.repository.AppIndicator3',
        'Xlib',
        'Xlib.display',
        'Xlib.ext.randr',
        'notify2',
    ]

# Define the analysis
a = Analysis(
    [str(main_script)],
    pathex=[str(current_dir)],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[str(current_dir / 'hooks')],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

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