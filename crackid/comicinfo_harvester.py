'''                __     _    __
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
from .yactools import yaclist

class comicinfo_harvester(object):
    def __init__(self, args):
        self.args = args
        self.pathlist = [ tdir for tdir in args['PATH'] if os.path.exists(tdir) ]
        self.cmxdb = cmxdb()
        self.procarch = procarch()
        self.num_files = self.num_books = self.num_cinfo = 0
        self.out = console_output()
        self.walkgen = yaclist if self.args['-y'] else os.walk

    def proc_cinfo(self, fullpath):
        j = {}
        outjson = self.args['-j']
        outxml = self.args['-r']

        if not os.path.isfile(fullpath):
            return None

        if self.procarch.open_archive(fullpath):
            xmlstr = self.procarch.extract_comicinfo()
            if xmlstr is None:
#                print(f"No comicinfo.xml file in {fullpath}")
                return None

            if outjson and self.num_cinfo > 0:
                print(',')
            self.num_cinfo += 1
            fn = os.path.basename(fullpath)
            if not outjson:
                self.out.center_title(fn)
            self.cmxdb.parse_xml_str(xmlstr)
            if outxml:
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

        return j

    def proc_file(self, fullpath):
        j = None
        self.num_files += 1
        lcext = fullpath.lower()[-4:]
        if lcext in ['.cbr', '.cbz', '.rar', '.zip']:
            self.num_books += 1
            j = self.proc_cinfo(fullpath)
        return (j is not None)

    def scan_dirs(self):
        ''' the outside of the loop... for each arg, call proc_file if it's
            a file, do os.walk on the arg if it's a dir...
        '''
        self.num_files = self.num_books = self.num_cinfo = 0
        outjson = self.args['-j']

        if outjson:
            print("[")
        for basedir in self.pathlist:
            if os.path.isfile(basedir):
                self.proc_file(basedir)
                continue

            if not os.path.isdir(basedir):
                continue
            if self.args['-y']:
                print(f"Preparing generatrix with root: {self.args['-y']} and subpath: {basedir}")
                gen = self.walkgen(self.args['-y'], subpath=basedir)
            else:
                gen = os.walk(basedir, followlinks=True)
            for dirpath, dirnames, filenames in gen:
                for fn in filenames:
                    fullpath = os.path.join(dirpath, fn)
                    self.proc_file(fullpath)
        if outjson:
            print("]")

        # Display totals

        pct = '{}%'.format(round(self.num_cinfo/self.num_books * 10000) / 100.0)
        self.out.color_pairs([('Total # Files', self.num_files), ('Books', self.num_books), ('ComicInfo files', self.num_cinfo), ('Pct. with XML', pct)])
