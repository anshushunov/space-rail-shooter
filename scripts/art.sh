#!/usr/bin/env bash
# Единая точка входа арт-пайплайна. Запуск из любого места: scripts/art.sh <команда>.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BLENDER="${BLENDER:-/c/Program Files/Blender Foundation/Blender 5.2/blender.exe}"
GODOT="${GODOT:-/c/gamedev/Godot_v4.7.1-stable_mono_win64/Godot_v4.7.1-stable_mono_win64_console.exe}"

# --python-exit-code ДО --python: Blender обрабатывает аргументы последовательно,
# после --python скрипт уже выполнен и флаг не влияет на код возврата.
blender_run() { "$BLENDER" -b --python-exit-code 1 --python "$1"; }

cmd="${1:-}"
shift || true
case "$cmd" in
  test)         (cd "$ROOT" && python -m unittest discover -s art/tests -v) ;;
  make-palette) blender_run "$ROOT/art/blender/scripts/make_palette.py" ;;
  ship)         blender_run "$ROOT/art/blender/scripts/ship.py" ;;
  export)       blender_run "$ROOT/art/export.py" ;;
  check)        blender_run "$ROOT/art/check_models.py" ;;
  import)       "$GODOT" --headless --path "$ROOT/game" --import ;;
  shot)         "$GODOT" --path "$ROOT/game" -s res://tools/screenshot.gd -- "${1:-2.5}" "${2:-res://../docs/playtests/shot.png}" ;;
  *)
    echo "usage: scripts/art.sh {test|make-palette|ship|export|check|import|shot [sec] [res://out.png]}" >&2
    exit 2 ;;
esac
