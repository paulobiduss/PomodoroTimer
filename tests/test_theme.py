import unittest

from core.constants import STATE_COMPLETED, STATE_FOCUS, STATE_LONG_BREAK, STATE_SHORT_BREAK
from ui.theme import (
    DARK_PALETTE,
    LIGHT_PALETTE,
    STATE_GRADIENTS,
    build_accent_stylesheets,
    build_stylesheet,
    gradient_for,
    palette_for,
    rgba_components,
)


class PaletteTest(unittest.TestCase):
    def test_returns_light_palette_for_light_theme(self):
        self.assertIs(LIGHT_PALETTE, palette_for("light"))

    def test_unknown_theme_falls_back_to_dark(self):
        self.assertIs(DARK_PALETTE, palette_for("sepia"))

    def test_every_palette_color_is_parseable(self):
        for palette in (DARK_PALETTE, LIGHT_PALETTE):
            for field in ("bg_top", "bg_bottom", "glass", "glass_hover", "glass_border",
                          "text", "text_muted", "track", "input_bg"):
                rgba_components(getattr(palette, field))


class GradientTest(unittest.TestCase):
    def test_each_state_has_its_own_gradient(self):
        states = (STATE_FOCUS, STATE_SHORT_BREAK, STATE_LONG_BREAK, STATE_COMPLETED)
        gradients = {gradient_for(state) for state in states}
        self.assertEqual(4, len(gradients))

    def test_unknown_state_uses_focus_gradient(self):
        self.assertEqual(STATE_GRADIENTS[STATE_FOCUS], gradient_for("unknown"))


class RgbaComponentsTest(unittest.TestCase):
    def test_parses_hex(self):
        self.assertEqual((255, 122, 69, 255), rgba_components("#FF7A45"))

    def test_parses_rgba_with_fractional_alpha(self):
        self.assertEqual((255, 255, 255, 128), rgba_components("rgba(255, 255, 255, 0.5)"))

    def test_rejects_invalid_color_with_value_in_message(self):
        with self.assertRaisesRegex(ValueError, "'blue'"):
            rgba_components("blue")


class StylesheetTest(unittest.TestCase):
    def test_base_stylesheet_uses_palette_colors(self):
        qss = build_stylesheet(LIGHT_PALETTE)
        self.assertIn(LIGHT_PALETTE.bg_top, qss)
        self.assertIn(LIGHT_PALETTE.text, qss)

    def test_accent_stylesheets_follow_state_gradient(self):
        start, end = gradient_for(STATE_SHORT_BREAK)
        accent = build_accent_stylesheets(DARK_PALETTE, STATE_SHORT_BREAK)
        self.assertIn(start, accent["stateLabel"])
        self.assertIn(end, accent["mainBtn"])
        self.assertEqual({"stateLabel", "mainBtn", "saveBtn", "longBreakCheck", "spinBox"}, set(accent))


if __name__ == "__main__":
    unittest.main()
