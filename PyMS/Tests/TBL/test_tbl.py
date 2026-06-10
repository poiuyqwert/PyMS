
from ...FileFormats.TBL import TBL, TBL_REF, compile_string, decompile_string
from ...Utilities.PyMSError import PyMSError

import io
import struct
import unittest
from unittest import mock


def _decompile_to_text(tbl: TBL, ref: bool = False) -> str:
	# Capture `decompile`'s output in memory by standing in for AtomicWriter.
	buffer = io.StringIO()
	writer = mock.MagicMock()
	writer.write.side_effect = buffer.write
	with mock.patch('PyMS.FileFormats.TBL.AtomicWriter', return_value=writer):
		tbl.decompile('out.txt', ref)
	return buffer.getvalue()


def _interpret_text(content: str) -> list[str]:
	tbl = TBL()
	with mock.patch('builtins.open', mock.mock_open(read_data=content)):
		tbl.interpret('in.txt')
	return tbl.strings


class Test_compile_string(unittest.TestCase):
	def test_numeric_escape(self) -> None:
		self.assertEqual(compile_string('<0>'), '\x00')
		self.assertEqual(compile_string('<65>'), 'A')

	def test_tab_escape(self) -> None:
		self.assertEqual(compile_string('a<9>b'), 'a\tb')

	def test_out_of_range_left_literal(self) -> None:
		self.assertEqual(compile_string('<256>'), '<256>')

	def test_non_numeric_left_literal(self) -> None:
		self.assertEqual(compile_string('<abc>'), '<abc>')

	def test_no_escapes(self) -> None:
		self.assertEqual(compile_string('plain text'), 'plain text')

	def test_multiple_escapes(self) -> None:
		self.assertEqual(compile_string('<60>x<62>'), '<x>')


class Test_decompile_string(unittest.TestCase):
	def test_control_chars(self) -> None:
		self.assertEqual(decompile_string('\x00'), '<0>')
		self.assertEqual(decompile_string('a\tb'), 'a<9>b')

	def test_hash_and_angle_brackets(self) -> None:
		self.assertEqual(decompile_string('#'), '<35>')
		self.assertEqual(decompile_string('<'), '<60>')
		self.assertEqual(decompile_string('>'), '<62>')

	def test_plain_text_unchanged(self) -> None:
		self.assertEqual(decompile_string('hello'), 'hello')

	def test_exclude_keeps_char_literal(self) -> None:
		self.assertEqual(decompile_string('#<>', exclude='#'), '#<60><62>')

	def test_include_adds_char_to_set(self) -> None:
		self.assertEqual(decompile_string('A', include='A'), '<65>')

	def test_round_trips_with_compile(self) -> None:
		original = '\x00\t#<>abc'
		self.assertEqual(compile_string(decompile_string(original)), original)


class Test_save_data(unittest.TestCase):
	def test_layout(self) -> None:
		tbl = TBL()
		tbl.strings = ['AB', 'C']
		self.assertEqual(tbl.save_data(), b'\x02\x00\x06\x00\x09\x00AB\x00C\x00')

	def test_null_terminator_not_doubled(self) -> None:
		without = TBL()
		without.strings = ['A']
		already = TBL()
		already.strings = ['A\x00']
		self.assertEqual(without.save_data(), already.save_data())
		self.assertEqual(without.save_data(), b'\x01\x00\x04\x00A\x00')

	def test_empty(self) -> None:
		tbl = TBL()
		tbl.strings = []
		self.assertEqual(tbl.save_data(), b'\x00\x00')


class Test_load_file(unittest.TestCase):
	def test_loads_strings_with_terminator(self) -> None:
		tbl = TBL()
		tbl.load_file(io.BytesIO(b'\x02\x00\x06\x00\x09\x00AB\x00C\x00'))
		self.assertEqual(tbl.strings, ['AB\x00', 'C\x00'])

	def test_round_trip_load_save_is_byte_identical(self) -> None:
		data = b'\x02\x00\x06\x00\x09\x00AB\x00C\x00'
		tbl = TBL()
		tbl.load_file(io.BytesIO(data))
		self.assertEqual(tbl.save_data(), data)

	def test_overlapping_offsets_share_string(self) -> None:
		data = struct.pack('<H', 2) + struct.pack('<H', 6) + struct.pack('<H', 6) + b'AB\x00'
		tbl = TBL()
		tbl.load_file(io.BytesIO(data))
		self.assertEqual(tbl.strings, ['AB\x00', 'AB\x00'])

	def test_empty(self) -> None:
		tbl = TBL()
		tbl.load_file(io.BytesIO(b'\x00\x00'))
		self.assertEqual(tbl.strings, [])

	def test_truncated_header_raises(self) -> None:
		tbl = TBL()
		with self.assertRaises(PyMSError):
			tbl.load_file(io.BytesIO(b'\x02\x00\x06\x00'))

	def test_empty_input_raises(self) -> None:
		tbl = TBL()
		with self.assertRaises(PyMSError):
			tbl.load_file(io.BytesIO(b''))


class Test_decompile(unittest.TestCase):
	def test_writes_decompiled_line_per_string(self) -> None:
		tbl = TBL()
		tbl.strings = ['a#b', 'x']
		self.assertEqual(_decompile_to_text(tbl), 'a<35>b\nx\n')

	def test_empty_string_becomes_blank_line(self) -> None:
		tbl = TBL()
		tbl.strings = ['a', '', 'b']
		self.assertEqual(_decompile_to_text(tbl), 'a\n\nb\n')

	def test_ref_prepends_reference(self) -> None:
		tbl = TBL()
		tbl.strings = ['x']
		self.assertEqual(_decompile_to_text(tbl, ref=True), TBL_REF + 'x\n')

	def test_write_error_raises(self) -> None:
		tbl = TBL()
		tbl.strings = ['x']
		with mock.patch('PyMS.FileFormats.TBL.AtomicWriter', side_effect=OSError('nope')):
			with self.assertRaises(PyMSError):
				tbl.decompile('out.txt')


class Test_interpret(unittest.TestCase):
	def test_parses_lines(self) -> None:
		content = 'Plain\nTab<9>here\nInline#comment\n#full comment\n\nHash<35>tag\n'
		self.assertEqual(_interpret_text(content), ['Plain', 'Tab\there', 'Inline', '', 'Hash#tag'])

	def test_inline_comment_stripped(self) -> None:
		self.assertEqual(_interpret_text('keep#drop\n'), ['keep'])

	def test_full_comment_line_dropped(self) -> None:
		self.assertEqual(_interpret_text('#just a comment\n'), [])

	def test_blank_line_becomes_empty_entry(self) -> None:
		self.assertEqual(_interpret_text('a\n\nb\n'), ['a', '', 'b'])

	def test_too_many_entries_raises(self) -> None:
		with self.assertRaises(PyMSError):
			_interpret_text('x\n' * 65537)

	def test_open_error_raises(self) -> None:
		tbl = TBL()
		with mock.patch('builtins.open', side_effect=OSError('nope')):
			with self.assertRaises(PyMSError):
				tbl.interpret('missing.txt')


class Test_decompile_interpret_round_trip(unittest.TestCase):
	def test_round_trips_arbitrary_strings(self) -> None:
		# decompile escapes #, <, >, newlines and control chars so the line-based
		# text format survives interpret unchanged.
		strings = ['Hello', 'a#b', 'tab\there', '', 'AB\x00', '<5>', 'line1\nline2', '> quote']
		tbl = TBL()
		tbl.strings = strings
		self.assertEqual(_interpret_text(_decompile_to_text(tbl)), strings)

	def test_binary_to_text_to_binary_is_identical(self) -> None:
		data = b'\x02\x00\x06\x00\x09\x00AB\x00C\x00'
		loaded = TBL()
		loaded.load_file(io.BytesIO(data))
		reinterpreted = TBL()
		reinterpreted.strings = _interpret_text(_decompile_to_text(loaded))
		self.assertEqual(reinterpreted.save_data(), data)
