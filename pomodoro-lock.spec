# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/pomodoro-ui-crossplatform.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/platform_abstraction', 'platform_abstraction'),
        ('src/gui', 'gui'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.messagebox',
        'win32api',
        'win32con',
        'win32gui',
        'winreg',
        'win10toast',
        'pystray',
        'PIL',
        'PIL.Image',
        'notify2',
        'gi',
        'gi.repository.Gtk',
        'gi.repository.GLib',
        'gi.repository.Gdk',
        'gi.repository.Notify',
        'gi.repository.AppIndicator3',
        'Xlib',
        'Xlib.display',
    ],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='pomodoro-lock-24.png',
) 