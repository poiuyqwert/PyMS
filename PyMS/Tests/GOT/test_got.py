
from ...FileFormats.GOT import (
	GOT,
	VictoryCondition, Resources, UnitStats, FogOfWar, StartingUnits, StartingPositions,
	PlayerTypes, Allies, TeamMode, CheatCodes, TournametMode,
)
from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO

import io
import unittest

# Every attribute set to a distinct non-default value, to exercise the full layout.
FIELDS = {
	'name': 'My Template',
	'subtype_name': 'Sub',
	'gametype_id': 10,
	'league_id': 5,
	'subtype_id': 3,
	'subtype_display': 100,
	'subtype_label': 7,
	'victory_condition': VictoryCondition.resources,
	'resources': Resources.income,
	'unit_stats': UnitStats.standard,
	'fog_of_war': FogOfWar.on,
	'starting_units': StartingUnits.workers_and_center,
	'starting_positions': StartingPositions.fixed,
	'player_types': PlayerTypes.single_ai,
	'allies': Allies.allowed,
	'team_mode': TeamMode.teams_4,
	'cheat_codes': CheatCodes.on,
	'tournament_mode': TournametMode.on,
	'victory_condition_value': 1000,
	'resources_value': 2000,
	'subtype_value': 500,
}

ALL_ENUMS = (
	VictoryCondition, Resources, UnitStats, FogOfWar, StartingUnits, StartingPositions,
	PlayerTypes, Allies, TeamMode, CheatCodes, TournametMode,
)


def _sample() -> GOT:
	got = GOT()
	for attr, value in FIELDS.items():
		setattr(got, attr, value)
	return got


def _assert_matches_sample(test: unittest.TestCase, got: GOT) -> None:
	for attr, value in FIELDS.items():
		test.assertEqual(getattr(got, attr), value, attr)


class Test_enum_requires_value(unittest.TestCase):
	def test_victory_condition(self) -> None:
		self.assertTrue(VictoryCondition.resources.requires_value)
		self.assertTrue(VictoryCondition.slaughter.requires_value)
		self.assertFalse(VictoryCondition.map_default.requires_value)
		self.assertFalse(VictoryCondition.melee.requires_value)

	def test_resources(self) -> None:
		self.assertTrue(Resources.fixed_value.requires_value)
		self.assertTrue(Resources.income.requires_value)
		self.assertFalse(Resources.map_default.requires_value)
		self.assertFalse(Resources.low.requires_value)


class Test_enum_metadata(unittest.TestCase):
	def test_all_returns_every_member(self) -> None:
		for enum_type in ALL_ENUMS:
			with self.subTest(enum=enum_type.__name__):
				self.assertEqual(set(enum_type.ALL()), set(enum_type))

	def test_display_name_present(self) -> None:
		for enum_type in ALL_ENUMS:
			for member in enum_type:
				with self.subTest(enum=enum_type.__name__, member=member.name):
					self.assertTrue(member.display_name)


class Test_save(unittest.TestCase):
	def test_size_and_magic(self) -> None:
		data = IO.output_to_bytes(_sample().save)
		self.assertEqual(len(data), 97)
		self.assertEqual(data[0], 3)

	def test_binary_round_trip(self) -> None:
		loaded = GOT()
		loaded.load(IO.output_to_bytes(_sample().save))
		_assert_matches_sample(self, loaded)

	def test_save_to_stream_matches_captured_bytes(self) -> None:
		got = _sample()
		buffer = io.BytesIO()
		got.save(buffer)
		self.assertEqual(buffer.getvalue(), IO.output_to_bytes(got.save))


class Test_load(unittest.TestCase):
	def test_invalid_size_raises(self) -> None:
		with self.assertRaises(PyMSError):
			GOT().load(io.BytesIO(b'\x00' * 50))

	def test_invalid_magic_raises(self) -> None:
		data = bytearray(IO.output_to_bytes(_sample().save))
		data[0] = 0
		with self.assertRaises(PyMSError):
			GOT().load(io.BytesIO(bytes(data)))

	def test_invalid_enum_value_raises(self) -> None:
		# Offset 73 holds the victory_condition byte; 99 is not a valid member.
		data = bytearray(IO.output_to_bytes(_sample().save))
		data[73] = 99
		with self.assertRaises(PyMSError):
			GOT().load(io.BytesIO(bytes(data)))


class Test_decompile_interpret(unittest.TestCase):
	def _decompile(self, got: GOT, include_reference: bool = False) -> str:
		output = io.StringIO()
		got.decompile(output, include_reference=include_reference)
		return output.getvalue()

	def test_text_round_trip(self) -> None:
		text = self._decompile(_sample())
		loaded = GOT()
		loaded.interpret(io.StringIO(text))
		_assert_matches_sample(self, loaded)

	def test_decompile_emits_fields(self) -> None:
		text = self._decompile(_sample())
		self.assertIn('name My Template', text)
		self.assertIn('victory_condition resources', text)
		self.assertIn('team_mode teams_4', text)

	def test_reference_block_included(self) -> None:
		text = self._decompile(_sample(), include_reference=True)
		self.assertTrue(text.startswith('#---'))
		self.assertIn("# 'victory_condition' options:", text)

	def test_round_trip_with_reference(self) -> None:
		# Reference comments must be ignored by interpret.
		text = self._decompile(_sample(), include_reference=True)
		loaded = GOT()
		loaded.interpret(io.StringIO(text))
		_assert_matches_sample(self, loaded)
