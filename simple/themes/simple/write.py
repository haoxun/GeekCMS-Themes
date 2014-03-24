
from geekcms.protocal import BasePlugin
from geekcms.protocal import PluginController as pcl
from geekcms.utils import PathResolver, ShareData

from .assets import (MarkdownFile, ArticleFile, AboutFile, StaticFile,
                     Page, ArticlePage, TimeLinePage,
                     ArchivePage, AboutPage, IndexPage)

class OutputCleaner(BasePlugin):

    plugin = 'clean'

    def run(self):
        pass


class IndexWriter(BasePlugin):

    plugin = 'write_index_page'

    def run(self):
        pass


class StaticWriter(BasePlugin):

    plugin = 'write_static'

    @pcl.accept_parameters(
        (pcl.RESOURCES, StaticFile),
    )
    def run(self, static_files):
        pass


class PageWriter(BasePlugin):

    plugin = 'write_page'

    @pcl.accept_parameters(
        (pcl.PRODUCTS, Page),
    )
    def run(self, pages):
        pass


class CNAMEWriter(BasePlugin):

    plugin = 'cname'

    def run(self):
        pass
