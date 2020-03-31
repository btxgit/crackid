''' Functions for working with YACreader
'''

import os
import sqlite3

def yaclist(base, **kwargs):
    ''' A drop-in replacement for os.walk that will iterate over each file
        in your YACreader Library.

        Note: The kwargs are not evaluated, even those that make sense in this context.
    '''

    print(f"Top: {base}")
    print(kwargs)
    if base[-1] == os.sep:
        base = base[:-1]

    if 'subpath' in kwargs:
        subpath = kwargs['subpath']
        baselen = len(base)
        subpath = subpath[baselen:]
        dbpath = base
        dirsql = '''(path=? OR path LIKE ?) AND '''
        dirparam = (subpath, subpath + os.sep + "%")
        print(f"subpath: {subpath}   base: {base}  dbpath: {dbpath}")
    else:
        dbpath = base
        subpath = None
        dirsql = ''
        dirparam = None

    dbbase = os.path.realpath(dbpath)
    db_rel = '.yacreaderlibrary/library.ydb'
    db_path = os.path.join(dbbase, db_rel)
    print(f"DB path: {db_path}")

    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        sql = '''SELECT id, parentid, path FROM folder WHERE %snumChildren > 0 AND path is not null;''' % dirsql
        print(f"Using SQL: {sql}")
        print(f"Using args: {dirparam}")
        dirs = []
        dpid = {}
        for row in cur.execute(sql, dirparam).fetchall():
            id, pid, path = row
            path = path.lstrip(os.sep)
            dirs.append((id, pid, path))
            if not  pid in dpid:
                dpid = [path]
            else:
                dpid.append(path)

        for id, pid, path in dirs:
            dirpath = os.path.join(base, path)
            sql = '''SELECT c.filename FROM comic c INNER JOIN comic_info i ON (c.comicinfoid=i.id) WHERE (c.parentid=?) AND (i.title is null AND i.number is null AND i.volume is null AND i.writer is null AND i.penciller is null AND i.colorist is null AND i.letterer is null AND i.coverartist is null AND i.date is null AND i.publisher is null);'''
            dirnames = dpid[id] if id in dpid else []
            filenames = [ os.path.basename(row[0]) for row in cur.execute(sql, (id, )) ]
            yield (dirpath, dirnames, filenames)
    cur.close()

def update_library(updates):
    updmap = [ ('Colorist', 'colorist'), ('CoverArtist', 'coverArtist'), ('Writer', 'writer'), ('Penciller', 'penciller'), ('Letterer', 'letterer'), ('Inker', 'inker'), ('Summary', 'synopsis'), ('Notes', 'notes') ]
    upds = []
    vals = []

    for k1n, k2n in updmap:
        if k1n in updates:
            upds.append(f'{k2n}=?')
            vals.append(updates[k1n])

if __name__ == '__main__':
    comic_dir = '/Volumes/6TB/Comics'
    gen = yaclist(comic_dir, subpath='/Volumes/6TB/Comics/NewUploads')
    for fp in gen:
        print(fp)
