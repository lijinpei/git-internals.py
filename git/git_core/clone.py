from git.context import Context
from git.command_base import GitCommand
from git.protocol import *
import sys

class GitClone(GitCommand):
    long_arg_handlers = {
            }
    short_arg_handlers = {
            }
    protocol_handlers = {
            'git': GitGitProtocol,
            'http': GitHttpProtocol,
            'https': GitHttpProtocol,
            'ssh': GitSshProtocol,
            }

    def __init__(self, context: Context, args):
        super().__init__(context)
        self.url = None
        self.directory = None
        self.parse_command_line_args(args)
        if self.directory == None:
            self.directory = GitClone.get_default_directory_from_url(self.url)

    def parse_command_line_args(self, args):
        argc = len(args)
        next_arg = 1
        while next_arg < argc:
            arg = args[next_arg]
            next_arg += 1
            if arg.startswith('--'):
                pass
            elif arg.startswith('-'):
                pass
            elif self.url == None:
                self.url = arg
            elif self.directory == None:
                self.directory = arg
            else:
                print('error: unknown argument ' + arg)
                sys.exit(1)

    @staticmethod
    def get_default_directory_from_url(url):
        last_slash_index = url.rfind('/')
        return url[last_slash_index + 1:]

    def run(self):
        protocol = None
        for prefix, proto_cls in self.protocol_handlers.items():
            if self.url.startswith(prefix + '://'):
                protocol = proto_cls()
                break
        if protocol == None:
            print('error: ' + self.url + ' is not a recognized url.')
            sys.exit(1)
        protocol.discover_refs(self.url)

def run(context: Context, args):
    command = GitClone(context, args)
    command.run()
