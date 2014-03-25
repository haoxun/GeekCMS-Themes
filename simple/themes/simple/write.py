
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
        for name in os.listdir(PathResolver.outputs()):
            if name.startswith('.'):
                continue

            path = os.path.join(
                PathResolver.outputs(),
                name,
            )
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                os.removedirs(path)


class _TargetAbsPath:

    def _get_tgt_abs_path(self, tgt_rel_path):
        path = os.path.join(
            PathResolver.outputs(),
            tgt_rel_path,
        )
        return path

    def _make_sure_dir_exist(self, tgt_abs_path):
        dir_path, _ = os.path.split(tgt_abs_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


class StaticWriter(BasePlugin, _TargetAbsPath):

    """
    1. Write static files of inputs.
    2. Write static files of themes.
    """

    plugin = 'write_static'

    @pcl.accept_parameters(
        (pcl.RESOURCES, StaticFile),
    )
    def run(self, static_files):
        for static_file in static_files:
            tgt_abs_path = self._get_tgt_abs_path(static_file.rel_path)
            self._make_sure_dir_exist(tgt_abs_path)
            shutil.copyfile(
                static_file.abs_path,
                tgt_abs_path,
            )


class PageWriter(BasePlugin, _TargetAbsPath):

    plugin = 'write_page'

    @pcl.accept_parameters(
        (pcl.PRODUCTS, Page),
    )
    def run(self, pages):
        for page in pages:
            tgt_abs_path = self._get_tgt_abs_path(page.rel_path)
            self._make_sure_dir_exist(tgt_abs_path)
            with open(tgt_abs_path, 'w') as f:
                f.write(page.text)


class CNAMEWriter(BasePlugin):

    plugin = 'cname'

    def run(self):
        tgt_abs_path = os.path.join(
            PathResolver.outputs(),
            'CNAME',
        )
        with open(tgt_abs_path, 'w') as f:
            f.write(ShareData.get('global.cname'))
