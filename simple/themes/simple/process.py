
import os
import re
from datetime import datetime
from functools import partial
from collections import OrderedDict

import mistune

from geekcms.protocal import BasePlugin
from geekcms.protocal import PluginController as pcl
from geekcms.protocal import BaseResource
from geekcms.utils import ShareData

from .assets import (MarkdownFile, ArticleFile, AboutFile, IndexFile,
                     Page, ArticlePage, TimeLinePage,
                     ArchivePage, AboutPage, IndexPage)
from .utils import (SyntaxHighlightRenderer, ArticlePageToFileMapping,
                    template_env, PageForRender, XMLOperation)


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

    def _get_url_of_share_data(self, key):
        return '/' + ShareData.get(key)

    def _get_particle_template_render(self, template_name):
        template = template_env.get_template(template_name)
        time_line_url = self._get_url_of_share_data('simple.time_line_page')
        archive_url = self._get_url_of_share_data('simple.archive_page')
        about_url = self._get_url_of_share_data('simple.about_page')

        partial_render = partial(
            template.render,
            # share fields.
            time_line_url=time_line_url,
            archive_url=archive_url,
            about_url=about_url,
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
        self._unique_rel_paths = []

    def _adjust_conflict_rel_path(self, rel_path):
        while rel_path in self._unique_rel_paths:
            rel_path = re.sub(r'.html$', '', rel_path) + 'remove_conflict.html'
        self._unique_rel_paths.append(rel_path)
        return rel_path

    def _generate_article_rel_path(self, rel_path_to_inputs):
        _, filename = os.path.split(rel_path_to_inputs)
        # generate url base on rel_path of inputs.
        rel_path = os.path.join(
            ShareData.get('simple.article'),
            filename,
        )
        # change extension to .html.
        head, _ = os.path.splitext(rel_path)
        rel_path = head + '.html'
        # adjust conflits url.
        rel_path = self._adjust_conflict_rel_path(rel_path)
        return rel_path

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
            rel_path = self._generate_article_rel_path(article_file.rel_path)
            html = self._render_html(article_file)
            # init ArticlePage.
            article_page = page_manager.create(html, rel_path)
            # set mapping.
            ArticlePageToFileMapping.set_mapping(article_page, article_file)


class _SimpleSpecialPageGenerator(_TemplateRender):

    def _generate_simple_special_page(self,
                                      files,
                                      page_cls,
                                      template_name):
        if len(files) != 1:
            raise SyntaxError("Wrong Number")
        single_file = files[0]

        template_render = self._get_particle_template_render(template_name)
        html = template_render(
            title=single_file.meta_data['title'],
            article_html=single_file.html,
        )

        page_manager = self.get_manager_bind_with_plugin(page_cls)
        page_manager.create(html)


class AboutPageGenerator(BasePlugin, _SimpleSpecialPageGenerator):

    plugin = 'gen_about_page'

    @pcl.accept_parameters(
        (pcl.RESOURCES, AboutFile),
    )
    def run(self, about_files):
        self._generate_simple_special_page(
            about_files,
            AboutPage,
            'article.html',
        )


class IndexPageGenerator(BasePlugin, _SimpleSpecialPageGenerator):

    plugin = 'gen_index_page'

    @pcl.accept_parameters(
        (pcl.RESOURCES, IndexFile),
    )
    def run(self, about_files):
        self._generate_simple_special_page(
            about_files,
            IndexPage,
            'article.html',
        )


class _PageForRenderGenerator:

    def _generate_sorted_pages(self, article_pages, reverse=False):
        pages = []
        for article_page in article_pages:
            pages.append(PageForRender(article_page))

        return sorted(pages, key=lambda x: x.post_time, reverse=reverse)


class TimeLinePageGenerator(BasePlugin,
                            _TemplateRender,
                            _PageForRenderGenerator):

    plugin = 'gen_time_line_page'

    @pcl.accept_parameters(
        (pcl.PRODUCTS, ArticlePage),
    )
    def run(self, article_pages):

        template_render = self._get_particle_template_render('time_line.html')
        pages = self._generate_sorted_pages(article_pages, True)
        html = template_render(pages=pages)

        page_manager = self.get_manager_bind_with_plugin(TimeLinePage)
        page_manager.create(html)


class ArchivePageGenerator(BasePlugin,
                           _TemplateRender,
                           _PageForRenderGenerator):

    plugin = 'gen_archive_page'

    def _construct_ordered_paths(self, pages, old_xml):
        ordered_paths = []
        raw_paths = [page.input_rel_path for page in pages]

        for node in old_xml.iter():
            if node.tag != XMLOperation.PAGE:
                continue
            path = node.attrib['path']
            if path in raw_paths:
                # avaliable path
                ordered_paths.append(path)
                raw_paths.remove(path)
        # extend new pages.
        ordered_paths.extend(raw_paths)
        return ordered_paths

    def _get_common_prefix(self, ordered_paths):
        dir_paths = []
        for head, tail in map(os.path.split, ordered_paths):
            dir_paths.append(head)

        # all aritcles should shoulde be placed in a single dir,
        # which is the root of the article tree.
        # leaf of the article tree represents article, while dir
        # represents topic.
        common_prefix = os.path.commonprefix(dir_paths)
        if not common_prefix.endswith('/'):
            common_prefix += '/'
        if '/' not in re.sub(common_prefix, '', ordered_paths[0]):
            # there is only a single topic.
            # go to an upper layer
            common_prefix, _ = os.path.split(common_prefix.rstrip('/'))
            common_prefix += '/'
        return common_prefix

    def _expand_article_tree(self, article_tree, dirs):
        cur_node = article_tree
        for dir in dirs:
            if dir in cur_node:
                cur_node = cur_node[dir]
            else:
                cur_node[dir] = {}
                cur_node = cur_node[dir]
        return cur_node

    def _construct_article_tree(self,
                                pages,
                                ordered_paths,
                                common_prefix):
        # construct mapping from input path to page.
        path_page_mapping = {}
        for page in pages:
            path_page_mapping[page.input_rel_path] = page

        # generate article_tree.
        article_tree = OrderedDict()
        for path in ordered_paths:
            rel_path = re.sub(common_prefix, '', path)
            head, _ = os.path.split(rel_path)
            dirs = head.split('/')

            cur_node = self._expand_article_tree(article_tree, dirs)
            if None not in cur_node:
                cur_node[None] = []

            cur_node[None].append({
                'path': path,
                'url': path_page_mapping[path].url,
                'title': path_page_mapping[path].title,
            })
        return article_tree

    @pcl.accept_parameters(
        (pcl.PRODUCTS, ArticlePage),
    )
    def run(self, article_pages):
        xml_operator = XMLOperation()
        pages = self._generate_sorted_pages(article_pages)

        old_xml = xml_operator.load_xml()
        ordered_paths = self._construct_ordered_paths(pages, old_xml)
        common_prefix = self._get_common_prefix(ordered_paths)
        article_tree = self._construct_article_tree(
            pages,
            ordered_paths,
            common_prefix,
        )
        xml_operator.generate_xml(article_tree)

        template_render = self._get_particle_template_render('archive.html')
        page_manager = self.get_manager_bind_with_plugin(ArchivePage)
        html = template_render(article_tree=article_tree)
        page_manager.create(html)
