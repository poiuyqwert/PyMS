
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKSectionOWNR(CHKSection):
	NAME = b'OWNR'
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
	def OWNER_NAME(v: int) -> str:
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

	def __init__(self, chk: CHK) -> None:
		CHKSection.__init__(self, chk)
		self.owners = [CHKSectionOWNR.HUMAN]*8 + [CHKSectionOWNR.INACTIVE]*3 + [CHKSectionOWNR.NEUTRAL]

	def load_data(self, data: bytes) -> None:
		self.owners = list(int(o) for o in struct.unpack('<12B', data[:12]))

	def save_data(self) -> bytes:
		return struct.pack('<12B', *self.owners)

	def decompile(self) -> str:
		result = f'{self.NAME.decode("ascii")}:\n'
		for n,value in enumerate(self.owners):
			result += f'\t{pad(f"Slot{n:02d}",str(value))} # {CHKSectionOWNR.OWNER_NAME(value)}\n'
		return result
