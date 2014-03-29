
import os
import shutil
import urllib.parse

from geekcms.protocol import BasePlugin
from geekcms.protocol import PluginController as pcl
from geekcms.utils import PathResolver, ShareData

from .assets import (Page, ArticlePage, TimeLinePage,
                     ArchivePage, AboutPage, IndexPage,
                     StaticFile)
from .utils import template_env


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
                shutil.rmtree(path)


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
        domain = ShareData.get('global.domain')
        tgt_abs_path = os.path.join(
            PathResolver.outputs(),
            'CNAME',
        )
        with open(tgt_abs_path, 'w') as f:
            f.write(domain)


class SitemapGenerator(BasePlugin):

    plugin = 'sitemap'

    @pcl.accept_parameters(
        (pcl.PRODUCTS, Page),
    )
    def run(self, pages):
        http_domain = 'http://{}'.format(ShareData.get('global.domain'))

        # generate sitemap.
        urls = []
        for page in pages:
            url = urllib.parse.urljoin(http_domain, page.url)
            urls.append(url)

        xml_template = template_env.get_template('simple_xml.xml')
        sitemap_abs_path = os.path.join(
            PathResolver.outputs(),
            'sitemap.xml',
        )
        with open(sitemap_abs_path, 'w') as f:
            xml_text = xml_template.render(urls=urls)
            f.write(xml_text)

        # add sitemap to robots.txt.
        robots_abs_path = os.path.join(
            PathResolver.outputs(),
            'robots.txt',
        )
        sitemap_url = urllib.parse.urljoin(
            http_domain,
            'sitemap.xml',
        )
        with open(robots_abs_path, 'a') as f:
            f.write('Sitemap: {}'.format(sitemap_url))
