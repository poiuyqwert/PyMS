
from enum import Enum

class DATID(Enum):
	units = 'Units'
	weapons = 'Weapons'
	flingy = 'Flingy'
	sprites = 'Sprites'
	images = 'Images'
	upgrades = 'Upgrades'
	techdata = 'Techdata'
	sfxdata = 'Sfxdata'
	portdata = 'Portdata'
	mapdata = 'Mapdata'
	orders = 'Orders'

	ALL: list['DATID']

	@property
	def filename(self): # type: () -> str
		if self == DATID.units:
			return 'units.dat'
		elif self == DATID.weapons:
			return 'weapons.dat'
		elif self == DATID.flingy:
			return 'flingy.dat'
		elif self == DATID.sprites:
			return 'sprites.dat'
		elif self == DATID.images:
			return 'images.dat'
		elif self == DATID.upgrades:
			return 'upgrades.dat'
		elif self == DATID.techdata:
			return 'techdata.dat'
		elif self == DATID.sfxdata:
			return 'sfxdata.dat'
		elif self == DATID.portdata:
			return 'portdata.dat'
		elif self == DATID.mapdata:
			return 'mapdata.dat'
		else: #if self == DATID.orders:
			return 'orders.dat'

	@property
	def tab_id(self): # type: () -> str
		return self.value

DATID.ALL = [DATID.units, DATID.weapons, DATID.flingy, DATID.sprites, DATID.images, DATID.upgrades, DATID.techdata, DATID.sfxdata, DATID.portdata, DATID.mapdata, DATID.orders]


class UnitsTabID(Enum):
	basic = 'Basic'
	advanced = 'Advanced'
	sounds = 'Sounds'
	graphics = 'Graphics'
	staredit = 'StarEdit'
	ai_actions = 'AI Actions'

	@property
	def tab_name(self): # type: () -> str
		return self.value


class DataID(Enum):
	stat_txt = 'stat_txt'
	unitnamestbl = 'unitnamestbl'
	imagestbl = 'imagestbl'
	sfxdatatbl = 'sfxdatatbl'
	portdatatbl = 'portdatatbl'
	mapdatatbl = 'mapdatatbl'

	cmdicons = 'cmdicons'
	iscriptbin = 'iscriptbin'

	ALL: list['DataID']

DataID.ALL = [DataID.stat_txt, DataID.unitnamestbl, DataID.imagestbl, DataID.sfxdatatbl, DataID.portdatatbl, DataID.mapdatatbl, DataID.cmdicons, DataID.iscriptbin]