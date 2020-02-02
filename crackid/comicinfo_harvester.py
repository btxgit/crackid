'''                __     _    __
 ___________ _____/ /__  (_)__/ /
/ __/ __/ _ `/ __/  '_/ / / _  / 
\__/_/  \_,_/\__/_/\_\ /_/\_,_/  
comic rack id class prototype btx
'''

import os
import sys
from shutil import get_terminal_size
from textwrap import TextWrapper
from colorama import Fore, Back, Style
from .cmxdb import cmxdb
from .procarch import procarch

def center_title(title):
    ts = get_terminal_size()
    tl = len(title)
    padl = round((ts.columns - tl) / 2)
    padr = ts.columns - (padl + tl)
    padlstr = ' ' * padl
    padrstr = ' ' * padr
    sys.stdout.write("\n" + Style.BRIGHT + Back.BLUE + Fore.WHITE + padlstr + title + padrstr + Style.RESET_ALL + "\n" + Fore.YELLOW + Style.DIM + ' ̅' * ts.columns + Style.RESET_ALL + "\n" )
    sys.stdout.flush()

def color_pairs(tups):
    olist = []
    for key, val in tups:
        kstr = Fore.GREEN + Style.NORMAL + '{}: '.format(key)
        vstr = Fore.GREEN + Style.BRIGHT + '{}'.format(val)
        olist.append('{}{}{}'.format(kstr, vstr, Style.RESET_ALL))
    olstr = ', '.join(olist)
    sys.stdout.write(olstr)
    sys.stdout.flush()

def output_attrib(k, val):
    aname_color = Style.NORMAL + Fore.MAGENTA
    aval_color = Style.BRIGHT + Fore.MAGENTA
    close_color = Style.RESET_ALL
    attrib_width = 20
    attrib_plus_pad = attrib_width + 3

    fmtstr1 = '{}{:>%ds} {}{} {}{}\n' % attrib_width
    fmtstr2 = '{} {}{} {}{}\n'

    ts = get_terminal_size()
    if val is None:
        return
    tl = len(val)
    max_val_width = ts.columns - attrib_plus_pad
    alllines = []
    
    for line in val.split('\n'):
        tl = len(line)
        lines = []
        
        if tl < max_val_width:
            alllines.append(line)
        else:
            tw = TextWrapper(width=ts.columns - attrib_plus_pad, break_on_hyphens=False, break_long_words=False)
#            line = ' ' * attrib_plus_pad + line
            for line in tw.wrap(line):
                alllines.append(line)

    totlines = len(alllines)
    first = True
#    sys.stdout.write("\n\n%s\n" % str(alllines))
#    sys.stdout.flush()
    for ln in range(totlines):
        line = alllines[ln].strip()
        if first:
            sep = '┉' if totlines == 1 else '╭'
            outstr = fmtstr1.format(aname_color, k, aval_color, sep, line, close_color)
            first = False
        else:
            if ln + 1 == totlines:
                sep = '╰'
            else:
                sep = '┊'
            outstr = fmtstr2.format(' ' * attrib_width, aval_color, sep, line, close_color)
        sys.stdout.write(outstr)
        sys.stdout.flush()


class comicinfo_harvester(object):
    def __init__(self, basedir='.'):
        self.cmxdb = cmxdb()
        self.procarch = procarch()
        self.basedir = os.path.realpath(basedir)
        self.num_files = self.num_books = self.num_cinfo = 0
        
    def process_file(self, fullpath):
        if self.procarch.open_archive(fullpath):
            xmlstr = self.procarch.extract_comicinfo()
            if xmlstr is None:
                return False
            self.num_cinfo += 1
            fn = os.path.basename(fullpath)
            center_title(fn)
            self.cmxdb.parse_xml_str(xmlstr)

            for k in sorted(self.cmxdb.doc.keys(), key=lambda x: x.lower()):
                if k.lower() == 'comicinfo':
                    continue
                val = self.cmxdb.doc[k]
                if val is None:
                    continue
                if not isinstance(val, str):
                    val = str(val)

                val = val.strip()
                if val == '':
                    continue
                output_attrib(k, val)
        return True

    def scan_dirs(self):
        self.num_files = self.num_books = self.num_cinfo = 0

        for dirpath, dirnames, filenames in os.walk(self.basedir, followlinks=True):
            for fn in filenames:
                self.num_files += 1
                lcext = fn.lower()[-4:]
                if lcext in ['.cbr', '.cbz', '.rar', '.zip']:
                    self.num_books += 1
                    fullpath = os.path.join(dirpath, fn)
                    if not self.process_file(fullpath):
                        continue
        print()
        pct = '{}%'.format(round(self.num_cinfo/self.num_books * 10000) / 100.0)
        color_pairs([('Total # Files', self.num_files), ('Books', self.num_books), ('ComicInfo files', self.num_cinfo), ('Pct. with XML', pct)])
