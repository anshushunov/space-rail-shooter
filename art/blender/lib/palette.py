"""Палитра 8×8 для всех моделей игры. Без импорта bpy на уровне модуля."""

SIZE = 8
CELL_PX = 32
TEXTURE_PX = SIZE * CELL_PX

# (col, row) -> цвет. row 0 — нижний ряд изображения (порядок пикселей bpy).
COLORS: dict[tuple[int, int], str] = {
    (0, 0): "#F2E9D8", (1, 0): "#D9CDB8", (2, 0): "#FFFFFF",
    (0, 1): "#F08A3C", (1, 1): "#C96A22",
    (0, 2): "#1E2A4A", (1, 2): "#2F3F6B", (2, 2): "#10162A",
    (0, 3): "#FFD23F",
    (0, 4): "#8A94A6", (1, 4): "#5B6478",
    (0, 5): "#6E5A4B", (1, 5): "#4E3F35", (2, 5): "#8C7561",
    (0, 6): "#40E0FF", (1, 6): "#A8F0FF",
    (0, 7): "#FFE566", (1, 7): "#FF4A3D", (2, 7): "#FF5AC8",
}

NAMES: dict[str, tuple[int, int]] = {
    "cream": (0, 0), "cream_dark": (1, 0), "white": (2, 0),
    "orange": (0, 1), "orange_dark": (1, 1),
    "navy": (0, 2), "navy_light": (1, 2), "black": (2, 2),
    "yellow": (0, 3),
    "gray": (0, 4), "gray_dark": (1, 4),
    "rock": (0, 5), "rock_dark": (1, 5), "rock_light": (2, 5),
    "emit_cyan": (0, 6), "emit_cyan_pale": (1, 6),
    "emit_yellow": (0, 7), "emit_red": (1, 7), "emit_magenta": (2, 7),
}

EMISSIVE_ROWS = {6, 7}


def resolve(cell) -> tuple[int, int]:
    """Имя ячейки или (col, row) -> (col, row)."""
    if isinstance(cell, str):
        return NAMES[cell]
    return (int(cell[0]), int(cell[1]))


def hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def cell_uv(cell) -> tuple[float, float]:
    col, row = resolve(cell)
    return ((col + 0.5) / SIZE, (row + 0.5) / SIZE)


def is_emissive(cell) -> bool:
    return resolve(cell)[1] in EMISSIVE_ROWS


def pixels_rgba() -> list[float]:
    """Плоский RGBA-буфер 256×256 в порядке bpy: строки снизу вверх."""
    px: list[float] = []
    for y in range(TEXTURE_PX):
        row = y // CELL_PX
        for x in range(TEXTURE_PX):
            col = x // CELL_PX
            r, g, b = hex_to_rgb(COLORS.get((col, row), "#000000"))
            px.extend((r, g, b, 1.0))
    return px


def write_png(path: str) -> None:
    """Сохраняет палитру через bpy без сторонних библиотек."""
    import bpy  # noqa: PLC0415

    img = bpy.data.images.get("palette_gen")
    if img is not None:
        bpy.data.images.remove(img)
    img = bpy.data.images.new("palette_gen", TEXTURE_PX, TEXTURE_PX, alpha=False)
    img.pixels = pixels_rgba()
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
