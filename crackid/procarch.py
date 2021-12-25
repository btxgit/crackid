r'''                __     _    __
 ___________ _____/ /__  (_)__/ /
/ __/ __/ _ `/ __/  '_/ / / _  /
\__/_/  \_,_/\__/_/\_\ /_/\_,_/
comic rack id class prototype btx
'''

import os
import zipfile
import rarfile
from colorama import Fore, Back, Style

class procarch(object):
    ''' Processes a single file (either rar or zip) and extracts comicinfo
        file (if any)
    '''

    def __init__(self):
        self.zipsig = bytes(b'PK\x03\x04')
        self.rarsig = bytes(b'Rar!')
        self.ao = None

    def open_archive(self, fullpath):
        sig = None
        self.fullpath = fullpath
        with open(self.fullpath, 'rb') as fd:
            sig = fd.read(16)

        bsig = sig[:4]

        if bsig == self.zipsig:
            self.ao = zipfile.ZipFile(self.fullpath)
        elif sig[0:4] == self.rarsig:
            self.ao = rarfile.RarFile(self.fullpath)
        else:
            print(f"{Style.BRIGHT}{Fore.RED}Illegal archive: {fullpath}{Style.RESET_ALL}")
            return False
        return True

    def extract_comicinfo(self):
        for ti in self.ao.infolist():
            if os.path.basename(ti.filename).lower() == 'comicinfo.xml':
                with self.ao.open(ti, 'r') as archread:
                    return archread.read()
        return None



