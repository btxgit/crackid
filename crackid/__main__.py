#!/usr/bin/env python3

'''
                   __     _    __
 ___________ _____/ /__  (_)__/ /
/ __/ __/ _ `/ __/  '_/ / / _  /
\__/_/  \_,_/\__/_/\_\ /_/\_,_/
----comic-rack-id-util-by-btx----

Usage:
  cinfo [-j | -r] [-y YACROOT] PATH...
  cinfo -h || cinfo --help

Options:
  -j             Display as JSON
  -r             Display as raw
  -y YACROOT     YAC (YACROOT must have the .yacreaderlibrary)
  -h --help      Show this screen
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
        base = input("Enter the directory to traverse: ")
        args['PATH'].append(base)

    cih = comicinfo_harvester(args)
    cih.scan_dirs()


if __name__ == '__main__':
    main()
