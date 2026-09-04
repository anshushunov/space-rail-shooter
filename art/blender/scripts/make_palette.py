"""Генерирует palette.png для Blender и копию для Godot. Запуск: blender -b --python этот_файл."""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART_BLENDER = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ART_BLENDER)

from lib import palette  # noqa: E402

OUT = os.path.join(ART_BLENDER, "palette.png")
GODOT_OUT = os.path.join(REPO, "game", "assets", "textures", "palette.png")

palette.write_png(OUT)
os.makedirs(os.path.dirname(GODOT_OUT), exist_ok=True)
shutil.copyfile(OUT, GODOT_OUT)

# Контроль: прочитать обратно и сверить центр ячейки (0,0).
import bpy  # noqa: E402

check = bpy.data.images.load(OUT)
w = check.size[0]
c = palette.CELL_PX // 2
i = (c * w + c) * 4
got = tuple(round(v, 3) for v in check.pixels[i:i + 3])
want = tuple(round(v, 3) for v in palette.hex_to_rgb(palette.COLORS[(0, 0)]))
print("PALETTE_WRITTEN", OUT, check.size[:], "cell00", got, "want", want)
if any(abs(a - b) > 2 / 255 for a, b in zip(got, want)):
    raise SystemExit("PALETTE_COLOR_MISMATCH")
