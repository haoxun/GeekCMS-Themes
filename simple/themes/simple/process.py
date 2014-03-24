
import os
import re
from datetime import datetime
from functools import partial

import mistune

from geekcms.protocal import BasePlugin
from geekcms.protocal import PluginController as pcl
from geekcms.protocal import BaseResource
from geekcms.utils import ShareData

from .assets import (MarkdownFile, ArticleFile, AboutFile,
                     Page, ArticlePage, TimeLinePage,
                     ArchivePage, AboutPage, IndexPage)
from .utils import (SyntaxHighlightRenderer, ArticlePageToFileMapping,
                    template_env)


class MarkdownProcessor(BasePlugin):

    """
    1. Extract meta data.
    2. Generate html from markdown.
    3. Attach meta data and html to resources.
    """

    plugin = 'md_to_html'

    md = mistune.Markdown(renderer=SyntaxHighlightRenderer())

    TITLE = 'title'
    DATE = 'date'

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
        for field in [self.TITLE, self.DATE]:
            if field not in meta_data:
                raise SyntaxError('Can Not Find {} In Article'.format(field))

    def _process_required_fileds(self, meta_data):
        meta_data[self.TITLE] = meta_data[self.TITLE][0]
        meta_data[self.DATE] = datetime.strptime(
            meta_data[self.DATE][0],
            '%d/%m/%Y',
        )

    def _extract_meta_data(self, text):
        lines = text.split(os.linesep)
        meta_data = self._extract_meta_from_lines(lines)

        self._check_required_fields(meta_data)
        self._process_required_fileds(meta_data)

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


class _TemplateRender:

    def _get_particle_template_render(self, template_name):
        template = template_env.get_template(template_name)
        partial_render = partial(
            template.render,
            # share fields.
            time_line_url=ShareData.get('simple.time_line_page'),
            archive_url=ShareData.get('simple.archive_page'),
            about_url=ShareData.get('simple.about_page'),
        )
        return partial_render


class ArticlePageGenerator(BasePlugin, _TemplateRender):

    """
    1. Generate rel_path of outputs directory. (simple.article + title)
    2. Deal with url confilcts.
    3. Register page to article mappings.
    """

    plugin = 'gen_article_page'

    def __init__(self):
        self._unique_urls = []

    def _adjust_conflict_url(self, url):
        while url in self._unique_urls:
            url = re.sub(r'.html$', '', url) + 'remove_conflict.html'
        self._unique_urls.append(url)
        return url

    def _generate_article_url(self, rel_path_to_inputs):
        _, filename = os.path.split(rel_path_to_inputs)
        # generate url base on rel_path of inputs.
        url = os.path.join(
            ShareData.get('simple.article'),
            filename,
        )
        # change extension to .html.
        head, _ = os.path.splitext(url)
        url = head + '.html'
        # adjust conflits url.
        url = self._adjust_conflict_url(url)
        return url

    def _render_html(self, article_file):
        template_render = self._get_particle_template_render('article.html')
        html = template_render(
            title=article_file.meta_data['title'],
            article_html=article_file.html,
        )
        return html

    @pcl.accept_parameters(
        (pcl.RESOURCES, ArticleFile),
    )
    def run(self, article_files):
        page_manager = self.get_manager_bind_with_plugin(ArticlePage)
        for article_file in article_files:
            # generate necessary attrs.
            url = self._generate_article_url(article_file.rel_path)
            html = self._render_html(article_file)
            # init ArticlePage.
            article_page = page_manager.create(html, url)
            # set mapping.
            ArticlePageToFileMapping.set_mapping(article_page, article_file)


class AboutPageGenerator(BasePlugin, _TemplateRender):

    plugin = 'gen_about_page'

    @pcl.accept_parameters(
        (pcl.RESOURCES, AboutFile),
    )
    def run(self, about_files):
        if len(about_files) != 1:
            raise SyntaxError("Wrong Number Of About")
        about_file = about_files[0]

        template_render = self._get_particle_template_render('about.html')
        html = template_render(
            title=about_file.meta_data['title'],
            article_html=about_file.html,
        )

        page_manager = self.get_manager_bind_with_plugin(AboutPage)
        page_manager.create(html)


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
