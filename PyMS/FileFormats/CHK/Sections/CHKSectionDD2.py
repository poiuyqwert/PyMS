
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKDoodadVisual:
	def __init__(self, chk: CHK) -> None:
		self.chk = chk
		self.doodadID = 0
		self.position = [0,0]
		self.owner = 0
		self.enabled = False

	def load_data(self, data: bytes) -> None:
		self.doodadID,x,y,self.owner,enabled = tuple(int(v) for v in struct.unpack('<3H2B', data[:8]))
		self.position = [x,y]
		self.enabled = bool(enabled)

	def save_data(self) -> bytes:
		return struct.pack('<3H2B', self.doodadID,self.position[0],self.position[1],self.owner,self.enabled)

	def decompile(self) -> str:
		result = "\t#\n"
		result += f'\t{pad("DoodadID", str(self.doodadID))}\n'
		result += f'\t{pad("Position", f"{self.position[0]},{self.position[1]}")}\n'
		result += f'\t{pad("Owner", str(self.owner))}\n'
		result += f'\t{pad("Enabled", str(self.enabled))}\n'
		return result

class CHKSectionDD2(CHKSection):
	NAME = b'DD2 '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)

	def __init__(self, chk: CHK) -> None:
		CHKSection.__init__(self, chk)
		self.doodads: list[CHKDoodadVisual] = []

	def load_data(self, data: bytes) -> None:
		self.doodads = []
		o = 0
		while o+8 <= len(data):
			doodad = CHKDoodadVisual(self.chk)
			doodad.load_data(data[o:o+8])
			self.doodads.append(doodad)
			o += 8

	def save_data(self) -> bytes:
		result = b''
		for doodad in self.doodads:
			result += doodad.save_data()
		return result

	def decompile(self) -> str:
		result = f'{self.NAME.decode("ascii")}:\n'
		for doodad in self.doodads:
			result += doodad.decompile()
		return result
