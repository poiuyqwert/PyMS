
from ...FileFormats.TRG.TRG import TRG, Format
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
		with self.assertRaises(PyMSError):
			_compile('String(1):\n  orphan\n\n')

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
		with self.assertRaises(PyMSError):
			_compile(PROPERTIES_TEXT.replace('  Health(100)\n', '  Health(100)\n  Health(50)\n'))

	def test_property_value_too_large_raises(self) -> None:
		# Owner is a u8, so 999 exceeds the field maximum.
		with self.assertRaises(PyMSError):
			_compile(PROPERTIES_TEXT.replace('Owner(5)', 'Owner(999)'))


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
		loaded.load(io.BytesIO(self._save(original)))
		self.assertEqual(loaded, original)

	def test_resave_is_byte_identical(self) -> None:
		data = self._save(_compile(NORMAL_TEXT))
		reloaded = TRG()
		reloaded.load(io.BytesIO(data))
		self.assertEqual(self._save(reloaded), data)

	def test_got_format_omits_header(self) -> None:
		data = self._save(_compile(NORMAL_TEXT), Format.got)
		self.assertNotEqual(data[:len(TRG.HEADER)], TRG.HEADER)

	def test_missing_header_raises(self) -> None:
		with self.assertRaises(PyMSError):
			TRG().load(io.BytesIO(b'not a valid header at all'))

	def test_referenced_unit_properties_round_trip(self) -> None:
		# An action references the properties, so binary save/load must retain them.
		original = _compile(PROPERTIES_TEXT)
		loaded = TRG()
		loaded.load(io.BytesIO(self._save(original)))
		self.assertEqual(loaded, original)
		self.assertEqual(loaded.unit_properties, original.unit_properties)
