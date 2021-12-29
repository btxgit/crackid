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
import warnings
warnings.simplefilter("ignore")
from PIL import Image
from io import BytesIO
import base64
import math
from textwrap import TextWrapper
import blessed

def kitty_image(data):
    from base64 import standard_b64encode

    def serialize_gr_command(**cmd):
        payload = cmd.pop('payload', None)
        cmd = ','.join('{}={}'.format(k, v) for k, v in cmd.items())
        ans = []
        w = ans.append
        w(b'\033_G'), w(cmd.encode('ascii'))
        if payload:
            w(b';')
            w(payload)
        w(b'\033\\')
        return b''.join(ans)


    def write_chunked(**cmd):
        data = standard_b64encode(cmd.pop('data'))
        while data:
            chunk, data = data[:4096], data[4096:]
            m = 1 if data else 0
            sys.stdout.buffer.write(serialize_gr_command(payload=chunk, m=m,
                                                        **cmd))
            sys.stdout.flush()
            cmd.clear()
        sys.stdout.buffer.write(b"\n")
        sys.stdout.flush()

    write_chunked(a='T', f=100, data=data)


class console_output(object):
    ''' TODO: turn into a usable class
    '''
    def __init__(self, args):
        self.args = args

        if os.environ['TERM'] == 'xterm-kitty':
            self.imgterm = 'kitty'
        else:
            self.imgterm = 'iterm2'
        
        self.args = args
        self.term = blessed.Terminal()
        if self.term.number_of_colors < 256:
            print("Got just %d colors" % self.term.number_of_colors)
            sys.exit(1)
        self.starty = None
        self.startx = None
        osver, _, arch =platform.mac_ver()
        self.is_macos = osver is not None and osver != ''
        if self.args['-g'] is not None:
            if 'x' not in self.args['-g']:
                print("[Error] The geometry must be specified in the form wxh  - example:  640x480")
                sys.exit(1)
                
            self.scwid, self.scht = [ int(sci, 10) for sci in self.args['-g'].lower().split('x') ]
        elif self.is_macos:
            self.scwid, self.scht = self.macos_get_pixwidth()
            self.scht -= 35
        else:
            print("[Error] The window geometry must be specified in order to display a cover.")
            sys.exit(1)
            
        print(self.term.clear)
        ts = get_terminal_size()
# Get how many pixels per character
        self.ppc_w = self.scwid / ts.columns
        self.ppc_h = self.scht / ts.lines
        print(self.term.move_yx(ts.lines-1, 0))

    def prepare_newbook(self):
        ''' This needs to exist because the attribute drawing code is called
            1 attribute at a time and can't recognize ahead of time if there
            will be a comicinfo.xml file within the next file.
        '''

        self.starty = None
        self.startx = None

    def center_title(self, title):
        ts = get_terminal_size()

        if self.args['-F']:
            pat = re.search(r'(.+) \((Digital|Webrip)\).+$', title, re.I)
            if pat is not None:
                title = pat.group(1)

        tl = len(title)
        padl = round((ts.columns - tl) / 2)
        padr = ts.columns - (padl + tl)
        padlstr = ' ' * padl
        padrstr = ' ' * padr
        linec = '⎽'
        linec = chr(0x2582)
        topline = linec * (ts.columns)
        linec = '⎺'
        linec = chr(0x2594)
        botline = linec * (ts.columns)
        tline = linec*(ts.columns)
        sys.stdout.write("\r" + self.term.blue_on_black + topline + self.term.normal)
        sys.stdout.write("%s\n" % self.term.bold + self.term.bright_white_on_darkblue + padlstr + title + padrstr + self.term.normal)
        sys.stdout.write('%s\n' % (self.term.blue_on_black + botline + self.term.normal))
        sys.stdout.flush()

    def macos_get_pixwidth(self):
        ''' Call applescript to get the pixel width & height of the current active iterm2 window
        '''
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
# Open cover img in pillow so we can generate a thumbnail-sized image
        im = Image.open(cov)

# Work out the cover's A/R
        w = im.width
        h = im.height
        ratio = (w * 1.0) / h
# Normalize on 320px high unless the cover is shorter
        th = 320
        if (th > h):
            th = h
        tw = int(round(th * ratio))

#        print(f"((scwid: {self.scwid} - tw: {tw}) / 2) // self.ppc_w: {self.ppc_w}")
# Use that info  to figure out how to position properly
        nc = math.ceil(tw / self.ppc_w)
        nch = math.ceil(th / self.ppc_h)

        self.starty, self.startx = self.term.get_location()
        self.starty -= nch
        self.startx = nc
#        print(f"Startx: {self.startx}  starrty: {self.starty}")
        b64fn = base64.b64encode(fn.encode('utf-8'))

# Make a lanczos thumbnail
        im.thumbnail(size=(tw, th), resample=Image.LANCZOS)
        io = BytesIO()

        with BytesIO() as ofd:
            if self.imgterm == 'kitty':
                fmt = 'PNG'
            else:
                fmt = im.format
            im.save(ofd, format=fmt)
            if self.imgterm == 'kitty':
                kitty_image(ofd.getvalue())
                return

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

            kstr = self.term.bold + self.term.black_on_white + '{}{}'.format(key, keysep)
            vstr = self.term.bold + self.term.black_on_white + '{}'.format(val)
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
        aname_color = self.term.darkmagenta
        aval_color = self.term.bold + self.term.bright_magenta
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
