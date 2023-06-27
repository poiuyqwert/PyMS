
from .utils import test_tileset, ID

from ...FileFormats.Tileset.Serialize import TileGroupField, DoodadGroupField, MegatileField

from ...Utilities import IO

import unittest

class Test_Export_TileGroup(unittest.TestCase):
	def test_all_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
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

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty]))

		self.assertEqual(result.strip(), expected.strip())

	def test_all_inc(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_inc}
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

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_inc]))

		self.assertEqual(result.strip(), expected.strip())

	def test_all_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
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

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full]))

		self.assertEqual(result.strip(), expected.strip())

	def test_all_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
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

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags]))

		self.assertEqual(result.strip(), expected.strip())

	def test_type_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	type 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], {TileGroupField.type: True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
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

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:True}))

		self.assertEqual(result.strip(), expected.strip())
	
	def test_flags_walkable_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.walkable 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.walkable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0002_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.unknown_0002 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.unknown_0002:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unwalkable_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.unwalkable 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.unwalkable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0008_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.unknown_0008 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.unknown_0008:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_has_doodad_cover_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.has_doodad_cover 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.has_doodad_cover:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0020_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.unknown_0020 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.unknown_0020:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.creep 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.creep:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unbuildable_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.unbuildable 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.unbuildable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_blocks_view_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.blocks_view 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.blocks_view:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_mid_ground_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.mid_ground 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.mid_ground:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_high_ground_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.high_ground 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.high_ground:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_occupied_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.occupied 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.occupied:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_receding_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.creep_receding 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.creep_receding:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_cliff_edge_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.cliff_edge 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.cliff_edge:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_temp_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.creep_temp 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.creep_temp:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_special_placeable_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	flags.special_placeable 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], fields={TileGroupField.flags:{TileGroupField.Flag.special_placeable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_edge_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	edge.left 0
	edge.up 0
	edge.right 0
	edge.down 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], {TileGroupField.edge: True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_piece_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_empty}
TileGroup:
	piece.left 0
	piece.up 0
	piece.right 0
	piece.down 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_empty], {TileGroupField.piece: True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_type_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	type 65535
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], {TileGroupField.type: True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
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

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:True}))

		self.assertEqual(result.strip(), expected.strip())
	
	def test_flags_walkable_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.walkable 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.walkable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0002_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.unknown_0002 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.unknown_0002:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unwalkable_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.unwalkable 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.unwalkable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0008_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.unknown_0008 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.unknown_0008:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_has_doodad_cover_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.has_doodad_cover 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.has_doodad_cover:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0020_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.unknown_0020 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.unknown_0020:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.creep 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.creep:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unbuildable_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.unbuildable 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.unbuildable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_blocks_view_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.blocks_view 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.blocks_view:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_mid_ground_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.mid_ground 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.mid_ground:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_high_ground_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.high_ground 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.high_ground:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_occupied_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.occupied 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.occupied:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_receding_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.creep_receding 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.creep_receding:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_cliff_edge_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.cliff_edge 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.cliff_edge:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_temp_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.creep_temp 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.creep_temp:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_special_placeable_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	flags.special_placeable 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], fields={TileGroupField.flags:{TileGroupField.Flag.special_placeable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_edge_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	edge.left 65535
	edge.up 65535
	edge.right 65535
	edge.down 65535
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], {TileGroupField.edge: True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_piece_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_full}
TileGroup:
	piece.left 65535
	piece.up 65535
	piece.right 65535
	piece.down 65535
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_full], {TileGroupField.piece: True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
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
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:True}))

		self.assertEqual(result.strip(), expected.strip())
	
	def test_flags_walkable_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.walkable 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.walkable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0002_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.unknown_0002 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.unknown_0002:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unwalkable_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.unwalkable 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.unwalkable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0008_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.unknown_0008 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.unknown_0008:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_has_doodad_cover_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.has_doodad_cover 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.has_doodad_cover:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0020_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.unknown_0020 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.unknown_0020:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.creep 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.creep:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unbuildable_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.unbuildable 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.unbuildable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_blocks_view_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.blocks_view 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.blocks_view:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_mid_ground_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.mid_ground 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.mid_ground:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_high_ground_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.high_ground 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.high_ground:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_occupied_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.occupied 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.occupied:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_receding_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.creep_receding 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.creep_receding:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_cliff_edge_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.cliff_edge 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.cliff_edge:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_temp_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.creep_temp 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.creep_temp:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_special_placeable_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of TileGroup {ID.basic_flags}
TileGroup:
	flags.special_placeable 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.basic_flags], fields={TileGroupField.flags:{TileGroupField.Flag.special_placeable:True}}))

		self.assertEqual(result.strip(), expected.strip())


class Test_Export_DoodadGroup(unittest.TestCase):
	def test_all_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
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

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty]))

		self.assertEqual(result.strip(), expected.strip())

	def test_all_inc(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_inc}
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

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_inc]))

		self.assertEqual(result.strip(), expected.strip())

	def test_all_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
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

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full]))

		self.assertEqual(result.strip(), expected.strip())

	def test_all_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
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

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags]))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
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

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:True}))

		self.assertEqual(result.strip(), expected.strip())
	
	def test_flags_walkable_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.walkable 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.walkable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0002_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.unknown_0002 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unknown_0002:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unwalkable_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.unwalkable 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unwalkable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0008_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.unknown_0008 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unknown_0008:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_has_doodad_cover_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.has_doodad_cover 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.has_doodad_cover:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0020_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.unknown_0020 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unknown_0020:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.creep 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.creep:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unbuildable_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.unbuildable 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unbuildable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_blocks_view_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.blocks_view 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.blocks_view:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_mid_ground_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.mid_ground 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.mid_ground:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_high_ground_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.high_ground 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.high_ground:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_occupied_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.occupied 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.occupied:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_receding_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.has_overlay_sprite 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.has_overlay_sprite:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_cliff_edge_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.has_overlay_unit 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.has_overlay_unit:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_temp_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.overlay_flipped 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.overlay_flipped:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_special_placeable_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	flags.special_placeable 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.special_placeable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_overlay_id_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	overlay_id 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.overlay_id:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_scr_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	scr 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.scr:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_string_id_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	string_id 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.string_id:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_unknown4_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	unknown4 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.unknown4:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_dddata_id_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	dddata_id 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.dddata_id:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_width_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	width 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.width:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_height_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	height 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.height:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_unknown8_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_empty}
DoodadGroup:
	unknown8 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_empty], fields={DoodadGroupField.unknown8:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
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
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:True}))

		self.assertEqual(result.strip(), expected.strip())
	
	def test_flags_walkable_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.walkable 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.walkable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0002_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.unknown_0002 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unknown_0002:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unwalkable_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.unwalkable 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unwalkable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0008_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.unknown_0008 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unknown_0008:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_has_doodad_cover_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.has_doodad_cover 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.has_doodad_cover:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0020_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.unknown_0020 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unknown_0020:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.creep 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.creep:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unbuildable_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.unbuildable 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unbuildable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_blocks_view_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.blocks_view 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.blocks_view:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_mid_ground_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.mid_ground 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.mid_ground:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_high_ground_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.high_ground 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.high_ground:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_occupied_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.occupied 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.occupied:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_receding_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.has_overlay_sprite 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.has_overlay_sprite:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_cliff_edge_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.has_overlay_unit 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.has_overlay_unit:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_temp_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.overlay_flipped 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.overlay_flipped:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_special_placeable_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	flags.special_placeable 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.special_placeable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_overlay_id_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	overlay_id 65535
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.overlay_id:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_scr_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	scr 65535
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.scr:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_string_id_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	string_id 65535
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.string_id:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_unknown4_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	unknown4 65535
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.unknown4:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_dddata_id_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	dddata_id 65535
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.dddata_id:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_width_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	width 65535
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.width:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_height_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	height 65535
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.height:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_unknown8_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_full}
DoodadGroup:
	unknown8 65535
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_full], fields={DoodadGroupField.unknown8:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
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
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:True}))

		self.assertEqual(result.strip(), expected.strip())
	
	def test_flags_walkable_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.walkable 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.walkable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0002_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.unknown_0002 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unknown_0002:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unwalkable_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.unwalkable 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unwalkable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0008_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.unknown_0008 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unknown_0008:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_has_doodad_cover_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.has_doodad_cover 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.has_doodad_cover:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unknown_0020_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.unknown_0020 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unknown_0020:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.creep 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.creep:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_unbuildable_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.unbuildable 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.unbuildable:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_blocks_view_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.blocks_view 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.blocks_view:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_mid_ground_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.mid_ground 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.mid_ground:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_high_ground_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.high_ground 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.high_ground:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_occupied_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.occupied 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.occupied:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_receding_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.has_overlay_sprite 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.has_overlay_sprite:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_cliff_edge_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.has_overlay_unit 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.has_overlay_unit:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_creep_temp_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.overlay_flipped 1
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.overlay_flipped:True}}))

		self.assertEqual(result.strip(), expected.strip())

	def test_flags_special_placeable_flags(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of DoodadGroup {ID.doodad_flags}
DoodadGroup:
	flags.special_placeable 0
"""

		result = IO.output_to_text(lambda s: tileset.export_group_settings(s, [ID.doodad_flags], fields={DoodadGroupField.flags:{DoodadGroupField.Flag.special_placeable:True}}))

		self.assertEqual(result.strip(), expected.strip())

class Test_Export_Megatile(unittest.TestCase):
	def test_all_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_empty}
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

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_empty]))

		self.assertEqual(result.strip(), expected.strip())

	def test_all_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_full}
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

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_full]))

		self.assertEqual(result.strip(), expected.strip())

	def test_all_crosshatch(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_crosshatch}
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

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_crosshatch]))

		self.assertEqual(result.strip(), expected.strip())

	def test_all_crosshatch2(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_crosshatch2}
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

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_crosshatch2]))

		self.assertEqual(result.strip(), expected.strip())

	def test_mid_ground_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_empty}
MegaTile:
	mid_ground:
		0000
		0000
		0000
		0000
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_empty], fields={MegatileField.mid_ground:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_high_ground_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_empty}
MegaTile:
	high_ground:
		0000
		0000
		0000
		0000
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_empty], fields={MegatileField.high_ground:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_walkable_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_empty}
MegaTile:
	walkable:
		0000
		0000
		0000
		0000
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_empty], fields={MegatileField.walkable:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_blocks_sight_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_empty}
MegaTile:
	blocks_sight:
		0000
		0000
		0000
		0000
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_empty], fields={MegatileField.blocks_sight:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_ramp_empty(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_empty}
MegaTile:
	ramp:
		0000
		0000
		0000
		0000
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_empty], fields={MegatileField.ramp:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_mid_ground_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_full}
MegaTile:
	mid_ground:
		1111
		1111
		1111
		1111
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_full], fields={MegatileField.mid_ground:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_high_ground_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_full}
MegaTile:
	high_ground:
		1111
		1111
		1111
		1111
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_full], fields={MegatileField.high_ground:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_walkable_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_full}
MegaTile:
	walkable:
		1111
		1111
		1111
		1111
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_full], fields={MegatileField.walkable:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_blocks_sight_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_full}
MegaTile:
	blocks_sight:
		1111
		1111
		1111
		1111
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_full], fields={MegatileField.blocks_sight:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_ramp_full(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_full}
MegaTile:
	ramp:
		1111
		1111
		1111
		1111
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_full], fields={MegatileField.ramp:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_mid_ground_crosshatch(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_crosshatch}
MegaTile:
	mid_ground:
		1010
		0101
		1010
		0101
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_crosshatch], fields={MegatileField.mid_ground:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_high_ground_crosshatch(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_crosshatch}
MegaTile:
	high_ground:
		1010
		0101
		1010
		0101
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_crosshatch], fields={MegatileField.high_ground:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_walkable_crosshatch(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_crosshatch}
MegaTile:
	walkable:
		1010
		0101
		1010
		0101
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_crosshatch], fields={MegatileField.walkable:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_blocks_sight_crosshatch(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_crosshatch}
MegaTile:
	blocks_sight:
		1010
		0101
		1010
		0101
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_crosshatch], fields={MegatileField.blocks_sight:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_ramp_crosshatch(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_crosshatch}
MegaTile:
	ramp:
		1010
		0101
		1010
		0101
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_crosshatch], fields={MegatileField.ramp:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_mid_ground_crosshatch2(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_crosshatch2}
MegaTile:
	mid_ground:
		0101
		1010
		0101
		1010
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_crosshatch2], fields={MegatileField.mid_ground:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_high_ground_crosshatch2(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_crosshatch2}
MegaTile:
	high_ground:
		0101
		1010
		0101
		1010
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_crosshatch2], fields={MegatileField.high_ground:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_walkable_crosshatch2(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_crosshatch2}
MegaTile:
	walkable:
		0101
		1010
		0101
		1010
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_crosshatch2], fields={MegatileField.walkable:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_blocks_sight_crosshatch2(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_crosshatch2}
MegaTile:
	blocks_sight:
		0101
		1010
		0101
		1010
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_crosshatch2], fields={MegatileField.blocks_sight:True}))

		self.assertEqual(result.strip(), expected.strip())

	def test_ramp_crosshatch2(self) -> None:
		tileset = test_tileset()
		expected = f"""
# Export of MegaTile {ID.mega_crosshatch2}
MegaTile:
	ramp:
		0101
		1010
		0101
		1010
"""

		result = IO.output_to_text(lambda s: tileset.export_megatile_settings(s, [ID.mega_crosshatch2], fields={MegatileField.ramp:True}))

		self.assertEqual(result.strip(), expected.strip())
