from __future__ import annotations

import os
import sys
from importlib.resources import files
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gdk, Gio, GLib, Gtk, Vte  # noqa: E402

from .core import editor_command, note_path, notes_directory


APP_ID = "io.github.goncsal.HyprNotepad"


class NoteWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application, path: Path, command: list[str]) -> None:
        super().__init__(application=application, title=f"Hypr Notepad - {path.name}")
        self.set_default_size(720, 480)
        self.set_size_request(420, 280)
        self._child_running = True
        self._close_approved = False

        self.terminal = Vte.Terminal()
        self.terminal.set_hexpand(True)
        self.terminal.set_vexpand(True)
        self.terminal.set_scrollback_lines(5_000)
        self.add(self.terminal)
        self.connect("delete-event", self._on_close_request)
        self.terminal.connect("child-exited", self._on_child_exited)

        argv = [*command, str(path)]
        self.terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            str(path.parent),
            argv,
            None,
            GLib.SpawnFlags.SEARCH_PATH,
            None,
            None,
            -1,
            None,
            self._on_spawned,
            None,
        )

    def _on_spawned(
        self,
        _terminal: Vte.Terminal,
        _pid: int,
        error: GLib.Error | None,
        _user_data: object,
    ) -> None:
        if error is not None:
            self._child_running = False
            show_error(self, "Could not start the editor", error.message)

    def _on_child_exited(self, _terminal: Vte.Terminal, _status: int) -> None:
        self._child_running = False
        self._close_approved = True
        self.destroy()

    def _on_close_request(self, _window: Gtk.Window, _event: object) -> bool:
        if self._close_approved or not self._child_running:
            return False

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.NONE,
            text="Close this note?",
        )
        dialog.format_secondary_text("Changes not saved in your editor will be lost.")
        dialog.add_button("Keep editing", Gtk.ResponseType.CANCEL)
        dialog.add_button("Close", Gtk.ResponseType.ACCEPT)
        dialog.set_default_response(Gtk.ResponseType.CANCEL)
        answer = dialog.run()
        dialog.destroy()
        if answer == Gtk.ResponseType.ACCEPT:
            self._close_approved = True
            return False
        return True


class HyprNotepad(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.NON_UNIQUE)

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)
        provider = Gtk.CssProvider()
        provider.load_from_path(str(files("hypr_notepad").joinpath("style.css")))
        screen = Gdk.Screen.get_default()
        if screen is not None:
            Gtk.StyleContext.add_provider_for_screen(
                screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def do_activate(self) -> None:
        dialog = Gtk.Dialog(title="New note", application=self, modal=True)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Open", Gtk.ResponseType.ACCEPT)
        dialog.set_default_response(Gtk.ResponseType.ACCEPT)
        dialog.set_resizable(False)

        content = dialog.get_content_area()
        content.set_border_width(18)
        content.set_spacing(10)
        label = Gtk.Label(label="Choose a name for the note.", xalign=0)
        entry = Gtk.Entry(placeholder_text="Note name")
        entry.set_activates_default(True)
        content.pack_start(label, False, False, 0)
        content.pack_start(entry, False, False, 0)
        dialog.show_all()
        answer = dialog.run()
        name = entry.get_text()
        dialog.destroy()
        if answer != Gtk.ResponseType.ACCEPT:
            self.quit()
            return

        try:
            directory = notes_directory(Path.home())
            path = note_path(directory, name)
            command = editor_command()
            directory.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
        except (OSError, RuntimeError, ValueError) as error:
            show_error(None, "Could not open the note", str(error), self.quit)
            return

        window = NoteWindow(self, path, command)
        window.show_all()
        window.present()


def show_error(
    parent: Gtk.Window | None,
    message: str,
    detail: str,
    callback: object | None = None,
) -> None:
    dialog = Gtk.MessageDialog(
        transient_for=parent,
        modal=True,
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=message,
    )
    dialog.format_secondary_text(detail)
    dialog.run()
    dialog.destroy()
    if callable(callback):
        callback()


def main() -> int:
    return HyprNotepad().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
