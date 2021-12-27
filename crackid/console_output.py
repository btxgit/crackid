r'''
                   __     _    __
 ___________ _____/ /__  (_)__/ /
/ __/ __/ _ `/ __/  '_/ / / _  /
\__/_/  \_,_/\__/_/\_\ /_/\_,_/
comic rack id class prototype btx
'''

import sys
import os
from shutil import get_terminal_size
import subprocess
import platform
import re
from PIL import Image
from io import BytesIO
import base64
import math
from textwrap import TextWrapper
import blessed

class console_output(object):
    ''' TODO: turn into a usable class
    '''
    def __init__(self, args):
        self.args = args
        self.term = blessed.Terminal()
        self.starty = None
        self.startx = None
        osver, _, arch =platform.mac_ver()
        self.is_macos = osver is not None and osver != ''
        print("\n\n\n\n\n\n\n\n\n\n\n")

    def prepare_newbook(self):
        ''' This needs to exist because the attribute drawing code is called
            1 attribute at a time and can't recognize ahead of time if there
            will be a comicinfo.xml file within the next file.
        '''

        self.starty = None
        self.startx = None

    def center_title(self, title):
        ts = get_terminal_size()
        pat = re.search(r'(.+) \(Digital\).+$', title, re.I)
        if pat is not None:
            title = pat.group(1)
        tl = len(title)
        padl = round((ts.columns - tl) / 2)
        padr = ts.columns - (padl + tl)
        padlstr = ' ' * padl
        padrstr = ' ' * padr
        linec = '⎽'
        topline = linec * (ts.columns)
        linec = '⎺'
        botline = linec * (ts.columns)
        tline = linec*(ts.columns)
        sys.stdout.write("\r" + self.term.bright_yellow_on_black + topline + self.term.normal)
        sys.stdout.write("%s\n" % self.term.white_on_blue + padlstr + title + padrstr + self.term.normal)
        sys.stdout.write('%s\n' % (self.term.bright_yellow_on_black + botline + self.term.normal))
        sys.stdout.flush()

    def macos_get_pixwidth(self):
        cmd = ['/usr/bin/osascript', '-e', '''tell application "iTerm2" to get the bounds of the front window''']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs, errs = p.communicate()

        x1, y1, x2, y2 = [ int(ti, 10) for ti in outs.decode('utf-8').strip().split(', ') ]
        wid = x2-x1
        ht = y2-y1
        return (wid, ht)

    def disp_cov(self, cov, fn):
        ''' This contains some nonstandard feature usage...
            - It calls the iTerm2 Image protocoll, which lets you
              display images in your term window, but has little
              support from other terminal programs.
            - It calls some Apple Script launcher (I think?) to
              get the current windows' dimensions in pixels.
            - For now, this method will fail on non-Macs
        '''
        if not self.is_macos:
            print("This is not running on macOS, which is the only supported platform for use with the -c (display cover) feature.")
            sys.exit(1)

# Get # of chars wide / lines high
        ts = get_terminal_size()
# Open cover img in pillow so we can generate a thumbnail-sized image
        im = Image.open(cov)
# Call applescript to get the pixel width & height of the current active iterm2 window
        scwid, scht = self.macos_get_pixwidth()

# Work out the cover's A/R
        w = im.width
        h = im.height
        fmt = im.format
        ratio = (w * 1.0) / h
# Normalize on 320px high unless the cover is shorter
        th = 320
        if (th > h):
            th = h
        tw = int(round(th * ratio))
# Get how many pixels per character
        ppc_w = scwid / ts.columns
        ppc_h = scht / ts.lines

#        print(f"((scwid: {scwid} - tw: {tw}) / 2) // ppc_w: {ppc_w}")
# Use that info  to figure out how to position properly
        nc = math.ceil(tw / ppc_w)
        nch = math.ceil(th / ppc_h) + 1

        self.starty, self.startx = self.term.get_location()
        self.starty -= nch
        self.startx = nc
#        print(f"Startx: {self.startx}  starrty: {self.starty}")
        b64fn = base64.b64encode(fn.encode('utf-8'))

# Make a lanczos thumbnail
        im.thumbnail(size=(tw, th), resample=Image.LANCZOS)
        io = BytesIO()

        with BytesIO() as ofd:
            im.save(ofd, format=fmt)
            d = base64.b64encode(ofd.getvalue())
# Write result to a BytesIO()

# This is just image protocol crap
        sys.stdout.write("\033]1337;File=inline=1;preserveAspectRatio=1;name='%s';width=%dpx;height=%dpx:" % (b64fn, tw, th))
        sys.stdout.write(d.decode('utf-8'))
        sys.stdout.write("\a")
        sys.stdout.write("\n")
#        sys.stdout.write("\n\033[A%s\n" % fn)
        sys.stdout.flush()


    def color_pairs(self, tups):
        ''' Create the end banner
        '''
        ts = get_terminal_size()
        ntups = len(tups)
        sepstr = ', '
        keysep = ': '
        sepwidth = (ntups - 1) * len(sepstr)
        olist = []
        kvlen = 0
        for key, val in tups:
            if not isinstance(val, str):
                val = str(val)

            kstr = self.term.black_on_white + '{}{}'.format(key, keysep)
            vstr = self.term.black_on_white + '{}'.format(val)
            kvlen += (len(key) + len(keysep) + len(val))
            olist.append('{}{}'.format(kstr, vstr))
        olstr = sepstr.join(olist)
        totwid = kvlen + sepwidth
        padl = round((ts.columns - totwid) / 2)
        padr = ts.columns - (totwid + padl)
        linec = '⎽'
        linetop = linec * ts.columns
        linec = '⎺'
        linebot = linec * ts.columns
        sys.stdout.write('\r{}{}\n'.format(self.term.white_on_black, linetop))
        sys.stdout.write('{}{}{}{}{}\n'.format(self.term.black_on_white, ' ' * padl, olstr, ' ' * padr, self.term.normal))
        sys.stdout.write('{}{}\n'.format(self.term.white_on_black, linebot))
        sys.stdout.flush()

    def output_attrib(self, k, val):
        ''' Output the fancy attributes, 1 at a time
        '''
        if val is None:
            return
        aname_color = self.term.magenta
        aval_color = self.term.bright_magenta
        close_color = self.term.normal
        attrib_width = 18
        if self.startx is None:
            self.startx = 0
        attrib_plus_pad = (attrib_width + 3 + self.startx)

        fmtstr1 = '{}{:>%ds} {}{} {}{}\n' % attrib_width
        fmtstr2 = '{} {}{} {}{}\n'

        ts = get_terminal_size()
        tl = len(val)
        max_val_width = ts.columns - attrib_plus_pad
        alllines = []
        repnl = '\n\n' if k == 'Summary' else '\n'

        val = val.replace('\n', repnl).rstrip('\n')

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
                if k == 'urls':
                    return
                if k in ['Web']:
                    line = self.term.link(line, 'Link to listing')
                outstr = fmtstr1.format(aname_color, k, aval_color, sep, line, close_color)
                first = False
            else:
                if ln + 1 == totlines:
                    sep = '╰'
                else:
                    sep = '┊'
                outstr = fmtstr2.format(' ' * attrib_width, aval_color, sep, line, close_color)

            if self.starty is not None:
                with self.term.location(y=self.starty, x=self.startx):
                    sys.stdout.write(outstr)
                    sys.stdout.flush()
                    self.starty += 1
            else:
                sys.stdout.write(outstr)
                sys.stdout.flush()


