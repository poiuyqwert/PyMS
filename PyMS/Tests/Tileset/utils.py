
from ...FileFormats.Tileset import Tileset
from ...FileFormats.Tileset.CV5 import CV5Group, CV5Flag
from ...FileFormats.Tileset.VF4 import VF4Megatile, VF4Flag

class ID:
	basic_empty: int
	basic_inc: int
	basic_full: int
	basic_flags: int

	doodad_empty: int
	doodad_inc: int
	doodad_full: int
	doodad_flags: int
	
	mega_empty: int
	mega_full: int
	mega_crosshatch: int
	mega_crosshatch2: int

class Max:
	u8 = 0xFF
	u16 = 0xFFFF

def group_empty(doodad: bool = False) -> CV5Group:
	group = CV5Group()
	group.type = CV5Group.TYPE_DOODAD if doodad else 0
	return group

def group_inc(doodad: bool = False) -> CV5Group:
	group = CV5Group()
	group.type = CV5Group.TYPE_DOODAD if doodad else 0
	group.flags = 1
	group._edge_left_or_overlay_id = 2
	group._edge_up_or_scr = 3
	group._edge_right_or_string_id = 4
	group._edge_down_or_unknown4 = 5
	group._piece_left_or_dddata_id = 6
	group._piece_up_or_width = 7
	group._piece_right_or_height = 8
	group._piece_down_or_unknown8 = 9
	return group

def group_full(doodad: bool = False) -> CV5Group:
	group = CV5Group()
	group.type = CV5Group.TYPE_DOODAD if doodad else Max.u16
	group.flags = Max.u16
	group._edge_left_or_overlay_id = Max.u16
	group._edge_up_or_scr = Max.u16
	group._edge_right_or_string_id = Max.u16
	group._edge_down_or_unknown4 = Max.u16
	group._piece_left_or_dddata_id = Max.u16
	group._piece_up_or_width = Max.u16
	group._piece_right_or_height = Max.u16
	group._piece_down_or_unknown8 = Max.u16
	return group

def group_flags(doodad: bool = False) -> CV5Group:
	group = CV5Group()
	group.type = CV5Group.TYPE_DOODAD if doodad else 0
	group.flags = CV5Flag.walkable | CV5Flag.unwalkable | CV5Flag.has_doodad_cover | CV5Flag.creep | CV5Flag.blocks_view | CV5Flag.high_ground | CV5Flag.creep_receding | CV5Flag.creep_temp
	return group

def mega_empty() -> VF4Megatile:
	return VF4Megatile()

def mega_full() -> VF4Megatile:
	megatile = VF4Megatile()
	megatile.flags = [0x1F] * 16
	return megatile

def mega_crosshatch() -> VF4Megatile:
	megatile = VF4Megatile()
	megatile.flags = ([0x1F, 0] * 2 + [0, 0x1F] * 2) * 2
	return megatile

def mega_crosshatch2() -> VF4Megatile:
	megatile = VF4Megatile()
	megatile.flags = ([0, 0x1F] * 2 + [0x1F, 0] * 2) * 2
	return megatile

def test_tileset() -> Tileset:
	tileset = Tileset()
	tileset.new_file()

	ID.basic_empty = tileset.cv5.add_group(group_empty())
	ID.basic_inc = tileset.cv5.add_group(group_inc())
	ID.basic_full = tileset.cv5.add_group(group_full())
	ID.basic_flags = tileset.cv5.add_group(group_flags())

	ID.doodad_empty = tileset.cv5.add_group(group_empty(True))
	ID.doodad_inc = tileset.cv5.add_group(group_inc(True))
	ID.doodad_full = tileset.cv5.add_group(group_full(True))
	ID.doodad_flags = tileset.cv5.add_group(group_flags(True))

	ID.mega_empty = tileset.vf4.add_megatile(mega_empty())
	ID.mega_full = tileset.vf4.add_megatile(mega_full())
	ID.mega_crosshatch = tileset.vf4.add_megatile(mega_crosshatch())
	ID.mega_crosshatch2 = tileset.vf4.add_megatile(mega_crosshatch2())

	return tileset
