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
import sqlite3
from .console_output import console_output
from shutil import get_terminal_size
from .yactools import yaclist, update_library
from time import time

class comicinfo_harvester(object):
    ''' Harvester's job is to decide on a source for a filelist generator
        that will be used to locate files to process.
    '''

    def __init__(self, args):
        self.args = args

        self.pathlist = [ tdir for tdir in args['PATH'] if os.path.exists(tdir) ]
        self.cmxdb = cmxdb()
        self.procarch = procarch()
        self.num_files = self.num_books = self.num_cinfo = 0
        self.out = console_output(args)
        self.walkgen = yaclist if self.args['-y'] else os.walk
        self.verbose = self.args['-v']
        self.db = None
        self.cur_dir = None
        self.cur_dirid = None
        if self.args['-D'] is not None:
            self.db = sqlite3.connect(self.args['-D'], isolation_level = 'DEFERRED')
            sql = '''CREATE TABLE IF NOT EXISTS crackdb(dirid integer, filename TEXT, json text, PRIMARY KEY(dirid, filename));
            CREATE TABLE IF NOT EXISTS dirs(dirid integer PRIMARY KEY autoincrement, directory TEXT not null);
            CREATE UNIQUE INDEX IF NOT EXISTS dirname ON dirs(directory ASC);'''
            self.db.executescript(sql)
            self.db.commit()

    def get_or_add_dirid(self, dir):
        ''' Locate the dirid entry in the dirs table for this current
            directory
         '''

# Simple 1 directory cache for the current directory
        if self.cur_dir is not None and self.cur_dir == dir:
            return self.cur_dirid

        sql = 'SELECT dirid FROM dirs WHERE directory=?;'
        t = (dir, )

# Set the cached dir name.  DOnt forget to set the dirid when
# we get it.
        self.cur_dir = dir
        for row in self.db.execute(sql, t):
            dirid = row[0]
            self.cur_dirid = dirid
            return(dirid)

# Must be a new entry.  Insert it and get the lastrowid
        sql = 'INSERT INTO dirs(directory) VALUES (?);'
        t = (dir, )

        cur = self.db.execute(sql, t)
        self.db.commit()
        dirid = cur.lastrowid
        self.cur_dirid = dirid
        return dirid

    def add_db(self, fullpath, doc):
        ''' Split up fullpath, get the dirid, check if
            it exists in the db, if so we're good.  If not,
            insert it.
        '''

        fn = os.path.basename(fullpath)
        dir = os.path.dirname(fullpath)
        dirid = self.get_or_add_dirid(dir)

        sql = 'SELECT COUNT(*) FROM crackdb WHERE (dirid=? AND filename=?);'
        t = (dirid, fn)

        cnt = 0
        for row in self.db.execute(sql, t):
            cnt = row[0]

        if cnt > 0:
            return

        j = json.dumps(doc)
        t = (dirid, fn, j)
        sql = 'INSERT INTO crackdb(dirid, filename, json) VALUES(?, ?, ?);'
        self.db.execute(sql, t)
        self.db.commit()

    def proc_xml(self, fullpath, xmlstr, outxml, outjson):
        ''' Parse xmlstr int oa JSON document, which
            we pass to the db routines before arranging it
            and ultimately displaying to screen.
        '''

        j = {'filename': os.path.basename(fullpath)}
        self.cmxdb.parse_xml_str(xmlstr)

        if outxml:
            xmlstr = xmlstr.decode('utf-8')
            print(xmlstr)

        if self.args['-D'] is not None:
            self.add_db(fullpath, self.cmxdb.doc)

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

        return j

    def proc_cinfo(self, fullpath, id):

        ''' Checks to see if fullpath is an archive.  If so, it checks to
            see if there is a comicinfo.xml - if so, return th string in
            xmlstr.

            For each attribute, call output_attrib()

            If update is set, then update the yacreader record

            Returns: dict containing the attributees or None
        '''
        j = None
        outjson = self.args['-j']
        outxml = self.args['-r']
        outcov = self.args['-c']
        xmlstr = cov = None

        if self.procarch.open_archive(fullpath):
            fn = os.path.basename(fullpath)

            self.out.prepare_newbook()
            xmlstr, cov = self.procarch.extract_comicinfo(self.args['-c'])

            if (xmlstr is not None and not outjson) or (outcov and cov is not None):
                self.out.center_title(fn)

            if outcov and cov is not None:
                if fn is None:
                    fn = os.path.basename(fullpath)
                self.out.disp_cov(cov, fn)

            if xmlstr is None:
                if self.verbose:
                    print(f"No comicinfo.xml file in {fullpath}")
            else:
                j = self.proc_xml(fullpath, xmlstr, outxml, outjson)

            if outjson and self.num_cinfo > 0:
                print(',')
            if j is not None:
                self.num_cinfo += 1

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
        ''' the outside of the loop...  for each self.pathlist (the PATH
            args on the cmdline),..
        '''

        self.num_files = self.num_books = self.num_cinfo = 0
        outjson = self.args['-j']

        if outjson:
            print("[")

        spin = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        n = 0
        ndirs = nfiles = 0

        if self.args['-v']:
            print(f"pathlist: {self.pathlist}")

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
        self.out.color_pairs([('Total # Files', self.num_files), ('Books', self.num_books), ('ComicInfo.xml files', self.num_cinfo), ('Pct. with XML', pct)])
