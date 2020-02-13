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


class comicinfo_harvester(object):
    def __init__(self, args):
        self.args = args
        self.pathlist = [ os.path.realpath(tdir) for tdir in args['PATH'] if os.path.exists(tdir) ]
        self.cmxdb = cmxdb()
        self.procarch = procarch()
        self.num_files = self.num_books = self.num_cinfo = 0
        self.out = console_output()

    def proc_cinfo(self, fullpath):
        j = {}
        outjson = self.args['-j']
        if self.procarch.open_archive(fullpath):
            xmlstr = self.procarch.extract_comicinfo()
            if xmlstr is None:
#                print(f"No comicinfo.xml file in {fullpath}")
                return False
            if outjson and self.num_cinfo > 0:
                print(',')
            self.num_cinfo += 1
            fn = os.path.basename(fullpath)
            if not outjson:
                self.out.center_title(fn)
            self.cmxdb.parse_xml_str(xmlstr)
            if self.args['-r']:
                print(xmlstr)
                return True

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

                if not outjson:
                    self.out.output_attrib(k, val)
                else:
                    j[k] = val
        if outjson:
            print(json.dumps(j))

        return True

    def proc_file(self, fullpath):
        self.num_files += 1
        lcext = fullpath.lower()[-4:]
        if lcext in ['.cbr', '.cbz', '.rar', '.zip']:
            self.num_books += 1

            return self.proc_cinfo(fullpath)
        return False

    def scan_dirs(self):
        self.num_files = self.num_books = self.num_cinfo = 0
        outjson = self.args['-j']

        if outjson:
            print("[")
        for basedir in self.pathlist:
            if os.path.isfile(basedir):
#                print(f"Processing file: {basedir}")
                self.proc_file(basedir)
                continue

            if not os.path.isdir(basedir):
                continue

            for dirpath, dirnames, filenames in os.walk(basedir, followlinks=True):
                for fn in filenames:
                    fullpath = os.path.join(dirpath, fn)
                    self.proc_file(fullpath)
        if outjson:
            print("]")

        print()
        pct = '{}%'.format(round(self.num_cinfo/self.num_books * 10000) / 100.0)
        self.out.color_pairs([('Total # Files', self.num_files), ('Books', self.num_books), ('ComicInfo files', self.num_cinfo), ('Pct. with XML', pct)])


