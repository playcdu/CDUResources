"""Ensure snapshot checks accept PNG recompression but reject stale artist tools."""
import base64
import copy
import io
import json
import unittest

from PIL import Image

from verify_control_explorer import verify


def png(size=(4, 4), changed_pixel=False, compression=6):
    image = Image.new("RGBA", size, (20, 70, 110, 255))
    if changed_pixel:
        image.putpixel((0, 0), (21, 70, 110, 255))
    output = io.BytesIO()
    image.save(output, format="PNG", compress_level=compression)
    return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii")


def page(screens):
    return "<script>\nconst SCREENS=" + json.dumps(screens) + ";\nrender();\n</script>"


class ExplorerFreshness(unittest.TestCase):
    def setUp(self):
        self.screens = {"auction": {"image": png(), "controls": [{"slot": 24, "action": "buy"}]}}
        self.original = page(self.screens)

    def test_same_pixels_with_different_compression_pass(self):
        changed = copy.deepcopy(self.screens)
        changed["auction"]["image"] = png(compression=0)
        self.assertNotEqual(changed["auction"]["image"], self.screens["auction"]["image"])
        verify(self.original, page(changed))

    def test_changed_pixel_or_dimensions_fail(self):
        for replacement in (png(changed_pixel=True), png(size=(2, 8))):
            with self.subTest(replacement=replacement):
                changed = copy.deepcopy(self.screens)
                changed["auction"]["image"] = replacement
                with self.assertRaisesRegex(ValueError, "stale"):
                    verify(self.original, page(changed))

    def test_changed_controls_fail(self):
        for field, value in (("slot", 25), ("action", "sell")):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.screens)
                changed["auction"]["controls"][0][field] = value
                with self.assertRaisesRegex(ValueError, "stale"):
                    verify(self.original, page(changed))

    def test_changed_page_or_script_fail(self):
        for changed in ("<h1>Changed</h1>" + self.original, self.original.replace("render();", "other();")):
            with self.subTest(changed=changed):
                with self.assertRaisesRegex(ValueError, "stale"):
                    verify(self.original, changed)

    def test_missing_screen_fails(self):
        changed = copy.deepcopy(self.screens)
        changed["shop"] = copy.deepcopy(changed["auction"])
        with self.assertRaisesRegex(ValueError, "stale"):
            verify(page(changed), self.original)

    def test_missing_data_fails(self):
        with self.assertRaisesRegex(ValueError, "Missing"):
            verify(self.original, "<html></html>")

    def test_changed_menu_order_fails(self):
        screens = {**self.screens, "shop": copy.deepcopy(self.screens["auction"])}
        with self.assertRaisesRegex(ValueError, "stale"):
            verify(page(screens), page(dict(reversed(list(screens.items())))))


if __name__ == "__main__":
    unittest.main()
