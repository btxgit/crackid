#!/usr/bin/env python3

r'''
                   __     _    __
 ___________ _____/ /__  (_)__/ /
/ __/ __/ _ `/ __/  '_/ / / _  /
\__/_/  \_,_/\__/_/\_\ /_/\_,_/
----comic-rack-id-util-by-btx----

Usage:
  crackid [-j | -r] [-v] PATH...
  crackid [-j | -r] [-u] [-v] -y YACROOT [PATH...]
  crackid -h || crackid --help

Options:
  -h|--help      Show this screen
  -j             Display as JSON
  -r             Display as raw
  -u             Update YACReader database
  -v             Verbose mode - output debug info
  -y YACROOT     YAC (YACROOT must have the .yacreaderlibrary)
  --version      Show the current version
'''

import os
import sys
from crackid import comicinfo_harvester
from colorama import init
from docopt import docopt
from . import __version__

init()

def main():
    args = docopt(__doc__, version=__version__)

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

