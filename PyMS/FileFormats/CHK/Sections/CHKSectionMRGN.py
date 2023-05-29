
from .CHKSectionSTR import CHKSectionSTR
from .CHKSectionVER import CHKSectionVER

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ...TBL import decompile_string

from ....Utilities.utils import pad, named_flags

import struct

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKLocation(object):
	NO_ELEVATION = 0
	LOW_GROUND = (1 << 0)
	MEDIUM_GROUND = (1 << 1)
	HIGH_GROUND = (1 << 2)
	ALL_GROUND = (LOW_GROUND | MEDIUM_GROUND | HIGH_GROUND)
	LOW_AIR = (1 << 3)
	MEDIUM_AIR = (1 << 4)
	HIGH_AIR = (1 << 5)
	ALL_AIR = (LOW_AIR | MEDIUM_AIR | HIGH_AIR)
	ALL_ELEVATIONS = (ALL_GROUND | ALL_AIR)

	def __init__(self, chk): # type: (CHK) -> None
		self.chk = chk
		self.clear()

	def load_data(self, data): # type: (bytes) -> None
		startX,startY,endX,endY,self.name,self.elevation = tuple(int(v) for v in struct.unpack('<4L2H', data[:20]))
		self.start = [startX,startY]
		self.end = [endX,endY]

	def save_data(self): # type: () -> bytes
		return struct.pack('<4L2H', self.start[0],self.start[1],self.end[0],self.end[1],self.name,self.elevation)

	def decompile(self): # type: () -> str
		result = '\t#\n'
		string = ''
		strings = cast(CHKSectionSTR, self.chk.get_section(CHKSectionSTR.NAME))
		if strings and self.name > -1 and self.name < len(strings.strings):
			string = ' # ' + decompile_string(strings.strings[self.name].text)
		data = {
			'Start': pad('%s,%s' % (self.start[0],self.start[1])),
			'End': pad('%s,%s' % (self.end[0],self.end[1])),
			'Name': '%s%s' % (self.name, string),
			'Elevation': named_flags(self.elevation, ["Low Ground", "Med. Ground", "High Ground", "Low Air", "Med. Air", "High Air"], 16),
		}
		for key in ['Start','End','Name','Elevation']:
			value = data[key]
			if isinstance(value, tuple):
				result += '\t%s%s\n' % (pad('#'), value[0])
				value = value[1]
			result += '\t%s\n' % pad(key, value)
		return result

	def in_use(self): # type: () -> bool
		return self.name > 0 or self.start[0] != 0 or self.start[1] != 0 or self.end[0] != 0 or self.end[1] != 0 # or self.elevation != 0

	def normalized_coords(self): # type: () -> tuple[int, int, int, int]
		return (min(self.start[0],self.end[0]), min(self.start[1],self.end[1]), max(self.start[0],self.end[0]), max(self.start[1],self.end[1]))

	def clear(self): # type: () -> None
		self.start = [0,0]
		self.end = [0,0]
		self.name = 0
		self.elevation = CHKLocation.NO_ELEVATION

class CHKSectionMRGN(CHKSection):
	NAME = 'MRGN'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	def __init__(self, chk): # type: (CHK) -> None
		CHKSection.__init__(self, chk)
		self.locations = [] # type: list[CHKLocation]
	
	def load_data(self, data): # type: (bytes) -> None
		self.locations = []
		o = 0
		while o+20 <= len(data):
			location = CHKLocation(self.chk)
			location.load_data(data[o:o+20])
			self.locations.append(location)
			o += 20

	def requires_post_processing(self): # type: () -> bool
		return True

	def process_data(self): # type: () -> None
		ver = cast(CHKSectionVER, self.chk.get_section(CHKSectionVER.NAME))
		count = 255 if ver.version >= CHKSectionVER.SC104 else 64
		while len(self.locations) < count:
			self.locations.append(CHKLocation(self.chk))

	def save_data(self): # type: () -> bytes
		result = b''
		for location in self.locations:
			result += location.save_data()
		return result

	def decompile(self): # type: () -> str
		result = '%s:\n' % (self.NAME)
		for location in self.locations:
			result += location.decompile()
		return result
