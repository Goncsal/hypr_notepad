# Hypr Notepad

Hypr Notepad opens a compact floating window with your preferred terminal editor. Press `SUPER+N`, enter a note name, and start writing. Notes are kept in `~/Desktop/Notes` when the Desktop directory exists, or `~/Notes` otherwise.

The app uses `$VISUAL`, then `$EDITOR`, and falls back to Neovim, Vim, Vi, or Nano. Closing the window while the editor is running asks for confirmation, protecting editor buffers that may not have been saved.

## Requirements

- Hyprland
- Python 3.11 or newer
- GTK 3 and its Python GObject bindings
- VTE 2.91 and its Python bindings
- A terminal editor

On Arch Linux, install the runtime dependencies with:

```sh
sudo pacman -S python-gobject gtk3 vte3
```

## Install

```sh
./install.sh
```

The installer creates an isolated environment under `~/.local/share/hypr-notepad` and adds a small integration file under `~/.config/hypr`. Lua-based Hyprland setups receive `hypr-notepad.lua`, while Hyprlang setups receive `hypr-notepad.conf`. It does not replace the main Hyprland configuration. Run the installer again after updating the project.

If `~/.local/bin` is not in `PATH`, add it in the environment used to start Hyprland.

## Appearance

The dedicated stylesheet is installed inside the Python package from `src/hypr_notepad/style.css`. It inherits the active GTK theme and uses the system monospace font at 12 pt by default. Change the `font-family`, `font-size`, and `padding` declarations to customize the editor window, then rerun `./install.sh`.

## Hyprland compatibility

The app does not use Hyprland internals. The installer supports Lua configuration, current Hyprlang match rules, and the legacy `windowrulev2` form. The Hyprlang binding follows `$mainMod`. The Lua integration uses `ALT`, matching the migrated configuration generated from this setup's `ALT_L` modifier.

## Development

```sh
python -m unittest discover -s tests
```

Install in editable mode for development:

```sh
python -m pip install --user -e .
```
