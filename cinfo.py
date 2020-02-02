#!/usr/bin/env python3

'''                __     _    __
 ___________ _____/ /__  (_)__/ /
/ __/ __/ _ `/ __/  '_/ / / _  / 
\__/_/  \_,_/\__/_/\_\ /_/\_,_/  
comic rack id class prototype btx
'''

import os
import sys
from crackid import comicinfo_harvester
from colorama import init


init()


if __name__ == '__main__':
    args = sys.argv[1:]
    argc = len(args)

    if argc == 0:
        base = input("Enter the directory to traverse: ")
        args.append(base)

    for base in args:
        cih = comicinfo_harvester(base)
        cih.scan_dirs()
