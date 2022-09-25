
from ..Utilities.utils import isstr

class ID(object):
	def __init__(self, id):
		self.id = id

	def __eq__(self, other):
		if isinstance(other, type(self)):
			return other.id == self.id
		if isstr(other):
			return other == self.id
		return False

	def __repr__(self):
		return '<%s "%s">' % (type(self).__name__, self.id)


class DATID(ID):
	# Initialized here to None for intellisense, real value assigned later
	units = None
	weapons = None
	flingy = None
	sprites = None
	images = None
	upgrades = None
	techdata = None
	sfxdata = None
	portdata = None
	mapdata = None
	orders = None
	ALL = None

	def __init__(self, id, filename, tab_id=None):
		self.filename = filename
		self.tab_id = tab_id or id
		ID.__init__(self, id)

DATID.units = DATID('Units', 'units.dat')
DATID.weapons = DATID('Weapons', 'weapons.dat')
DATID.flingy = DATID('Flingy', 'flingy.dat')
DATID.sprites = DATID('Sprites', 'sprites.dat')
DATID.images = DATID('Images', 'images.dat')
DATID.upgrades = DATID('Upgrades', 'upgrades.dat')
DATID.techdata = DATID('Techdata', 'techdata.dat')
DATID.sfxdata = DATID('Sfxdata', 'sfxdata.dat')
DATID.portdata = DATID('Portdata', 'portdata.dat')
DATID.mapdata = DATID('Mapdata', 'mapdata.dat')
DATID.orders = DATID('Orders', 'orders.dat')

DATID.ALL = [DATID.units, DATID.weapons, DATID.flingy, DATID.sprites, DATID.images, DATID.upgrades, DATID.techdata, DATID.sfxdata, DATID.portdata, DATID.mapdata, DATID.orders]


class UnitsTabID(ID):
	# Initialized here to None for intellisense, real value assigned later
	basic = None
	advanced = None
	sounds = None
	graphics = None
	staredit = None
	ai_actions = None

	def __init__(self, id, tab_name=None):
		self.tab_name = tab_name or id
		ID.__init__(self, id)

UnitsTabID.basic = UnitsTabID('Basic')
UnitsTabID.advanced = UnitsTabID('Advanced')
UnitsTabID.sounds = UnitsTabID('Sounds')
UnitsTabID.graphics = UnitsTabID('Graphics')
UnitsTabID.staredit = UnitsTabID('StarEdit')
UnitsTabID.ai_actions = UnitsTabID('AI Actions')


class DataID(ID):
	# Initialized here to None for intellisense, real value assigned later
	stat_txt = None
	unitnamestbl = None
	imagestbl = None
	sfxdatatbl = None
	portdatatbl = None
	mapdatatbl = None

	cmdicons = None
	iscriptbin = None

	ALL = None

DataID.stat_txt = DataID('stat_txt')
DataID.unitnamestbl = DataID('unitnamestbl')
DataID.imagestbl = DataID('imagestbl')
DataID.sfxdatatbl = DataID('sfxdatatbl')
DataID.portdatatbl = DataID('portdatatbl')
DataID.mapdatatbl = DataID('mapdatatbl')

DataID.cmdicons = DataID('cmdicons')
DataID.iscriptbin = DataID('iscriptbin')

DataID.ALL = [DataID.stat_txt, DataID.unitnamestbl, DataID.imagestbl, DataID.sfxdatatbl, DataID.portdatatbl, DataID.mapdatatbl, DataID.cmdicons, DataID.iscriptbin]