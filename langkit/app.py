import os
import sys
import traceback

from .commands import help, PLUGINS
from .lang import Lang
from .ui import *


def help(cmd=None):
    print("""
lk -- develop artifacts for artificial languages
          
Available commands
""")
    for name, func in PLUGINS.items():
        doc = func.__doc__.strip()
        i = doc.find('-')
        syntax, doc = doc[:i].rstrip(), doc[i+1:].lstrip()
        print(f"  lk LANGDIR {name} {syntax}\n      {doc}\n")
    print("  lk help [cmd]\n      display general help, or help on a specific command\n")

def match_command(which):
    for name, func in PLUGINS.items():
        if name == which:
            return func
    sys.stderr.write("\nCan't find command '%s'.\n" % which)
    return help.cmd

def main(argv = None):
    if not argv:
        argv = sys.argv
    show_help = len(argv) < 3
    if not show_help:
        try:
            if not os.path.isdir(argv[1]):
                print("First argument must be a folder that contains a language.")
                show_help = True
            lang = Lang(argv[1])
            cmd = match_command(argv[2])
            if cmd:
                cmd(lang, *argv[3:])
            else:
                sys.stderr.write('\nBad command-line syntax.\n')
                show_help = True
        except KeyboardInterrupt:
            sys.stdout.write('\n')
            sys.exit(0)
        except Exception as e:
            err = traceback.format_exc()
            cprint(err, ERROR_COLOR)
            show_help = True
    if show_help:
        help()
        sys.exit(1)

if __name__ == '__main__':
    main()