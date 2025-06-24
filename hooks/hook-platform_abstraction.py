# PyInstaller hook for platform_abstraction module

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all submodules
hiddenimports = collect_submodules('platform_abstraction')

# Add specific imports that might be missed
hiddenimports += [
    'platform_abstraction.linux',
    'platform_abstraction.windows',
    'platform_abstraction.__init__',
]

# Collect data files if any
datas = collect_data_files('platform_abstraction') 