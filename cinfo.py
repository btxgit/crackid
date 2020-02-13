#!/usr/bin/env python3

'''
                   __     _    __
 ___________ _____/ /__  (_)__/ /
/ __/ __/ _ `/ __/  '_/ / / _  /
\__/_/  \_,_/\__/_/\_\ /_/\_,_/
----comic-rack-id-util-by-btx----

Usage:
  cinfo [-j | -r] PATH...
  cinfo -h || cinfo --help

Options:
  -j             Display as JSON
  -r             Display as raw
  -h --help      Show this screen

'''

import os
import sys
from crackid import comicinfo_harvester
from colorama import init
from docopt import docopt

__version__='0.4.0'

init()


if __name__ == '__main__':
    args = docopt(__doc__, version=__version__)

    if len(args['PATH']) == 0:
        base = input("Enter the directory to traverse: ")
        args['PATH'].append(base)

    cih = comicinfo_harvester(args)
    cih.scan_dirs()



