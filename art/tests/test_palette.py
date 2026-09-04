import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "blender"))

from lib import palette  # noqa: E402


class PaletteTests(unittest.TestCase):
    def test_cell_uv_is_cell_center(self):
        self.assertEqual(palette.cell_uv((0, 0)), (0.0625, 0.0625))
        self.assertEqual(palette.cell_uv((7, 7)), (0.9375, 0.9375))
        self.assertEqual(palette.cell_uv("cream"), palette.cell_uv((0, 0)))

    def test_every_name_points_to_defined_color(self):
        for name, cell in palette.NAMES.items():
            self.assertIn(cell, palette.COLORS, name)

    def test_colors_are_valid_unique_hex(self):
        seen = set()
        for cell, color in palette.COLORS.items():
            self.assertRegex(color, r"^#[0-9A-F]{6}$", str(cell))
            self.assertNotIn(color, seen, f"дубликат {color}")
            seen.add(color)
            self.assertTrue(0 <= cell[0] < palette.SIZE and 0 <= cell[1] < palette.SIZE)

    def test_emissive_rows(self):
        self.assertTrue(palette.is_emissive("emit_cyan"))
        self.assertTrue(palette.is_emissive("emit_red"))
        self.assertFalse(palette.is_emissive("cream"))
        self.assertFalse(palette.is_emissive("yellow"))

    def test_emissive_names_match_rows(self):
        for name, (_col, row) in palette.NAMES.items():
            emissive_row = row in palette.EMISSIVE_ROWS
            if name.startswith("emit_"):
                self.assertTrue(emissive_row, f"{name} не в эмиссивном ряду")
            else:
                self.assertFalse(emissive_row, f"{name} в эмиссивном ряду без префикса emit_")

    def test_hex_to_rgb(self):
        self.assertEqual(palette.hex_to_rgb("#FFFFFF"), (1.0, 1.0, 1.0))
        r, g, b = palette.hex_to_rgb("#F08A3C")
        self.assertAlmostEqual(r, 0xF0 / 255)
        self.assertAlmostEqual(g, 0x8A / 255)
        self.assertAlmostEqual(b, 0x3C / 255)

    def test_pixels_have_cell_colors_at_cell_centers(self):
        px = palette.pixels_rgba()
        self.assertEqual(len(px), palette.TEXTURE_PX * palette.TEXTURE_PX * 4)

        def at(col, row):
            x = col * palette.CELL_PX + palette.CELL_PX // 2
            y = row * palette.CELL_PX + palette.CELL_PX // 2
            i = (y * palette.TEXTURE_PX + x) * 4
            return tuple(px[i:i + 3]), px[i + 3]

        rgb, a = at(0, 0)
        self.assertEqual(a, 1.0)
        for got, want in zip(rgb, palette.hex_to_rgb(palette.COLORS[(0, 0)])):
            self.assertAlmostEqual(got, want)
        rgb, _ = at(7, 7)  # незанятая ячейка чёрная
        self.assertEqual(rgb, (0.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
