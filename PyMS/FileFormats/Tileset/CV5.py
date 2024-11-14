
from __future__ import annotations

from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from typing import BinaryIO

class CV5Flag:
	walkable          = 0x0001 # Walkable (gets overwritten by SC based on VF4 flags)
	unknown_0002      = 0x0002
	unwalkable        = 0x0004 # Unwalkable (gets overwritten by SC based on VF4 flags)
	unknown_0008      = 0x0008
	has_doodad_cover  = 0x0010 # Has doodad cover
	unknown_0020      = 0x0020
	creep             = 0x0040 # Creep (Zerg can build here when this flag is combined with the Temporary creep flag)
	unbuildable       = 0x0080
	blocks_view       = 0x0100 # Blocks view (gets overwritten by SC based on VF4 flags)
	mid_ground        = 0x0200 # Mid Ground (gets overwritten by SC based on VF4 flags)
	high_ground       = 0x0400 # High Ground (gets overwritten by SC based on VF4 flags)
	occupied          = 0x0800 # Occupied (unbuildable until a building on this tile gets removed)
	creep_receding    = 0x1000 # Receding creep
	cliff_edge        = 0x2000 # Cliff edge (gets overwritten by SC based on VF4 flags)
	creep_temp        = 0x4000 # Temporary creep (Zerg can build here when this flag is combined with the Creep flag)
	special_placeable = 0x8000 # Allow Beacons/Start Locations to be placeable

class CV5DoodadFlag:
	has_overlay_sprite = 0x1000 # Has Sprites.dat overlay (is not cleared by SC, so this flag also counts as Receding creep)
	has_overlay_unit   = 0x2000 # Has Units.dat overlay
	overlay_flipped    = 0x4000 # Overlay is flipped (unused) (is not cleared SC, so this flag also counts as Temporary creep)

class CV5Group(object):
	TYPE_DOODAD = 1
	SCR = 1

	def __init__(self) -> None:
		self.type = 0 
		self.flags = 0
		self._edge_left_or_overlay_id = 0
		self._edge_up_or_scr = 0
		self._edge_right_or_string_id = 0
		self._edge_down_or_unknown4 = 0
		self._piece_left_or_dddata_id = 0
		self._piece_up_or_width = 0
		self._piece_right_or_height = 0
		self._piece_down_or_unknown8 = 0
		self.megatile_ids: list[int] = []

	def load_data(self, data: bytes) -> None:
		self.type,\
			self.flags,\
			self._edge_left_or_overlay_id,\
			self._edge_up_or_scr,\
			self._edge_right_or_string_id,\
			self._edge_down_or_unknown4,\
			self._piece_left_or_dddata_id,\
			self._piece_up_or_width,\
			self._piece_right_or_height,\
			self._piece_down_or_unknown8 = list(int(v) for v in struct.unpack('<10H', data[:20]))
		self.megatile_ids = list(int(v) for v in struct.unpack('<16H', data[20:]))

	def save_data(self) -> bytes:
		values = [
			self.type,
			self.flags,
			self._edge_left_or_overlay_id,
			self._edge_up_or_scr,
			self._edge_right_or_string_id,
			self._edge_down_or_unknown4,
			self._piece_left_or_dddata_id,
			self._piece_up_or_width,
			self._piece_right_or_height,
			self._piece_down_or_unknown8
		] + self.megatile_ids
		return struct.pack('<26H', *values)

	def update_settings(self, group: CV5Group) -> None:
		self.type = group.type
		self.flags = group.flags
		self._edge_left_or_overlay_id = group._edge_left_or_overlay_id
		self._edge_up_or_scr = group._edge_up_or_scr
		self._edge_right_or_string_id = group._edge_right_or_string_id
		self._edge_down_or_unknown4 = group._edge_down_or_unknown4
		self._piece_left_or_dddata_id = group._piece_left_or_dddata_id
		self._piece_up_or_width = group._piece_up_or_width
		self._piece_right_or_height = group._piece_right_or_height
		self._piece_down_or_unknown8 = group._piece_down_or_unknown8

	@property
	def basic_edge_left(self) -> int:
		return self._edge_left_or_overlay_id
	@basic_edge_left.setter
	def basic_edge_left(self, value: int) -> None:
		self._edge_left_or_overlay_id = value

	@property
	def basic_edge_up(self) -> int:
		return self._edge_up_or_scr
	@basic_edge_up.setter
	def basic_edge_up(self, value: int) -> None:
		self._edge_up_or_scr = value

	@property
	def basic_edge_right(self) -> int:
		return self._edge_right_or_string_id
	@basic_edge_right.setter
	def basic_edge_right(self, value: int) -> None:
		self._edge_right_or_string_id = value

	@property
	def basic_edge_down(self) -> int:
		return self._edge_down_or_unknown4
	@basic_edge_down.setter
	def basic_edge_down(self, value: int) -> None:
		self._edge_down_or_unknown4 = value

	@property
	def basic_piece_left(self) -> int:
		return self._piece_left_or_dddata_id
	@basic_piece_left.setter
	def basic_piece_left(self, value: int) -> None:
		self._piece_left_or_dddata_id = value

	@property
	def basic_piece_up(self) -> int:
		return self._piece_up_or_width
	@basic_piece_up.setter
	def basic_piece_up(self, value: int) -> None:
		self._piece_up_or_width = value

	@property
	def basic_piece_right(self) -> int:
		return self._piece_right_or_height
	@basic_piece_right.setter
	def basic_piece_right(self, value: int) -> None:
		self._piece_right_or_height = value

	@property
	def basic_piece_down(self) -> int:
		return self._piece_down_or_unknown8
	@basic_piece_down.setter
	def basic_piece_down(self, value: int) -> None:
		self._piece_down_or_unknown8 = value


	@property
	def doodad_overlay_id(self) -> int:
		return self._edge_left_or_overlay_id
	@doodad_overlay_id.setter
	def doodad_overlay_id(self, value: int) -> None:
		self._edge_left_or_overlay_id = value

	@property
	def doodad_scr(self) -> int:
		return self._edge_up_or_scr
	@doodad_scr.setter
	def doodad_scr(self, value: int) -> None:
		self._edge_up_or_scr = value

	@property
	def doodad_string_id(self) -> int:
		return self._edge_right_or_string_id
	@doodad_string_id.setter
	def doodad_string_id(self, value: int) -> None:
		self._edge_right_or_string_id = value

	@property
	def doodad_unknown4(self) -> int:
		return self._edge_down_or_unknown4
	@doodad_unknown4.setter
	def doodad_unknown4(self, value: int) -> None:
		self._edge_down_or_unknown4 = value

	@property
	def doodad_dddata_id(self) -> int:
		return self._piece_left_or_dddata_id
	@doodad_dddata_id.setter
	def doodad_dddata_id(self, value: int) -> None:
		self._piece_left_or_dddata_id = value

	@property
	def doodad_width(self) -> int:
		return self._piece_up_or_width
	@doodad_width.setter
	def doodad_width(self, value: int) -> None:
		self._piece_up_or_width = value

	@property
	def doodad_height(self) -> int:
		return self._piece_right_or_height
	@doodad_height.setter
	def doodad_height(self, value: int) -> None:
		self._piece_right_or_height = value

	@property
	def doodad_unknown8(self) -> int:
		return self._piece_down_or_unknown8
	@doodad_unknown8.setter
	def doodad_unknown8(self, value: int) -> None:
		self._piece_down_or_unknown8 = value

	def __eq__(self, other: Any) -> bool:
		if not isinstance(other, CV5Group):
			return False
		if other.type != self.type:
			return False
		if other.flags != self.flags:
			return False
		if other._edge_left_or_overlay_id != self._edge_left_or_overlay_id:
			return False
		if other._edge_up_or_scr != self._edge_up_or_scr:
			return False
		if other._edge_right_or_string_id != self._edge_right_or_string_id:
			return False
		if other._edge_down_or_unknown4 != self._edge_down_or_unknown4:
			return False
		if other._piece_left_or_dddata_id != self._piece_left_or_dddata_id:
			return False
		if other._piece_up_or_width != self._piece_up_or_width:
			return False
		if other._piece_right_or_height != self._piece_right_or_height:
			return False
		if other._piece_down_or_unknown8 != self._piece_down_or_unknown8:
			return False
		if other.megatile_ids != self.megatile_ids:
			return False
		return True

class CV5(object):
	MAX_ID = 4095

	def __init__(self) -> None:
		self._groups: list[CV5Group] = []

	def group_count(self) -> int:
		return len(self._groups)

	def groups_remaining(self) -> int:
		return (CV5.MAX_ID+1) - len(self._groups)
 
	def get_group(self, id: int) -> CV5Group:
		return self._groups[id]

	def add_group(self, group: CV5Group) -> int:
		id = len(self._groups)
		self._groups.append(group)
		return id

	def load_file(self, file: str | BinaryIO) -> None:
		data = load_file(file, 'CV5')
		if data and len(data) % 52:
			raise PyMSError('Load',"'%s' is an invalid CV5 file" % file)
		groups: list[CV5Group] = []
		try:
			o = 0
			while o + 51 < len(data):
				group = CV5Group()
				group.load_data(data[o:o+52])
				groups.append(group)
				o += 52
		except:
			raise PyMSError('Load',"Unsupported CV5 file '%s', could possibly be corrupt" % file)
		self._groups = groups

	def save_file(self, file: str | BinaryIO) -> None:
		data = b''
		for group in self._groups:
			data += group.save_data()
		if isinstance(file, str):
			try:
				f = AtomicWriter(file)
				f.write(data)
				f.close()
			except:
				raise PyMSError('Save',"Could not save the CV5 to '%s'" % file)
		else:
			file.write(data)
			file.close()
