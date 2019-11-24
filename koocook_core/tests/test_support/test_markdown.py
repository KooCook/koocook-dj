import json
import os
import unittest

from ...support.markdown import MarkdownSource


def load_article():

    dir_path = os.path.dirname(os.path.realpath(__file__))
    article = json.loads(open(os.path.join(dir_path, "test_markdown/article.json")).read())
    return article


class TestMarkdownSource(unittest.TestCase):

    def setUp(self) -> None:
        self.text = "This is a no markdown text"

    def test_no_markdown_characters(self):
        char = "*"
        with self.subTest("Asterisk"):
            source = MarkdownSource(char)
            self.assertEqual(source.rendered, f"<p>{char}</p>")

        char = "`"
        with self.subTest("Backtick"):
            source = MarkdownSource(char)
            self.assertEqual(source.rendered, f"<p>{char}</p>")

    def test_no_markdown_texts(self):
        no_md_text = "This is a no markdown text"
        source = MarkdownSource(no_md_text)
        self.assertEqual(source.rendered, f"<p>{no_md_text}</p>")

    def test_markdown_bold_tag(self):
        text = "Never really over"

        md_text = f"**{text}**"
        with self.subTest("Asterisk-denoted tag"):
            source = MarkdownSource(md_text)
            self.assertEqual(source.rendered, f"<p><strong>{text}</strong></p>")

        md_text = f"__{text}__"
        with self.subTest("Tag denoted with double underscores"):
            source = MarkdownSource(md_text)
            self.assertEqual(source.rendered, f"<p><strong>{text}</strong></p>")

    def test_markdown_italic_tag(self):
        text = "Never Really Over"
        md_text = f"*{text}*"
        source = MarkdownSource(md_text)
        with self.subTest("Tag denoted with a single asterisk"):
            self.assertEqual(source.rendered, f"<p><em>{text}</em></p>")

        md_text = f"_{text}_"
        source = MarkdownSource(md_text)
        with self.subTest("Tag denoted with a single underscore"):
            self.assertEqual(source.rendered, f"<p><em>{text}</em></p>")

    def test_markdown_code_tag(self):
        text = "Both my knees"
        md_text = f"`{text}`"
        source = MarkdownSource(md_text)
        self.assertEqual(source.rendered, f"<p><code>{text}</code></p>")

    def test_markdown_link_tag(self):
        link = "http://www.SabrinaCarpenter.com"
        text = f"[I'm fakin']({link})"
        source = MarkdownSource(text)
        self.assertEqual(source.rendered, f"<p><a href=\"{link}\">I&#x27;m fakin&#x27;</a></p>")

    def test_markdown_with_html(self):
        mixed_text = f"<strong>{self.text}</strong> **{self.text}**"

        with self.subTest():
            source = MarkdownSource(mixed_text)
            self.assertEqual(source.source, f"__{self.text}__ **{self.text}**")
            self.assertEqual(source.rendered, f"<p><strong>{self.text}</strong> <strong>{self.text}</strong></p>")
            mixed_text = f"*{self.text}* <em>{self.text}</em> **{self.text}**"

        with self.subTest():
            source = MarkdownSource(mixed_text)
            self.assertEqual(source.source, f"*{self.text}* _{self.text}_ **{self.text}**")
            self.assertEqual(source.rendered, f"<p><em>{self.text}</em> <em>{self.text}</em> "
                                              f"<strong>{self.text}</strong></p>")

    # This prevents malicious attacks
    def test_html_escape(self):
        with self.subTest():
            source = MarkdownSource("\"**Test**\"")
            self.assertEqual(source.rendered, "<p>&quot;<strong>Test</strong>&quot;</p>")
        with self.subTest():
            source = MarkdownSource("<script></script>")
            self.assertEqual(source.rendered, "<p>&lt;script&gt;&lt;/script&gt;</p>")

    def test_html_escaped(self):
        with self.subTest():
            source = MarkdownSource("&lt;&gt;")
            self.assertEqual(source.rendered, "<p>&lt;&gt;</p>")

        with self.subTest():
            source = MarkdownSource("&quot; *&lt;&gt;* __&amp;__")
            self.assertEqual(source.rendered, "<p>&quot; <em>&lt;&gt;</em> <strong>&amp;</strong></p>")

    # A test fixture provided by markdown-it
    def test_article(self):
        self.maxDiff = None
        self.article = load_article()
        source = MarkdownSource(self.article['source'])
        self.assertEqual(source.rendered, self.article["rendered"])
