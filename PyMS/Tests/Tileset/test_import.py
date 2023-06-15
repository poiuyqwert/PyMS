
from ...FileFormats.Tileset.VF4 import VF4Flag

from .utils import *

import unittest

class Test_Import_TileGroup(unittest.TestCase):
	def test_all_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	type 0
	flags.walkable 0
	flags.unknown_0002 0
	flags.unwalkable 0
	flags.unknown_0008 0
	flags.has_doodad_cover 0
	flags.unknown_0020 0
	flags.creep 0
	flags.unbuildable 0
	flags.blocks_view 0
	flags.mid_ground 0
	flags.high_ground 0
	flags.occupied 0
	flags.creep_receding 0
	flags.cliff_edge 0
	flags.creep_temp 0
	flags.special_placeable 0
	edge.left 0
	edge.up 0
	edge.right 0
	edge.down 0
	piece.left 0
	piece.up 0
	piece.right 0
	piece.down 0
"""
		expected = group_empty()
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_all_inc(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	type 0
	flags.walkable 1
	flags.unknown_0002 0
	flags.unwalkable 0
	flags.unknown_0008 0
	flags.has_doodad_cover 0
	flags.unknown_0020 0
	flags.creep 0
	flags.unbuildable 0
	flags.blocks_view 0
	flags.mid_ground 0
	flags.high_ground 0
	flags.occupied 0
	flags.creep_receding 0
	flags.cliff_edge 0
	flags.creep_temp 0
	flags.special_placeable 0
	edge.left 2
	edge.up 3
	edge.right 4
	edge.down 5
	piece.left 6
	piece.up 7
	piece.right 8
	piece.down 9
"""
		expected = group_inc()
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_all_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	type 65535
	flags.walkable 1
	flags.unknown_0002 1
	flags.unwalkable 1
	flags.unknown_0008 1
	flags.has_doodad_cover 1
	flags.unknown_0020 1
	flags.creep 1
	flags.unbuildable 1
	flags.blocks_view 1
	flags.mid_ground 1
	flags.high_ground 1
	flags.occupied 1
	flags.creep_receding 1
	flags.cliff_edge 1
	flags.creep_temp 1
	flags.special_placeable 1
	edge.left 65535
	edge.up 65535
	edge.right 65535
	edge.down 65535
	piece.left 65535
	piece.up 65535
	piece.right 65535
	piece.down 65535
"""
		expected = group_full()
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_all_flags(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	type 0
	flags.walkable 1
	flags.unknown_0002 0
	flags.unwalkable 1
	flags.unknown_0008 0
	flags.has_doodad_cover 1
	flags.unknown_0020 0
	flags.creep 1
	flags.unbuildable 0
	flags.blocks_view 1
	flags.mid_ground 0
	flags.high_ground 1
	flags.occupied 0
	flags.creep_receding 1
	flags.cliff_edge 0
	flags.creep_temp 1
	flags.special_placeable 0
	edge.left 0
	edge.up 0
	edge.right 0
	edge.down 0
	piece.left 0
	piece.up 0
	piece.right 0
	piece.down 0
"""
		expected = group_flags()
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_type_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	type 0
"""
		expected = group_full()
		expected.type = 0
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_flags_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	flags.walkable 0
	flags.unknown_0002 0
	flags.unwalkable 0
	flags.unknown_0008 0
	flags.has_doodad_cover 0
	flags.unknown_0020 0
	flags.creep 0
	flags.unbuildable 0
	flags.blocks_view 0
	flags.mid_ground 0
	flags.high_ground 0
	flags.occupied 0
	flags.creep_receding 0
	flags.cliff_edge 0
	flags.creep_temp 0
	flags.special_placeable 0
"""
		expected = group_full()
		expected.flags = 0
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_edge_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	edge.left 0
	edge.up 0
	edge.right 0
	edge.down 0
"""
		expected = group_full()
		expected.basic_edge_left = 0
		expected.basic_edge_up = 0
		expected.basic_edge_right = 0
		expected.basic_edge_down = 0
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_edge_left_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	edge.left 0
"""
		expected = group_full()
		expected.basic_edge_left = 0
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_edge_up_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	edge.up 0
"""
		expected = group_full()
		expected.basic_edge_up = 0
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_edge_right_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	edge.right 0
"""
		expected = group_full()
		expected.basic_edge_right = 0
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_edge_down_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	edge.down 0
"""
		expected = group_full()
		expected.basic_edge_down = 0
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_piece_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	piece.left 0
	piece.up 0
	piece.right 0
	piece.down 0
"""
		expected = group_full()
		expected.basic_piece_left = 0
		expected.basic_piece_up = 0
		expected.basic_piece_right = 0
		expected.basic_piece_down = 0
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_piece_left_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	piece.left 0
"""
		expected = group_full()
		expected.basic_piece_left = 0
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_piece_up_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	piece.up 0
"""
		expected = group_full()
		expected.basic_piece_up = 0
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_piece_right_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	piece.right 0
"""
		expected = group_full()
		expected.basic_piece_right = 0
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_piece_down_empty(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	piece.down 0
"""
		expected = group_full()
		expected.basic_piece_down = 0
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_type_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	type 65535
"""
		expected = group_empty()
		expected.type = Max.u16
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_flags_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	flags.walkable 1
	flags.unknown_0002 1
	flags.unwalkable 1
	flags.unknown_0008 1
	flags.has_doodad_cover 1
	flags.unknown_0020 1
	flags.creep 1
	flags.unbuildable 1
	flags.blocks_view 1
	flags.mid_ground 1
	flags.high_ground 1
	flags.occupied 1
	flags.creep_receding 1
	flags.cliff_edge 1
	flags.creep_temp 1
	flags.special_placeable 1
"""
		expected = group_empty()
		expected.flags = Max.u16
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_edge_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	edge.left 65535
	edge.up 65535
	edge.right 65535
	edge.down 65535
"""
		expected = group_empty()
		expected.basic_edge_left = Max.u16
		expected.basic_edge_up = Max.u16
		expected.basic_edge_right = Max.u16
		expected.basic_edge_down = Max.u16
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_edge_left_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	edge.left 65535
"""
		expected = group_empty()
		expected.basic_edge_left = Max.u16
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_edge_up_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	edge.up 65535
"""
		expected = group_empty()
		expected.basic_edge_up = Max.u16
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_edge_right_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	edge.right 65535
"""
		expected = group_empty()
		expected.basic_edge_right = Max.u16
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_edge_down_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	edge.down 65535
"""
		expected = group_empty()
		expected.basic_edge_down = Max.u16
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_piece_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	piece.left 65535
	piece.up 65535
	piece.right 65535
	piece.down 65535
"""
		expected = group_empty()
		expected.basic_piece_left = Max.u16
		expected.basic_piece_up = Max.u16
		expected.basic_piece_right = Max.u16
		expected.basic_piece_down = Max.u16
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_piece_left_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	piece.left 65535
"""
		expected = group_empty()
		expected.basic_piece_left = Max.u16
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_piece_up_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	piece.up 65535
"""
		expected = group_empty()
		expected.basic_piece_up = Max.u16
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_piece_right_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	piece.right 65535
"""
		expected = group_empty()
		expected.basic_piece_right = Max.u16
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_piece_down_full(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	piece.down 65535
"""
		expected = group_empty()
		expected.basic_piece_down = Max.u16
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_flags_enable(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	flags.walkable 1
"""
		expected = group_empty()
		expected.flags |= CV5Flag.walkable
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

	def test_flags_enable_nop(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	flags.walkable 1
"""
		expected = group_full()
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_flags_disable(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	flags.walkable 0
"""
		expected = group_full()
		expected.flags &= ~CV5Flag.walkable
		
		tileset.import_group_settings(settings, [ID.basic_full])
		result = tileset.cv5.get_group(ID.basic_full)

		self.assertEqual(result, expected)

	def test_flags_disable_nop(self) -> None:
		tileset = test_tileset()
		settings = """
TileGroup:
	flags.walkable 0
"""
		expected = group_empty()
		
		tileset.import_group_settings(settings, [ID.basic_empty])
		result = tileset.cv5.get_group(ID.basic_empty)

		self.assertEqual(result, expected)

class Test_Import_DoodadGroup(unittest.TestCase):
	def test_all_empty(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	flags.walkable 0
	flags.unknown_0002 0
	flags.unwalkable 0
	flags.unknown_0008 0
	flags.has_doodad_cover 0
	flags.unknown_0020 0
	flags.creep 0
	flags.unbuildable 0
	flags.blocks_view 0
	flags.mid_ground 0
	flags.high_ground 0
	flags.occupied 0
	flags.has_overlay_sprite 0
	flags.has_overlay_unit 0
	flags.overlay_flipped 0
	flags.special_placeable 0
	overlay_id 0
	scr 0
	string_id 0
	unknown4 0
	dddata_id 0
	width 0
	height 0
	unknown8 0
"""
		expected = group_empty(True)
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_all_inc(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	flags.walkable 1
	flags.unknown_0002 0
	flags.unwalkable 0
	flags.unknown_0008 0
	flags.has_doodad_cover 0
	flags.unknown_0020 0
	flags.creep 0
	flags.unbuildable 0
	flags.blocks_view 0
	flags.mid_ground 0
	flags.high_ground 0
	flags.occupied 0
	flags.has_overlay_sprite 0
	flags.has_overlay_unit 0
	flags.overlay_flipped 0
	flags.special_placeable 0
	overlay_id 2
	scr 3
	string_id 4
	unknown4 5
	dddata_id 6
	width 7
	height 8
	unknown8 9
"""
		expected = group_inc(True)
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_all_full(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	flags.walkable 1
	flags.unknown_0002 1
	flags.unwalkable 1
	flags.unknown_0008 1
	flags.has_doodad_cover 1
	flags.unknown_0020 1
	flags.creep 1
	flags.unbuildable 1
	flags.blocks_view 1
	flags.mid_ground 1
	flags.high_ground 1
	flags.occupied 1
	flags.has_overlay_sprite 1
	flags.has_overlay_unit 1
	flags.overlay_flipped 1
	flags.special_placeable 1
	overlay_id 65535
	scr 65535
	string_id 65535
	unknown4 65535
	dddata_id 65535
	width 65535
	height 65535
	unknown8 65535
"""
		expected = group_full(True)
		
		tileset.import_group_settings(settings, [ID.doodad_empty])
		result = tileset.cv5.get_group(ID.doodad_empty)

		self.assertEqual(result, expected)

	def test_all_flags(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	flags.walkable 1
	flags.unknown_0002 0
	flags.unwalkable 1
	flags.unknown_0008 0
	flags.has_doodad_cover 1
	flags.unknown_0020 0
	flags.creep 1
	flags.unbuildable 0
	flags.blocks_view 1
	flags.mid_ground 0
	flags.high_ground 1
	flags.occupied 0
	flags.has_overlay_sprite 1
	flags.has_overlay_unit 0
	flags.overlay_flipped 1
	flags.special_placeable 0
	overlay_id 0
	scr 0
	string_id 0
	unknown4 0
	dddata_id 0
	width 0
	height 0
	unknown8 0
"""
		expected = group_flags(True)
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_flags_empty(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	flags.walkable 0
	flags.unknown_0002 0
	flags.unwalkable 0
	flags.unknown_0008 0
	flags.has_doodad_cover 0
	flags.unknown_0020 0
	flags.creep 0
	flags.unbuildable 0
	flags.blocks_view 0
	flags.mid_ground 0
	flags.high_ground 0
	flags.occupied 0
	flags.has_overlay_sprite 0
	flags.has_overlay_unit 0
	flags.overlay_flipped 0
	flags.special_placeable 0
"""
		expected = group_full(True)
		expected.flags = 0
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_overlay_id_empty(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	overlay_id 0
"""
		expected = group_full(True)
		expected.doodad_overlay_id = 0
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_scr_empty(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	scr 0
"""
		expected = group_full(True)
		expected.doodad_scr = 0
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_string_id_empty(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	string_id 0
"""
		expected = group_full(True)
		expected.doodad_string_id = 0
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_unknown4_empty(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	unknown4 0
"""
		expected = group_full(True)
		expected.doodad_unknown4 = 0
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_dddata_id_empty(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	dddata_id 0
"""
		expected = group_full(True)
		expected.doodad_dddata_id = 0
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_width_empty(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	width 0
"""
		expected = group_full(True)
		expected.doodad_width = 0
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_height_empty(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	height 0
"""
		expected = group_full(True)
		expected.doodad_height = 0
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_unknown8_empty(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	unknown8 0
"""
		expected = group_full(True)
		expected.doodad_unknown8 = 0
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_overlay_id_full(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	overlay_id 65535
"""
		expected = group_empty(True)
		expected.doodad_overlay_id = Max.u16
		
		tileset.import_group_settings(settings, [ID.doodad_empty])
		result = tileset.cv5.get_group(ID.doodad_empty)

		self.assertEqual(result, expected)

	def test_scr_full(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	scr 65535
"""
		expected = group_empty(True)
		expected.doodad_scr = Max.u16
		
		tileset.import_group_settings(settings, [ID.doodad_empty])
		result = tileset.cv5.get_group(ID.doodad_empty)

		self.assertEqual(result, expected)

	def test_string_id_full(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	string_id 65535
"""
		expected = group_empty(True)
		expected.doodad_string_id = Max.u16
		
		tileset.import_group_settings(settings, [ID.doodad_empty])
		result = tileset.cv5.get_group(ID.doodad_empty)

		self.assertEqual(result, expected)

	def test_unknown4_full(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	unknown4 65535
"""
		expected = group_empty(True)
		expected.doodad_unknown4 = Max.u16
		
		tileset.import_group_settings(settings, [ID.doodad_empty])
		result = tileset.cv5.get_group(ID.doodad_empty)

		self.assertEqual(result, expected)

	def test_dddata_id_full(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	dddata_id 65535
"""
		expected = group_empty(True)
		expected.doodad_dddata_id = Max.u16
		
		tileset.import_group_settings(settings, [ID.doodad_empty])
		result = tileset.cv5.get_group(ID.doodad_empty)

		self.assertEqual(result, expected)

	def test_width_full(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	width 65535
"""
		expected = group_empty(True)
		expected.doodad_width = Max.u16
		
		tileset.import_group_settings(settings, [ID.doodad_empty])
		result = tileset.cv5.get_group(ID.doodad_empty)

		self.assertEqual(result, expected)

	def test_height_full(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	height 65535
"""
		expected = group_empty(True)
		expected.doodad_height = Max.u16
		
		tileset.import_group_settings(settings, [ID.doodad_empty])
		result = tileset.cv5.get_group(ID.doodad_empty)

		self.assertEqual(result, expected)

	def test_unknown8_full(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	unknown8 65535
"""
		expected = group_empty(True)
		expected.doodad_unknown8 = Max.u16
		
		tileset.import_group_settings(settings, [ID.doodad_empty])
		result = tileset.cv5.get_group(ID.doodad_empty)

		self.assertEqual(result, expected)

	def test_flags_enable(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	flags.walkable 1
"""
		expected = group_empty(True)
		expected.flags |= CV5Flag.walkable
		
		tileset.import_group_settings(settings, [ID.doodad_empty])
		result = tileset.cv5.get_group(ID.doodad_empty)

		self.assertEqual(result, expected)

	def test_flags_enable_nop(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	flags.walkable 1
"""
		expected = group_full(True)
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_flags_disable(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	flags.walkable 0
"""
		expected = group_full(True)
		expected.flags &= ~CV5Flag.walkable
		
		tileset.import_group_settings(settings, [ID.doodad_full])
		result = tileset.cv5.get_group(ID.doodad_full)

		self.assertEqual(result, expected)

	def test_flags_disable_nop(self) -> None:
		tileset = test_tileset()
		settings = """
DoodadGroup:
	flags.walkable 0
"""
		expected = group_empty(True)
		
		tileset.import_group_settings(settings, [ID.doodad_empty])
		result = tileset.cv5.get_group(ID.doodad_empty)

		self.assertEqual(result, expected)

class Test_Import_Megatile(unittest.TestCase):
	def test_all_empty(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	mid_ground:
		0000
		0000
		0000
		0000
	high_ground:
		0000
		0000
		0000
		0000
	walkable:
		0000
		0000
		0000
		0000
	blocks_sight:
		0000
		0000
		0000
		0000
	ramp:
		0000
		0000
		0000
		0000
"""
		expected = mega_empty()

		tileset.import_megatile_settings(settings, [ID.mega_full])
		result = tileset.vf4.get_megatile(ID.mega_full)

		self.assertEqual(result, expected)

	def test_all_full(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	mid_ground:
		1111
		1111
		1111
		1111
	high_ground:
		1111
		1111
		1111
		1111
	walkable:
		1111
		1111
		1111
		1111
	blocks_sight:
		1111
		1111
		1111
		1111
	ramp:
		1111
		1111
		1111
		1111
"""
		expected = mega_full()

		tileset.import_megatile_settings(settings, [ID.mega_empty])
		result = tileset.vf4.get_megatile(ID.mega_empty)

		self.assertEqual(result, expected)

	def test_all_crosshatch(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	mid_ground:
		1010
		0101
		1010
		0101
	high_ground:
		1010
		0101
		1010
		0101
	walkable:
		1010
		0101
		1010
		0101
	blocks_sight:
		1010
		0101
		1010
		0101
	ramp:
		1010
		0101
		1010
		0101
"""
		expected = mega_crosshatch()

		tileset.import_megatile_settings(settings, [ID.mega_empty])
		result = tileset.vf4.get_megatile(ID.mega_empty)

		self.assertEqual(result, expected)

	def test_all_crosshatch2(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	mid_ground:
		0101
		1010
		0101
		1010
	high_ground:
		0101
		1010
		0101
		1010
	walkable:
		0101
		1010
		0101
		1010
	blocks_sight:
		0101
		1010
		0101
		1010
	ramp:
		0101
		1010
		0101
		1010
"""
		expected = mega_crosshatch2()

		tileset.import_megatile_settings(settings, [ID.mega_empty])
		result = tileset.vf4.get_megatile(ID.mega_empty)

		self.assertEqual(result, expected)

	def test_mid_ground_empty(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	mid_ground:
		0000
		0000
		0000
		0000
"""
		expected = mega_full()
		for n in range(16):
			expected.flags[n] &= ~VF4Flag.mid_ground

		tileset.import_megatile_settings(settings, [ID.mega_full])
		result = tileset.vf4.get_megatile(ID.mega_full)

		self.assertEqual(result, expected)

	def test_high_ground_empty(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	high_ground:
		0000
		0000
		0000
		0000
"""
		expected = mega_full()
		for n in range(16):
			expected.flags[n] &= ~VF4Flag.high_ground

		tileset.import_megatile_settings(settings, [ID.mega_full])
		result = tileset.vf4.get_megatile(ID.mega_full)

		self.assertEqual(result, expected)

	def test_walkable_empty(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	walkable:
		0000
		0000
		0000
		0000
"""
		expected = mega_full()
		for n in range(16):
			expected.flags[n] &= ~VF4Flag.walkable

		tileset.import_megatile_settings(settings, [ID.mega_full])
		result = tileset.vf4.get_megatile(ID.mega_full)

		self.assertEqual(result, expected)

	def test_blocks_sight_empty(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	blocks_sight:
		0000
		0000
		0000
		0000
"""
		expected = mega_full()
		for n in range(16):
			expected.flags[n] &= ~VF4Flag.blocks_sight

		tileset.import_megatile_settings(settings, [ID.mega_full])
		result = tileset.vf4.get_megatile(ID.mega_full)

		self.assertEqual(result, expected)

	def test_ramp_empty(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	ramp:
		0000
		0000
		0000
		0000
"""
		expected = mega_full()
		for n in range(16):
			expected.flags[n] &= ~VF4Flag.ramp

		tileset.import_megatile_settings(settings, [ID.mega_full])
		result = tileset.vf4.get_megatile(ID.mega_full)

		self.assertEqual(result, expected)

	def test_mid_ground_full(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	mid_ground:
		1111
		1111
		1111
		1111
"""
		expected = mega_empty()
		for n in range(16):
			expected.flags[n] |= VF4Flag.mid_ground

		tileset.import_megatile_settings(settings, [ID.mega_empty])
		result = tileset.vf4.get_megatile(ID.mega_empty)

		self.assertEqual(result, expected)

	def test_high_ground_full(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	high_ground:
		1111
		1111
		1111
		1111
"""
		expected = mega_empty()
		for n in range(16):
			expected.flags[n] |= VF4Flag.high_ground

		tileset.import_megatile_settings(settings, [ID.mega_empty])
		result = tileset.vf4.get_megatile(ID.mega_empty)

		self.assertEqual(result, expected)

	def test_walkable_full(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	walkable:
		1111
		1111
		1111
		1111
"""
		expected = mega_empty()
		for n in range(16):
			expected.flags[n] |= VF4Flag.walkable

		tileset.import_megatile_settings(settings, [ID.mega_empty])
		result = tileset.vf4.get_megatile(ID.mega_empty)

		self.assertEqual(result, expected)

	def test_blocks_sight_full(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	blocks_sight:
		1111
		1111
		1111
		1111
"""
		expected = mega_empty()
		for n in range(16):
			expected.flags[n] |= VF4Flag.blocks_sight

		tileset.import_megatile_settings(settings, [ID.mega_empty])
		result = tileset.vf4.get_megatile(ID.mega_empty)

		self.assertEqual(result, expected)

	def test_ramp_full(self) -> None:
		tileset = test_tileset()
		settings = """
MegaTile:
	ramp:
		1111
		1111
		1111
		1111
"""
		expected = mega_empty()
		for n in range(16):
			expected.flags[n] |= VF4Flag.ramp

		tileset.import_megatile_settings(settings, [ID.mega_empty])
		result = tileset.vf4.get_megatile(ID.mega_empty)

		self.assertEqual(result, expected)
