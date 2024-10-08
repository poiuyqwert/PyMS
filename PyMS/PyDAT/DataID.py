
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

	@property
	def ALL(self) -> tuple['DATID', ...]:
		return (DATID.units, DATID.weapons, DATID.flingy, DATID.sprites, DATID.images, DATID.upgrades, DATID.techdata, DATID.sfxdata, DATID.portdata, DATID.mapdata, DATID.orders)

	@property
	def filename(self) -> str:
		match self:
			case DATID.units:
				return 'units.dat'
			case DATID.weapons:
				return 'weapons.dat'
			case DATID.flingy:
				return 'flingy.dat'
			case DATID.sprites:
				return 'sprites.dat'
			case DATID.images:
				return 'images.dat'
			case DATID.upgrades:
				return 'upgrades.dat'
			case DATID.techdata:
				return 'techdata.dat'
			case DATID.sfxdata:
				return 'sfxdata.dat'
			case DATID.portdata:
				return 'portdata.dat'
			case DATID.mapdata:
				return 'mapdata.dat'
			case DATID.orders:
				return 'orders.dat'

	@property
	def tab_id(self) -> str:
		return self.value


class UnitsTabID(Enum):
	basic = 'Basic'
	advanced = 'Advanced'
	sounds = 'Sounds'
	graphics = 'Graphics'
	staredit = 'StarEdit'
	ai_actions = 'AI Actions'

	@property
	def tab_name(self) -> str:
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

	@property
	def ALL(self) -> tuple['DataID', ...]:
		return (DataID.stat_txt, DataID.unitnamestbl, DataID.imagestbl, DataID.sfxdatatbl, DataID.portdatatbl, DataID.mapdatatbl, DataID.cmdicons, DataID.iscriptbin)

AnyID = DATID | DataID
