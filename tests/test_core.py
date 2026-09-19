from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from hypr_notepad.core import editor_command, note_path, notes_directory


class NotesDirectoryTests(TestCase):
    def test_uses_existing_desktop(self) -> None:
        home = Path("/home/user")
        desktop = home / "Desktop"
        with patch.object(Path, "is_dir", return_value=True):
            self.assertEqual(notes_directory(home, desktop), desktop / "Notes")

    def test_falls_back_to_home(self) -> None:
        home = Path("/home/user")
        desktop = home / "Desktop"
        with patch.object(Path, "is_dir", return_value=False):
            self.assertEqual(notes_directory(home, desktop), home / "Notes")


class NotePathTests(TestCase):
    def test_adds_markdown_extension(self) -> None:
        self.assertEqual(note_path(Path("/notes"), "ideas"), Path("/notes/ideas.md"))

    def test_preserves_extension(self) -> None:
        self.assertEqual(note_path(Path("/notes"), "todo.txt"), Path("/notes/todo.txt"))

    def test_rejects_paths(self) -> None:
        for name in ("", "../secret", "folder/note", "folder\\note"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                note_path(Path("/notes"), name)


class EditorCommandTests(TestCase):
    def test_visual_has_priority_and_supports_arguments(self) -> None:
        self.assertEqual(
            editor_command({"VISUAL": "nvim -f", "EDITOR": "nano"}),
            ["nvim", "-f"],
        )

