
from geekcms.protocal import BasePlugin
from geekcms.protocal import PluginController as pcl
from geekcms.protocal import BaseResource

from .assets import (MarkdownFile, ArticleFile, AboutFile,
                     Page, ArticlePage, TimeLinePage,
                     ArchivePage, AboutPage, IndexPage)


class MarkdownProcessor(BasePlugin):

    """
    1. Extract meta data.
    2. Generate html from markdown.
    3. Attach meta data and html to resources.
    """

    plugin = 'md_to_html'

    def _extract_meta_data(self, text):
        return meta_data, processed_text

    def _generate_html(self, text):
        pass

    @pcl.accept_parameters(
        (pcl.RESOURCES, MarkdownFile),
    )
    def run(self, markdown_files):
        pass


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
        about_file = about_files[0]
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
