import unittest


from ...support.markdown import MarkdownSource


def load_article():
    import json, os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    article = json.loads(open(os.path.join(dir_path, "test_markdown/article.json")).read())
    return article


class TestMarkdownSource(unittest.TestCase):

    def setUp(self) -> None:
        self.text = "This is a no markdown text"

    def test_no_markdown_characters(self):
        no_md_text = "*"
        source = MarkdownSource(no_md_text)
        self.assertEqual(source.rendered, f"<p>{no_md_text}</p>")
        no_md_text = "`"
        source = MarkdownSource(no_md_text)
        self.assertEqual(source.rendered, f"<p>{no_md_text}</p>")

    def test_no_markdown_texts(self):
        no_md_text = "This is a no markdown text"
        source = MarkdownSource(no_md_text)
        self.assertEqual(source.rendered, f"<p>{no_md_text}</p>")

    def test_markdown_bold_tag(self):
        text = "Never really over"
        md_text = f"**{text}**"
        source = MarkdownSource(md_text)
        self.assertEqual(source.rendered, f"<p><strong>{text}</strong></p>")
        md_text = f"__{text}__"
        source = MarkdownSource(md_text)
        self.assertEqual(source.rendered, f"<p><strong>{text}</strong></p>")

    def test_markdown_italic_tag(self):
        text = "Never Really Over"
        md_text = f"*{text}*"
        source = MarkdownSource(md_text)
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
        no_md_text = f"<strong>{self.text}</strong> **{self.text}**"
        source = MarkdownSource(no_md_text)
        self.assertEqual(source.source, f"__{self.text}__ **{self.text}**")
        self.assertEqual(source.rendered, f"<p><strong>{self.text}</strong> <strong>{self.text}</strong></p>")
        no_md_text = f"*{self.text}* <em>{self.text}</em> **{self.text}**"
        source = MarkdownSource(no_md_text)
        self.assertEqual(source.source, f"*{self.text}* _{self.text}_ **{self.text}**")
        self.assertEqual(source.rendered, f"<p><em>{self.text}</em> <em>{self.text}</em> "
                                          f"<strong>{self.text}</strong></p>")

    # This prevents malicious attacks
    def test_html_escape(self):
        source = MarkdownSource("\"**Test**\"")
        self.assertEqual(source.rendered, "<p>&quot;<strong>Test</strong>&quot;</p>")
        source = MarkdownSource("<script></script>")
        self.assertEqual(source.rendered, "<p>&lt;script&gt;&lt;/script&gt;</p>")

    def test_html_escaped(self):
        source = MarkdownSource("&lt;&gt;")
        self.assertEqual(source.rendered, "<p>&lt;&gt;</p>")

        source = MarkdownSource("&quot; *&lt;&gt;* __&amp;__")
        self.assertEqual(source.rendered, "<p>&quot; <em>&lt;&gt;</em> <strong>&amp;</strong></p>")

    # A test fixture provided by markdown-it
    def test_article(self):
        self.maxDiff = None
        self.article = load_article()
        source = MarkdownSource(self.article['source'])
        self.assertEqual(source.rendered, self.article["rendered"])
