
import os

from geekcms.protocal import BasePlugin
from geekcms.utils import PathResolver
from geekcms.protocal import PluginController as pcl

from .assets import ArticleFile, AboutFile, StaticFile, IndexFile
from .utils import AVALIABLE_MD_EXTENSIONS


class _LoadMethod:

    def _get_dir_path_of_inpouts(self, dirname):
        dir_path = os.path.join(
            PathResolver.inputs(),
            dirname,
        )
        return dir_path


    def _load_files_in_dir(self, top, avaliable_exts=None):

        for dirpath, dirnames, filenames in os.walk(top):
            for name in filenames:
                _, ext = os.path.splitext(name)

                if avaliable_exts is None:
                    pass
                elif ext not in avaliable_exts:
                    continue
                elif name.startswith('.'):
                    continue

                yield os.path.join(dirpath, name)


    def _load(self, dirname, resource_cls, avaliable_exts=None):
        # get abs path of dirname.
        dir_path = self._get_dir_path_of_inpouts(dirname)
        # get manager of resource_cls.
        manager = self.get_manager_bind_with_plugin(resource_cls)
        # walk through path of dirname.
        for abs_path in self._load_files_in_dir(dir_path, avaliable_exts):
            manager.create(abs_path)


class StaticFileLoader(BasePlugin, _LoadMethod):

    plugin = 'load_static'

    def run(self):
        self._load('static', StaticFile)


class AboutMeLoader(BasePlugin, _LoadMethod):

    plugin = 'load_about'

    def run(self):
        self._load('about', AboutFile, AVALIABLE_MD_EXTENSIONS)


class IndexLoader(BasePlugin, _LoadMethod):

    plugin = 'load_index'

    def run(self):
        self._load('index', IndexFile, AVALIABLE_MD_EXTENSIONS)

class ArticleLoader(BasePlugin, _LoadMethod):

    plugin = 'load_article'

    def run(self):
        self._load('article', ArticleFile, AVALIABLE_MD_EXTENSIONS)
