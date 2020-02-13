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
                       'cvid': (r'\[CVDB(\d+)\]', 'https://comicvine.gamespot.com/ext/4000-{}/', 'ComicVine Book ID'),
                       'isbn': (r'\[ISBN(\d13)\]', 'https://www.amazon.com/gp/search/ref=sr_adv_b/?search-alias=stripbooks&unfiltered=1&field-keywords=&field-author=&field-title=&field-isbn={}&field-publisher=&node=&field-p_n_condition-type=&p_n_feature_browse-bin=&field-age_range=&field-language=&field-dateop=&field-datemod=&field-dateyear=&sort=relevanceexprank&Adv-Srch-Books-Submit.x=42&Adv-Srch-Books-Submit.y=6', 'International Standard Book Number'),
                       'dmdnum': (r'\[DMDDB([A-Z]{3}\d+)\]', 'https://www.previewsworld.com/Catalog/{}', 'Diamond Number'),
                       'asin': (r'\[ASIN([A-Z0-9]{10})\]', 'https://www.amazon.com/dp/{}', 'Amazon Standard Identification Number')
                       }

    def parse_xml_str(self, xmlstr):
        self.doc = {}

        # Fix up broken ComicInfo files
        if b'& ' in xmlstr:
            xmlstr = xmlstr.replace(b'& ', b'&amp; ')

        # Parse XML
        self.root = ET.fromstring(xmlstr)

        # Pull in every tag- they vary too much to whitelist
        for cinf in self.root.findall('.'):
            for cinfch in cinf.iter():
                if cinfch.text is None:
                    continue
#                cinval = cinfch.text.replace('\n', '  ')
                cinval = re.sub(r'\s\s+', '  ', cinfch.text)
                txt = cinval if cinval != '' else None
                tag = cinfch.tag
                self.doc[tag] = txt
        urls = set()
        if 'Web' in self.doc:
            urls.add(self.doc['Web'])
            weburl = urlparse(self.doc['Web'])
        else:
            weburl = None

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


