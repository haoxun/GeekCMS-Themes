
import os
import shutil

from geekcms.protocal import BasePlugin
from geekcms.protocal import PluginController as pcl
from geekcms.utils import PathResolver, ShareData

from .assets import (Page, ArticlePage, TimeLinePage,
                     ArchivePage, AboutPage, IndexPage,
                     StaticFile)

class OutputCleaner(BasePlugin):

    plugin = 'clean'

    def run(self, resources):
        shutil.rmtree(PathResolver.outputs())
        os.mkdir(PathResolver.outputs())


class StaticWriter(BasePlugin):

    """
    1. Write static files of inputs.
    2. Write static files of themes.
    """

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
