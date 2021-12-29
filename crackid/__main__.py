#!/usr/bin/env python3

r'''
                   __     _    __
 ___________ _____/ /__  (_)__/ /
/ __/ __/ _ `/ __/  '_/ / / _  /
\__/_/  \_,_/\__/_/\_\ /_/\_,_/
----comic-rack-id-util-by-btx----

Usage:
  crackid [-cFv] [-j | -r] [-g WxY] PATH...
  crackid [-cFuv] [-j | -r] [-g WxY] -y YACROOT [PATH...]
  crackid -h || crackid --help

Options:
  -h|--help      Show this screen
  -c             Display the cover [for iTerm2 only currently]
  -F             Filename minimization - minimize the filename in some cases
  -g WxY         Specify the width and height of your term window - do not include the decorations.  Use the wxy form like 320x240.
  -j             Display as JSON
  -r             Display as raw
  -u             Update YACReader database
  -v             Verbose mode - output debug info
  -y YACROOT     YAC (YACROOT must have the .yacreaderlibrary)
  --version      Show the current version
'''

import os
import sys
import platform
from crackid import comicinfo_harvester
from colorama import init
from docopt import docopt
from . import __version__

init()

def main():
    args = docopt(__doc__, version=__version__)

    if args['-c']:
        if ('LC_TERMINAL' not in os.environ or os.environ['LC_TERMINAL'] != 'iTerm2') and os.environ['TERM'] != 'xterm-kitty':
            print("[Error] Unable to use the -c functionality on non-iTerm2 terminals.")
            sys.exit(1)

    if len(args['PATH']) == 0:
        if not args['-y']:
            base = input("Enter the directory to traverse: ")
            args['PATH'].append(base)
        else:
            args['PATH'].append(args['-y'])

    cih = comicinfo_harvester(args)
    cih.scan_dirs()


if __name__ == '__main__':
    main()
