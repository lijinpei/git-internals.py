import sys
from git.context import Context

should_print_version = False
should_print_help = False

command_line_context = Context()

def cmd_version_handler(next_arg, args):
    should_print_version = True
    return next_arg

def cmd_help_handler(next_arg, args):
    should_print_help = True
    return next_arg

def error_cmd_handler(next_arg, args):
    this_arg = args[next_arg - 1]
    print('unknown command line argument:', this_arg, file=sys.stderr)
    sys.exit(1)

def print_help():
    pass
