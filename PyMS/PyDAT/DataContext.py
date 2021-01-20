
from ..Utilities.utils import BASE_DIR
from ..Utilities.Settings import Settings

import os, re

class DataContext(object):
    def __init__(self):
        self.settings = Settings('PyDAT', '1')
        self.palettes = {}
        self.grp_cache = {}
        self.icon_cache = {}
        self.hints = {}
        with open(os.path.join(BASE_DIR,'PyMS','Data','Hints.txt'),'r') as hints:
            for l in hints:
                m = re.match('(\\S+)=(.+)\n?', l)
                if m:
                    self.hints[m.group(1)] = m.group(2)
