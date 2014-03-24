
import os

from geekcms.protocal import BaseResource, BaseProduct, BaseMessage
from geekcms.utils import PathResolver, ShareData


class _File(BaseResource):

    def __init__(self, abs_path):
        self.abs_path = abs_path

    @property
    def rel_path(self):
        path = os.path.relpath(
            self.abs_path,
            # rel_path with inputs directory as base.
            PathResolver.inputs(),
        )
        return path

    @property
    def text(self):
        with open(self.abs_path) as f:
            data = f.read()
        return data


# loaded files.
class MarkdownFile(_File):
    pass


class ArticleFile(MarkdownFile):
    pass


class AboutFile(MarkdownFile):
    pass


class IndexFile(MarkdownFile):
    pass


class StaticFile(_File):
    pass


# pages
class Page(BaseProduct):

    def __init__(self, text, rel_path):
        # rel_path with outputs directory as base.
        self.rel_path = rel_path
        self.text = text


class ArticlePage(Page):
    pass


class _SpecialPage(Page):

    def __init__(self, text):
        super().__init__(
            text,
            self.REL_PATH,
        )


class TimeLinePage(_SpecialPage):

    REL_PATH = ShareData.get('simple.time_line_page')


class ArchivePage(_SpecialPage):

    REL_PATH = ShareData.get('simple.archive_page')


class AboutPage(_SpecialPage):

    REL_PATH = ShareData.get('simple.about_page')


class IndexPage(_SpecialPage):

    REL_PATH = ShareData.get('simple.index_page')


# class DeleteFileMessage(BaseMessage):
#
#     def __init__(self, rel_path):
#         self.rel_path = rel_path
#
#     @property
#     def delete_abs_path(self):
#         path = os.path.join(
#             PathResolver.outputs(),
#             self.rel_path,
#         )
#         return path
#
#
# class CopyFileMessage(BaseMessage):
#
#     def __init__(self, from_rel_path, to_rel_path):
#         self.from_rel_path = from_rel_path
#         self.to_rel_path = to_rel_path
#
#     @property
#     def from_abs_path(self):
#         path = os.path.join(
#             PathResolver.inputs(),
#             self.from_rel_path,
#         )
#         return path
#
#     @property
#     def to_abs_path(self):
#         path = os.path.join(
#             PathResolver.outputs(),
#             self.to_rel_path,
#         )
#         return path
