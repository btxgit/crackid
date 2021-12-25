```
                                       oooo         o8o        .o8
                                       `888         `"'       "888
 .ooooo.  oooo d8b  .oooo.    .ooooo.   888  oooo  oooo   .oooo888
d88' `"Y8 `888""8P `P  )88b  d88' `"Y8  888 .8P'   `888  d88' `888
888        888      .oP"888  888        888888.     888  888   888
888   .o8  888     d8(  888  888   .o8  888 `88b.   888  888   888
`Y8bod8P' d888b    `Y888""8o `Y8bod8P' o888o o888o o888o `Y8bod88P"

```
crackid - ComicRack ID Library and Utility

# Introduction #

crackid is a Python3 class library designed to work with comic book .cbr and .cbz files that have ComicInfo.xml files, as produced by by the software ComicRack.  These xml files contain various pieces of metadata about the cbr/cbz file.  It is a widely held belief that these files should only be added by the creator of the content.  This class will allow you to read the files, but it will not allow writing to them.

# Requirements #

* Python 3.6+
* Python dependencies
  * colorama==0.4.4
  * rarfile>=3.1
  * docopt>=0.6.2

# Installation #
```
python setup.py install
```

# Usage #
```
* crackid /path/to/comicfile.cbz
* crackid /path/to.directory/containing/books
* crackid -u -y /path/to/YACLibraryRoot
* crackid /both/directories /and/individual/books.cbz

The crackid program currently only supports console ANSI output

# YACReaderLibrary Integration
```
* It's experimental, so backup your YACROOM/.yacreaderlibrary/library.ydb file!
* Purpose is to pull metadata from the ComicInfo files this program harvests, and update the YACReader database.
* To use, first update your local comic library in the YACReaderLibrary, then EXIT, then run this.
* It currently works by querying the YACReader database and returning a list of all the books that have no metadata aside from issue #.
* If you specify the -u flag, it will update the record - otherwise it just uses the database for the files to process.

# crackid in use #
![In Action](https://github.com/btxgit/crackid/blob/master/crackid3.gif?raw=true)
