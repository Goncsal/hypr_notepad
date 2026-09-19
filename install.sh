#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
config_home=${XDG_CONFIG_HOME:-"$HOME/.config"}
data_home=${XDG_DATA_HOME:-"$HOME/.local/share"}
bin_home=${HOME}/.local/bin
app_home=${data_home}/hypr-notepad
hypr_dir=${config_home}/hypr
hypr_config=${hypr_dir}/hyprland.conf
hypr_lua=${hypr_dir}/hyprland.lua

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required" >&2
  exit 1
}

python3 -c 'import gi; gi.require_version("Gtk", "3.0"); gi.require_version("Vte", "2.91")' 2>/dev/null || {
  echo "GTK 3, VTE 2.91, and their Python bindings are required." >&2
  echo "Arch: sudo pacman -S python-gobject gtk3 vte3" >&2
  exit 1
}

python3 -m venv --system-site-packages "$app_home/venv"
"$app_home/venv/bin/python" -m pip install --no-build-isolation --no-deps --upgrade "$project_dir"
mkdir -p "$data_home/applications" "$hypr_dir" "$bin_home"
ln -sf "$app_home/venv/bin/hypr-notepad" "$bin_home/hypr-notepad"
install -m 0755 "$project_dir/scripts/hypr-notepad-position" "$bin_home/hypr-notepad-position"
install -m 0644 "$project_dir/assets/hypr-notepad.desktop" "$data_home/applications/"

hypr_version=$(Hyprland --version 2>/dev/null | sed -n 's/.*Hyprland v\{0,1\}\([0-9][0-9.]*\).*/\1/p' | head -n 1)
if [ -n "$hypr_version" ] && [ "$(printf '%s\n' "$hypr_version" 0.53.0 | sort -V | head -n 1)" = "0.53.0" ]; then
  rules_file="$project_dir/hypr/hypr-notepad.conf"
else
  rules_file="$project_dir/hypr/hypr-notepad-legacy.conf"
fi
generated_rules=$(mktemp)
trap 'rm -f "$generated_rules"' EXIT HUP INT TERM
sed "s|exec, hypr-notepad|exec, $bin_home/hypr-notepad|" "$rules_file" > "$generated_rules"
install -m 0644 "$generated_rules" "$hypr_dir/hypr-notepad.conf"

source_line="source = $hypr_dir/hypr-notepad.conf"
if [ -f "$hypr_config" ]; then
  grep -Fqx "$source_line" "$hypr_config" || printf '\n%s\n' "$source_line" >> "$hypr_config"
else
  printf '%s\n' "$source_line" > "$hypr_config"
fi

if [ -f "$hypr_lua" ]; then
  generated_lua=$(mktemp)
  sed -e "s|@EXEC@|$bin_home/hypr-notepad|" \
      -e "s|@POSITIONER@|$bin_home/hypr-notepad-position|" \
      "$project_dir/hypr/hypr-notepad.lua" > "$generated_lua"
  install -m 0644 "$generated_lua" "$hypr_dir/hypr-notepad.lua"
  rm -f "$generated_lua"
  lua_line="dofile(\"$hypr_dir/hypr-notepad.lua\")"
  grep -Fqx "$lua_line" "$hypr_lua" || printf '\n%s\n' "$lua_line" >> "$hypr_lua"
fi

command -v hyprctl >/dev/null 2>&1 && hyprctl reload >/dev/null 2>&1 || true
echo "Hypr Notepad installed. Press \$mainMod+N to open it."
