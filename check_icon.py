import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

icon_theme = Gtk.IconTheme.get_default()
if icon_theme.has_icon("pomodoro-lock"):
    print("Icon 'pomodoro-lock' found in theme!")
else:
    print("Icon 'pomodoro-lock' NOT found in theme.")