
from . import utils

from ...FileFormats.AIBIN.CodeHandlers import CodeTypes
from ...FileFormats.AIBIN.CodeHandlers.AIParseContext import AIParseContext
from ...FileFormats.AIBIN.CodeHandlers.DataContext import DataContext
from ...FileFormats.AIBIN.CodeHandlers.AIByteCodeCompiler import AIByteCodeCompiler
from ...FileFormats.AIBIN.CodeHandlers.AIDecompileContext import AIDecompileContext

from ...FileFormats.DAT import UnitsDAT, UpgradesDAT, TechDAT, DATUnit
from ...FileFormats.TBL import TBL

from ...Utilities.BytesScanner import BytesScanner
from ...Utilities.PyMSError import PyMSError

import unittest

def _units_dat(unit_id: int | None = None, **fields: int) -> UnitsDAT:
	units_dat = UnitsDAT()
	units_dat.new_file()
	if unit_id is not None:
		entry = units_dat.get_entry(unit_id)
		for name, value in fields.items():
			setattr(entry, name, value)
	return units_dat

def _units_parse_context(units_dat: UnitsDAT, spellcasters: list[int] | None = None) -> AIParseContext:
	parse_context = utils.parse_context('', data_context=DataContext(units_dat=units_dat))
	if spellcasters:
		parse_context.spellcasters = spellcasters
	return parse_context

def _stattxt_data_context(strings: list[str], **kwargs) -> DataContext:
	tbl = TBL()
	tbl.strings = strings
	return DataContext(stattxt_tbl=tbl, **kwargs)


class Test_ByteCodeType(unittest.TestCase):
	def test_parse_and_validate(self) -> None:
		byte = CodeTypes.ByteCodeType()
		self.assertEqual(byte.parse(utils.parse_context('0')), 0)
		self.assertEqual(byte.parse(utils.parse_context('255')), 255)

	def test_validate_rejects_out_of_range(self) -> None:
		byte = CodeTypes.ByteCodeType()
		with self.assertRaises(PyMSError):
			byte.parse(utils.parse_context('256'))

	def test_compile_decompile_round_trip(self) -> None:
		byte = CodeTypes.ByteCodeType()
		builder = AIByteCodeCompiler()
		byte.compile(7, builder)
		data = bytes(builder.data)
		self.assertEqual(data, b'\x07')
		self.assertEqual(byte.decompile(BytesScanner(data), AIDecompileContext(data)), 7)


class Test_WordCodeType(unittest.TestCase):
	def test_accepts(self) -> None:
		word = CodeTypes.WordCodeType()
		self.assertTrue(word.accepts(CodeTypes.WordCodeType()))
		self.assertTrue(word.accepts(CodeTypes.ByteCodeType()))
		self.assertFalse(word.accepts(CodeTypes.DWordCodeType()))

	def test_compatible(self) -> None:
		word = CodeTypes.WordCodeType()
		cases = (
			(CodeTypes.WordCodeType(), 2),
			(CodeTypes.ByteCodeType(), 1),
			(CodeTypes.DWordCodeType(), 0),
		)
		for other_type, expected in cases:
			self.assertEqual(word.compatible(other_type), expected, f'word.compatible({type(other_type).__name__})')

	def test_compile_decompile_round_trip(self) -> None:
		word = CodeTypes.WordCodeType()
		builder = AIByteCodeCompiler()
		word.compile(513, builder)
		data = bytes(builder.data)
		self.assertEqual(data, b'\x01\x02')
		self.assertEqual(word.decompile(BytesScanner(data), AIDecompileContext(data)), 513)


class Test_DWordCodeType(unittest.TestCase):
	def test_accepts(self) -> None:
		dword = CodeTypes.DWordCodeType()
		self.assertTrue(dword.accepts(CodeTypes.DWordCodeType()))
		self.assertTrue(dword.accepts(CodeTypes.WordCodeType()))
		self.assertTrue(dword.accepts(CodeTypes.ByteCodeType()))

	def test_compatible(self) -> None:
		dword = CodeTypes.DWordCodeType()
		cases = (
			(CodeTypes.DWordCodeType(), 3),
			(CodeTypes.WordCodeType(), 2),
			(CodeTypes.ByteCodeType(), 1),
			(CodeTypes.StringCodeType(), 0),
		)
		for other_type, expected in cases:
			self.assertEqual(dword.compatible(other_type), expected, f'dword.compatible({type(other_type).__name__})')

	def test_compile_decompile_round_trip(self) -> None:
		dword = CodeTypes.DWordCodeType()
		builder = AIByteCodeCompiler()
		dword.compile(16909060, builder)
		data = bytes(builder.data)
		self.assertEqual(data, b'\x04\x03\x02\x01')
		self.assertEqual(dword.decompile(BytesScanner(data), AIDecompileContext(data)), 16909060)


class Test_BlockCodeType_decompile(unittest.TestCase):
	def test_decompile_plain_address(self) -> None:
		data = b'\x05\x00'
		block = CodeTypes.BlockCodeType()
		self.assertEqual(block.decompile(BytesScanner(data), AIDecompileContext(data)), 5)

	def test_decompile_resolves_expanded_long_jump(self) -> None:
		data = b'\x05\x00'
		context = AIDecompileContext(data)
		context.aise_context.expanded = True
		context.aise_context.loaded_long_jumps = {5: 99}
		block = CodeTypes.BlockCodeType()
		self.assertEqual(block.decompile(BytesScanner(data), context), 99)

	def test_decompile_expanded_without_mapping(self) -> None:
		data = b'\x05\x00'
		context = AIDecompileContext(data)
		context.aise_context.expanded = True
		context.aise_context.loaded_long_jumps = {}
		block = CodeTypes.BlockCodeType()
		self.assertEqual(block.decompile(BytesScanner(data), context), 5)


class Test_UnitCodeType_accepts(unittest.TestCase):
	def test_accepts_unit_family(self) -> None:
		unit = CodeTypes.UnitCodeType()
		self.assertTrue(unit.accepts(CodeTypes.UnitCodeType()))
		self.assertTrue(unit.accepts(CodeTypes.BuildingCodeType()))
		self.assertTrue(unit.accepts(CodeTypes.MilitaryCodeType()))
		self.assertTrue(unit.accepts(CodeTypes.GGMilitaryCodeType()))
		self.assertTrue(unit.accepts(CodeTypes.AAMilitaryCodeType()))

	def test_rejects_non_unit_types(self) -> None:
		unit = CodeTypes.UnitCodeType()
		self.assertFalse(unit.accepts(CodeTypes.WordCodeType()))
		self.assertFalse(unit.accepts(CodeTypes.UpgradeCodeType()))

	def test_compatible_only_exact_unit(self) -> None:
		unit = CodeTypes.UnitCodeType()
		self.assertTrue(unit.compatible(CodeTypes.UnitCodeType()))
		# A `building` is a unit subtype so it is still compatible.
		self.assertTrue(unit.compatible(CodeTypes.BuildingCodeType()))
		self.assertFalse(unit.compatible(CodeTypes.WordCodeType()))


class Test_UnitCodeType_serialize(unittest.TestCase):
	def test_serialize_uses_unit_name(self) -> None:
		data_context = _stattxt_data_context(['Marine', 'Ghost', 'Vulture'])
		_, serialize_context = utils.serialize_context(data_context=data_context)
		unit = CodeTypes.UnitCodeType()
		self.assertEqual(unit.serialize(1, serialize_context), CodeTypes.StringCodeType.serialize_string('Ghost'))

	def test_serialize_falls_back_to_number(self) -> None:
		_, serialize_context = utils.serialize_context()
		unit = CodeTypes.UnitCodeType()
		self.assertEqual(unit.serialize(1, serialize_context), '1')


class Test_UnitCodeType_lex(unittest.TestCase):
	def test_lex_quoted_unit_name(self) -> None:
		data_context = _stattxt_data_context(['Marine', 'Ghost', 'Vulture'])
		parse_context = utils.parse_context('"Ghost"', data_context=data_context)
		unit = CodeTypes.UnitCodeType()
		self.assertEqual(unit.parse(parse_context), 1)

	def test_lex_open_string_unit_name_in_parens(self) -> None:
		data_context = _stattxt_data_context(['Marine', 'Ghost', 'Vulture'])
		parse_context = utils.parse_context('Ghost)', data_context=data_context)
		parse_context.command_in_parens = True
		unit = CodeTypes.UnitCodeType()
		self.assertEqual(unit.parse(parse_context), 1)

	def test_lex_falls_back_to_integer(self) -> None:
		data_context = _stattxt_data_context(['Marine', 'Ghost', 'Vulture'])
		parse_context = utils.parse_context('2', data_context=data_context)
		unit = CodeTypes.UnitCodeType()
		self.assertEqual(unit.parse(parse_context), 2)


class Test_UnitCodeType_limits(unittest.TestCase):
	def test_get_limits_is_inclusive_max(self) -> None:
		parse_context = utils.parse_context('')
		unit = CodeTypes.UnitCodeType()
		min_id, max_id = unit.get_limits(parse_context)
		self.assertEqual(min_id, 0)
		self.assertEqual(max_id, UnitsDAT.FORMAT.entries - 1)

	def test_get_limits_respects_expanded_units_setting(self) -> None:
		parse_context = utils.parse_context('')
		parse_context.settings.expanded_units = 400
		unit = CodeTypes.UnitCodeType()
		self.assertEqual(unit.get_limits(parse_context), (0, 399))

	def test_validate_boundary(self) -> None:
		parse_context = utils.parse_context('')
		unit = CodeTypes.UnitCodeType()
		# Highest valid id must not raise.
		unit.validate(UnitsDAT.FORMAT.entries - 1, parse_context)
		# `entry_count` itself is out of range and must raise (it didn't before the fix).
		with self.assertRaises(PyMSError):
			unit.validate(UnitsDAT.FORMAT.entries, parse_context)


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

	def test_compatible(self) -> None:
		building = CodeTypes.BuildingCodeType()
		cases = (
			(CodeTypes.BuildingCodeType(), 2),
			(CodeTypes.UnitCodeType(), 1),
			(CodeTypes.WordCodeType(), 0),
		)
		for other_type, expected in cases:
			self.assertEqual(building.compatible(other_type), expected, f'building.compatible({type(other_type).__name__})')


class Test_BuildingCodeType_validate(unittest.TestCase):
	def test_warns_for_non_building_unit(self) -> None:
		parse_context = _units_parse_context(_units_dat())
		CodeTypes.BuildingCodeType().validate(0, parse_context)
		self.assertEqual(len(parse_context.warnings), 1)

	def test_no_warning_when_building_flag_set(self) -> None:
		units_dat = _units_dat(5, special_ability_flags=DATUnit.SpecialAbilityFlag.building)
		parse_context = _units_parse_context(units_dat)
		CodeTypes.BuildingCodeType().validate(5, parse_context)
		self.assertEqual(len(parse_context.warnings), 0)

	def test_no_warning_when_resource_miner_flag_set(self) -> None:
		units_dat = _units_dat(5, special_ability_flags=DATUnit.SpecialAbilityFlag.resource_miner)
		parse_context = _units_parse_context(units_dat)
		CodeTypes.BuildingCodeType().validate(5, parse_context)
		self.assertEqual(len(parse_context.warnings), 0)

	def test_no_warning_for_overlord(self) -> None:
		parse_context = _units_parse_context(_units_dat())
		CodeTypes.BuildingCodeType().validate(42, parse_context)
		self.assertEqual(len(parse_context.warnings), 0)


class Test_MilitaryCodeType(unittest.TestCase):
	def test_accepts_military_family(self) -> None:
		military = CodeTypes.MilitaryCodeType()
		self.assertTrue(military.accepts(CodeTypes.MilitaryCodeType()))
		self.assertTrue(military.accepts(CodeTypes.GGMilitaryCodeType()))
		self.assertTrue(military.accepts(CodeTypes.AAMilitaryCodeType()))
		self.assertFalse(military.accepts(CodeTypes.UnitCodeType()))
		self.assertFalse(military.accepts(CodeTypes.BuildingCodeType()))

	def test_compatible(self) -> None:
		military = CodeTypes.MilitaryCodeType()
		cases = (
			(CodeTypes.MilitaryCodeType(), 2),
			(CodeTypes.UnitCodeType(), 1),
			(CodeTypes.WordCodeType(), 0),
		)
		for other_type, expected in cases:
			self.assertEqual(military.compatible(other_type), expected, f'military.compatible({type(other_type).__name__})')

	def test_warns_for_building_unit(self) -> None:
		units_dat = _units_dat(5, special_ability_flags=DATUnit.SpecialAbilityFlag.building)
		parse_context = _units_parse_context(units_dat)
		CodeTypes.MilitaryCodeType().validate(5, parse_context)
		self.assertEqual(len(parse_context.warnings), 1)

	def test_no_warning_for_non_building_unit(self) -> None:
		parse_context = _units_parse_context(_units_dat())
		CodeTypes.MilitaryCodeType().validate(0, parse_context)
		self.assertEqual(len(parse_context.warnings), 0)


class Test_GGMilitaryCodeType(unittest.TestCase):
	def test_accepts(self) -> None:
		gg = CodeTypes.GGMilitaryCodeType()
		self.assertTrue(gg.accepts(CodeTypes.GGMilitaryCodeType()))
		self.assertTrue(gg.accepts(CodeTypes.GAMilitaryCodeType()))
		self.assertTrue(gg.accepts(CodeTypes.MilitaryCodeType()))
		self.assertFalse(gg.accepts(CodeTypes.UnitCodeType()))

	def test_compatible(self) -> None:
		gg = CodeTypes.GGMilitaryCodeType()
		cases = (
			(CodeTypes.GGMilitaryCodeType(), 4),
			(CodeTypes.GAMilitaryCodeType(), 3),
			(CodeTypes.MilitaryCodeType(), 2),
			(CodeTypes.UnitCodeType(), 1),
			(CodeTypes.WordCodeType(), 0),
		)
		for other_type, expected in cases:
			self.assertEqual(gg.compatible(other_type), expected, f'gg.compatible({type(other_type).__name__})')

	def test_warns_for_unit_without_ground_weapon(self) -> None:
		units_dat = _units_dat(5, ground_weapon=130, attack_unit=0, subunit1=228)
		parse_context = _units_parse_context(units_dat)
		CodeTypes.GGMilitaryCodeType().validate(5, parse_context)
		self.assertEqual(len(parse_context.warnings), 1)

	def test_no_warning_for_spellcaster(self) -> None:
		units_dat = _units_dat(5, ground_weapon=130, attack_unit=0, subunit1=228)
		parse_context = _units_parse_context(units_dat, spellcasters=[5])
		CodeTypes.GGMilitaryCodeType().validate(5, parse_context)
		self.assertEqual(len(parse_context.warnings), 0)

	def test_no_warning_for_unit_with_ground_weapon(self) -> None:
		parse_context = _units_parse_context(_units_dat())
		CodeTypes.GGMilitaryCodeType().validate(0, parse_context)
		self.assertEqual(len(parse_context.warnings), 0)


class Test_GAMilitaryCodeType(unittest.TestCase):
	def test_accepts(self) -> None:
		ga = CodeTypes.GAMilitaryCodeType()
		self.assertTrue(ga.accepts(CodeTypes.GAMilitaryCodeType()))
		self.assertTrue(ga.accepts(CodeTypes.GGMilitaryCodeType()))
		self.assertTrue(ga.accepts(CodeTypes.MilitaryCodeType()))
		self.assertFalse(ga.accepts(CodeTypes.UnitCodeType()))

	def test_compatible(self) -> None:
		ga = CodeTypes.GAMilitaryCodeType()
		cases = (
			(CodeTypes.GAMilitaryCodeType(), 4),
			(CodeTypes.GGMilitaryCodeType(), 3),
			(CodeTypes.MilitaryCodeType(), 2),
			(CodeTypes.UnitCodeType(), 1),
			(CodeTypes.WordCodeType(), 0),
		)
		for other_type, expected in cases:
			self.assertEqual(ga.compatible(other_type), expected, f'ga.compatible({type(other_type).__name__})')

	def test_warns_for_unit_without_ground_weapon(self) -> None:
		units_dat = _units_dat(5, ground_weapon=130, attack_unit=0, subunit1=228)
		parse_context = _units_parse_context(units_dat)
		CodeTypes.GAMilitaryCodeType().validate(5, parse_context)
		self.assertEqual(len(parse_context.warnings), 1)


class Test_AGMilitaryCodeType(unittest.TestCase):
	def test_accepts(self) -> None:
		ag = CodeTypes.AGMilitaryCodeType()
		self.assertTrue(ag.accepts(CodeTypes.AGMilitaryCodeType()))
		self.assertTrue(ag.accepts(CodeTypes.AAMilitaryCodeType()))
		self.assertTrue(ag.accepts(CodeTypes.MilitaryCodeType()))
		self.assertFalse(ag.accepts(CodeTypes.UnitCodeType()))

	def test_compatible(self) -> None:
		ag = CodeTypes.AGMilitaryCodeType()
		cases = (
			(CodeTypes.AGMilitaryCodeType(), 4),
			(CodeTypes.AAMilitaryCodeType(), 3),
			(CodeTypes.MilitaryCodeType(), 2),
			(CodeTypes.UnitCodeType(), 1),
			(CodeTypes.WordCodeType(), 0),
		)
		for other_type, expected in cases:
			self.assertEqual(ag.compatible(other_type), expected, f'ag.compatible({type(other_type).__name__})')

	def test_warns_for_unit_without_air_weapon(self) -> None:
		units_dat = _units_dat(5, air_weapon=130, attack_unit=53, subunit1=228)
		parse_context = _units_parse_context(units_dat)
		CodeTypes.AGMilitaryCodeType().validate(5, parse_context)
		self.assertEqual(len(parse_context.warnings), 1)


class Test_AAMilitaryCodeType(unittest.TestCase):
	def test_accepts(self) -> None:
		aa = CodeTypes.AAMilitaryCodeType()
		self.assertTrue(aa.accepts(CodeTypes.AAMilitaryCodeType()))
		self.assertTrue(aa.accepts(CodeTypes.AGMilitaryCodeType()))
		self.assertTrue(aa.accepts(CodeTypes.MilitaryCodeType()))
		self.assertFalse(aa.accepts(CodeTypes.UnitCodeType()))

	def test_compatible(self) -> None:
		aa = CodeTypes.AAMilitaryCodeType()
		cases = (
			(CodeTypes.AAMilitaryCodeType(), 4),
			(CodeTypes.AGMilitaryCodeType(), 3),
			(CodeTypes.MilitaryCodeType(), 2),
			(CodeTypes.UnitCodeType(), 1),
			(CodeTypes.WordCodeType(), 0),
		)
		for other_type, expected in cases:
			self.assertEqual(aa.compatible(other_type), expected, f'aa.compatible({type(other_type).__name__})')

	def test_warns_for_unit_without_air_weapon(self) -> None:
		units_dat = _units_dat(5, air_weapon=130, attack_unit=53, subunit1=228)
		parse_context = _units_parse_context(units_dat)
		CodeTypes.AAMilitaryCodeType().validate(5, parse_context)
		self.assertEqual(len(parse_context.warnings), 1)

	def test_no_warning_for_spellcaster(self) -> None:
		units_dat = _units_dat(5, air_weapon=130, attack_unit=53, subunit1=228)
		parse_context = _units_parse_context(units_dat, spellcasters=[5])
		CodeTypes.AAMilitaryCodeType().validate(5, parse_context)
		self.assertEqual(len(parse_context.warnings), 0)


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


class Test_UpgradeCodeType(unittest.TestCase):
	def test_accepts_and_compatible(self) -> None:
		upgrade = CodeTypes.UpgradeCodeType()
		self.assertTrue(upgrade.accepts(CodeTypes.UpgradeCodeType()))
		self.assertFalse(upgrade.accepts(CodeTypes.UnitCodeType()))
		self.assertTrue(upgrade.compatible(CodeTypes.UpgradeCodeType()))
		self.assertFalse(upgrade.compatible(CodeTypes.TechnologyCodeType()))

	def test_serialize_uses_upgrade_name(self) -> None:
		upgrades_dat = UpgradesDAT()
		upgrades_dat.new_file()
		upgrades_dat.get_entry(3).label = 2  # stat_txt index 1 -> 'One'
		data_context = _stattxt_data_context(['Zero', 'One', 'Two'], upgrades_dat=upgrades_dat)
		_, serialize_context = utils.serialize_context(data_context=data_context)
		self.assertEqual(CodeTypes.UpgradeCodeType().serialize(3, serialize_context), CodeTypes.StringCodeType.serialize_string('One'))

	def test_serialize_falls_back_to_number(self) -> None:
		_, serialize_context = utils.serialize_context()
		self.assertEqual(CodeTypes.UpgradeCodeType().serialize(7, serialize_context), '7')

	def test_lex_quoted_upgrade_name(self) -> None:
		upgrades_dat = UpgradesDAT()
		upgrades_dat.new_file()
		upgrades_dat.get_entry(3).label = 2
		data_context = _stattxt_data_context(['Zero', 'One', 'Two'], upgrades_dat=upgrades_dat)
		parse_context = utils.parse_context('"One"', data_context=data_context)
		self.assertEqual(CodeTypes.UpgradeCodeType().parse(parse_context), 3)

	def test_validate_rejects_out_of_range(self) -> None:
		with self.assertRaises(PyMSError):
			CodeTypes.UpgradeCodeType().validate(99999, utils.parse_context(''))

	def test_get_limits(self) -> None:
		self.assertEqual(CodeTypes.UpgradeCodeType().get_limits(utils.parse_context('')), (0, UpgradesDAT.FORMAT.entries))
		parse_context = utils.parse_context('')
		parse_context.settings.expanded_upgrades = 100
		self.assertEqual(CodeTypes.UpgradeCodeType().get_limits(parse_context), (0, 100))


class Test_TechnologyCodeType(unittest.TestCase):
	def test_accepts_and_compatible(self) -> None:
		technology = CodeTypes.TechnologyCodeType()
		self.assertTrue(technology.accepts(CodeTypes.TechnologyCodeType()))
		self.assertFalse(technology.accepts(CodeTypes.UpgradeCodeType()))
		self.assertTrue(technology.compatible(CodeTypes.TechnologyCodeType()))
		self.assertFalse(technology.compatible(CodeTypes.UpgradeCodeType()))

	def test_serialize_uses_technology_name(self) -> None:
		techdata_dat = TechDAT()
		techdata_dat.new_file()
		techdata_dat.get_entry(4).label = 3  # stat_txt index 2 -> 'Two'
		data_context = _stattxt_data_context(['Zero', 'One', 'Two'], techdata_dat=techdata_dat)
		_, serialize_context = utils.serialize_context(data_context=data_context)
		self.assertEqual(CodeTypes.TechnologyCodeType().serialize(4, serialize_context), CodeTypes.StringCodeType.serialize_string('Two'))

	def test_serialize_falls_back_to_number(self) -> None:
		_, serialize_context = utils.serialize_context()
		self.assertEqual(CodeTypes.TechnologyCodeType().serialize(5, serialize_context), '5')

	def test_validate_rejects_out_of_range(self) -> None:
		with self.assertRaises(PyMSError):
			CodeTypes.TechnologyCodeType().validate(99999, utils.parse_context(''))

	def test_get_limits(self) -> None:
		self.assertEqual(CodeTypes.TechnologyCodeType().get_limits(utils.parse_context('')), (0, TechDAT.FORMAT.entries))
		parse_context = utils.parse_context('')
		parse_context.settings.expanded_tech = 80
		self.assertEqual(CodeTypes.TechnologyCodeType().get_limits(parse_context), (0, 80))


class Test_StringCodeType(unittest.TestCase):
	def test_accepts_and_compatible(self) -> None:
		string = CodeTypes.StringCodeType()
		self.assertTrue(string.accepts(CodeTypes.StringCodeType()))
		self.assertFalse(string.accepts(CodeTypes.ByteCodeType()))
		self.assertTrue(string.compatible(CodeTypes.StringCodeType()))
		self.assertFalse(string.compatible(CodeTypes.ByteCodeType()))

	def test_serialize(self) -> None:
		_, serialize_context = utils.serialize_context()
		self.assertEqual(CodeTypes.StringCodeType().serialize('Hello', serialize_context), "'Hello'")

	def test_parse(self) -> None:
		self.assertEqual(CodeTypes.StringCodeType().parse(utils.parse_context('"Hello"')), 'Hello')


class Test_CompareCodeType(unittest.TestCase):
	def test_accepts_and_compatible(self) -> None:
		compare = CodeTypes.CompareCodeType()
		self.assertTrue(compare.accepts(CodeTypes.CompareCodeType()))
		self.assertFalse(compare.accepts(CodeTypes.ByteCodeType()))
		self.assertTrue(compare.compatible(CodeTypes.CompareCodeType()))
		self.assertFalse(compare.compatible(CodeTypes.ByteCodeType()))

	def test_parse(self) -> None:
		compare = CodeTypes.CompareCodeType()
		self.assertEqual(compare.parse(utils.parse_context('GreaterThan')), 1)
		self.assertEqual(compare.parse(utils.parse_context('LessThan')), 0)

	def test_serialize(self) -> None:
		_, serialize_context = utils.serialize_context()
		compare = CodeTypes.CompareCodeType()
		self.assertEqual(compare.serialize(1, serialize_context), 'GreaterThan')
		self.assertEqual(compare.serialize(0, serialize_context), 'LessThan')

	def test_parse_rejects_unknown_case(self) -> None:
		with self.assertRaises(PyMSError):
			CodeTypes.CompareCodeType().parse(utils.parse_context('Nope'))


class Test_TBLStringCodeType(unittest.TestCase):
	def test_comment_returns_stattxt_string(self) -> None:
		data_context = _stattxt_data_context(['Zero\x00', 'One\x00', 'Two\x00'])
		_, serialize_context = utils.serialize_context(data_context=data_context)
		self.assertEqual(CodeTypes.TBLStringCodeType().comment(1, serialize_context), 'One')

	def test_comment_out_of_range_is_none(self) -> None:
		data_context = _stattxt_data_context(['Zero\x00'])
		_, serialize_context = utils.serialize_context(data_context=data_context)
		self.assertIsNone(CodeTypes.TBLStringCodeType().comment(99, serialize_context))

	def test_comment_without_tbl_is_none(self) -> None:
		_, serialize_context = utils.serialize_context()
		self.assertIsNone(CodeTypes.TBLStringCodeType().comment(1, serialize_context))

	def test_compile_decompile_round_trip(self) -> None:
		tbl_string = CodeTypes.TBLStringCodeType()
		builder = AIByteCodeCompiler()
		tbl_string.compile(70000, builder)
		data = bytes(builder.data)
		self.assertEqual(data, b'\x70\x11\x01\x00')
		self.assertEqual(tbl_string.decompile(BytesScanner(data), AIDecompileContext(data)), 70000)


class Test_BinFileCodeType(unittest.TestCase):
	def test_parse(self) -> None:
		bin_file = CodeTypes.BinFileCodeType()
		self.assertEqual(bin_file.parse(utils.parse_context('aiscript')), 0)
		self.assertEqual(bin_file.parse(utils.parse_context('bwscript')), 1)

	def test_serialize(self) -> None:
		_, serialize_context = utils.serialize_context()
		bin_file = CodeTypes.BinFileCodeType()
		self.assertEqual(bin_file.serialize(0, serialize_context), 'aiscript')
		self.assertEqual(bin_file.serialize(1, serialize_context), 'bwscript')

	def test_parse_rejects_unknown_case(self) -> None:
		with self.assertRaises(PyMSError):
			CodeTypes.BinFileCodeType().parse(utils.parse_context('nope'))


class Test_BoolCodeType(unittest.TestCase):
	def test_parse(self) -> None:
		bool_type = CodeTypes.BoolCodeType()
		self.assertTrue(bool_type.parse(utils.parse_context('true')))
		self.assertFalse(bool_type.parse(utils.parse_context('false')))
		self.assertTrue(bool_type.parse(utils.parse_context('1')))
		self.assertFalse(bool_type.parse(utils.parse_context('0')))

	def test_serialize(self) -> None:
		_, serialize_context = utils.serialize_context()
		bool_type = CodeTypes.BoolCodeType()
		self.assertEqual(bool_type.serialize(True, serialize_context), 'True')
		self.assertEqual(bool_type.serialize(False, serialize_context), 'False')

	def test_keywords(self) -> None:
		self.assertEqual(CodeTypes.BoolCodeType().keywords(), ('true', 'false'))


class Test_DataContext_stattxt_string(unittest.TestCase):
	def test_valid_id_returns_string(self) -> None:
		data_context = _stattxt_data_context(['Marine\x00', 'Ghost\x00', 'Vulture\x00'])
		self.assertEqual(data_context.stattxt_string(0), 'Marine')
		self.assertEqual(data_context.stattxt_string(2), 'Vulture')

	def test_out_of_upper_bound_returns_none(self) -> None:
		data_context = _stattxt_data_context(['Marine\x00'])
		self.assertIsNone(data_context.stattxt_string(1))

	def test_negative_id_returns_none(self) -> None:
		data_context = _stattxt_data_context(['Marine\x00', 'Ghost\x00', 'Vulture\x00'])
		self.assertIsNone(data_context.stattxt_string(-1))

	def test_no_tbl_returns_none(self) -> None:
		self.assertIsNone(DataContext().stattxt_string(0))
