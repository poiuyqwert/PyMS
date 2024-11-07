
from .CV5 import CV5Flag, CV5DoodadFlag
from .VF4 import VF4Flag

from ...Utilities import Serialize
from ...Utilities.PyMSError import PyMSError
from ...Utilities import JSON

import re
from collections import OrderedDict

class TileGroupField:
	type = 'type'
	flags = 'flags'
	edge = 'edge'
	piece = 'piece'

	class Flag:
		walkable = 'walkable'
		unknown_0002 = 'unknown_0002'
		unwalkable = 'unwalkable'
		unknown_0008 = 'unknown_0008'
		has_doodad_cover = 'has_doodad_cover'
		unknown_0020 = 'unknown_0020'
		creep = 'creep'
		unbuildable = 'unbuildable'
		blocks_view = 'blocks_view'
		mid_ground = 'mid_ground'
		high_ground = 'high_ground'
		occupied = 'occupied'
		creep_receding = 'creep_receding'
		cliff_edge = 'cliff_edge'
		creep_temp = 'creep_temp'
		special_placeable = 'special_placeable'

class DoodadGroupField:
	flags = 'flags'
	overlay_id = 'overlay_id'
	scr = 'scr'
	string_id = 'string_id'
	unknown4 = 'unknown4'
	dddata_id = 'dddata_id'
	width = 'width'
	height = 'height'
	unknown8 = 'unknown8'

	class Flag:
		walkable = 'walkable'
		unknown_0002 = 'unknown_0002'
		unwalkable = 'unwalkable'
		unknown_0008 = 'unknown_0008'
		has_doodad_cover = 'has_doodad_cover'
		unknown_0020 = 'unknown_0020'
		creep = 'creep'
		unbuildable = 'unbuildable'
		blocks_view = 'blocks_view'
		mid_ground = 'mid_ground'
		high_ground = 'high_ground'
		occupied = 'occupied'
		has_overlay_sprite = 'has_overlay_sprite'
		has_overlay_unit = 'has_overlay_unit'
		overlay_flipped = 'overlay_flipped'
		special_placeable = 'special_placeable'

class MegatileField:
	mid_ground = 'mid_ground'
	high_ground = 'high_ground'
	walkable = 'walkable'
	blocks_sight = 'blocks_sight'
	ramp = 'ramp'

class GroupTypeEncoder(Serialize.IntEncoder):
	def decode(self, value: JSON.Value) -> int:
		value = Serialize.IntEncoder.decode(self, value)
		if value == 1:
			raise PyMSError('Decode', f"'TileGroup' can't have type 1 (doodad type). Must be a 'DoodadGroup' to be doodad type.")
		return value

class MiniFlagsMultiEncoder(Serialize.SplitEncoder[list[int], list[bool]]):
	def __init__(self, flag: int) -> None:
		self.attr = 'flags'
		self.flag = flag

	def encode(self, value: list[int]) -> JSON.Value:
		result = ''
		for n,flags in enumerate(value):
			if n and not n % 4:
				result += '\n'
			has_flag = (flags & self.flag) == self.flag
			result += '1' if has_flag else '0'
		return result
	
	RE_LINE = re.compile(r'\s*([TtFf01]{4})\s*')
	def decode(self, value: JSON.Value, current: list[bool] | None) -> list[bool]:
		if not isinstance(value, str):
			raise PyMSError('Decoding', f"Expected a string, got '{value}'")
		lines = value.splitlines()
		if not len(lines) == 4:
			raise PyMSError('Decoding', f"Expected 4 lines of flags, got '{len(lines)}'")
		if current is not None:
			result = current
		else:
			result = []
		for line in lines:
			match = MiniFlagsMultiEncoder.RE_LINE.match(line)
			if not match:
				raise PyMSError('Decoding', f"Expected 4 flags, got '{line}'")
			line = match.group(1)
			for flag in line:
				result.append(Serialize.BoolEncoder.parse(flag))
		return result

	def apply(self, value: list[bool], current: list[int]) -> list[int]:
		result = list(current)
		for index,has_flag in enumerate(value):
			if has_flag:
				result[index] |= self.flag
			else:
				result[index] &= ~self.flag
		return result

TileGroupDef = Serialize.Definition('TileGroup', Serialize.IDMode.comment, {
	TileGroupField.type: GroupTypeEncoder(),
	TileGroupField.flags: Serialize.IntFlagEncoder({
		TileGroupField.Flag.walkable: CV5Flag.walkable,
		TileGroupField.Flag.unknown_0002: CV5Flag.unknown_0002,
		TileGroupField.Flag.unwalkable: CV5Flag.unwalkable,
		TileGroupField.Flag.unknown_0008: CV5Flag.unknown_0008,
		TileGroupField.Flag.has_doodad_cover: CV5Flag.has_doodad_cover,
		TileGroupField.Flag.unknown_0020: CV5Flag.unknown_0020,
		TileGroupField.Flag.creep: CV5Flag.creep,
		TileGroupField.Flag.unbuildable: CV5Flag.unbuildable,
		TileGroupField.Flag.blocks_view: CV5Flag.blocks_view,
		TileGroupField.Flag.mid_ground: CV5Flag.mid_ground,
		TileGroupField.Flag.high_ground: CV5Flag.high_ground,
		TileGroupField.Flag.occupied: CV5Flag.occupied,
		TileGroupField.Flag.creep_receding: CV5Flag.creep_receding,
		TileGroupField.Flag.cliff_edge: CV5Flag.cliff_edge,
		TileGroupField.Flag.creep_temp: CV5Flag.creep_temp,
		TileGroupField.Flag.special_placeable: CV5Flag.special_placeable,
	}),
	TileGroupField.edge: Serialize.JoinEncoder((
		('_edge_left_or_overlay_id', 'left', Serialize.IntEncoder()),
		('_edge_up_or_scr', 'up', Serialize.IntEncoder()),
		('_edge_right_or_string_id', 'right', Serialize.IntEncoder()),
		('_edge_down_or_unknown4', 'down', Serialize.IntEncoder()),
	)),
	TileGroupField.piece: Serialize.JoinEncoder((
		('_piece_left_or_dddata_id', 'left', Serialize.IntEncoder()),
		('_piece_up_or_width', 'up', Serialize.IntEncoder()),
		('_piece_right_or_height', 'right', Serialize.IntEncoder()),
		('_piece_down_or_unknown8', 'down', Serialize.IntEncoder()),
	)),
})

DoodadGroupDef = Serialize.Definition('DoodadGroup', Serialize.IDMode.comment, {
	DoodadGroupField.flags: Serialize.IntFlagEncoder({
		DoodadGroupField.Flag.walkable: CV5Flag.walkable,
		DoodadGroupField.Flag.unknown_0002: CV5Flag.unknown_0002,
		DoodadGroupField.Flag.unwalkable: CV5Flag.unwalkable,
		DoodadGroupField.Flag.unknown_0008: CV5Flag.unknown_0008,
		DoodadGroupField.Flag.has_doodad_cover: CV5Flag.has_doodad_cover,
		DoodadGroupField.Flag.unknown_0020: CV5Flag.unknown_0020,
		DoodadGroupField.Flag.creep: CV5Flag.creep,
		DoodadGroupField.Flag.unbuildable: CV5Flag.unbuildable,
		DoodadGroupField.Flag.blocks_view: CV5Flag.blocks_view,
		DoodadGroupField.Flag.mid_ground: CV5Flag.mid_ground,
		DoodadGroupField.Flag.high_ground: CV5Flag.high_ground,
		DoodadGroupField.Flag.occupied: CV5Flag.occupied,
		DoodadGroupField.Flag.has_overlay_sprite: CV5DoodadFlag.has_overlay_sprite,
		DoodadGroupField.Flag.has_overlay_unit: CV5DoodadFlag.has_overlay_unit,
		DoodadGroupField.Flag.overlay_flipped: CV5DoodadFlag.overlay_flipped,
		DoodadGroupField.Flag.special_placeable: CV5Flag.special_placeable,
	}),
	DoodadGroupField.overlay_id: Serialize.RenameEncoder('_edge_left_or_overlay_id', Serialize.IntEncoder()),
	DoodadGroupField.scr: Serialize.RenameEncoder('_edge_up_or_scr', Serialize.IntEncoder()),
	DoodadGroupField.string_id: Serialize.RenameEncoder('_edge_right_or_string_id', Serialize.IntEncoder()),
	DoodadGroupField.unknown4: Serialize.RenameEncoder('_edge_down_or_unknown4', Serialize.IntEncoder()),
	DoodadGroupField.dddata_id: Serialize.RenameEncoder('_piece_left_or_dddata_id', Serialize.IntEncoder()),
	DoodadGroupField.width: Serialize.RenameEncoder('_piece_up_or_width', Serialize.IntEncoder()),
	DoodadGroupField.height: Serialize.RenameEncoder('_piece_right_or_height', Serialize.IntEncoder()),
	DoodadGroupField.unknown8: Serialize.RenameEncoder('_piece_down_or_unknown8', Serialize.IntEncoder()),
})

MegatileDef = Serialize.Definition('MegaTile', Serialize.IDMode.comment, {
	MegatileField.mid_ground: MiniFlagsMultiEncoder(VF4Flag.mid_ground),
	MegatileField.high_ground: MiniFlagsMultiEncoder(VF4Flag.high_ground),
	MegatileField.walkable: MiniFlagsMultiEncoder(VF4Flag.walkable),
	MegatileField.blocks_sight: MiniFlagsMultiEncoder(VF4Flag.blocks_sight),
	MegatileField.ramp: MiniFlagsMultiEncoder(VF4Flag.ramp),
})
