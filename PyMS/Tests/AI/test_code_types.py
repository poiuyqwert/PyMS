
from . import utils

from ...FileFormats.AIBIN.CodeHandlers import CodeTypes
from ...FileFormats.AIBIN.CodeHandlers import AISEIdleOrder
from ...FileFormats.AIBIN.CodeHandlers.AIParseContext import AIParseContext
from ...FileFormats.AIBIN.CodeHandlers.DataContext import DataContext

from ...FileFormats.DAT import UnitsDAT

from ...Utilities.PyMSError import PyMSError

import unittest

class Test_WordCodeType_compatible(unittest.TestCase):
	def test_compatible(self) -> None:
		word = CodeTypes.WordCodeType()
		cases = (
			(CodeTypes.WordCodeType(), 2),
			(CodeTypes.ByteCodeType(), 1),
			(CodeTypes.DWordCodeType(), 0),
		)
		for other_type, expected in cases:
			self.assertEqual(word.compatible(other_type), expected, f'word.compatible({type(other_type).__name__})')


class Test_BuildingCodeType_accepts(unittest.TestCase):
	def test_accepts_unit_family(self) -> None:
		building = CodeTypes.BuildingCodeType()
		self.assertTrue(building.accepts(CodeTypes.BuildingCodeType()))
		self.assertTrue(building.accepts(CodeTypes.UnitCodeType()))
		# A `military` variable resolves to a unit id and is accepted (see round-trip corpus).
		self.assertTrue(building.accepts(CodeTypes.MilitaryCodeType()))

	def test_rejects_non_unit_types(self) -> None:
		building = CodeTypes.BuildingCodeType()
		self.assertFalse(building.accepts(CodeTypes.WordCodeType()))
		self.assertFalse(building.accepts(CodeTypes.ByteCodeType()))
		self.assertFalse(building.accepts(CodeTypes.DWordCodeType()))


class Test_UnitCodeType_limits(unittest.TestCase):
	def test_get_limits_is_inclusive_max(self) -> None:
		parse_context = utils.parse_context('')
		unit = CodeTypes.UnitCodeType()
		min_id, max_id = unit.get_limits(parse_context)
		self.assertEqual(min_id, 0)
		self.assertEqual(max_id, UnitsDAT.FORMAT.entries - 1)

	def test_validate_boundary(self) -> None:
		parse_context = utils.parse_context('')
		unit = CodeTypes.UnitCodeType()
		# Highest valid id must not raise.
		unit.validate(UnitsDAT.FORMAT.entries - 1, parse_context)
		# `entry_count` itself is out of range and must raise (it didn't before the fix).
		with self.assertRaises(PyMSError):
			unit.validate(UnitsDAT.FORMAT.entries, parse_context)


class Test_Unit_validate_no_index_error(unittest.TestCase):
	def _parse_context(self) -> AIParseContext:
		data_context = DataContext(units_dat=UnitsDAT())
		return utils.parse_context('', data_context=data_context)

	def test_building_validate_does_not_index_out_of_range(self) -> None:
		parse_context = self._parse_context()
		building = CodeTypes.BuildingCodeType()
		# Must not raise IndexError (or any error) for an id beyond the (empty) dat.
		building.validate(0, parse_context)

	def test_military_validate_does_not_index_out_of_range(self) -> None:
		parse_context = self._parse_context()
		military = CodeTypes.MilitaryCodeType()
		military.validate(0, parse_context)


class Test_TileFlags_merge(unittest.TestCase):
	def test_merges_with_matching_tile_flags(self) -> None:
		a = AISEIdleOrder.TileFlags(False, 0x04)
		b = AISEIdleOrder.TileFlags(False, 0x08)
		self.assertTrue(a.merge(b))
		self.assertEqual(a.flags, 0x0C)

	def test_does_not_merge_across_without(self) -> None:
		a = AISEIdleOrder.TileFlags(False, 0x04)
		b = AISEIdleOrder.TileFlags(True, 0x08)
		self.assertFalse(a.merge(b))
		self.assertEqual(a.flags, 0x04)

	def test_does_not_merge_with_unit_flags(self) -> None:
		a = AISEIdleOrder.TileFlags(False, 0x04)
		other = AISEIdleOrder.UnitFlags(False, 0x08)
		# Before the fix this wrongly returned True and corrupted `flags`.
		self.assertFalse(a.merge(other))
		self.assertEqual(a.flags, 0x04)
