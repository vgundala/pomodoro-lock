import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

win = Gtk.Window()
win.set_decorated(False)
win.set_keep_above(True)
win.set_default_size(300, 100)
win.move(50, 50)
label = Gtk.Label(label="Test Timer")
win.add(label)
win.show_all()
Gtk.main() 