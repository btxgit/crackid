''' Functions for working with YACreader
'''

import sys
import os
import sqlite3
import re

def yaclist(base, **kwargs):
    ''' A drop-in replacement for os.walk that will iterate over each file
        in your YACreader Library.

        Note: The kwargs are only evaluated for yaclist-specific parameters.
    '''

#    print(f"Top: {base}")
#    print(kwargs)
    base = base.rstrip(os.sep)
    verbose = False

    if 'verbose' in kwargs:
        verbose = kwargs['verbose']

    if 'subpath' in kwargs:
        subpath = kwargs['subpath']
        baselen = len(base)
        subpath = subpath[baselen:].rstrip(os.sep)
        dbpath = base
        dirsql = '''(path=? OR path LIKE ?) AND '''
        dirparam = (subpath, subpath + os.sep + "%")
#        print(f"subpath: {subpath}   base: {base}  dbpath: {dbpath}")
    else:
        dbpath = base
        subpath = None
        dirsql = ''
        dirparam = None

    dbbase = os.path.realpath(dbpath)
    db_rel = '.yacreaderlibrary/library.ydb'
    db_path = os.path.join(dbbase, db_rel)
#    print(f"DB path: {db_path}")

    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        sql = '''SELECT id, parentid, path FROM folder WHERE %snumChildren > 0 AND path is not null;''' % dirsql

        if verbose:
            print(f"Using SQL: {sql}")
            print(f"Using args: {dirparam}")
        dirs = []
        dpid = {}
        for row in cur.execute(sql, dirparam).fetchall():
            id, pid, path = row
#            path = path.lstrip(os.sep)
            dirs.append((id, pid, path))
            if not  pid in dpid:
                dpid = [path]
            else:
                dpid.append(path)

        for id, pid, path in dirs:
            dirpath = os.path.join(base, path.lstrip(os.sep))
            sql = '''SELECT c.filename, i.id FROM comic c INNER JOIN comic_info i ON (c.comicinfoid=i.id) WHERE (c.parentid=?) AND (i.title is null AND i.volume is null AND i.writer is null AND i.penciller is null AND i.colorist is null AND i.letterer is null AND i.coverartist is null AND i.date is null AND i.publisher is null);'''
            dirnames = dpid[id] if id in dpid else []
            filenames = [ (os.path.basename(row[0]), row[1]) for row in cur.execute(sql, (id, )) ]

            if verbose:
                print(f"Yielding {dirpath}, {dirnames}, {filenames}")

            yield (dirpath, dirnames, filenames)
    cur.close()

def update_library(db_path, id, updates):
    updmap = [ ('Colorist', 'colorist'), ('CoverArtist', 'coverArtist'), ('Writer', 'writer'), ('Penciller', 'penciller'), ('Letterer', 'letterer'), ('Inker', 'inker'), ('Summary', 'synopsis'), ('Notes', 'notes'),  ('Publisher', 'publisher'), ('Number', 'number'), ('Series', 'Volume') ]
    upds = []
    vals = []

    for k1n, k2n in updmap:
        if k1n in updates and updates[k1n] is not None:
            if k1n == 'Number':
                if isinstance(updates[k1n], str):
                    if ' ' in updates[k1n]:
                        if 'filename' not in updates:
                            print("Error: Missing filename attribute in updates.")
                            sys.exit(1)

                        pat = re.search(r'(.+) (\d+) \(?of (\d+)\)?', updates['filename'])
                        if pat is not None:
                            base, num, count = pat.groups()
                            if num.isdigit():
                                num = int(num, 10)
                                upds.append('Number=?')
                                vals.append(num)
                            if count.isdigit():
                                count = int(count, 10)
                                upds.append('Count=?')
                                vals.append(count)
                            continue
                        else:
                            vl = updates[k1n].split(' ', 1)
                            updates[k1n] = vl[0]
                            if updates[k1n].isdigit():
                                updates[k1n] = int(updates[k1n], 10)
            upds.append(f'{k2n}=?')
            vals.append(updates[k1n])

    if len(upds) == 0:
        return

    updstr = ', '.join(upds)
    sql = f'UPDATE comic_info SET {updstr} WHERE id=?;'
    vals.append(id)
#    print(f"Executing sql: {sql} with vals: {vals}")
    with sqlite3.connect(db_path, isolation_level='DEFERRED') as con:
        con.execute(sql, vals)
        con.commit()

if __name__ == '__main__':
    comic_dir = '/path/to/Comics'
    gen = yaclist(comic_dir, subpath='/pat/to/Comics/2021-01-14/')
    for fp in gen:
        print(fp)
