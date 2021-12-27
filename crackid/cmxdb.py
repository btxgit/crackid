'''                __     _    __
 ___________ _____/ /__  (_)__/ /
/ __/ __/ _ `/ __/  '_/ / / _  /
\__/_/  \_,_/\__/_/\_\ /_/\_,_/
comic rack id class prototype btx
'''

import os
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

class cmxdb(object):
    ''' Parses a comicinfo.xml file, finds the IDs, generates the related
        URLs
    '''

    def __init__(self):
        self.tree = self.root = None
        self.doc = {}
        self.idfind = {'cmxid': (r'\[CMXDB(\d+)\]', 'https://www.comixology.com/ext/digital-comic/{}', 'Comixology Book ID'),
                       'odid': (r'\[ODDB(\d+)\]', 'https://overdrive.com/media/{}', 'Overdrive Book ID'),
                       'cvid': (r'\[CVDB(\d+)\]', 'https://comicvine.gamespot.com/ext/4000-{}/', 'ComicVine Book ID'),
                       'issue id': (r'\[Issue ID (\d+)\]', 'https://comicvine.gamespot.com/ext/4000-{}/', 'ComicTagger and Mylar CVID variant'),
                       'isbn': (r'\[ISBN(\d{13})\]', 'https://www.amazon.com/gp/search/ref=sr_adv_b/?search-alias=stripbooks&unfiltered=1&field-keywords=&field-author=&field-title=&field-isbn={}', 'International Standard Book Number'),
                       'gcd': (r'\[GCD(\d+)\]', 'https://www.comics.org/issue/{}/', 'Grand Comics Database'),
                       'dmdnum': (r'\[DMDDB([A-Z]{3}\d+)\]', 'https://www.previewsworld.com/Catalog/{}', 'Diamond Number'),
                       'asin': (r'\[ASIN([A-Z0-9]{10})\]', 'https://www.amazon.com/dp/{}', 'Amazon Standard Identification Number')
                       }

    def parse_xml_str(self, xmlstr1):
        ''' parses <xmlstr> into json doc self.doc, where it can
            be processed and shipped off to market
        '''

        self.doc = {}

        try:
            xmlstr1 = xmlstr1.decode('utf-8')
        except Exception as e:
            print("[Error] Caught exception while trying to decdode XML:", e)
            return

        # Fix up broken ComicInfo files - for some reason, the ampersand
        # isn't escaped sometimes.  ALso remove illegal XML characters.
        if '& ' in xmlstr1:
            xmlstr1 = xmlstr.replace('& ', '&amp; ')

        xmlstr = ''

        for cs in xmlstr1:
            c = ord(cs)
            if (c == 0x9) or (c == 0xA) or (c == 0xD) or ((c >= 0x20) and (c <= 0xD7FF)) or ((c >= 0xE000) and (c <= 0xFFFD)) or ((c >= 0x10000) and (c <= 0x10FFFF)):
                xmlstr += cs
            else:
                print("[Error] Stripping illegalUnicode codepoint for XML (%04x)" % c)

        # Parse XML

        try:
            self.root = ET.fromstring(xmlstr)
        except Exception as e:
            print("XML Parse Error:", e)
            return

        # Pull in every tag- they vary too much to whitelist
        for cinf in self.root.findall('.'):
            for cinfch in cinf.iter():
                if cinfch.text is None:
                    continue
                cinval = re.sub(r'\s\s+', '  ', cinfch.text)
                txt = cinval if cinval != '' else None
                tag = cinfch.tag
                self.doc[tag] = txt

        # Gather the URLs, both the supplied and derived
        urls = set()
        if 'Web' in self.doc:
            urls.add(self.doc['Web'])
            weburl = urlparse(self.doc['Web'])
        else:
            weburl = None

        # Generate the derived URLs
        if 'Notes' in self.doc and self.doc['Notes'] is not None:
            for k in self.idfind.keys():
                rexp = self.idfind[k][0]
                fmt = self.idfind[k][1]
                pat = re.search(rexp, self.doc['Notes'], re.I)
                if pat is not None:
                    self.doc[k] = pat.group(1)
                    url = fmt.format(self.doc[k])
                    if url != '':
                        newurl =  urlparse(url)
                        if (weburl is None) or (weburl.netloc != newurl.netloc) or (os.path.basename(weburl.path) != os.path.basename(newurl.path)):
                            urls.add(url)
        if len(urls) > 0:
            self.doc['urls'] = list(urls)

        for k in sorted(self.doc.keys()):
            val = self.doc[k]
            if val is None:
                continue
            if k.lower() == 'comicinfo':
                continue
            if isinstance(val, list):
                val = '\n'.join(val)
            self.doc[k] = val.strip()




