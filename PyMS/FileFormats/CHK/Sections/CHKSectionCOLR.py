
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

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
