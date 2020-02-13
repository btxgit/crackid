import os
import sys
import re

class strip_spaces(object):
    def __init__(self):
        self.reg = re.compile(r'\s+$')

    def stripfn(self, fn):
        with open(fn, 'rt', encoding='utf-8') as fd:
            s = fd.read()

        with open(fn, 'wt', encoding='utf-8') as fd:
            for line in s.split('\n'):
                s2 = self.reg.sub('', line)
                fd.write(f"{s2}\n")

    def strip_all(self, bd):
        basedir = os.path.realpath(bd)

        for dirpath, dirnames, filenames in os.walk(basedir):
            if 'bak' in dirnames:
                dirnames.remove('bak')

            for fn in filenames:
                if not fn.endswith('.py'):
                    continue

                fp = os.path.join(dirpath, fn)
                if os.path.exists(fp):
                    self.stripfn(fp)

if __name__ == '__main__':
    ssp = strip_spaces()
    setupdir = os.path.dirname(os.path.realpath(sys.argv[0]))
    ssp.strip_all(setupdir)



