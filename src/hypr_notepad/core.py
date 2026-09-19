from __future__ import annotations

import os
import shlex
import shutil
from pathlib import Path


def notes_directory(home: Path, desktop: Path | None = None) -> Path:
    """Return Desktop/Notes when Desktop exists, otherwise ~/Notes."""
    candidate = desktop if desktop is not None else home / "Desktop"
    return (candidate / "Notes") if candidate.is_dir() else (home / "Notes")


def note_path(directory: Path, name: str) -> Path:
    """Build a safe Markdown note path from a user-provided name."""
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("Enter a note name.")
    if cleaned in {".", ".."} or "/" in cleaned or "\\" in cleaned or "\0" in cleaned:
        raise ValueError("Use a name without slashes.")
    if not Path(cleaned).suffix:
        cleaned += ".md"
    return directory / cleaned


def editor_command(environ: dict[str, str] | None = None) -> list[str]:
    """Resolve the user's preferred terminal editor."""
    env = os.environ if environ is None else environ
    for variable in ("VISUAL", "EDITOR"):
        value = env.get(variable, "").strip()
        if value:
            command = shlex.split(value)
            if command:
                return command
    for candidate in ("nvim", "vim", "vi", "nano"):
        if shutil.which(candidate):
            return [candidate]
    raise RuntimeError("No terminal editor found. Set $VISUAL or $EDITOR.")

