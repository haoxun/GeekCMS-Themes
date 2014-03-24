
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

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
        return cls._page_to_file_mapping[article_page]


def _get_env():
    template_path = os.path.join(
        PathResolver.theme_dir('simple'),
        'templates',
    )
    loader = FileSystemLoader(template_path)
    env = Environment(loader=loader)
    return env


template_env = _get_env()


class PageForRender:

    def __init__(self, article_page):
        self.url = article_page.rel_path

        article_file = ArticlePageToFileMapping.get_mapping(article_page)
        self.title = article_file.meta_data['title']
        self.post_time = article_file.meta_data['date'].strftime('%Y-%m-%d')
        self.input_rel_path = article_file.rel_path


class XMLOperation:

    ROOT = 'root'
    TOPIC = 'topic'
    PAGE = 'page'

    XML_REL_PATH = 'archive_xml'

    def _get_xml_abs_path(self):
        xml_path = os.path.join(
            PathResolver.theme_state('simple'),
            self.XML_REL_PATH,
        )
        return xml_path

    def construct_xml_tree(self, xml_parent, article_parent):
        if None in article_parent:
            # leaf
            for item in article_parent[None]:
                page = ET.SubElement(xml_parent, self.PAGE)
                page.attrib['title'] = item['title']
                page.attrib['path'] = item['path']
                page.attrib['url'] = item['url']
        else:
            # recursive build
            for topic_name, sub_article_parent in article_parent.items():
                topic = ET.SubElement(xml_parent, self.TOPIC)
                topic.attrib['name'] = topic_name
                self.construct_xml_tree(topic, sub_article_parent)

    def load_xml(self):
        xml_path = self._get_xml_abs_path()
        try:
            with open(xml_path) as f:
                archive_xml_str = f.read()
            old_xml = ET.fromstring(archive_xml_str)
        except:
            old_xml = ET.Element(self.ROOT)
        return old_xml

    def generate_xml(self, article_tree):
        xml_path = self._get_xml_abs_path()
        new_xml = ET.Element(self.ROOT)
        self.construct_xml_tree(new_xml, article_tree)

        raw_xml = ET.tostring(new_xml, encoding='UTF-8')
        reparse = minidom.parseString(raw_xml)
        xml_str = reparse.toprettyxml(' ' * 4, os.linesep, 'UTF-8')
        with open(xml_path, 'wb') as f:
            f.write(xml_str)
