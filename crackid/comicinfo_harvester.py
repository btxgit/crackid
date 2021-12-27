r'''                __     _    __
 ___________ _____/ /__  (_)__/ /
/ __/ __/ _ `/ __/  '_/ / / _  /
\__/_/  \_,_/\__/_/\_\ /_/\_,_/
comic rack id class prototype btx
'''

import os
import sys
from .cmxdb import cmxdb
from .procarch import procarch
from pprint import pprint
import json
from .console_output import console_output
from shutil import get_terminal_size
from .yactools import yaclist, update_library
from time import time

class comicinfo_harvester(object):
    def __init__(self, args):
        self.args = args

        self.pathlist = [ tdir for tdir in args['PATH'] if os.path.exists(tdir) ]
        self.cmxdb = cmxdb()
        self.procarch = procarch()
        self.num_files = self.num_books = self.num_cinfo = 0
        self.out = console_output(args)
        self.walkgen = yaclist if self.args['-y'] else os.walk
        self.verbose = self.args['-v']

    def proc_cinfo(self, fullpath, id):

        ''' Checks to see if fullpath is an archive.  If so, it checks to
            see if there is a comicinfo.xml - if so, return th string in
            xmlstr.

            For each attribute, call output_attrib()

            If update is set, then update the yacreader record

            Returns: dict containing the attributees or None
        '''

        j = {'filename': os.path.basename(fullpath)}
        outjson = self.args['-j']
        outxml = self.args['-r']



        if self.procarch.open_archive(fullpath):
            xmlstr = self.procarch.extract_comicinfo()
            if xmlstr is None:
                if self.verbose:
                    print(f"No comicinfo.xml file in {fullpath}")
                return None

            if outjson and self.num_cinfo > 0:
                print(',')
            self.num_cinfo += 1
            fn = os.path.basename(fullpath)

            if not outjson:
                self.out.center_title(fn)

            self.cmxdb.parse_xml_str(xmlstr)

            if outxml:
                xmlstr = xmlstr.decode('utf-8')
                print(xmlstr)

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

                if not outjson and not outxml:
                    self.out.output_attrib(k, val)
                j[k] = val
        else:
            print(f"Error: Unable to open archive: {fullpath}")
            return None

        if outjson:
            print(json.dumps(j))

        if self.args['-y'] and self.args['-u']:
            dbbase = os.path.realpath(self.args['-y'])
            db_rel = '.yacreaderlibrary/library.ydb'
            db_path = os.path.join(dbbase, db_rel)
            update_library(db_path, id, j)

        return j

    def proc_file(self, fullpath, id):

        ''' Called for each file we want to process.  Does a little sanity
            checking vs.  the file, then calls self.proc_cinfo().

            Returns: True if this file had a parsable ComicInfo file,
            something, False otherwise
        '''

        j = None
        self.num_files += 1

        if not os.path.isfile(fullpath):
            if self.verbose:
                print(f"Pathname {fullpath} is not a file.")
            return None

        lcext = fullpath.lower()[-4:]
        if lcext in ['.cbr', '.cbz', '.rar', '.zip']:
            self.num_books += 1

            if self.verbose:
                print(f"Processing file: {fullpath}")

            j = self.proc_cinfo(fullpath, id)
        return (j is not None)

    def scan_dirs(self):
        ''' the outside of the loop... for each self.pathlist (the PATH args on the cmdline),..

        '''
        self.num_files = self.num_books = self.num_cinfo = 0
        outjson = self.args['-j']

        if outjson:
            print("[")
            
        spin = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        n = 0
        ndirs = nfiles = 0
        for basedir in self.pathlist:
            if os.path.isfile(basedir):
                self.proc_file(basedir, None)
                continue

            if not os.path.isdir(basedir):
                continue
            if self.args['-y']:
#                print(f"Preparing generatrix with root: {self.args['-y']} and subpath: {basedir}")
                gen = self.walkgen(self.args['-y'], subpath=basedir, verbose=self.verbose)
            else:
                gen = os.walk(basedir, followlinks=True)

            for dirpath, dirnames, filenames in gen:
                bdp = os.path.basename(dirpath)
                for fnt in filenames:
                    if isinstance(fnt, tuple):
                        fn, id = fnt
                    else:
                        fn = fnt
                        id = None

                    if self.verbose:
                        print(f"Dirpath: {dirpath}   fn: {fn}")

                    fullpath = os.path.join(dirpath, fn)
                    self.proc_file(fullpath, id)
                    nfiles += 1
                    if bdp == '':
                        bdp = os.sep
                    ts = get_terminal_size()
                    clr = ts.columns * ' '
                    sys.stdout.write("\r%s\r%s   Dirs: %d, Fiiles: %d" % (clr, spin[n], ndirs, nfiles))
                    n += 1
                    if n >= len(spin):
                        n = 0
                        
                    sys.stdout.flush()
                ndirs += 1
        if outjson:
            print("]")

        # Display totals

        if self.num_books > 0:
            pct = '{}%'.format(round(self.num_cinfo/self.num_books * 10000) / 100.0)
        else:
            pct = "N/A"
        print
        self.out.color_pairs([('Total # Files', self.num_files), ('Books', self.num_books), ('ComicInfo files', self.num_cinfo), ('Pct. with XML', pct)])


