
from ...FileFormats.TRG import Parameters
from ...FileFormats.TRG import Constants
from ...FileFormats.TRG.Condition import Condition
from ...FileFormats.TRG.Action import Action
from ...FileFormats.TRG.TRG import TRG
from ...FileFormats import TBL
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning

import unittest


def _trg_with_units(*names: str) -> TRG:
	tbl = TBL.TBL()
	tbl.strings = list(names)
	return TRG(stat_txt=tbl)


TRG_EMPTY = TRG()


class Test_NumberParameter(unittest.TestCase):
	PARAM = Parameters.NumberParameter()

	def test_decompile(self) -> None:
		condition = Condition()
		condition.number = 42
		self.assertEqual(self.PARAM.condition_decompile(condition, TRG_EMPTY), '42')

	def test_compile_bounds(self) -> None:
		condition = Condition()
		self.PARAM.condition_compile('4294967295', condition, TRG_EMPTY)
		self.assertEqual(condition.number, 4294967295)

	def test_compile_out_of_range_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.PARAM.condition_compile('4294967296', Condition(), TRG_EMPTY)

	def test_compile_non_numeric_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.PARAM.condition_compile('abc', Condition(), TRG_EMPTY)


class Test_PlayerParameter(unittest.TestCase):
	PARAM = Parameters.PlayerParameter()

	def test_decompile_keyword(self) -> None:
		self.assertEqual(self.PARAM.decompile(Constants.PlayerGroup.all_players), 'All Players')

	def test_decompile_numeric_when_unknown(self) -> None:
		self.assertEqual(self.PARAM.decompile(200), '200')

	def test_compile_keyword(self) -> None:
		self.assertEqual(self.PARAM.compile('Force 1'), Constants.PlayerGroup.force_1)

	def test_compile_player_prefix(self) -> None:
		self.assertEqual(self.PARAM.compile('Player 1'), 0)

	def test_compile_numeric(self) -> None:
		self.assertEqual(self.PARAM.compile('200'), 200)

	def test_compile_out_of_range_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.PARAM.compile('256')


class Test_ComparisonParameter(unittest.TestCase):
	PARAM = Parameters.ComparisonParameter()

	def test_decompile_keyword(self) -> None:
		condition = Condition()
		condition.comparison = Constants.Comparison.at_least
		self.assertEqual(self.PARAM.condition_decompile(condition, TRG_EMPTY), 'At Least')

	def test_compile_keyword(self) -> None:
		condition = Condition()
		self.assertIsNone(self.PARAM.condition_compile('Exactly', condition, TRG_EMPTY))
		self.assertEqual(condition.comparison, Constants.Comparison.exactly)

	def test_compile_numeric_warns(self) -> None:
		condition = Condition()
		warning = self.PARAM.condition_compile('5', condition, TRG_EMPTY)
		self.assertIsInstance(warning, PyMSWarning)
		self.assertEqual(condition.comparison, 5)

	def test_compile_invalid_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.PARAM.condition_compile('Maybe', Condition(), TRG_EMPTY)


class Test_UnitTypeParameter(unittest.TestCase):
	PARAM = Parameters.UnitTypeParameter()

	def test_unit_name_single_component(self) -> None:
		self.assertEqual(Parameters.UnitTypeParameter.unit_name('Marine\x00*\x00'), 'Marine')

	def test_unit_name_two_components(self) -> None:
		self.assertEqual(Parameters.UnitTypeParameter.unit_name('Terran Marine\x00Gauss Rifle\x00'), 'Terran Marine<0>Gauss Rifle')

	def test_keyword_decompile(self) -> None:
		condition = Condition()
		condition.unit_type = Constants.UnitType.men
		self.assertEqual(self.PARAM.condition_decompile(condition, TRG_EMPTY), 'Men')

	def test_decompile_resolves_unit_name(self) -> None:
		trg = _trg_with_units('Marine\x00*\x00')
		condition = Condition()
		condition.unit_type = 0
		self.assertEqual(self.PARAM.condition_decompile(condition, trg), 'Marine')

	def test_compile_unit_name(self) -> None:
		trg = _trg_with_units('Marine\x00*\x00', 'Ghost\x00*\x00')
		condition = Condition()
		self.PARAM.condition_compile('Ghost', condition, trg)
		self.assertEqual(condition.unit_type, 1)

	def test_compile_sets_unit_used_flag(self) -> None:
		condition = Condition()
		self.PARAM.condition_compile('5', condition, TRG_EMPTY)
		self.assertTrue(condition.flags & Constants.ConditionFlag.unit_used)


class Test_LocationParameter(unittest.TestCase):
	PARAM = Parameters.LocationParameter()

	def test_decompile_anywhere(self) -> None:
		condition = Condition()
		condition.location_index = 64
		self.assertEqual(self.PARAM.condition_decompile(condition, TRG_EMPTY), 'Anywhere')

	def test_decompile_offset_by_one(self) -> None:
		condition = Condition()
		condition.location_index = 1
		self.assertEqual(self.PARAM.condition_decompile(condition, TRG_EMPTY), 'Location 0')

	def test_compile_anywhere(self) -> None:
		condition = Condition()
		self.PARAM.condition_compile('Anywhere', condition, TRG_EMPTY)
		self.assertEqual(condition.location_index, 64)

	def test_compile_location_prefix(self) -> None:
		condition = Condition()
		self.PARAM.condition_compile('Location 0', condition, TRG_EMPTY)
		self.assertEqual(condition.location_index, 1)

	def test_compile_out_of_range_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.PARAM.condition_compile('255', Condition(), TRG_EMPTY)


class Test_SwitchParameter(unittest.TestCase):
	PARAM = Parameters.SwitchParameter()

	def test_decompile(self) -> None:
		condition = Condition()
		condition.switch_index = 3
		self.assertEqual(self.PARAM.condition_decompile(condition, TRG_EMPTY), 'Switch 3')

	def test_compile_with_prefix(self) -> None:
		condition = Condition()
		self.PARAM.condition_compile('Switch 3', condition, TRG_EMPTY)
		self.assertEqual(condition.switch_index, 3)

	def test_compile_bare_number(self) -> None:
		condition = Condition()
		self.PARAM.condition_compile('255', condition, TRG_EMPTY)
		self.assertEqual(condition.switch_index, 255)

	def test_compile_out_of_range_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.PARAM.condition_compile('256', Condition(), TRG_EMPTY)


class Test_ResourceTypeParameter(unittest.TestCase):
	PARAM = Parameters.ResourceTypeParameter()

	def test_compile_keyword(self) -> None:
		condition = Condition()
		self.assertIsNone(self.PARAM.condition_compile('Ore and Gas', condition, TRG_EMPTY))
		self.assertEqual(condition.resource_type, Constants.ResourceType.ore_and_gas)

	def test_compile_numeric_warns(self) -> None:
		condition = Condition()
		warning = self.PARAM.condition_compile('9', condition, TRG_EMPTY)
		self.assertIsInstance(warning, PyMSWarning)
		self.assertEqual(condition.resource_type, 9)

	def test_compile_invalid_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.PARAM.condition_compile('Wood', Condition(), TRG_EMPTY)

	def test_decompile(self) -> None:
		condition = Condition()
		condition.resource_type = Constants.ResourceType.gas
		self.assertEqual(self.PARAM.condition_decompile(condition, TRG_EMPTY), 'Gas')


class Test_TimeParameter(unittest.TestCase):
	def test_decompile_duration(self) -> None:
		action = Action()
		action.duration = 1500
		self.assertEqual(Parameters.TimeParameter().action_decompile(action, TRG_EMPTY), '1500')

	def test_decompile_transmission(self) -> None:
		action = Action()
		action.transmission_duration = 99
		self.assertEqual(Parameters.TimeParameter(transmission=True).action_decompile(action, TRG_EMPTY), '99')

	def test_compile(self) -> None:
		action = Action()
		Parameters.TimeParameter().action_compile('1500', action, TRG_EMPTY)
		self.assertEqual(action.duration, 1500)


class Test_StringParameter(unittest.TestCase):
	PARAM = Parameters.StringParameter()

	def test_decompile_no_string(self) -> None:
		self.assertEqual(self.PARAM.action_decompile(Action(), TRG_EMPTY), 'No String')

	def test_decompile_string(self) -> None:
		action = Action()
		action.string_index = 5
		self.assertEqual(self.PARAM.action_decompile(action, TRG_EMPTY), 'String 5')

	def test_compile_no_string(self) -> None:
		action = Action()
		action.string_index = 9
		self.PARAM.action_compile('No String', action, TRG_EMPTY)
		self.assertEqual(action.string_index, 0)

	def test_compile_zero_warns(self) -> None:
		action = Action()
		self.assertIsInstance(self.PARAM.action_compile('String 0', action, TRG_EMPTY), PyMSWarning)


class Test_QuantityParameter(unittest.TestCase):
	PARAM = Parameters.QuantityParameter()

	def test_decompile_all(self) -> None:
		self.assertEqual(self.PARAM.action_decompile(Action(), TRG_EMPTY), 'All')

	def test_decompile_number(self) -> None:
		action = Action()
		action.quantity = 7
		self.assertEqual(self.PARAM.action_decompile(action, TRG_EMPTY), '7')

	def test_compile_all(self) -> None:
		action = Action()
		self.PARAM.action_compile('All', action, TRG_EMPTY)
		self.assertEqual(action.quantity, 0)


class Test_WAVParameter(unittest.TestCase):
	PARAM = Parameters.WAVParameter()

	def test_decompile_no_wav(self) -> None:
		self.assertEqual(self.PARAM.action_decompile(Action(), TRG_EMPTY), 'No WAV')

	def test_compile_with_prefix(self) -> None:
		action = Action()
		self.PARAM.action_compile('WAV 4', action, TRG_EMPTY)
		self.assertEqual(action.wav_string_index, 4)


class Test_DisplayParameter(unittest.TestCase):
	PARAM = Parameters.DisplayParameter()

	def test_decompile_always(self) -> None:
		action = Action()
		action.flags |= Constants.ActionFlag.always_display
		self.assertEqual(self.PARAM.action_decompile(action, TRG_EMPTY), 'Always Display')

	def test_decompile_subtitles(self) -> None:
		self.assertEqual(self.PARAM.action_decompile(Action(), TRG_EMPTY), 'Only With Subtitles')

	def test_compile_sets_and_clears_flag(self) -> None:
		action = Action()
		self.PARAM.action_compile('Always Display', action, TRG_EMPTY)
		self.assertTrue(action.flags & Constants.ActionFlag.always_display)
		self.PARAM.action_compile('Only With Subtitles', action, TRG_EMPTY)
		self.assertFalse(action.flags & Constants.ActionFlag.always_display)


class Test_PropertiesParameter(unittest.TestCase):
	PARAM = Parameters.PropertiesParameter()

	def test_decompile_one_based(self) -> None:
		action = Action()
		action.unit_properties_index = 0
		self.assertEqual(self.PARAM.action_decompile(action, TRG_EMPTY), 'Properties 1')

	def test_compile_stores_zero_based(self) -> None:
		action = Action()
		self.PARAM.action_compile('Properties 64', action, TRG_EMPTY)
		self.assertEqual(action.unit_properties_index, 63)
		self.assertTrue(action.flags & Constants.ActionFlag.unit_property_used)

	def test_compile_out_of_range_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.PARAM.action_compile('Properties 65', Action(), TRG_EMPTY)


class Test_SlotParameter(unittest.TestCase):
	PARAM = Parameters.SlotParameter()

	def test_decompile_one_based(self) -> None:
		action = Action()
		action.slot = 0
		self.assertEqual(self.PARAM.action_decompile(action, TRG_EMPTY), 'Slot 1')

	def test_compile(self) -> None:
		action = Action()
		self.PARAM.action_compile('Slot 4', action, TRG_EMPTY)
		self.assertEqual(action.slot, 3)


class Test_PercentageParameter(unittest.TestCase):
	PARAM = Parameters.PercentageParameter()

	def test_decompile_appends_percent(self) -> None:
		action = Action()
		action.number = 50
		self.assertEqual(self.PARAM.action_decompile(action, TRG_EMPTY), '50%')

	def test_compile_strips_percent(self) -> None:
		action = Action()
		self.PARAM.action_compile('50%', action, TRG_EMPTY)
		self.assertEqual(action.number, 50)

	def test_compile_over_100_warns(self) -> None:
		action = Action()
		self.assertIsInstance(self.PARAM.action_compile('150', action, TRG_EMPTY), PyMSWarning)


class Test_OrderParameter(unittest.TestCase):
	PARAM = Parameters.OrderParameter()

	def test_decompile(self) -> None:
		action = Action()
		action.order = Constants.Order.patrol
		self.assertEqual(self.PARAM.action_decompile(action, TRG_EMPTY), 'Patrol')

	def test_compile(self) -> None:
		action = Action()
		self.PARAM.action_compile('Attack', action, TRG_EMPTY)
		self.assertEqual(action.order, Constants.Order.attack)


class Test_RawFieldParameter(unittest.TestCase):
	def test_limits(self) -> None:
		self.assertEqual(Parameters.LongParameter(0).limit, 4294967295)
		self.assertEqual(Parameters.ShortParamater(0).limit, 65535)
		self.assertEqual(Parameters.ByteParameter(0).limit, 255)

	def test_action_compile_and_decompile(self) -> None:
		param = Parameters.ByteParameter(8)
		action = Action()
		param.action_compile('200', action, TRG_EMPTY)
		self.assertEqual(action.fields[8], 200)
		self.assertEqual(param.action_decompile(action, TRG_EMPTY), '200')

	def test_condition_compile_and_decompile(self) -> None:
		param = Parameters.ByteParameter(4)
		condition = Condition()
		param.condition_compile('200', condition, TRG_EMPTY)
		self.assertEqual(condition.fields[4], 200)
		self.assertEqual(param.condition_decompile(condition, TRG_EMPTY), '200')

	def test_compile_over_limit_raises(self) -> None:
		with self.assertRaises(PyMSError):
			Parameters.ByteParameter(8).action_compile('256', Action(), TRG_EMPTY)


class Test_MemoryParameter(unittest.TestCase):
	PARAM = Parameters.MemoryParameter()

	def test_decompile_base_address(self) -> None:
		# Lowercase `0x` prefix with uppercase hex digits.
		condition = Condition()
		condition.unit_type = 0
		condition.player_group = 0
		self.assertEqual(self.PARAM.condition_decompile(condition, TRG_EMPTY), '0x0058A364')

	def test_compile_hex(self) -> None:
		condition = Condition()
		self.PARAM.condition_compile('0x0058A364', condition, TRG_EMPTY)
		self.assertEqual(condition.player_group, 0)

	def test_compile_accepts_any_hex_case(self) -> None:
		# Compile must accept either prefix case and either digit case.
		for value in ('0X0058A364', '0x0058a364', '0X0058a364'):
			condition = Condition()
			self.PARAM.condition_compile(value, condition, TRG_EMPTY)
			self.assertEqual(condition.player_group, 0)

	def test_round_trip(self) -> None:
		source = Condition()
		source.unit_type = 0
		source.player_group = 7
		text = self.PARAM.condition_decompile(source, TRG_EMPTY)
		result = Condition()
		self.PARAM.condition_compile(text, result, TRG_EMPTY)
		self.assertEqual(result.player_group, 7)

	def test_not_multiple_of_four_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.PARAM.condition_compile('0x0058A365', Condition(), TRG_EMPTY)

	def test_invalid_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.PARAM.condition_compile('notanumber', Condition(), TRG_EMPTY)


class Test_MaskParameter(unittest.TestCase):
	PARAM = Parameters.MaskParameter()

	def test_decompile_enabled(self) -> None:
		# Lowercase `0x` prefix with uppercase hex digits.
		condition = Condition()
		condition.mask = 0xABCD
		condition.masked = Constants.Mask.enabled
		self.assertEqual(self.PARAM.condition_decompile(condition, TRG_EMPTY), '0x0000ABCD')

	def test_decompile_disabled(self) -> None:
		condition = Condition()
		condition.mask = 0x1234
		condition.masked = Constants.Mask.disabled
		self.assertEqual(self.PARAM.condition_decompile(condition, TRG_EMPTY), 'No Mask')

	def test_compile_no_mask(self) -> None:
		condition = Condition()
		self.PARAM.condition_compile('No Mask', condition, TRG_EMPTY)
		self.assertEqual(condition.mask, 0)
		self.assertEqual(condition.masked, Constants.Mask.disabled)

	def test_compile_hex(self) -> None:
		condition = Condition()
		self.PARAM.condition_compile('0xFF', condition, TRG_EMPTY)
		self.assertEqual(condition.mask, 255)
		self.assertEqual(condition.masked, Constants.Mask.enabled)

	def test_compile_accepts_uppercase_hex(self) -> None:
		condition = Condition()
		self.PARAM.condition_compile('0XFF', condition, TRG_EMPTY)
		self.assertEqual(condition.mask, 255)

	def test_round_trip(self) -> None:
		source = Condition()
		source.mask = 0x1234
		source.masked = Constants.Mask.enabled
		text = self.PARAM.condition_decompile(source, TRG_EMPTY)
		result = Condition()
		self.PARAM.condition_compile(text, result, TRG_EMPTY)
		self.assertEqual(result.mask, 0x1234)

	def test_too_high_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.PARAM.condition_compile('0x100000000', Condition(), TRG_EMPTY)
