import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gtk, Vte, Gdk
from gi.repository import GLib


class Terminal(Vte.Terminal):

    def __init__(self):
        super(Vte.Terminal, self).__init__()

        self.spawn_async(Vte.PtyFlags.DEFAULT,
                         "/tmp",
                         ["/bin/bash"],
                         None,
                         GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                         None,
                         None,
                         -1,
                         None,
                         None
                         )

        self.set_font_scale(0.9)
        self.set_scroll_on_output(True)
        self.set_scroll_on_keystroke(True)
        palette = [Gdk.RGBA(0.4, 0.8, 1.0, 1.0)] * 16
        self.set_colors(Gdk.RGBA(1.0, 1.0, 1.0, 1.0), Gdk.RGBA(0.3, 0.3, 0.3, 1.0), palette)
        self.connect("key_press_event", self.copy_or_paste)
        self.connect("current-directory-uri-changed", self.wd_changed)

        self.set_scrollback_lines(-1)
        self.set_audible_bell(0)

    def copy_or_paste(self, widget, event):
        control_key = Gdk.ModifierType.CONTROL_MASK
        shift_key = Gdk.ModifierType.SHIFT_MASK
        if event.type == Gdk.EventType.KEY_PRESS:
            if event.state == shift_key | control_key:
                if event.keyval == 67:
                    self.copy_clipboard()
                elif event.keyval == 86:
                    self.paste_clipboard()
                return True

    def wd_changed(self, *args):
        workingDir = self.get_current_directory_uri()
        print("workingDir changed to:", workingDir)


class MyWindow(Gtk.Window):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__()

    def main(self):
        self.terminal = Terminal()
        self.cb = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        self.cb.wait_for_text()
        self.cb.set_text("python3", -1)
        self.connect('delete-event', Gtk.main_quit)
        self.scrolled_win = Gtk.ScrolledWindow()
        self.scrolled_win.add(self.terminal)
        self.add(self.scrolled_win)
        self.set_title("Terminal")
        self.resize(800, 300)
        self.move(0, 0)
        self.show_all()
        self.terminal.paste_primary()
        self.terminal.grab_focus()
        self.terminal.feed_child([13])


if __name__ == "__main__":
    win = MyWindow()
    win.main()
    Gtk.main()