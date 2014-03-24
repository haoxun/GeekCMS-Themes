
import os

import mistune

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from jinja2 import Environment
from jinja2 import FileSystemLoader

from geekcms.utils import PathResolver, ShareData


AVALIABLE_MD_EXTENSIONS = [
    '.markdown',
    '.mdown',
    '.mkdn',
    '.md',
    '.mkd',
    '.mdwn',
    '.mdtxt',
    '.mdtext',
]


class SyntaxHighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()
        return highlight(code, lexer, formatter)


class ArticlePageToFileMapping:

    _page_to_file_mapping = {}

    @classmethod
    def set_mapping(cls, article_page, article_file):
        cls._page_to_file_mapping[article_page] = article_file

    @classmethod
    def get_mapping(cls, article_page):
        return cls._page_to_file_mapping(article_page)


def _get_env():
    template_path = os.path.join(
        PathResolver.theme_dir('simple'),
        'templates',
    )
    loader = FileSystemLoader(template_path)
    env = Environment(loader=loader)
    return env


template_env = _get_env()
