
"""
Usage:
    geekcms gitupload

"""

from datetime import datetime
import subprocess
import os

from geekcms.protocol import BaseExtendedProcedure
from geekcms.utils import PathResolver


class CWDContextManager:

    def __enter__(self):
        os.chdir(PathResolver.outputs())

    def __exit__(self, *args, **kwargs):
        os.chdir(PathResolver.project_path)


class GitUploader(BaseExtendedProcedure):

    def get_command_and_explanation(self):
        return ('gitupload',
                'Automatically commit and push all files of outputs.')

    def get_doc(self):
        return __doc__

    def run(self, args):
        commit_text = 'GeekCMS Update, {}'.format(
            datetime.now().strftime('%c'),
        )
        commands = [
            ['git', 'add', '--all', '.'],
            ['git', 'commit', '-m', commit_text],
            ['git', 'push'],
        ]
        with CWDContextManager():
            for command in commands:
                subprocess.check_call(command)
