import unittest


from ...support.markdown import MarkdownSource


# TODO: Preliminary tests
class TestMarkdown(unittest.TestCase):
    def test_proper_escape(self):
        source = MarkdownSource("\"**Test**\"")
        self.assertEqual(source.rendered, "<p>&quot;<strong>Test</strong>&quot;</p>")

    def test_escaped(self):
        source = MarkdownSource("&lt;&gt;")
        self.assertEqual(source.rendered, "<p>&lt;&gt;</p>")
