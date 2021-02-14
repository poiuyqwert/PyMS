
from ..Utilities.utils import isstr

class ID(object):
	def __init__(self, id):
		self.id = id

	def __eq__(self, other):
		if isinstance(other, ID):
			return other.id == self.id
		if isstr(other):
			return other == self.id
		return False

	def __repr__(self):
		return '<%s "%s">' % (type(self).__name__, self.id)

class DATID:
	units = ID('Units')
	weapons = ID('Weapons')
	flingy = ID('Flingy')
	sprites = ID('Sprites')
	images = ID('Images')
	upgrades = ID('Upgrades')
	techdata = ID('Techdata')
	sfxdata = ID('Sfxdata')
	portdata = ID('Portdata')
	mapdata = ID('Mapdata')
	orders = ID('Orders')

	ALL = [units, weapons, flingy, sprites, images, upgrades, techdata, sfxdata, portdata, mapdata, orders]

class DataID:
	stat_txt = ID('stat_txt')
	unitnamestbl = ID('unitnamestbl')
	imagestbl = ID('imagestbl')
	sfxdatatbl = ID('sfxdatatbl')
	portdatatbl = ID('portdatatbl')
	mapdatatbl = ID('mapdatatbl')

	cmdicons = ID('cmdicons')
	iscriptbin = ID('iscriptbin')

	ALL = [stat_txt, unitnamestbl, imagestbl, sfxdatatbl, portdatatbl, mapdatatbl, cmdicons, iscriptbin]