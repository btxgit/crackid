import sys
from shutil import get_terminal_size
from textwrap import TextWrapper
from colorama import Fore, Back, Style

class console_output(object):
    def __init__(self):
        pass

    def center_title(self, title):
        ts = get_terminal_size()
        tl = len(title)
        padl = round((ts.columns - tl) / 2)
        padr = ts.columns - (padl + tl)
        padlstr = ' ' * padl
        padrstr = ' ' * padr
        sys.stdout.write("\n" + Style.BRIGHT + Back.BLUE + Fore.WHITE + padlstr + title + padrstr + Style.RESET_ALL + "\n" + Fore.YELLOW + Style.DIM + ' ̅' * ts.columns + Style.RESET_ALL + "\n" )
        sys.stdout.flush()

    def color_pairs(self, tups):
        ntups = len(tups)
        sepstr = ', '
        keysep = ': '
        sepwidth = (ntups - 1) * len(sepstr)
        olist = []
        kvlen = 0
        for key, val in tups:
            if not isinstance(val, str):
                val = str(val)
            kstr = Fore.GREEN + Style.NORMAL + '{}{}'.format(key, keysep)
            vstr = Fore.GREEN + Style.BRIGHT + '{}'.format(val)
            kvlen += (len(key) + len(keysep) + len(val))
            olist.append('{}{}{}'.format(kstr, vstr, Style.RESET_ALL))
        olstr = sepstr.join(olist)
        totwid = kvlen + sepwidth
        numspaces = (totwid // 2)
        sys.stdout.write('{}{}'.format(' ' * numspaces, olstr))
        sys.stdout.flush()

    def output_attrib(self, k, val):
        if val is None:
            return
        aname_color = Style.NORMAL + Fore.MAGENTA
        aval_color = Style.BRIGHT + Fore.MAGENTA
        close_color = Style.RESET_ALL
        attrib_width = 20
        attrib_plus_pad = attrib_width + 3

        fmtstr1 = '{}{:>%ds} {}{} {}{}\n' % attrib_width
        fmtstr2 = '{} {}{} {}{}\n'

        ts = get_terminal_size()
        tl = len(val)
        max_val_width = ts.columns - attrib_plus_pad
        alllines = []

        val = val.replace('\n', '\n\n').rstrip('\n')

        for line in val.split('\n'):
            tl = len(line)
            lines = []

            if tl < max_val_width:
                alllines.append(line)
            else:
                tw = TextWrapper(width=ts.columns - attrib_plus_pad, break_on_hyphens=False, break_long_words=False)
                for line in tw.wrap(line):
                    alllines.append(line)

        totlines = len(alllines)
        first = True
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


