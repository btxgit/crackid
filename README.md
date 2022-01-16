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

crackid is a Python3 class library designed to work with comic book .cbr and
.cbz files that have ComicInfo.xml files, as produced by by the software
ComicRack.  These xml files contain various pieces of metadata about the
cbr/cbz file.  It is a widely held belief that these files should only be
added by the creator of the content.  This class will allow you to read the
files, but it will not allow writing to them.

It will, however, allow you to update the libraries of YACReader.
Hopefully, that makes what should be a fantastic tool a bit more usable.

There is also a new feature - it will display the cover in the terminal
right next the metadata.  And good news to all of you who wanted this to be
usable on Linux - now there is support for kitty
(https://sw.kovidgoyal.net/kitty/) and WezTerm
(https://wezfurlong.org/wezterm/).  Both seem to be exceptionally good
termainls that are pushing terminal emulation ahead.

This verison of crackid also supports Sixels, which are the legacy way to
support raster graphics in a terminal window.  iTerm2 and WezTerm both
support Sixels, as does XTerm - but you need to enable support for sixels at
buildtime.  YMMV, please give it a shot if you're having trouble with cover
view.

If you don't care about the cover view fewtaure, pretty much any terminal will do.

# Who is this For #

* Do you have a seed box that you SSH into, and grab comics?  This is pretty
  amazing for that scenario.
* Are you looking for a tool to kick start your YACReaderLibrary?  This
  program can help with that.
* Are you looking for a way to dump a copy of all the ComicInfo.xml files in
  a database?  This does that, although calling it "in a database" is
  pushing it a bit.  Yes, it uses a database, but it converts the .XML file
  into a JSON object, dumps it to a string, then writes it to the database
  just like that - which can be useful if you plan to put the data in Mongo,
  for example.  You have options.

# Requirements #

* Python 3.6+
* Python dependencies
  * blessed>=1.19.0
  * rarfile>=3.1
  * docopt>=0.6.2

# Good to Haves... #

* iTerm2 on MacOS, or kitty or WezTerm on Linux / MacOS

# Installation #
```
python setup.py install
```

# Usage #
* crackid /path/to/comicfile.cbz
* crackid /path/to.directory/containing/books
* crackid -u -y /path/to/YACLibraryRoot
* crackid -c /path/to/your/comics
* crackid /both/directories /and/individual/books.cbz
* crackid -c --sixel /path/to/comics

```
The crackid program is designed to support multiple output metods.  For now,
we're sticking to the Console / Terminal emulation.
```

# Issues #

* Currently, I haven't come up with a good way of determining the height and
  width of terminal windows - without the decorations / non-typeable
  sections.  I allow somoene to specify this geometry with the -g flag.

* There aren't too many Terminal programs that supprot all of the special
  features of the terminals - 24-bit color and bitmap graphics in the
  Termianl (as in, when you're SSH'd into a server, you can view the cover
  and 24-bit color as long as you're using one of the supported Terminal
  programs (iTerm, KiTTY, WezTerm support both).

# YACReaderLibrary Integration
* It's experimental, so backup your YACROOT/.yacreaderlibrary/library.ydb
  file!
* Purpose is to pull metadata from the ComicInfo files this program
  harvests, and update the YACReader database.
* To use, first update your local comic library in the YACReaderLibrary,
  then EXIT, then run this.
* It currently works by querying the YACReader database and returning a list
  of all the books that have no metadata aside from issue #.
* If you specify the -u flag, it will update the record - otherwise it just
  uses the database for the files to process.

# crackid in use #
![In Action](https://github.com/btxgit/crackid/blob/master/crackid3.gif?raw=true)

# New cover view feature
![Shiny](https://github.com/btxgit/crackid/blob/master/crackid4.gif?raw=true)
