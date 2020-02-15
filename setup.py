#!/usr/bin/env python3
            
import os
import re, sys
from setuptools import setup, find_packages
from setuptools import Command
from shutil import rmtree

class strip_spaces(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
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


class CleanCommand(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def clean_subdirs(self, basedir, clean_sfx=["~", ".bak"]):
        for rdir, dirs, fns in os.walk(basedir):
            for fn in fns:
                sys.stdout.write(".")
                sys.stdout.flush()
                do_rm = False
                for chk_sfx in clean_sfx:
                    if fn.endswith(chk_sfx):
                        do_rm = True
                        break
                
                if do_rm:
                    rmpath = os.path.join(rdir, fn)
                    print("Unlink path: {}".format(rmpath))

    def run(self):
        if '__file__' in dir():
            basedir = os.path.realpath(os.path.dirname(__file__))
        else:
            basedir = os.path.realpath('.')
        dpath = os.path.join(basedir, 'dist')
        bpath = os.path.join(basedir, 'build')
        print("Cleaning dist path...")
        rmtree(dpath, ignore_errors=True)
        print("Cleaning build path...")
        rmtree(bpath, ignore_errors=True)
        print("Removing garbage files...")
        self.clean_subdirs(basedir)

inrel=['colorama==0.4.1', 'rarfile==3.1']

def build_config(**kw):
    bcfg = {}
    
    for k in kw:
        bcfg[k] = kw[k]
    
    return bcfg
    
with open('crackid/__init__.py', 'rb') as fd:
    s = fd.read().decode('utf-8')

pat = re.search(r'''__version__\s*=\s*\'([^\']+)\'''', s)
if not pat:
    print("Unable to determine the verison number from the riphd.py file.")
    sys.exit(1)
    
rip_ver = pat.group(1)
# maj, min, rel = [ int(rv, 10) for rv in rip_ver.split('.') ]
# rel += 1
# rip_ver = f'{maj}.{min}.{rel}'

bcfg = build_config(
    name='crackid',
    version=rip_ver,
    packages=find_packages(),
#    py_modules=['crackid'],
    entry_points={
        'console_scripts': [ 'crackid=crackid.__main__:main' ]
    },
    description='ComicRack ComicInfo.xml file reader / consumer',
    author='btx',
    author_email='btx@btx.btx',
    license='MIT',
    url='http://donkeykong.net/crackid.tgz',
    install_requires=inrel
)

setup(zip_safe=False, cmdclass={ 'distclean': CleanCommand }, **bcfg)
