import unittest

from tools.render_version_info import parse_version, render_version_info


class ParseVersionTest(unittest.TestCase):
    def test_parses_tag_with_v_prefix(self):
        self.assertEqual((1, 0, 3), parse_version("v1.0.3"))

    def test_parses_tag_without_v_prefix(self):
        self.assertEqual((2, 10, 0), parse_version("2.10.0"))

    def test_rejects_malformed_tag(self):
        with self.assertRaises(ValueError):
            parse_version("not-a-version")


class RenderVersionInfoTest(unittest.TestCase):
    def test_embeds_version_tuple_and_string(self):
        content = render_version_info("v1.0.3")

        self.assertIn("filevers=(1, 0, 3, 0)", content)
        self.assertIn('StringStruct(u"FileVersion", u"1.0.3.0")', content)
        self.assertIn('StringStruct(u"ProductVersion", u"1.0.3.0")', content)
