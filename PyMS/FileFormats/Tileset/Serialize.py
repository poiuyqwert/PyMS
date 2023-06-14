
from .CV5 import CV5Flag, CV5DoodadFlag
from .VF4 import VF4Flag

from ...Utilities import Serialize
from ...Utilities.PyMSError import PyMSError

import re

class TileGroupField:
	type = 'type'
	flags = 'flags'
	edge_left = '_edge_left_or_overlay_id'
	edge_up = '_edge_up_or_scr'
	edge_right = '_edge_right_or_string_id'
	edge_down = '_edge_down_or_unknown4'
	piece_left = '_piece_left_or_dddata_id'
	piece_up = '_piece_up_or_width'
	piece_right = '_piece_right_or_height'
	piece_down = '_piece_down_or_unknown8'

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
	overlay_id = '_edge_left_or_overlay_id'
	scr = '_edge_up_or_scr'
	string_id = '_edge_right_or_string_id'
	unknown4 = '_edge_down_or_unknown4'
	dddata_id = '_piece_left_or_dddata_id'
	width = '_piece_up_or_width'
	height = '_piece_right_or_height'
	unknown8 = '_piece_down_or_unknown8'

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
	def decode(self, value: Serialize.JSONValue) -> int:
		value = Serialize.IntEncoder.decode(self, value)
		if value == 1:
			raise PyMSError('Decode', f"'TileGroup' can't have type 1 (doodad type). Must be a 'DoodadGroup' to be doodad type.")
		return value

class MiniFlagsMultiEncoder(Serialize.SplitEncoder[list[int]]):
	def __init__(self, flag: int) -> None:
		self.attr = 'flags'
		self.flag = flag

	def encode(self, value: list[int]) -> Serialize.JSONValue:
		result = ''
		for n,flags in enumerate(value):
			if n and not n % 4:
				result += '\n'
			has_flag = (flags & self.flag) == self.flag
			result += '1' if has_flag else '0'
		return result
	
	RE_LINE = re.compile(r'\s*([01]{4})\s*')
	def decode(self, value: Serialize.JSONValue, current: list[int] | None) -> list[int]:
		if not isinstance(value, str):
			raise PyMSError('Decoding', f"Expected a string, got '{value}'")
		lines = value.splitlines()
		if not len(lines) == 4:
			raise PyMSError('Decoding', f"Expected 4 lines of flags, got '{len(lines)}'")
		if current is not None:
			result = current
		else:
			result = [0] * 16
		for x,line in enumerate(lines):
			match = MiniFlagsMultiEncoder.RE_LINE.match(line)
			if not match:
				raise PyMSError('Decoding', f"Expected 4 flags, got '{line}'")
			line = match.group(1)
			for y,flag in enumerate(line):
				if flag == '0':
					continue
				n = (y * 4) + x
				result[n] |= self.flag
		return result

TileGroupDef = Serialize.Definition('TileGroup', Serialize.IDMode.comment, {
	TileGroupField.type: GroupTypeEncoder(),
	TileGroupField.flags: Serialize.IntFlagEncoder({
		'walkable': CV5Flag.walkable,
		'unknown_0002': CV5Flag.unknown_0002,
		'unwalkable': CV5Flag.unwalkable,
		'unknown_0008': CV5Flag.unknown_0008,
		'has_doodad_cover': CV5Flag.has_doodad_cover,
		'unknown_0020': CV5Flag.unknown_0020,
		'creep': CV5Flag.creep,
		'unbuildable': CV5Flag.unbuildable,
		'blocks_view': CV5Flag.blocks_view,
		'mid_ground': CV5Flag.mid_ground,
		'high_ground': CV5Flag.high_ground,
		'occupied': CV5Flag.occupied,
		'creep_receding': CV5Flag.creep_receding,
		'cliff_edge': CV5Flag.cliff_edge,
		'creep_temp': CV5Flag.creep_temp,
		'special_placeable': CV5Flag.special_placeable,
	}),
	TileGroupField.edge_left: Serialize.JoinEncoder('edge', 'left', Serialize.IntEncoder()),
	TileGroupField.edge_up: Serialize.JoinEncoder('edge', 'up', Serialize.IntEncoder()),
	TileGroupField.edge_right: Serialize.JoinEncoder('edge', 'right', Serialize.IntEncoder()),
	TileGroupField.edge_down: Serialize.JoinEncoder('edge', 'down', Serialize.IntEncoder()),
	TileGroupField.piece_left: Serialize.JoinEncoder('piece', 'left', Serialize.IntEncoder()),
	TileGroupField.piece_up: Serialize.JoinEncoder('piece', 'up', Serialize.IntEncoder()),
	TileGroupField.piece_right: Serialize.JoinEncoder('piece', 'right', Serialize.IntEncoder()),
	TileGroupField.piece_down: Serialize.JoinEncoder('piece', 'down', Serialize.IntEncoder()),
})

DoodadGroupDef = Serialize.Definition('DoodadGroup', Serialize.IDMode.comment, {
	DoodadGroupField.flags: Serialize.IntFlagEncoder({
		'walkable': CV5Flag.walkable,
		'unknown_0002': CV5Flag.unknown_0002,
		'unwalkable': CV5Flag.unwalkable,
		'unknown_0008': CV5Flag.unknown_0008,
		'has_doodad_cover': CV5Flag.has_doodad_cover,
		'unknown_0020': CV5Flag.unknown_0020,
		'creep': CV5Flag.creep,
		'unbuildable': CV5Flag.unbuildable,
		'blocks_view': CV5Flag.blocks_view,
		'mid_ground': CV5Flag.mid_ground,
		'high_ground': CV5Flag.high_ground,
		'occupied': CV5Flag.occupied,
		'has_overlay_sprite': CV5DoodadFlag.has_overlay_sprite,
		'has_overlay_unit': CV5DoodadFlag.has_overlay_unit,
		'overlay_flipped': CV5DoodadFlag.overlay_flipped,
		'special_placeable': CV5Flag.special_placeable,
	}),
	DoodadGroupField.overlay_id: Serialize.RenameEncoder('overlay_id', Serialize.IntEncoder()),
	DoodadGroupField.scr: Serialize.RenameEncoder('scr', Serialize.IntEncoder()),
	DoodadGroupField.string_id: Serialize.RenameEncoder('string_id', Serialize.IntEncoder()),
	DoodadGroupField.unknown4: Serialize.RenameEncoder('unknown4', Serialize.IntEncoder()),
	DoodadGroupField.dddata_id: Serialize.RenameEncoder('dddata_id', Serialize.IntEncoder()),
	DoodadGroupField.width: Serialize.RenameEncoder('width', Serialize.IntEncoder()),
	DoodadGroupField.height: Serialize.RenameEncoder('height', Serialize.IntEncoder()),
	DoodadGroupField.unknown8: Serialize.RenameEncoder('unknown8', Serialize.IntEncoder()),
})

MegatileDef = Serialize.Definition('MegaTile', Serialize.IDMode.comment, {
	MegatileField.mid_ground: MiniFlagsMultiEncoder(VF4Flag.mid_ground),
	MegatileField.high_ground: MiniFlagsMultiEncoder(VF4Flag.high_ground),
	MegatileField.walkable: MiniFlagsMultiEncoder(VF4Flag.walkable),
	MegatileField.blocks_sight: MiniFlagsMultiEncoder(VF4Flag.blocks_sight),
	MegatileField.ramp: MiniFlagsMultiEncoder(VF4Flag.ramp),
})
