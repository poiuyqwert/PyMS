
from ...FileFormats.TRG.TRG import TRG, Format
from ...FileFormats.TRG.Constants import BriefingActionType
from ...FileFormats.TRG.UnitProperties import FieldFlag, StateFlag
from ...Utilities.PyMSError import PyMSError

import io
import unittest

# A normal trigger with a string, exercising conditions, actions, and a string entry.
NORMAL_TEXT = '''String(1):
  Hello World

Trigger(Player 1):
  Conditions:
    Always()
  Actions:
    DisplayTextMessage(String 1, Always Display)
    Victory()

'''

# A trigger whose enabled mask forces the Memory/SetMemory definitions, exercising
# the uppercase 0X hex form for both the memory address and the mask.
MEMORY_TEXT = '''Trigger(Player 1):
  Conditions:
    Memory(0x0058A364, At Least, 5, 0x0000FFFF)
  Actions:
    SetMemory(0x0058A364, Set To, 10, 0x0000FFFF)

'''


# A trigger with a CreateUnitWithProperties action referencing UnitProperties, so
# the properties are exercised through parse, decompile, and binary save/load.
PROPERTIES_TEXT = '''UnitProperties(1):
  Owner(5)
  Health(100)
  Cloaked()

Trigger(Player 1):
  Conditions:
    Always()
  Actions:
    CreateUnitWithProperties(Player 1, 1, 0, Anywhere, Properties 1)

'''


# A mission briefing trigger, exercising briefing-only actions and briefing actions
# that share a name with a normal action but take different parameters. Briefing
# triggers have no Conditions: or Actions: headers - actions are listed directly.
BRIEFING_TEXT = '''String(1):
  Briefing incoming

BriefingTrigger():
    ShowPortrait(0, Slot 1)
    DisplayTextMessage(String 1, 3000)
    Transmission(String 1, Slot 1, No WAV, 2000, Set To, 4000)

'''


def _compile(text: str) -> TRG:
	trg = TRG()
	trg.compile(io.StringIO(text))
	return trg


class Test_text_round_trip(unittest.TestCase):
	def test_compile_populates_model(self) -> None:
		trg = _compile(NORMAL_TEXT)
		self.assertEqual(len(trg.triggers), 1)
		self.assertEqual(trg.strings, {1: 'Hello World'})
		self.assertEqual(trg.format, Format.normal)

	def test_decompile_matches_source(self) -> None:
		trg = _compile(NORMAL_TEXT)
		output = io.StringIO()
		trg.decompile(output)
		self.assertEqual(output.getvalue(), NORMAL_TEXT)

	def test_memory_round_trip(self) -> None:
		# The memory/mask parameters use an uppercase 0X hex form that must
		# survive decompile -> compile.
		trg = _compile(MEMORY_TEXT)
		output = io.StringIO()
		trg.decompile(output)
		self.assertEqual(output.getvalue(), MEMORY_TEXT)

	def test_no_triggers_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_compile('String(1):\n  orphan\n\n')
		self.assertIn('No triggers', str(cm.exception))

	def test_compile_parses_unit_properties(self) -> None:
		trg = _compile(PROPERTIES_TEXT)
		props = trg.unit_properties[0]
		self.assertEqual(props.owner, 5)
		self.assertEqual(props.hit_points, 100)
		self.assertTrue(props.fields_available_flags & FieldFlag.owner)
		self.assertTrue(props.fields_available_flags & FieldFlag.hit_points)
		self.assertTrue(props.state_flags & StateFlag.cloaked)

	def test_unit_properties_decompile_matches_source(self) -> None:
		trg = _compile(PROPERTIES_TEXT)
		output = io.StringIO()
		trg.decompile(output)
		self.assertEqual(output.getvalue(), PROPERTIES_TEXT)

	def test_duplicate_property_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_compile(PROPERTIES_TEXT.replace('  Health(100)\n', '  Health(100)\n  Health(50)\n'))
		self.assertIn('Property already defined', str(cm.exception))

	def test_property_value_too_large_raises(self) -> None:
		# Owner is a u8, so 999 exceeds the field maximum.
		with self.assertRaises(PyMSError) as cm:
			_compile(PROPERTIES_TEXT.replace('Owner(5)', 'Owner(999)'))
		self.assertIn('Integer parameter too large', str(cm.exception))

	def test_briefing_compile_populates_model(self) -> None:
		trg = _compile(BRIEFING_TEXT)
		self.assertEqual(trg.format, Format.briefing)
		self.assertEqual(len(trg.triggers), 1)
		self.assertEqual(trg.strings, {1: 'Briefing incoming'})

	def test_briefing_actions_use_briefing_definitions(self) -> None:
		# Actions in a BriefingTrigger must resolve against the briefing action set,
		# including names shared with normal actions (like DisplayTextMessage and
		# Transmission, which take different parameters in a briefing).
		trg = _compile(BRIEFING_TEXT)
		action_types = [action.action_type for action in trg.triggers[0].actions]
		self.assertEqual(action_types, [BriefingActionType.show_portrait, BriefingActionType.text_message, BriefingActionType.transmission])

	def test_briefing_decompile_matches_source(self) -> None:
		trg = _compile(BRIEFING_TEXT)
		output = io.StringIO()
		trg.decompile(output)
		self.assertEqual(output.getvalue(), BRIEFING_TEXT)

	def test_briefing_actions_header_raises(self) -> None:
		# A BriefingTrigger holds only actions, listed directly - an Actions: header
		# is not part of the briefing syntax.
		with self.assertRaises(PyMSError) as cm:
			_compile(BRIEFING_TEXT.replace('BriefingTrigger():\n', 'BriefingTrigger():\n  Actions:\n'))
		self.assertIn('Expected an action', str(cm.exception))

	def test_briefing_only_action_in_normal_trigger_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_compile(NORMAL_TEXT.replace('    Victory()\n', '    ShowPortrait(0, Slot 1)\n'))
		self.assertIn("Unknown action name 'ShowPortrait'", str(cm.exception))

	def test_normal_only_action_in_briefing_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_compile(BRIEFING_TEXT.replace('    ShowPortrait(0, Slot 1)\n', '    Victory()\n'))
		self.assertIn("Unknown action name 'Victory'", str(cm.exception))


class Test_binary_round_trip(unittest.TestCase):
	def _save(self, trg: TRG, trg_format: Format | None = None) -> bytes:
		buffer = io.BytesIO()
		trg.save(buffer, trg_format)
		return buffer.getvalue()

	def test_save_writes_header(self) -> None:
		data = self._save(_compile(NORMAL_TEXT))
		self.assertEqual(data[:len(TRG.HEADER)], TRG.HEADER)

	def test_load_reproduces_model(self) -> None:
		original = _compile(NORMAL_TEXT)
		loaded = TRG()
		loaded.load(self._save(original))
		self.assertEqual(loaded, original)

	def test_resave_is_byte_identical(self) -> None:
		data = self._save(_compile(NORMAL_TEXT))
		reloaded = TRG()
		reloaded.load(data)
		self.assertEqual(self._save(reloaded), data)

	def test_got_format_omits_header(self) -> None:
		data = self._save(_compile(NORMAL_TEXT), Format.got)
		self.assertNotEqual(data[:len(TRG.HEADER)], TRG.HEADER)

	def test_missing_header_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			TRG().load(b'not a valid header at all')
		self.assertIn('Not a valid .trg file (missing header)', str(cm.exception))

	def test_briefing_load_reproduces_model(self) -> None:
		original = _compile(BRIEFING_TEXT)
		loaded = TRG()
		loaded.load(self._save(original), Format.briefing)
		self.assertEqual(loaded, original)

	def test_briefing_resave_is_byte_identical(self) -> None:
		data = self._save(_compile(BRIEFING_TEXT))
		reloaded = TRG()
		reloaded.load(data, Format.briefing)
		self.assertEqual(self._save(reloaded), data)

	def test_briefing_load_decompiles_to_source(self) -> None:
		loaded = TRG()
		loaded.load(self._save(_compile(BRIEFING_TEXT)), Format.briefing)
		output = io.StringIO()
		loaded.decompile(output)
		self.assertEqual(output.getvalue(), BRIEFING_TEXT)

	def test_referenced_unit_properties_round_trip(self) -> None:
		# An action references the properties, so binary save/load must retain them.
		original = _compile(PROPERTIES_TEXT)
		loaded = TRG()
		loaded.load(self._save(original))
		self.assertEqual(loaded, original)
		self.assertEqual(loaded.unit_properties, original.unit_properties)
