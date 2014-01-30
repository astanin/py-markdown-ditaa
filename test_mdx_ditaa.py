from __future__ import unicode_literals
import markdown as md
from nose.tools import assert_equal
import os


def test_with_fenced_code():
    markdown_source = "\n".join(
        ["Test diagram:",
         "",
         "```ditaa",
         "+---+",
         "| A |",
         "+---+",
         "```",
         "",
         " Test code:",
         "",
         "```python",
         "def f():",
         "    pass",
         "```"])

    html = md.markdown(markdown_source, extensions=["fenced_code", "ditaa"])
    if os.path.exists("diagram-1d900348.png"):
        os.unlink("diagram-1d900348.png")

    expected_html = "\n".join(
        ['<p>Test diagram:</p>',
         '<p><img alt="diagram-1d900348.png" src="diagram-1d900348.png" /></p>',
         '<p>Test code:</p>',
         '<pre><code class="python">def f():',
         '    pass',
         '</code></pre>'])

    assert_equal(html, expected_html)
