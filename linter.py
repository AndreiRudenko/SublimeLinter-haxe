import re
import logging
from SublimeLinter.lint import Linter, util
from os import path
from os.path import relpath

logger = logging.getLogger('SublimeLinter.plugins.haxe')

class Haxe(Linter):

    print("[SublimeLinter-haxe] init")

    regex = r'^.*?(?P<filename>.*hx):(?P<line>\d+):\D*(?P<col>\d+)[^:]*(?:(?P<error>:)|(?P<warning>:\s?Warning\s?:))\s?(?P<message>.+)'
    regex_apath = re.compile(r'^(?:[A-Za-z]:)+[\\/]')

    multiline = False
    tempfile_suffix = '-'
    error_stream = util.STREAM_STDERR
    defaults = {
        'selector': 'source.haxe'
    }
    cwd = ''

    def cmd(self):

        self.cwd = self.context['file_path']
        hxml_path = self.context['file_name']
        haxe_path = "haxe"
        
        # use settings from haxe_sublime plugin if possible
        from haxe_sublime import haxe
        from haxe_sublime import haxe_completion
        haxe = haxe._haxe_
        haxe_completion = haxe_completion._haxe_completion_
        if haxe and haxe.hxml_file != "":
            self.cwd = haxe.get_working_dir()
            hxml_path = haxe.hxml_file
            haxe_path = haxe_completion.haxe_path
            port = str(haxe_completion.port)
            return (
                haxe_path,
                '--no-output',
                '--connect', port,
                '--cwd', self.cwd,
                hxml_path,
                '-r'
            )
        
        return (
            haxe_path,
            '--no-output',
            '--cwd', self.cwd,
            hxml_path,
            '-r'
        )

    def on_stderr(self, stderr):
        print(stderr)
        if stderr:
            self.notify_failure()
            logger.error(stderr)

    def split_match(self, match):
        match, line, col, error, warning, message, near = super().split_match(match)
        
        match_name = match.group('filename')
        has_abs_path = self.regex_apath.search(match_name)
        if has_abs_path:
            match_name = relpath(match_name, self.cwd)

        file_name = relpath(self.filename, self.cwd)

        if match_name != file_name:
            return None

        return match, line, col, error, warning, message, near


