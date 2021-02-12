
from ..Utilities.utils import isstr

class DATID(object):
	def __init__(self, id):
		self.id = id

	def __eq__(self, other):
		if isinstance(other, DATID):
			return other.id == self.id
		if isstr(other):
			return other == self.id
		return False

DATID.units = DATID('Units')
DATID.weapons = DATID('Weapons')
DATID.flingy = DATID('Flingy')
DATID.sprites = DATID('Sprites')
DATID.images = DATID('Images')
DATID.upgrades = DATID('Upgrades')
DATID.techdata = DATID('Techdata')
DATID.sfxdata = DATID('Sfxdata')
DATID.portdata = DATID('Portdata')
DATID.mapdata = DATID('Mapdata')
DATID.orders = DATID('Orders')

DATID.ALL = [DATID.units, DATID.weapons, DATID.flingy, DATID.sprites, DATID.images, DATID.upgrades, DATID.techdata, DATID.sfxdata, DATID.portdata, DATID.mapdata, DATID.orders]
