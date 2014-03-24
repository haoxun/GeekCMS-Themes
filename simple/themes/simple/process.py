
import os
import re

import mistune

from geekcms.protocal import BasePlugin
from geekcms.protocal import PluginController as pcl
from geekcms.protocal import BaseResource
from .assets import (MarkdownFile, ArticleFile, AboutFile,
                     Page, ArticlePage, TimeLinePage,
                     ArchivePage, AboutPage, IndexPage)
from .utils import SyntaxHighlightRenderer


class MarkdownProcessor(BasePlugin):

    """
    1. Extract meta data.
    2. Generate html from markdown.
    3. Attach meta data and html to resources.
    """

    plugin = 'md_to_html'

    md = mistune.Markdown(renderer=SyntaxHighlightRenderer())

    def _extract_meta_from_lines(self, lines):
        # code of meta.py of Python-Markdown.
        META_RE =\
            re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
        META_MORE_RE = re.compile(r'^[ ]{4,}(?P<value>.*)')

        meta = {}
        key = None
        while lines:
            line = lines.pop(0)
            if line.strip() == '':
                break # blank line - done
            m1 = META_RE.match(line)
            if m1:
                key = m1.group('key').lower().strip()
                value = m1.group('value').strip()
                try:
                    meta[key].append(value)
                except KeyError:
                    meta[key] = [value]
            else:
                m2 = META_MORE_RE.match(line)
                if m2 and key:
                    # Add another line to existing key
                    meta[key].append(m2.group('value').strip())
                else:
                    lines.insert(0, line)
                    break # no meta data - done
        return meta

    def _check_required_fields(self, meta_data):
        TITEL = 'title'
        DATE = 'date'
        for field in [TITEL, DATE]:
            if field not in meta_data:
                raise SyntaxError('Can Not Find {} In Article'.format(field))

    def _extract_meta_data(self, text):
        lines = text.split(os.linesep)
        meta_data = self._extract_meta_from_lines(lines)
        self._check_required_fields(meta_data)

        return meta_data, os.linesep.join(lines)

    def _generate_html(self, text):
        return self.md.render(text)

    @pcl.accept_parameters(
        (pcl.RESOURCES, MarkdownFile),
    )
    def run(self, md_files):
        for md_file in md_files:
            meta_data, processed_text = self._extract_meta_data(md_file.text)
            html = self._generate_html(processed_text)
            md_file.meta_data = meta_data
            md_file.html = html


class ArticlePageGenerator(BasePlugin):

    plugin = 'gen_article_page'

    @pcl.accept_parameters(
        (pcl.RESOURCES, ArticleFile),
    )
    def run(self, article_files):
        pass


class AboutPageGenerator(BasePlugin):

    plugin = 'gen_about_page'

    @pcl.accept_parameters(
        (pcl.RESOURCES, AboutFile),
    )
    def run(self, about_files):
        # about_file = about_files[0]
        pass


class TimeLinePageGenerator(BasePlugin):

    plugin = 'gen_time_line_page'

    @pcl.accept_parameters(
        (pcl.PRODUCTS, ArticlePage),
    )
    def run(self, article_pages):
        pass


class ArchivePageGenerator(BasePlugin):

    plugin = 'gen_archive_page'

    @pcl.accept_parameters(
        (pcl.PRODUCTS, ArticlePage),
    )
    def run(self, archive_pages):
        pass
