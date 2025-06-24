# PyInstaller hook for gui module

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all submodules
hiddenimports = collect_submodules('gui')

# Add specific imports that might be missed
hiddenimports += [
    'gui.gtk_ui',
    'gui.tkinter_ui',
    'gui.__init__',
]

# Collect data files if any
datas = collect_data_files('gui') 