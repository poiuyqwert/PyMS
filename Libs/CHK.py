from utils import *
from fileutils import *
import TRG, TBL, AIBIN

import struct, math

PADDING = 20

def pad(label, value='', span=PADDING):
	label = str(label)
	return '%s%s%s' % (label, ' ' * (span - len(label)), value)

def named_flags(flags, names, count, skip=0):
	header = ''
	values = ''
	for n in range(count):
		f = flags & (1 << n)
		name = 'Unknown%d' % n
		if n >= skip and n-skip < len(names) and names[n-skip]:
			name = names[n-skip]
		header += pad(name)
		values += pad(1 if f else 0)
	return (header,values)

def binary(flags, count):
	result = ''
	for n in range(count):
		result = ('1' if flags & (1 << n) else '0') + result
	return result

class CHKSection:
	def __init__(self, chk):
		self.chk = chk

	def load_data(self, data):
		pass

	def save_data(self):
		pass

	def decompile(self):
		pass

	def interpret(self):
		pass

class CHKSectionUnknown(CHKSection):
	def __init__(self, chk, name):
		CHKSection.__init__(self, chk)
		self.name = name
		self.data = None

	def load_data(self, data):
		self.data = data

	def save_data(self):
		return self.data

	def decompile(self):
		return '%s: # Unknown\n\t%s\n' % (self.name, pad('Data',self.data.encode('hex')))

class CHKSectionVER(CHKSection):
	NAME = "VER "

	BETA = 57
	SC100 = 59
	SC104 = 63
	BW = 205
	@staticmethod
	def VER_NAME(v):
		names = {
			CHKSectionVER.BETA:'Beta',
			CHKSectionVER.SC100:'StarCraft 1.00',
			CHKSectionVER.SC104:'StarCraft 1.04+',
			CHKSectionVER.BW:'BroodWar'
		}
		return names.get(v,'Unknown')

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.version = CHKSectionVER.BW
		typeSect = chk.sections.get(CHKSectionTYPE.NAME)
		if typeSect and not typeSect.type == CHKSectionTYPE.BROODWAR:
			self.version = CHKSectionVER.SC104

	def load_data(self, data):
		self.version = struct.unpack('<H', data[:2])[0]

	def save_data(self):
		return struct.pack('<H', self.version)

	def decompile(self):
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Version',self.version), CHKSectionVER.VER_NAME(self.version))

class CHKRequirements:
	VER_NONE = 0
	VER_VANILLA = (1 << 0)
	VER_HYBRID = (1 << 1)
	VER_BROODWAR = (1 << 2)
	VER_VANILLA_HYBRID = VER_VANILLA | VER_HYBRID
	VER_BROODWAR_HYBRID = VER_BROODWAR | VER_HYBRID
	VER_ALL = VER_VANILLA | VER_HYBRID | VER_BROODWAR

	MODE_NONE = 0
	MODE_MELEE = (1 << 0)
	MODE_UMS = (1 << 1)
	MODE_ALL = MODE_MELEE | MODE_UMS

	def __init__(self, vers=VER_ALL, modes=MODE_ALL):
		self.vers = []
		if vers & CHKRequirements.VER_VANILLA:
			self.vers.append(CHKSectionVER.SC100)
		if vers & CHKRequirements.VER_HYBRID:
			self.vers.append(CHKSectionVER.SC104)
		if vers & CHKRequirements.VER_BROODWAR:
			self.vers.append(CHKSectionVER.BW)

		self.modes = modes

	def is_required(self, chk, game_mode=MODE_ALL):
		verSect = chk.get_section(CHKSectionVER.NAME)
		if verSect.version in self.vers and game_mode & self.modes:
			return True
		return False

class CHKSectionTYPE(CHKSection):
	NAME = "TYPE"
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)

	STARCRAFT = "RAWS"
	BROODWAR = "RAWB"
	@staticmethod
	def TYPE_NAME(t):
		names = {
			CHKSectionTYPE.STARCRAFT:'StarCraft',
			CHKSectionTYPE.BROODWAR:'BroodWar'
		}
		return names.get(t,'Unknown')

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.type = CHKSectionTYPE.BROODWAR
		verSect = chk.sections.get(CHKSectionVER.NAME)
		if verSect and not verSect.type == CHKSectionVER.BW:
			self.type = CHKSectionTYPE.STARCRAFT

	def load_data(self, data):
		self.type = data[:4]

	def save_data(self):
		return self.type

	def decompile(self):
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Type',self.type), CHKSectionTYPE.TYPE_NAME(self.type))

class CHKSectionIVER(CHKSection):
	NAME = 'IVER'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)

	BETA = 9
	RELEASE = 10
	@staticmethod
	def VER_NAME(v):
		names = {
			CHKSectionIVER.BETA:'Beta',
			CHKSectionIVER.RELEASE:'Release'
		}
		return names.get(v,'Unknown')

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.version = CHKSectionIVER.RELEASE
		verSect = chk.sections.get(CHKSectionVER.NAME)
		if verSect and verSect.version == CHKSectionVER.BETA:
			self.version = CHKSectionIVER.BETA
	
	def load_data(self, data):
		self.version = struct.unpack('<H', data[:2])[0]
	
	def save_data(self):
		return struct.pack('<H', self.version)

	def decompile(self):
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Version',self.version), CHKSectionIVER.VER_NAME(self.version))

class CHKSectionIVE2(CHKSection):
	NAME = 'IVE2'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)

	RELEASE = 11
	@staticmethod
	def VER_NAME(v):
		names = {
			CHKSectionIVE2.RELEASE:'Release'
		}
		return names.get(v,'Unknown')

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.version = CHKSectionIVE2.RELEASE
	
	def load_data(self, data):
		self.version = struct.unpack('<H', data[:2])[0]
	
	def save_data(self):
		return struct.pack('<H', self.version)

	def decompile(self):
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Version',self.version), CHKSectionIVE2.VER_NAME(self.version))

class CHKSectionVCOD(CHKSection):
	NAME = 'VCOD'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)

	DEFAULT_CODE = '4\x19\xcaw\x99\xdchq\n`\xbf\xc3\xa7\xe7u\xa7\x1f)}\xa6\xd7\xb0:\xbb\xcc1$\xed\x17L\x13\x0be \xa2\xb7\x91\xbd\x18k\x8d\xc3]\xdd\xe2z\xd57\xf6Yd\xd4c\x9a\x12\x0fC\\.F\xe3t\xf8*\x08j7\x067\xf6\xd6;\x0e\x94c\x16Eg\\\xec\xd7{\xf7\xb7\x1a\xfc\xd4\x9es\xfa?\x8c.\xc0\xe1\x0f\xd1t\t\x07\x95\xe3d\xd7u\x16ht\x99\xa7O\xda\xd5 \x18\x1f\xe7\xe6\xa0\xbe\xa6\xb6\xe3\x1f\xca\x0c\xefp1\xd5\x1a1M\xb8$5\xe3\xf8\xc7}\xe1\x1aX\xde\xf4\x05\'C\xba\xac\xdb\x07\xdci\xbe\n\xa8\x8f\xecI\xd7X\x16?\xe5\xdb\xc1\x8aA\xcf\xc0\x05\x9d\xca\x1cr\xa2\xb1_\xa5\xc4#p\x9b\x84\x04\xe1\x14\x80{\x90\xda\xfa\xdbi\x06\xa3\xf3\x0f@\xbe\xf3\xce\xd4\xe3\xc9\xcb\xd7Z@\x014\xf2h\x14\xf88\x8e\xc5\x1a\xfe\xd6=KS\x05\x05\xfa4\x10E\x8e\xdd\x91i\xfe\xaf\xe0\xee\xf0\xf3H~\xdd\x9f\xad\xdcubz\xac\xe51\x1bbg \xcd6M\xe0\x98!t\xfb\tyq6g\xcd\x7fw_\xd6<\xa2\xa2\xa6\xc6\x1a\xe3\xcejN\xcd\xa9l\x86\xba\x9d;\xb5\xf4v\xfd\xf8D\xf0\xbc.\xe9n)#%/k\x08\xab\'Dz\x12\xcc\x99\xed\xdc\xf2u\xc5<8~\xf7\x1c\x1b\xc5\xd1-\x94e\x06\xc9H\xdd\xbe2-\xac\xb5\xc92\x81fJ\xd845?\x15\xdf\xb2\xee\xeb\xb6\x04\xf6M\x965B\x94\x9cb\x8a\xd3aR\xa8{o\xdca\xfc\xf4l\x14-\xfe\x99\xea\xa4\n\xe8\xd9\xfe\x13\xd0HDY\x80f\xf3\xe34\xd9\x8d\x19\x16\xd7c\xfe0\x18~:\x9b\x8d\x0f\xb1\x12\xf0\xf5\x8c\nxX\xdb>c\xb8\x8c:\xaa\xf3\x8e7\x8a\x1a.\\1\xf9\xef\xe3m\xe3~\x9b\xbd>\x13\xc6D\xc0\xb9\xbc:\xda\x90\xa4\xad\xb0t\xf8W\'\x89G\xe6?7\xe4ByZ\xdfC\x8d\xee\xb4\nI\xe8<\xc3\x88\x1a\x88\x01kv\x8a\xc3\xfd\xa3\x16zNV\xa7\x7f\xcb\xba\x02^\x1c\xec\xb0\xb9\xc9v\x1e\x82\xb19>\xc9W\xc5\x19$8L]/T\xb8o]W\x8e0\xa1\nRm\x18q^\x13\x06\xc3Y\x1f\xdc>b\xdc\xda\xb5\xeb\x1b\x91\x95\xf9\xa7\x91\xd5\xda3S\xcek\xf5\x00p\x01\x7f\xd8\xee\xe8\xc0\n\xf1\xcec\xeb\xb6\xd3x\xef\xcc\xa5\xaa]\xbc\xa4\x96\xab\xf2\xd2a\xff\xea\x9a\xa8j\xed\xa2\xbd>\xeda9\xc1\x82\x92\x166#\xb1\xb0\xa0$\xe5\x05\x9b\xa7\xaa\r\x12\x9b3\x83\x92 \xda%\xb0\xec\xfc$\xd08#\xfc\x95\xf2t\x80s\xe5\x19\x97P}DE\x93D\xdb\xa2\xad\x1diD\x14\xee\xe7,\x7f\x87\xff8\x9e2\xf1M\xbc)\xdaB\'&\xfe\xc1\xd2+\xa9\xf6Bz\x0e\xcb\xe8|\xd1\x0f[\xecVi\xb7a1\xb4m\xf9%@4ym\xfaS\xa7\x0b\xfa\xa4\x82\xce\xc3EIa\rE,\x8f(I`\xf7\xf3}\xc9\x1e\x0f\xd0\x89\xc1&R\xf8\xd3M\x8f5\x14\xba\x9d_\x0b\x07\xa9J\x00\xf7\"&/>g\xfb\x1f\xa1\x9c\x11\xc6iO]fX4\x15\x90l\xe5TF\xaf_c\xd6\x8a\x0c\x95\xdf\xbd\r\xe4\xaf\xbf@@L\xa3\xf6Qq)\xed&\xf8\x85(\"\xd5\xbf\xbe\xcf\xfa(\xc5\x7fQ\xb8\x06c\x07\xec\xbd\x8f)\xfaU~q\x1a@2f\xe8\xd4\xde\x9d\xd4^\xfc\x93z=\xd5;\xcdu.\x80\nOt\x87\x1b\xcc\x8f\xea\x9a\xa9\xdb|\x16S\xe5\xef\xabx\xc1n\xa4r\x89Z\x98,pP\xfb\xa1\xdf\x1fk\xb7\xd9D\x07\x80\x82V\xfd\xbf\xc0\x83\x0eI\xd0[\x1ehj\x0e\x9a\xc2\x0b/\x8eC\xa0\xe1\x99\x0c\xf6\xb2\xe0z\x1c^,\xc8\xa0E<\x0b\xe9\x88\xac\xb9\x96\xc6t\xae\x83*\xbb\x13\xfae\xebO\x1f\xa6\xb0\x8a\x8a\xe1\x81\xe9\xb8\xb9\xd5U\x15NE\xf2\xad\x9b>\xc25~_\x92.r\xb6[h#n\xc6E\x0e\xe9;\x87\xd4\xf4A\xc0\xe3\xa8\x05D\xbe\xe4\x0f\x8a\x13\x1a\xc47\xf4Z@U\xef\x9dy\x1dKJy:\x9cv\x857\xcc\x82=\x0f\xb6`\xa6\x93~\xbd\\\xc2\xc4r\xc7\x7f\x90M\x1b\x96\x10\x13\x05hh5\xc0{\xffF\x85C*'
	DEFAULT_OPCODES = (1, 4, 5, 6, 2, 1, 5, 2, 0, 3, 7, 7, 5, 4, 6, 3)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.code = CHKSectionVCOD.DEFAULT_CODE
		self.opcodes = CHKSectionVCOD.DEFAULT_OPCODES
	
	def load_data(self, data):
		self.code = data[:1024]
		self.opcodes = list(struct.unpack('<16B',data[1024:1024+16]))
	
	def save_data(self):
		return self.code + struct.pack('<16B',*self.opcodes)

	def decompile(self):
		result = '%s:\n\t%s\n' % (self.NAME, pad('Code',self.code.encode('hex')))
		for n,opcode in enumerate(self.opcodes):
			result += '\t%s\n' % (pad('Opcode%02d' % n, opcode))
		return result

class CHKSectionIOWN(CHKSection):
	NAME = 'IOWN'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)

	INACTIVE = 0
	COMPUTER_GAME_INVALID = 1 # INVALID
	OCCUPIED_HUMAN_INVALID = 2 # INVALID
	RESUE_PASSIVE = 3
	UNUSED = 4
	COMPUTER = 5
	HUMAN = 6
	NEUTRAL = 7
	CLOSED_INVALID = 8 # INVALID
	@staticmethod
	def OWNER_NAME(v):
		names = {
			CHKSectionIOWN.INACTIVE:'Inactive',
			CHKSectionIOWN.COMPUTER_GAME_INVALID:'Occupied by Computer (Invalid)',
			CHKSectionIOWN.OCCUPIED_HUMAN_INVALID:'Occupied by Human Player (Invalid)',
			CHKSectionIOWN.RESUE_PASSIVE: 'Rescue Passive',
			CHKSectionIOWN.UNUSED: 'Unused',
			CHKSectionIOWN.COMPUTER: 'Computer',
			CHKSectionIOWN.HUMAN: 'Human',
			CHKSectionIOWN.NEUTRAL: 'Neutral',
			CHKSectionIOWN.CLOSED_INVALID: 'Closed (Invalid)'
		}
		return names.get(v,'Unknown')
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.owners = [CHKSectionIOWN.HUMAN]*8 + [CHKSectionIOWN.INACTIVE]*4
	
	def load_data(self, data):
		self.owners = list(struct.unpack('<12B', data[:12]))
	
	def save_data(self):
		return struct.pack('<12B', *self.owners)

	def decompile(self):
		result = '%s:\n' % self.NAME
		for n,value in enumerate(self.owners):
			result += '\t%s # %s\n' % (pad('Slot%02d' % n,value), CHKSectionIOWN.OWNER_NAME(value))
		return result

class CHKSectionOWNR(CHKSection):
	NAME = 'OWNR'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)

	INACTIVE = 0
	COMPUTER_GAME_INVALID = 1 # INVALID
	OCCUPIED_HUMAN_INVALID = 2 # INVALID
	RESUE_PASSIVE = 3
	UNUSED = 4
	COMPUTER = 5
	HUMAN = 6
	NEUTRAL = 7
	CLOSED_INVALID = 8 # INVALID
	@staticmethod
	def OWNER_NAME(v):
		names = {
			CHKSectionOWNR.INACTIVE:'Inactive',
			CHKSectionOWNR.COMPUTER_GAME_INVALID:'Occupied by Computer (Invalid)',
			CHKSectionOWNR.OCCUPIED_HUMAN_INVALID:'Occupied by Human Player (Invalid)',
			CHKSectionOWNR.RESUE_PASSIVE: 'Rescue Passive',
			CHKSectionOWNR.UNUSED: 'Unused',
			CHKSectionOWNR.COMPUTER: 'Computer',
			CHKSectionOWNR.HUMAN: 'Human',
			CHKSectionOWNR.NEUTRAL: 'Neutral',
			CHKSectionOWNR.CLOSED_INVALID: 'Closed (Invalid)'
		}
		return names.get(v,'Unknown')
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.owners = [CHKSectionOWNR.HUMAN]*8 + [CHKSectionOWNR.INACTIVE]*3 + [CHKSectionOWNR.NEUTRAL]
	
	def load_data(self, data):
		self.owners = list(struct.unpack('<12B', data[:12]))
	
	def save_data(self):
		return struct.pack('<12B', *self.owners)

	def decompile(self):
		result = '%s:\n' % self.NAME
		for n,value in enumerate(self.owners):
			result += '\t%s # %s\n' % (pad('Slot%02d' % n,value), CHKSectionOWNR.OWNER_NAME(value))
		return result

class CHKSectionERA(CHKSection):
	NAME = 'ERA '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)

	BADLANDS = 0
	SPACE = 1
	INSTALLATION = 2
	ASHWORLD = 3
	JUNGLE = 4
	DESERT = 5
	ARCTIC = 6
	TWILIGHT = 7
	@staticmethod
	def TILESET_NAME(t):
		return ['Badlands','Space Platform','Installation','Ashworld','Jungle','Desert','Arctic','Twilight'][t % (CHKSectionERA.TWILIGHT+1)]

	@staticmethod
	def TILESET_FILE(t):
		return ['badlands','platform','install','ashworld','jungle','desert','ice','twilight'][t % (CHKSectionERA.TWILIGHT+1)]

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.tileset = CHKSectionERA.BADLANDS
	
	def load_data(self, data):
		self.tileset = struct.unpack('<H', data[:2])[0]
	
	def save_data(self):
		return struct.pack('<H', self.tileset)

	def decompile(self):
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Tileset',self.tileset), CHKSectionERA.TILESET_NAME(self.tileset))

class CHKSectionDIM(CHKSection):
	NAME = 'DIM '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)

	TINY = 64
	SMALL = 96
	MEDIUM = 128
	LARGE = 192
	HUGE = 256
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.width = CHKSectionDIM.MEDIUM
		self.height = CHKSectionDIM.MEDIUM
	
	def load_data(self, data):
		self.width,self.height = struct.unpack('<2H', data[:4])
	
	def save_data(self):
		return struct.pack('<2H', self.width, self.height)
	
	def decompile(self):
		return '%s:\n\t%s\n\t%s\n' % (self.NAME, pad('Width',self.width), pad('Height',self.height))

class CHKSectionSIDE(CHKSection):
	NAME = 'SIDE'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	ZERG = 0
	TERRAN = 1
	PROTOSS = 2
	UNUSED_INDEPENDENT = 3
	UNUSED_NEUTRAL = 4
	USER_SELECT = 5
	RANDOM = 6
	INACTIVE = 7
	@staticmethod
	def SIDE_NAME(v):
		names = {
			CHKSectionSIDE.ZERG:'Zerg',
			CHKSectionSIDE.TERRAN:'Terran',
			CHKSectionSIDE.PROTOSS:'Protoss',
			CHKSectionSIDE.UNUSED_INDEPENDENT: 'Unused (Independent)',
			CHKSectionSIDE.UNUSED_NEUTRAL: 'Unused (Neutral)',
			CHKSectionSIDE.USER_SELECT: 'User Select',
			CHKSectionSIDE.RANDOM: 'Random',
			CHKSectionSIDE.INACTIVE: 'Inactive'
		}
		return names.get(v,'Unknown')

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.sides = [CHKSectionSIDE.RANDOM] * 8 + [CHKSectionSIDE.INACTIVE] * 4
	
	def load_data(self, data):
		self.sides = list(struct.unpack('<12B', data[:12]))
	
	def save_data(self):
		return struct.pack('<12B', *self.sides)
	
	def decompile(self):
		result = '%s:\n' % self.NAME
		for n,value in enumerate(self.sides):
			result += '\t%s # %s\n' % (pad('Slot%02d' % n,value), CHKSectionSIDE.SIDE_NAME(value))
		return result

class CHKSectionMTXM(CHKSection):
	NAME = 'MTXM'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.raw_map = ''
		self.map = None
	
	def load_data(self, data):
		self.raw_map = data
	
	def process_data(self):
		if self.map != None:
			return
		self.map = []
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		diff = dims.width*dims.height - len(self.raw_map)
		if diff > 0:
			self.raw_map += '\0' * diff
		struct_format = '<%dH' % dims.width
		for y in range(dims.height):
			offset = y*dims.width*2
			values = struct.unpack(struct_format, self.raw_map[offset:offset+dims.width*2])
			self.map.append([[(v & 0xFFF0) >> 4,v & 0xF] for v in values])
	
	def save_data(self):
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		result = ''
		struct_format = '<%dH' % dims.width
		for r in self.map:
			values = [v[0] << 4 + v[1] for v in r]
			result += struct.pack(struct_format, *values)
		return result

	def decompile(self):
		result = '%s:\n' % self.NAME
		for row in self.map:
			for t in row:
				result += pad(t,span=6)
			result += '\n'
		return result

class CHKUnitAvailability:
	def __init__(self):
		self.available = True
		self.default = True

class CHKSectionPUNI(CHKSection):
	NAME = 'PUNI'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.availability = []
		for u in range(228):
			self.availability.append([])
			for p in range(12):
				self.availability[-1].append(CHKUnitAvailability())
		self.globalAvailability = [True] * 228
	
	def load_data(self, data):
		offset = 0
		for p in range(12):
			availability = list(struct.unpack('<228B', data[offset:offset+228]))
			offset += 228
			for u in range(228):
				self.availability[u][p].available = availability[u]
		self.globalAvailability = list(struct.unpack('<228B', data[offset:offset+228]))
		offset += 228
		for p in range(12):
			defaults = list(struct.unpack('<228B', data[offset:offset+228]))
			offset += 228
			for u in range(228):
				self.availability[u][p].default = defaults[u]
	
	def save_data(self):
		result = ''
		for p in range(12):
			availability = [self.availability[u][p].available for u in range(228)]
			result += struct.pack('<228B', *availability)
		result += struct.pack('<228B', *self.globalAvailability)
		for p in range(12):
			defaults = [self.availability[u][p].default for u in range(228)]
			result += struct.pack('<228B', *defaults)
		return result

	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Available','Use Defaults']:
			result += pad(name)
		result += '\n'
		for p in range(12):
			result += '\t# Player %d\n' % (p+1)
			for u in range(228):
				result += '\t' + pad('Unit%03d' % u)
				result += pad(self.availability[u][p].available)
				result += '%s\n' % self.availability[u][p].default
		result += '\t%s\n' % pad('# Global','Available')
		for u in range(228):
			result += '\t%s\n' % pad('Unit%03d' % u, self.globalAvailability[u])
		return result

class CHKUpgradeLevels:
	def __init__(self):
		self.maxLevel = 3
		self.startLevel = 0
		self.default = True

class CHKSectionUPGR(CHKSection):
	NAME = 'UPGR'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	UPGRADES = 46
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.levels = []
		for u in range(self.UPGRADES):
			self.levels.append([])
			for p in range(12):
				self.levels[-1].append(CHKUpgradeLevels())
		self.maxLevels = []
		self.startLevels = []
	
	def load_data(self, data):
		o = 0
		for p in range(12):
			maxLevels = list(struct.unpack('<%dB' % self.UPGRADES, data[o:o+self.UPGRADES]))
			o += self.UPGRADES
			startLevels = list(struct.unpack('<%dB' % self.UPGRADES, data[o:o+self.UPGRADES]))
			o += self.UPGRADES
			for u in range(self.UPGRADES):
				self.levels[u][p].maxLevel = maxLevels[u]
				self.levels[u][p].startLevel = startLevels[u]
		self.maxLevels = list(struct.unpack('<%dB' % self.UPGRADES, data[o:o+self.UPGRADES]))
		o += self.UPGRADES
		self.startLevels = list(struct.unpack('<%dB' % self.UPGRADES, data[o:o+self.UPGRADES]))
		o += self.UPGRADES
		for p in range(12):
			defaults = list(struct.unpack('<%dB' % self.UPGRADES, data[o:o+self.UPGRADES]))
			o += self.UPGRADES
			for u in range(self.UPGRADES):
				self.levels[u][p].default = defaults[u]

	def save_data(self):
		result = ''
		for p in range(12):
			maxLevels = [self.levels[u][p].maxLevel for u in range(self.UPGRADES)]
			startLevels = [self.levels[u][p].startLevel for u in range(self.UPGRADES)]
			result += struct.pack('<%dB' % self.UPGRADES, *maxLevels)
			result += struct.pack('<%dB' % self.UPGRADES, *startLevels)
		result += struct.pack('<%dB' % self.UPGRADES, *self.maxLevels)
		result += struct.pack('<%dB' % self.UPGRADES, *self.startLevels)
		for p in range(12):
			defaults = [self.levels[u][p].default for u in range(self.UPGRADES)]
			result += struct.pack('<%dB' % self.UPGRADES, *defaults)
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Max Levels','Start Level','Use Defaults']:
			result += pad(name)
		result += '\n'
		for p in range(12):
			result += '\t# Player %d\n' % (p+1)
			for u in range(self.UPGRADES):
				result += '\t' + pad('Upgrade%02d' % u)
				result += pad(self.levels[u][p].maxLevel)
				result += pad(self.levels[u][p].startLevel)
				result += '%s\n' % self.levels[u][p].default
		result += '\t' + pad('# Global')
		for name in ['Max Levels','Start Level']:
			result += pad(name)
		result += '\n'
		for u in range(self.UPGRADES):
			result += '\t' + pad('Upgrade%02d' % u)
			result += pad(self.maxLevels[u])
			result += '%s\n' % self.startLevels[u]
		return result

class CHKTechAvailability:
	def __init__(self):
		self.available = 3
		self.researched = 0
		self.default = True

class CHKSectionPTEC(CHKSection):
	NAME = 'PTEC'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	TECHS = 24
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.availability = []
		for u in range(self.TECHS):
			self.availability.append([])
			for p in range(12):
				self.availability[-1].append(CHKTechAvailability())
		self.globalAvailability = []
		self.globallyResearched = []
	
	def load_data(self, data):
		o = 0
		for p in range(12):
			availability = list(struct.unpack('<%dB' % self.TECHS, data[o:o+self.TECHS]))
			o += self.TECHS
			researched = list(struct.unpack('<%dB' % self.TECHS, data[o:o+self.TECHS]))
			o += self.TECHS
			for u in range(self.TECHS):
				self.availability[u][p].available = availability[u]
				self.availability[u][p].researched = researched[u]
		self.globalAvailability = list(struct.unpack('<%dB' % self.TECHS, data[o:o+self.TECHS]))
		o += self.TECHS
		self.globallyResearched = list(struct.unpack('<%dB' % self.TECHS, data[o:o+self.TECHS]))
		o += self.TECHS
		for p in range(12):
			defaults = list(struct.unpack('<%dB' % self.TECHS, data[o:o+self.TECHS]))
			o += self.TECHS
			for u in range(self.TECHS):
				self.availability[u][p].default = defaults[u]

	def save_data(self):
		result = ''
		for p in range(12):
			availability = [self.availability[u][p].available for u in range(self.TECHS)]
			researched = [self.availability[u][p].researched for u in range(self.TECHS)]
			result += struct.pack('<%dB' % self.TECHS, *availability)
			result += struct.pack('<%dB' % self.TECHS, *researched)
		result += struct.pack('<%dB' % self.TECHS, *self.globalAvailability)
		result += struct.pack('<%dB' % self.TECHS, *self.globallyResearched)
		for p in range(12):
			defaults = [self.availability[u][p].default for u in range(self.TECHS)]
			result += struct.pack('<%dB' % self.TECHS, *defaults)
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Available','Researched','Use Defaults']:
			result += pad(name)
		result += '\n'
		for p in range(12):
			result += '\t# Player %d\n' % (p+1)
			for u in range(self.TECHS):
				result += '\t' + pad('Tech%02d' % u)
				result += pad(self.availability[u][p].available)
				result += pad(self.availability[u][p].researched)
				result += '%s\n' % self.availability[u][p].default
		result += '\t' + pad('# Global')
		for name in ['Available','Researched']:
			result += pad(name)
		result += '\n'
		for u in range(self.TECHS):
			result += '\t' + pad('Tech%02d' % u)
			result += pad(self.globalAvailability[u])
			result += '%s\n' % self.globallyResearched[u]
		return result

class CHKUnit:
	NYDUS_LINK = (1 << 9)
	ADDON_LINK = (1 << 10)

	CLOAK = (1 << 0)
	BURROW = (1 << 1)
	IN_TRANSIT = (1 << 2)
	HULLUCINATED = (1 << 3)
	INVINCIBLE = (1 << 4)

	OWNER = (1 << 0)
	HEALTH = (1 << 1)
	SHIELDS = (1 << 2)
	ENERGY = (1 << 3)
	RESOURCE = (1 << 4)
	HANGER = (1 << 5)

	def __init__(self, chk, ref_id):
		self.ref_id = ref_id
		self.chk = chk
		self.instanceID = 0
		self.position = [0,0]
		self.unit_id = 0
		self.buildingRelation = 0
		self.validAbilities = 0
		self.validProperties = 0
		self.owner = 0
		self.health = 0
		self.shields = 0
		self.energy = 0
		self.resources = 0
		self.hangerUnits = 0
		self.abilityStates = 0
		self.unitRelationID = 0

	def load_data(self, data):
		self.instanceID,x,y,self.unit_id,self.buildingRelation,self.validAbilities,self.validProperties,self.owner,self.health,self.shields,self.energy,self.resources,self.hangerUnits,self.abilityStates,self.unitRelationID = \
			struct.unpack('<L6H4BL2H4xL', data[:36])
		self.position = [x,y]

	def save_data(self):
		return struct.pack('<L6H4BL2H4xL', self.instanceID,self.position[0],self.position[1],self.unit_id,self.buildingRelation,self.validAbilities,self.validProperties,self.owner,self.health,self.shields,self.energy,self.resources,self.hangerUnits,self.abilityStates,self.unitRelationID)

	def decompile(self):
		result = '\t#\n'
		data = {
			'InstanceID': self.instanceID,
			'Position': '%s,%s' % (self.position[0], self.position[1]),
			'UnitID': self.unit_id,
			'BuildingRelation': named_flags(self.buildingRelation, ["Nydus Link","Addon Link"], 16, 9),
			'ValidAbilities': named_flags(self.validAbilities, ["Cloak", "Burrow", "In Transit", "Hullucinated", "Invincible"], 16),
			'ValidProperties': named_flags(self.validProperties, ["Owner", "Health", "Shields", "Energy", "Resources", "Hanger"], 16),
			'Owner': self.owner + 1,
			'Health': '%s%%' % self.health,
			'Shields': '%s%%' % self.shields,
			'Energy': '%s%%' % self.energy,
			'Resources': self.resources,
			'HangerUnits': self.hangerUnits,
			'AbilityStates': named_flags(self.validAbilities, ["Cloaked", "Burrowed", "In Transit", "Hullucinated", "Invincible"], 16),
			'UnitRelationID': self.unitRelationID
		}
		for key in ['InstanceID','Position','UnitID','BuildingRelation','ValidAbilities','ValidProperties','Owner','Health','Shields','Energy','Resources','HangerUnits','AbilityStates','UnitRelationID']:
			value = data[key]
			if isinstance(value, tuple):
				result += '\t%s%s\n' % (pad('#'), value[0])
				value = value[1]
			result += '\t%s\n' % pad(key, value)
		return result

class CHKSectionUNIT(CHKSection):
	NAME = 'UNIT'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.units = {}
		self.unused_ids = []
	
	def load_data(self, data):
		self.units = {}
		o = 0
		ref_id = 0
		while o+36 <= len(data):
			unit = CHKUnit(self.chk, ref_id)
			unit.load_data(data[o:o+36])
			self.units[ref_id] = unit
			ref_id += 1
			o += 36

	def unit_count(self):
		return len(self.units)

	def nth_unit(self, n):
		ref_ids = sorted(self.units.keys())
		return self.units[ref_ids[n]]

	def get_unit(self, ref_id):
		return self.units.get(ref_id)
	
	def save_data(self):
		result = ''
		for ref_id in sorted(self.units.keys()):
			unit = self.units[ref_id]
			result += unit.save_data()
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for ref_id in sorted(self.units.keys()):
			unit = self.units[ref_id]
			result += unit.decompile()
		return result

# ISOM

class CHKSectionTILE(CHKSection):
	NAME = 'TILE'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.raw_map = ''
		self.map = None
	
	def load_data(self, data):
		self.raw_map = data
	
	def process_data(self):
		if self.map != None:
			return
		self.map = []
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		diff = dims.width*dims.height - len(self.raw_map)
		if diff > 0:
			self.raw_map += '\0' * diff
		struct_format = '<%dH' % dims.width
		for y in range(dims.height):
			offset = y*dims.width*2
			values = struct.unpack(struct_format, self.raw_map[offset:offset+dims.width*2])
			self.map.append([[(v & 0xFFF0) >> 4,v & 0xF] for v in values])

	def save_data(self):
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		result = ''
		struct_format = '<%dH' % dims.width
		for r in self.map:
			values = [v[0] << 4 + v[1] for v in r]
			result += struct.pack(struct_format, *values)
		return result

	def decompile(self):
		result = '%s:\n' % self.NAME
		for row in self.map:
			for t in row:
				result += pad(t,span=6)
			result += '\n'
		return result

class CHKDoodadVisual:
	def __init__(self, chk):
		self.chk = chk
		self.doodadID = 0
		self.position = [0,0]
		self.owner = 0
		self.enabled = False

	def load_data(self, data):
		self.doodadID,x,y,self.owner,self.enabled = struct.unpack('<3H2B', data[:8])
		self.position = [x,y]

	def save_data(self):
		return struct.pack('<3H2B', self.doodadID,self.position[0],self.position[1],self.owner,self.enabled)

	def decompile(self):
		result = "\t#\n"
		result += '\t%s\n' % pad('DoodadID', self.doodadID)
		result += '\t%s\n' % pad('Position', '%s,%s' % (self.position[0],self.position[1]))
		result += '\t%s\n' % pad('Owner', self.owner)
		result += '\t%s\n' % pad('Enabled', self.enabled)
		return result

class CHKSectionDD2(CHKSection):
	NAME = 'DD2 '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.doodads = []
	
	def load_data(self, data):
		self.doodads = []
		o = 0
		while o+8 <= len(data):
			doodad = CHKDoodadVisual(self.chk)
			doodad.load_data(data[o:o+8])
			self.doodads.append(doodad)
			o += 8
	
	def save_data(self):
		result = ''
		for doodad in self.doodads:
			result += doodad.save_data()
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for doodad in self.doodads:
			result += doodad.decompile()
		return result

class CHKDoodad:
	SPRITE = (1 << 12)
	DISABLED = (1 << 15)

	def __init__(self, chk):
		self.chk = chk
		self.doodadID = 0
		self.position = [0,0]
		self.owner = 0
		self.flags = 0

	def load_data(self, data):
		self.doodadID,x,y,self.owner,self.flags = struct.unpack('<3HBxH', data[:10])
		self.position = [x,y]

	def save_data(self):
		return struct.pack('<3HBxH', self.doodadID,self.position[0],self.position[1],self.owner,self.flags)

	def decompile(self):
		result = "\t#\n"
		result += '\t%s\n' % pad('DoodadID', self.doodadID)
		result += '\t%s\n' % pad('Position', '%s,%s' % (self.position[0],self.position[1]))
		result += '\t%s\n' % pad('Owner', self.owner)
		header,values = named_flags(self.flags, ["Sprite",None,None,"Disabled"], 16, 12)
		result += '\t%s%s\n' % (pad('#'), header)
		result += '\t%s\n' % pad('Flags', values)
		return result

class CHKSectionTHG2(CHKSection):
	NAME = 'THG2'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.doodads = []
	
	def load_data(self, data):
		self.doodads = []
		o = 0
		while o+10 <= len(data):
			doodad = CHKDoodad(self.chk)
			doodad.load_data(data[o:o+10])
			self.doodads.append(doodad)
			o += 10
	
	def save_data(self):
		result = ''
		for doodad in self.doodads:
			result += doodad.save_data()
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for doodad in self.doodads:
			result += doodad.decompile()
		return result

class CHKSectionMASK(CHKSection):
	NAME = 'MASK'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.raw_map = ''
		self.map = None
	
	def load_data(self, data):
		self.raw_map = data
	
	def process_data(self):
		if self.map != None:
			return
		self.map = []
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		diff = dims.width*dims.height - len(self.raw_map)
		if diff > 0:
			self.raw_map += '\xFF' * diff
		struct_format = '<%dB' % dims.width
		for y in range(dims.height):
			offset = y*dims.width
			self.map.append(list(struct.unpack(struct_format, self.raw_map[offset:offset+dims.width])))
	
	def save_data(self):
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		result = ''
		struct_format = '<%dB' % dims.width
		for r in self.map:
			result += struct.pack(struct_format, *r)
		return result

	def decompile(self):
		result = '%s:\n' % self.NAME
		for row in self.map:
			for t in row:
				result += pad(binary(t,8),span=9)
			result += '\n'
		return result

class CHKString:
	def __init__(self, sect, string_id, text, refs=1):
		self.sect = sect
		self.string_id = string_id
		self.text = text
		self.references = refs

	def retain(self):
		self.references += 1

	def release(self):
		self.references -= 1
		if self.references == 0:
			self.sect.delete_string(self.string_id)

class CHKSectionSTR(CHKSection):
	NAME = 'STR '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.strings = {}
		self.open_ids = []
	
	def load_data(self, data):
		self.strings = {}
		self.open_ids = []
		string_id = 0
		count = struct.unpack('<H', data[:2])[0]
		for n in range(count):
			offset = struct.unpack('<H', data[2+n*2:4+n*2])[0]
			end = data.find('\0', offset, len(data))
			if end == -1:
				end = len(data)
			text = data[offset:end]
			string = self.lookup_string(text)
			if string:
				string.retain()
			else:
				string = CHKString(self, string_id, text)
			self.strings[string_id] = string
			string_id += 1
	
	def string_count(self):
		return len(self.strings)

	def highest_index(self):
		index = 0
		if self.strings:
			index = list(sorted(self.strings.keys()))[-1]
		return index

	def save_data(self):
		count = self.highest_index() + 1
		result = struct.pack('<H', count)
		strings = ''
		offset = 2+count*2
		for string_id in enumerate(count):
			result += struct.pack('<H', offset+len(strings))
			strings += self.get_string(string_id, '') + '\0'
		return result + strings

	def string_exists(self, string_id):
		return string_id in self.strings

	def lookup_string(self, text):
		for string in self.strings.values():
			if string.text == text:
				return string
		return None

	def add_string(self, text):
		string = self.lookup_string(text)
		if string:
			string.retain()
		else:
			index = self.string_count()
			if self.open_ids:
				index = self.open_ids[0]
				del self.open_ids[0]
			string = CHKString(self, index, text)
			self.strings[index] = string
		return string

	def remove_text(self, text):
		string = self.lookup_string(text)
		if string:
			string.release()

	def remove_string(self, string_id):
		string = self.strings.get(string_id)
		if string:
			string.release()

	def get_string(self, string_id):
		return self.strings.get(string_id)

	def get_text(self, string_id, default=None):
		string = self.get_string(string_id)
		if string:
			return string.text
		return default

	def set_string(self, string_id, text):
		string = self.get_string(string_id)
		if string:
			if string.references == 1:
				string.text = text
			else:
				string = self.lookup_string(text)
		if not string:
			string = self.add_string(text)
		return string

	def delete_string(self, string_id):
		if string_id in self.strings:
			del self.strings[string_id]
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for n,string in self.strings.iteritems():
			result += '\t%s"%s"\n' % (pad('String %d' % (n+1)), string.text.replace('\\','\\\\').replace('"','\\"'))
		return result

class CHKUnitProperties:
	def __init__(self, chk):
		self.chk = chk
		self.validAbilities = 0
		self.validProperties = 0
		self.owner = 0
		self.health = 0
		self.shields = 0
		self.energy = 0
		self.resources = 0
		self.hangerUnits = 0
		self.abilityStates = 0

	def load_data(self, data):
		self.validAbilities,self.validProperties,self.owner,self.health,self.shields,self.energy,self.resources,self.hangerUnits,self.abilityStates = \
			struct.unpack('<2H4BL2H4x', data[:20])

	def save_data(self):
		return struct.pack('<2H4BL2H4x', self.validAbilities,self.validProperties,self.owner,self.health,self.shields,self.energy,self.resources,self.hangerUnits,self.abilityStates)

	def decompile(self):
		result = '\t#\n'
		data = {
			'ValidAbilities': named_flags(self.validAbilities, ["Cloak", "Burrow", "In Transit", "Hullucinated", "Invincible"], 16),
			'ValidProperties': named_flags(self.validProperties, ["Owner", "Health", "Shields", "Energy", "Resources", "Hanger"], 16),
			'Owner': self.owner + 1,
			'Health': '%s%%' % self.health,
			'Shields': '%s%%' % self.shields,
			'Energy': '%s%%' % self.energy,
			'Resources': self.resources,
			'HangerUnits': self.hangerUnits,
			'AbilityStates': named_flags(self.validAbilities, ["Cloaked", "Burrowed", "In Transit", "Hullucinated", "Invincible"], 16),
		}
		for key in ['ValidAbilities','ValidProperties','Owner','Health','Shields','Energy','Resources','HangerUnits','AbilityStates']:
			value = data[key]
			if isinstance(value, tuple):
				result += '\t%s%s\n' % (pad('#'), value[0])
				value = value[1]
			result += '\t%s\n' % pad(key, value)
		return result

class CHKSectionUPRP(CHKSection):
	NAME = 'UPRP'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.properties = []
	
	def load_data(self, data):
		self.properties = []
		o = 0
		while o+20 <= len(data):
			properties = CHKUnitProperties(self.chk)
			properties.load_data(data[o:o+20])
			self.properties.append(properties)
			o += 20
	
	def save_data(self):
		result = ''
		for properties in self.properties:
			result += properties.save_data()
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for properties in self.properties:
			result += properties.decompile()
		return result

class CHKSectionUPUS(CHKSection):
	NAME = 'UPUS'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.properties_used = [False] * 64
	
	def load_data(self, data):
		self.properties_used = list(struct.unpack('<64B', data[:64]))
	
	def save_data(self):
		return struct.pack('<64B', *self.properties_used)
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for n,u in enumerate(self.properties_used):
			result += '\t%s\n' % pad('Properties%02d' % n, u)
		return result

class CHKLocation:
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

	def __init__(self, chk):
		self.chk = chk
		self.clear()

	def load_data(self, data):
		startX,startY,endX,endY,self.name,self.elevation = struct.unpack('<4L2H', data[:20])
		self.start = [startX,startY]
		self.end = [endX,endY]

	def save_data(self):
		return struct.pack('<4L2H', self.start[0],self.start[1],self.end[0],self.end[1],self.name,self.elevation)

	def decompile(self):
		result = '\t#\n'
		string = ''
		strings = self.chk.get_section(CHKSectionSTR.NAME)
		if strings and self.name > -1 and self.name < len(strings.strings):
			string = ' # ' + strings.strings[self.name].text
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

	def in_use(self):
		return self.name > 0 or self.start[0] != 0 or self.start[1] != 0 or self.end[0] != 0 or self.end[1] != 0 # or self.elevation != 0

	def normalized_coords(self):
		return (min(self.start[0],self.end[0]), min(self.start[1],self.end[1]), max(self.start[0],self.end[0]), max(self.start[1],self.end[1]))

	def clear(self):
		self.start = [0,0]
		self.end = [0,0]
		self.name = 0
		self.elevation = CHKLocation.NO_ELEVATION

class CHKSectionMRGN(CHKSection):
	NAME = 'MRGN'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.locations = []
	
	def load_data(self, data):
		self.locations = []
		o = 0
		while o+20 <= len(data):
			location = CHKLocation(self.chk)
			location.load_data(data[o:o+20])
			self.locations.append(location)
			o += 20

	def process_data(self):
		ver = self.chk.get_section(CHKSectionVER.NAME)
		count = 255 if ver.version >= CHKSectionVER.SC104 else 64
		while len(self.locations) < count:
			self.locations.append(CHKLocation(self.chk))

	def save_data(self):
		result = ''
		for location in self.locations:
			result += location.save_data()
		return result

	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for location in self.locations:
			result += location.decompile()
		return result

class CHKSectionTRIG(CHKSection):
	NAME = 'TRIG'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.trg = None
	
	def load_data(self, data):
		self.trg = TRG.TRG(self.chk.stat_txt, self.chk.aiscript)
		self.trg.load_data(data, True)
	
	def save_data(self):
		if self.trg:
			return self.trg.compile_data(True)
		return ''
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		if self.trg:
			result += self.trg.decompile_data()
		return result

class CHKSectionMBRF(CHKSection):
	NAME = 'MBRF'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.trg = None
	
	def load_data(self, data):
		self.trg = TRG.TRG(self.chk.stat_txt, self.chk.aiscript)
		self.trg.load_data(data, True, True)
	
	def save_data(self):
		if self.trg:
			return self.trg.compile_data(True)
		return ''
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		if self.trg:
			result += self.trg.decompile_data()
		return result

class CHKSectionSPRP(CHKSection):
	NAME = 'SPRP'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.scenarioName = 0
		self.description = 0
	
	def load_data(self, data):
		self.scenarioName,self.description = struct.unpack('<HH', data[:4])
	
	def save_data(self):
		return struct.pack('<HH', self.scenarioName, self.description)
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t%s\n' % pad('ScenarioName', 'String %d' % self.scenarioName)
		result += '\t%s\n' % pad('Description', 'String %d' % self.description)
		return result

class CHKForce:
	RANDOM_START = (1 << 0)
	ALLIES = (1 << 1)
	ALLIED_VICTORY = (1 << 2)
	SHARED_VISION = (1 << 4)

	def __init__(self):
		self.name = 0
		self.properties = 0

class CHKSectionFORC(CHKSection):
	NAME = 'FORC'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.playerForces = [0] * 8
		self.forces = []
		for f in range(4):
			self.forces.append(CHKForce())
	
	def load_data(self, data):
		o = 0
		self.playerForces = list(struct.unpack('<8B', data[o:o+8]))
		o += 8
		names = list(struct.unpack('<4H', data[o:o+8]))
		o += 8
		properties = list(struct.unpack('<4B', data[o:o+4]))
		for f in range(4):
			self.forces[f].name = names[f]
			self.forces[f].properties = properties[f]
	
	def save_data(self):
		names = []
		properties = []
		for force in self.forces:
			names.append(force.name)
			properties.append(force.properties)
		return struct.pack('<8B4H4B', *(self.playerForces + names + properties))
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t%s\n' % pad('#', 'Force')
		for p in range(8):
			result += '\t%s\n' % pad('Player %d' % (p+1), self.playerForces[p]+1)
		properties = ''
		for f,force in enumerate(self.forces):
			result += '\t%s\n' % pad('Name%d' % (f+1), 'String %d' % force.name)
			header,values = named_flags(force.properties, ["Random Start","Allies","Allied Victory","Shared Vision"], 8)
			if not properties:
				properties = '\t%s%s\n' % (pad('#'), header)
			properties += '\t%s\n' % pad('Properies%d' % (f+1), values)
		return result + properties

class CHKSectionWAV(CHKSection):
	NAME = 'WAV '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.paths = [0] * 512
	
	def load_data(self, data):
		self.paths = list(struct.unpack('<512L', data[:2048]))
	
	def save_data(self):
		return struct.pack('<512L', *self.paths)
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for w in range(512):
			result += '\t%s\n' % pad('Wav%03d' % w, 'String %d' % self.paths[w])
		return result

class CHKUnitStats:
	def __init__(self):
		self.default = True
		self.health = 0
		self.shields = 0
		self.armor = 0
		self.buildTime = 0
		self.costMinerals = 0
		self.costGas = 0
		self.name = 0
class CHKWeaponStats:
	def __init__(self):
		self.damage = 0
		self.damageUpgrade = 0

class CHKSectionUNIS(CHKSection):
	NAME = 'UNIS'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	UNITS = 228
	WEAPONS = 100
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.unit_stats = []
		for n in range(self.UNITS):
			self.unit_stats.append(CHKUnitStats())
		self.weapon_stats = []
		for n in range(self.WEAPONS):
			self.weapon_stats.append(CHKWeaponStats())
	
	def load_data(self, data):
		o = 0
		defaults = list(struct.unpack('<%dB' % self.UNITS, data[o:o+self.UNITS]))
		o += self.UNITS
		healths = list(struct.unpack('<%dL' % self.UNITS, data[o:o+self.UNITS*4]))
		o += self.UNITS*4
		shields = list(struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		armor = list(struct.unpack('<%dB' % self.UNITS, data[o:o+self.UNITS]))
		o += self.UNITS
		buildTimes = list(struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		costMinerals = list(struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		costGas = list(struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		names = list(struct.unpack('<%dH' % self.UNITS, data[o:o+self.UNITS*2]))
		o += self.UNITS*2
		for n,values in enumerate(zip(defaults,healths,shields,armor,buildTimes,costMinerals,costGas,names)):
			stat = self.unit_stats[n]
			stat.default,stat.health,stat.shields,stat.armor,stat.buildTime,stat.costMinerals,stat.costGas,stat.name = values
		damage = list(struct.unpack('<%dH' % self.WEAPONS, data[o:o+self.WEAPONS*2]))
		o += self.WEAPONS*2
		damageUpgrade = list(struct.unpack('<%dH' % self.WEAPONS, data[o:o+self.WEAPONS*2]))
		for n,values in enumerate(zip(damage,damageUpgrade)):
			stat = self.weapon_stats[n]
			stat.damage,stat.damageUpgrade = values

	def save_data(self):
		defaults = []
		healths = []
		shields = []
		armor = []
		buildTimes = []
		costMinerals = []
		costGas = []
		names = []
		damage = []
		damageUpgrade = []
		for stat in self.unit_stats:
			defaults.append(stat.default)
			healths.append(stat.health)
			shields.append(stat.shields)
			armor.append(stat.armor)
			buildTimes.append(stat.buildTime)
			costMinerals.append(stat.costMinerals)
			costGas.append(stat.costGas)
			names.append(stat.name)
		for stat in self.weapon_stats:
			damage.append(stat.damage)
			damageUpgrade.append(stat.damageUpgrade)
		result = struct.pack('<%dB' % self.UNITS, *defaults)
		result += struct.pack('<%dL' % self.UNITS, *healths)
		result += struct.pack('<%dH' % self.UNITS, *shields)
		result += struct.pack('<%dB' % self.UNITS, *armor)
		result += struct.pack('<%dH' % self.UNITS, *buildTimes)
		result += struct.pack('<%dH' % self.UNITS, *costMinerals)
		result += struct.pack('<%dH' % self.UNITS, *costGas)
		result += struct.pack('<%dH' % self.UNITS, *names)
		result += struct.pack('<%dH' % self.WEAPONS, *damage)
		result += struct.pack('<%dH' % self.WEAPONS, *damageUpgrade)
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Use Defaults','Health','Shields','Armor','Build Time','Mineral Cost','Gas Cost','Name']:
			result += pad(name)
		result += '\n'
		for n,stat in enumerate(self.unit_stats):
			result += '\t' + pad('Unit%03d' % n)
			result += pad(stat.default)
			result += pad(stat.health / 256.0)
			result += pad(stat.shields)
			result += pad(stat.armor)
			result += pad(stat.buildTime)
			result += pad(stat.costMinerals)
			result += pad(stat.costGas)
			result += '%s\n' % stat.name
		result += '\t' + pad('#')
		for name in ['Damage','Damage Upgrade']:
			result += pad(name)
		result += '\n'
		for n,stat in enumerate(self.weapon_stats):
			result += '\t' + pad('Weapon%03d' % n)
			result += pad(stat.damage)
			result += '%s\n' % stat.damageUpgrade
		return result

class CHKUpgradeStats:
	def __init__(self):
		self.default = True
		self.costMinerals = 0
		self.costMineralsIncrease = 0
		self.costGas = 0
		self.costGasIncrease = 0
		self.buildTime = 0
		self.buildTimeIncrease = 0

class CHKSectionUPGS(CHKSection):
	NAME = 'UPGS'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	UPGRADES = 46
	PAD = False
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.stats = []
		for n in range(self.UPGRADES):
			self.stats.append(CHKUpgradeStats())
	
	def load_data(self, data):
		o = 0
		defaults = list(struct.unpack('<%dB' % self.UPGRADES, data[o:o+self.UPGRADES]))
		o += self.UPGRADES+self.PAD
		costMinerals = list(struct.unpack('<%dH' % self.UPGRADES, data[o:o+self.UPGRADES*2]))
		o += self.UPGRADES*2
		costMineralsIncreases = list(struct.unpack('<%dH' % self.UPGRADES, data[o:o+self.UPGRADES*2]))
		o += self.UPGRADES*2
		costGas = list(struct.unpack('<%dH' % self.UPGRADES, data[o:o+self.UPGRADES*2]))
		o += self.UPGRADES*2
		costGasIncreases = list(struct.unpack('<%dH' % self.UPGRADES, data[o:o+self.UPGRADES*2]))
		o += self.UPGRADES*2
		buildTimes = list(struct.unpack('<%dH' % self.UPGRADES, data[o:o+self.UPGRADES*2]))
		o += self.UPGRADES*2
		buildTimeIncreases = list(struct.unpack('<%dH' % self.UPGRADES, data[o:o+self.UPGRADES*2]))
		for n,values in enumerate(zip(defaults,costMinerals,costMineralsIncreases,costGas,costGasIncreases,buildTimes,buildTimeIncreases)):
			stat = self.stats[n]
			stat.default,stat.costMinerals,stat.costMineralsIncrease,stat.costGas,stat.costGasIncrease,stat.buildTime,stat.buildTimeIncrease = values

	def save_data(self):
		defaults = []
		costMinerals = []
		costMineralsIncreases = []
		costGas = []
		costGasIncreases = []
		buildTimes = []
		buildTimeIncreases = []
		for stat in self.stats:
			defaults.append(stat.default)
			costMinerals.append(stat.costMinerals)
			costMineralsIncreases.append(stat.costMineralsIncrease)
			costGas.append(stat.costGas)
			costGasIncreases.append(stat.costGasIncrease)
			buildTimes.append(stat.buildTime)
			buildTimeIncreases.append(stat.buildTimeIncrease)
		result = struct.pack('<%dB' % self.UPGRADES, *defaults)
		if self.PAD:
			result += '\0'
		result += struct.pack('<%dH' % self.UPGRADES, *costMinerals)
		result += struct.pack('<%dH' % self.UPGRADES, *costMineralsIncreases)
		result += struct.pack('<%dH' % self.UPGRADES, *costGas)
		result += struct.pack('<%dH' % self.UPGRADES, *costGasIncreases)
		result += struct.pack('<%dH' % self.UPGRADES, *buildTimes)
		result += struct.pack('<%dH' % self.UPGRADES, *buildTimeIncreases)
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Use Defaults','Minerals','Minerals Increase','Gas','Gas Increase','Build Time','Build Time Increase']:
			result += pad(name)
		result += '\n'
		for n,stat in enumerate(self.stats):
			result += '\t' + pad('Upgrade%02d' % n)
			result += pad(stat.default)
			result += pad(stat.costMinerals)
			result += pad(stat.costMineralsIncrease)
			result += pad(stat.costGas)
			result += pad(stat.costGasIncrease)
			result += pad(stat.buildTime)
			result += '%s\n' % stat.buildTimeIncrease
		return result

class CHKTechStats:
	def __init__(self):
		self.default = True
		self.costMinerals = 0
		self.costGas = 0
		self.buildTime = 0
		self.energyUsed = 0

class CHKSectionTECS(CHKSection):
	NAME = 'TECS'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	TECHS = 24
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.stats = []
		for n in range(self.TECHS):
			self.stats.append(CHKTechStats())
	
	def load_data(self, data):
		o = 0
		defaults = list(struct.unpack('<%dB' % self.TECHS, data[o:o+self.TECHS]))
		o += self.TECHS
		costMinerals = list(struct.unpack('<%dH' % self.TECHS, data[o:o+self.TECHS*2]))
		o += self.TECHS*2
		costGas = list(struct.unpack('<%dH' % self.TECHS, data[o:o+self.TECHS*2]))
		o += self.TECHS*2
		buildTimes = list(struct.unpack('<%dH' % self.TECHS, data[o:o+self.TECHS*2]))
		o += self.TECHS*2
		energyUsed = list(struct.unpack('<%dH' % self.TECHS, data[o:o+self.TECHS*2]))
		for n,values in enumerate(zip(defaults,costMinerals,costGas,buildTimes,energyUsed)):
			stat = self.stats[n]
			stat.default,stat.costMinerals,stat.costGas,stat.buildTime,stat.energyUsed = values

	def save_data(self):
		defaults = []
		costMinerals = []
		costGas = []
		buildTimes = []
		energyUsed = []
		for stat in self.stats:
			defaults.append(stat.default)
			costMinerals.append(stat.costMinerals)
			costGas.append(stat.costGas)
			buildTimes.append(stat.buildTime)
			energyUsed.append(stat.energyUsed)
		result = struct.pack('<%dB' % self.TECHS, *defaults)
		result += struct.pack('<%dH' % self.TECHS, *costMinerals)
		result += struct.pack('<%dH' % self.TECHS, *costGas)
		result += struct.pack('<%dH' % self.TECHS, *buildTimes)
		result += struct.pack('<%dH' % self.TECHS, *energyUsed)
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Use Defaults','Minerals','Gas','Build Time','Energy Used']:
			result += pad(name)
		result += '\n'
		for n,stat in enumerate(self.stats):
			result += '\t' + pad('Tech%02d' % n)
			result += pad(stat.default)
			result += pad(stat.costMinerals)
			result += pad(stat.costGas)
			result += pad(stat.buildTime)
			result += '%s\n' % stat.energyUsed
		return result

class CHKSectionSWNM(CHKSection):
	NAME = 'SWNM'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.names = [0] * 256
	
	def load_data(self, data):
		self.names = list(struct.unpack('<256L', data[:256*4]))
	
	def save_data(self):
		return struct.pack('<256L', *self.names)
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for n,name in enumerate(self.names):
			result += '\t%s\n' % (pad('Switch %d' % n, 'String %d' % name))
		return result

class CHKSectionCOLR(CHKSection):
	NAME = 'COLR'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_BROODWAR, CHKRequirements.MODE_ALL)
	
	RED = 0
	BLUE = 1
	TEAL = 2
	PURPLE = 3
	ORANGE = 4
	BROWN = 5
	WHITE = 6
	YELLOW = 7
	GREEN = 8
	PALE_YELLOW = 9
	TAN = 10
	NEUTRAL = 11
	PALE_GREEN = 12
	BLUEISH_GREY = 13
	PALE_YELLOW_2 = 14
	CYAN = 15
	BLACK = 17

	DEFAULT_COLORS = [RED,BLUE,TEAL,PURPLE,ORANGE,BROWN,WHITE,YELLOW]

	@staticmethod
	def COLOR_NAME(c):
		names = {
			CHKSectionCOLR.RED:'Red',
			CHKSectionCOLR.BLUE:'Blue',
			CHKSectionCOLR.TEAL:'Teal',
			CHKSectionCOLR.PURPLE:'Purple',
			CHKSectionCOLR.ORANGE:'Orange',
			CHKSectionCOLR.BROWN:'Brown',
			CHKSectionCOLR.WHITE:'White',
			CHKSectionCOLR.YELLOW:'Yellow',
			CHKSectionCOLR.GREEN:'Green',
			CHKSectionCOLR.PALE_YELLOW:'Pale Yellow',
			CHKSectionCOLR.TAN:'Tan',
			CHKSectionCOLR.NEUTRAL:'Neutral',
			CHKSectionCOLR.PALE_GREEN:'Pale Green',
			CHKSectionCOLR.BLUEISH_GREY:'Blueish Grey',
			CHKSectionCOLR.PALE_YELLOW_2:'Pale Yellow (2)',
			CHKSectionCOLR.CYAN:'Cyan',
			CHKSectionCOLR.BLACK:'Black'
		}
		return names.get(c,'Unknown')

	@staticmethod
	def PALETTE_INDICES(c):
		names = {
			CHKSectionCOLR.RED:111,
			CHKSectionCOLR.BLUE:165,
			CHKSectionCOLR.TEAL:159,
			CHKSectionCOLR.PURPLE:164,
			CHKSectionCOLR.ORANGE:179,
			CHKSectionCOLR.BROWN:19,
			CHKSectionCOLR.WHITE:255,
			CHKSectionCOLR.YELLOW:135,
			CHKSectionCOLR.GREEN:117,
			CHKSectionCOLR.PALE_YELLOW:136, # ?
			CHKSectionCOLR.TAN:33, # ?
			CHKSectionCOLR.NEUTRAL:127, # ?
			# CHKSectionCOLR.PALE_GREEN:,
			# CHKSectionCOLR.BLUEISH_GREY:,
			CHKSectionCOLR.PALE_YELLOW_2:137, # ?
			CHKSectionCOLR.CYAN:128,
			CHKSectionCOLR.BLACK:0
		}
		return names.get(c,0)

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.colors = CHKSectionCOLR.DEFAULT_COLORS
	
	def load_data(self, data):
		self.colors = list(struct.unpack('<8B', data[:8]))
	
	def save_data(self):
		return struct.pack('<8B', *self.colors)
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for p,c in enumerate(self.colors):
			result += '\t%s # %s\n' % (pad('Player%d' % (p+1), c), CHKSectionCOLR.COLOR_NAME(c))
		return result

class CHKSectionPUPx(CHKSectionUPGR):
	NAME = 'PUPx'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_BROODWAR_HYBRID, CHKRequirements.MODE_UMS)

	UPGRADES = 61

class CHKSectionPTEx(CHKSectionPTEC):
	NAME = 'PTEx'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_BROODWAR_HYBRID, CHKRequirements.MODE_UMS)

	TECHS = 44

class CHKSectionUNIx(CHKSectionUNIS):
	NAME = 'UNIx'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_BROODWAR_HYBRID, CHKRequirements.MODE_UMS)

	WEAPONS = 130

class CHKSectionUPGx(CHKSectionUPGS):
	NAME = 'UPGx'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_BROODWAR_HYBRID, CHKRequirements.MODE_UMS)

	UPGRADES = 61
	PAD = True

class CHKSectionTECx(CHKSectionTECS):
	NAME = 'TECx'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_BROODWAR_HYBRID, CHKRequirements.MODE_UMS)

	TECHS = 44

# class CHKSection(CHKSection):
#	NAME = ''
#	
# 	def __init__(self, chk):
# 		CHKSection.__init__(self, chk)
#	
# 	def load_data(self, data):
# 		pass
#	
# 	def save_data(self):
# 		pass
	
# 	def decompile(self):
# 		result = '%s:\n' % (self.NAME)
#		return result

class CHK:
	SECTION_TYPES = {
		CHKSectionTYPE.NAME:CHKSectionTYPE,
		CHKSectionVER.NAME:CHKSectionVER,
		CHKSectionIVER.NAME:CHKSectionIVER,
		CHKSectionIVE2.NAME:CHKSectionIVE2,
		CHKSectionVCOD.NAME:CHKSectionVCOD,
		CHKSectionIOWN.NAME:CHKSectionIOWN,
		CHKSectionOWNR.NAME:CHKSectionOWNR,
		CHKSectionERA.NAME:CHKSectionERA,
		CHKSectionDIM.NAME:CHKSectionDIM,
		CHKSectionSIDE.NAME:CHKSectionSIDE,
		CHKSectionMTXM.NAME:CHKSectionMTXM,
		CHKSectionPUNI.NAME:CHKSectionPUNI,
		CHKSectionUPGR.NAME:CHKSectionUPGR,
		CHKSectionPTEC.NAME:CHKSectionPTEC,
		CHKSectionUNIT.NAME:CHKSectionUNIT,
		CHKSectionTILE.NAME:CHKSectionTILE,
		CHKSectionDD2.NAME:CHKSectionDD2,
		CHKSectionTHG2.NAME:CHKSectionTHG2,
		CHKSectionMASK.NAME:CHKSectionMASK,
		CHKSectionSTR.NAME:CHKSectionSTR,
		CHKSectionUPRP.NAME:CHKSectionUPRP,
		CHKSectionUPUS.NAME:CHKSectionUPUS,
		CHKSectionMRGN.NAME:CHKSectionMRGN,
		CHKSectionTRIG.NAME:CHKSectionTRIG,
		CHKSectionMBRF.NAME:CHKSectionMBRF,
		CHKSectionSPRP.NAME:CHKSectionSPRP,
		CHKSectionFORC.NAME:CHKSectionFORC,
		CHKSectionWAV.NAME:CHKSectionWAV,
		CHKSectionUNIS.NAME:CHKSectionUNIS,
		CHKSectionUPGS.NAME:CHKSectionUPGS,
		CHKSectionTECS.NAME:CHKSectionTECS,
		CHKSectionSWNM.NAME:CHKSectionSWNM,
		CHKSectionCOLR.NAME:CHKSectionCOLR,
		CHKSectionPUPx.NAME:CHKSectionPUPx,
		CHKSectionPTEx.NAME:CHKSectionPTEx,
		CHKSectionUNIx.NAME:CHKSectionUNIx,
		CHKSectionUPGx.NAME:CHKSectionUPGx,
		CHKSectionTECx.NAME:CHKSectionTECx
	}

	def __init__(self, stat_txt=None, aiscript=None):
		if isinstance(stat_txt, TBL.TBL):
			self.stat_txt = stat_txt
		else:
			if stat_txt == None:
				stat_txt = os.path.join(BASE_DIR,'Libs', 'MPQ', 'rez', 'stat_txt.tbl')
			self.stat_txt = TBL.TBL()
			self.stat_txt.load_file(stat_txt)
		if isinstance(aiscript, AIBIN.AIBIN):
			self.aiscript = aiscript
		else:
			if aiscript == None:
				aiscript = os.path.join(BASE_DIR,'Libs', 'MPQ', 'scripts', 'aiscript.bin')
			self.aiscript = AIBIN.AIBIN(stat_txt=self.stat_txt)
			self.aiscript.load_file(aiscript)
		self.sections = {}
		self.section_order = []

	def get_section(self, name, game_mode=CHKRequirements.MODE_ALL):
		sect_class = CHK.SECTION_TYPES[name]
		required = False

		if name == CHKSectionVER.NAME:
			required = True
		elif sect_class:
			required = sect_class.REQUIREMENTS.is_required(self, game_mode)
		sect = self.sections.get(name)
		if required and sect == None and sect_class:
			sect = sect_class(self)
			self.sections[name] = sect
		return sect

	def player_color(self, player):
		colors = CHKSectionCOLR.DEFAULT_COLORS
		colr = self.get_section(CHKSectionCOLR.NAME)
		if colr:
			colors = colr.colors
		colors.extend((CHKSectionCOLR.GREEN,CHKSectionCOLR.PALE_YELLOW,CHKSectionCOLR.TAN,CHKSectionCOLR.NEUTRAL))
		return colors[player]

	def load_file(self, file):
		data = load_file(file, 'CHK')
		try:
			self.load_data(data)
		except PyMSError, e:
			raise e
		except:
			raise PyMSError('Load',"Unsupported CHK file '%s', could possibly be corrupt" % file)

	def load_data(self, data):
		offset = 0
		sections = {}
		section_order = []
		toProcess = []
		while offset < len(data)-8:
			name,length = struct.unpack('<4sL', data[offset:offset+8])
			offset += 8
			sect_class = CHK.SECTION_TYPES.get(name)
			if not sect_class:
				sect = CHKSectionUnknown(self, name)
			else:
				sect = sect_class(self)
			sect.load_data(data[offset:offset+min(length,len(data)-offset)])
			sections[name] = sect
			section_order.append(name)
			if hasattr(sect, "process_data"):
				toProcess.append(sect)
			offset += length
		self.sections = sections
		self.section_order = section_order
		for sect in toProcess:
			sect.process_data()

	def save_file(self, file):
		data = self.save_data()
		try:
			f = AtomicWriter(file, 'wb')
		except:
			raise PyMSError('Save',"Could not save CHK to file '%s'" % file)
		f.write(data)
		f.close()

	def save_data(self):
		print '========= Save'
		result = ''
		order = []
		order.extend(self.section_order)
		for name in self.sections.keys():
			if not name in order:
				order.append(name)
		for name in order:
			section = self.sections.get(name)
			if section:
				print name
				data = section.save_data()
				result += struct.pack('<4sL', section.name, len(data))
				result += data
		return result