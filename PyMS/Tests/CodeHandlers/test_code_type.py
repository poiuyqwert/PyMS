
from ._helpers import make_parse_context, make_language

from ...Utilities.CodeHandlers import CodeType
from ...Utilities.CodeHandlers.CodeBlock import CodeBlock
from ...Utilities.CodeHandlers.SerializeContext import SerializeContext
from ...Utilities.CodeHandlers.DecompileContext import DecompileContext
from ...Utilities.CodeHandlers.DecompileStrategy import DecompileStrategy
from ...Utilities.CodeHandlers.ByteCodeCompiler import ByteCodeCompiler
from ...Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from ...Utilities.BytesScanner import BytesScanner
from ...Utilities.PyMSError import PyMSError
from ...Utilities import Struct

import unittest, io


def serialize_context(definitions: DefinitionsHandler | None = None) -> SerializeContext:
	return SerializeContext(io.StringIO(), definitions=definitions)


class Test_CodeType_Base(unittest.TestCase):
	def test_find_by_name_found(self) -> None:
		a = CodeType.IntCodeType('a', 'a', Struct.l_u8)
		b = CodeType.IntCodeType('b', 'b', Struct.l_u8)
		self.assertIs(CodeType.CodeType.find_by_name('b', [a, b]), b)

	def test_find_by_name_missing(self) -> None:
		a = CodeType.IntCodeType('a', 'a', Struct.l_u8)
		self.assertIsNone(CodeType.CodeType.find_by_name('z', [a]))

	def test_accepts_same_type(self) -> None:
		a = CodeType.IntCodeType('a', 'a', Struct.l_u8)
		b = CodeType.IntCodeType('b', 'b', Struct.l_u16)
		self.assertTrue(a.accepts(b))

	def test_accepts_unrelated_type_is_false(self) -> None:
		i = CodeType.IntCodeType('i', 'i', Struct.l_u8)
		f = CodeType.FloatCodeType('f', 'f', Struct.l_float)
		self.assertFalse(i.accepts(f))


class Test_IntCodeType_Lex(unittest.TestCase):
	def test_lex_integer(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u16)
		self.assertEqual(int_type.lex(make_parse_context('42')), 42)

	def test_lex_negative_integer(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_s16)
		self.assertEqual(int_type.lex(make_parse_context('-5')), -5)

	def test_lex_hex_allowed(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u16, allow_hex=True)
		self.assertEqual(int_type.lex(make_parse_context('0x10')), 16)

	def test_lex_hex_rejected_when_not_allowed(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u16)
		with self.assertRaises(PyMSError):
			int_type.lex(make_parse_context('0x10'))

	def test_invalid_integer_value_reports_a_source_line(self) -> None:
		# Like the sibling parse-failure branch, the type-mismatch failure
		# should attach the source line so diagnostics are consistent.
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u16)
		try:
			int_type.lex(make_parse_context('notanumber'))
		except PyMSError as e:
			self.assertIsNotNone(e.line)
			return
		self.fail('expected a PyMSError')


class Test_IntCodeType_Validate(unittest.TestCase):
	def test_within_limits(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u8, limits=(0, 10))
		int_type.validate(5, make_parse_context(''))  # no raise

	def test_too_small(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u8, limits=(5, 10))
		with self.assertRaises(PyMSError):
			int_type.validate(1, make_parse_context(''))

	def test_too_large(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u8, limits=(0, 10))
		with self.assertRaises(PyMSError):
			int_type.validate(11, make_parse_context(''))

	def test_default_limits_from_bytecode_type(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u8)
		self.assertEqual(int_type.get_limits(make_parse_context('')), (0, 255))

	def test_parse_rejects_out_of_range(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u8, limits=(0, 10))
		with self.assertRaises(PyMSError):
			int_type.parse(make_parse_context('99'))


class Test_IntCodeType_Binary(unittest.TestCase):
	def test_compile(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u16)
		builder = ByteCodeCompiler()
		int_type.compile(0x2000, builder)
		self.assertEqual(builder.data, b'\x00\x20')

	def test_decompile(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u16)
		scanner = BytesScanner(b'\x00\x20')
		context = DecompileContext(b'\x00\x20', make_language())
		self.assertEqual(int_type.decompile(scanner, context), 0x2000)

	def test_compile_decompile_roundtrip(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u32)
		builder = ByteCodeCompiler()
		int_type.compile(123456, builder)
		scanner = BytesScanner(bytes(builder.data))
		context = DecompileContext(bytes(builder.data), make_language())
		self.assertEqual(int_type.decompile(scanner, context), 123456)


class Test_IntCodeType_Serialize(unittest.TestCase):
	def test_serialize_plain_value(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u16)
		self.assertEqual(int_type.serialize(42, serialize_context()), '42')

	def test_serialize_uses_matching_variable_name(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u16)
		definitions = DefinitionsHandler()
		definitions.set_variable('answer', 42, int_type)
		self.assertEqual(int_type.serialize(42, serialize_context(definitions)), 'answer')

	def test_serialize_falls_back_when_no_matching_variable(self) -> None:
		int_type = CodeType.IntCodeType('i', 'i', Struct.l_u16)
		definitions = DefinitionsHandler()
		definitions.set_variable('answer', 42, int_type)
		self.assertEqual(int_type.serialize(7, serialize_context(definitions)), '7')


class Test_FloatCodeType(unittest.TestCase):
	def test_lex_float(self) -> None:
		float_type = CodeType.FloatCodeType('f', 'f', Struct.l_float)
		self.assertAlmostEqual(float_type.lex(make_parse_context('3.5')), 3.5)

	def test_lex_rejects_integer_token(self) -> None:
		float_type = CodeType.FloatCodeType('f', 'f', Struct.l_float)
		with self.assertRaises(PyMSError):
			float_type.lex(make_parse_context('3'))

	def test_validate_limits(self) -> None:
		float_type = CodeType.FloatCodeType('f', 'f', Struct.l_float, limits=(0.0, 1.0))
		with self.assertRaises(PyMSError):
			float_type.validate(2.0, make_parse_context(''))

	def test_compile_decompile_roundtrip(self) -> None:
		float_type = CodeType.FloatCodeType('f', 'f', Struct.l_float)
		builder = ByteCodeCompiler()
		float_type.compile(0.5, builder)
		scanner = BytesScanner(bytes(builder.data))
		context = DecompileContext(bytes(builder.data), make_language())
		self.assertAlmostEqual(float_type.decompile(scanner, context), 0.5)


class Test_AddressCodeType(unittest.TestCase):
	def test_is_a_block_reference(self) -> None:
		addr = CodeType.AddressCodeType('a', 'a', Struct.l_u16)
		self.assertTrue(addr.block_reference)

	def test_lex_identifier_returns_block(self) -> None:
		addr = CodeType.AddressCodeType('a', 'a', Struct.l_u16)
		context = make_parse_context('target')
		block = addr.lex(context)
		self.assertIsInstance(block, CodeBlock)
		# Looking up the same name returns the same block instance.
		self.assertIs(context.get_block('target'), block)

	def test_lex_rejects_non_identifier(self) -> None:
		addr = CodeType.AddressCodeType('a', 'a', Struct.l_u16)
		with self.assertRaises(PyMSError):
			addr.lex(make_parse_context('123'))

	def test_serialize_uses_strategy_label(self) -> None:
		addr = CodeType.AddressCodeType('a', 'a', Struct.l_u16)
		block = CodeBlock()
		context = serialize_context()
		context.strategy = DecompileStrategy([block], {block: 'my_label'}, [], {})
		self.assertEqual(addr.serialize(block, context), 'my_label')

	def test_compile_emits_block_ref(self) -> None:
		addr = CodeType.AddressCodeType('a', 'a', Struct.l_u16)
		block = CodeBlock()
		builder = ByteCodeCompiler()
		addr.compile(block, builder)
		# A placeholder offset (0) is written and a pending ref is recorded.
		self.assertEqual(len(builder.data), 2)
		self.assertIn(block, builder.block_refs)


class Test_StrCodeType(unittest.TestCase):
	def test_serialize_string_roundtrip(self) -> None:
		self.assertEqual(CodeType.StrCodeType.parse_string(CodeType.StrCodeType.serialize_string('hello')), 'hello')

	def test_serialize_string_is_quoted(self) -> None:
		self.assertIn(CodeType.StrCodeType.serialize_string('hi')[0], '"\'')

	def test_parse_string_rejects_invalid(self) -> None:
		with self.assertRaises(PyMSError):
			CodeType.StrCodeType.parse_string('not quoted')

	def test_decompile_drops_trailing_null(self) -> None:
		str_type = CodeType.StrCodeType('s', 's')
		scanner = BytesScanner(b'hello\x00')
		context = DecompileContext(b'hello\x00', make_language())
		self.assertEqual(str_type.decompile(scanner, context), 'hello')

	def test_compile_appends_null(self) -> None:
		str_type = CodeType.StrCodeType('s', 's')
		builder = ByteCodeCompiler()
		str_type.compile('hi', builder)
		self.assertEqual(builder.data, b'hi\x00')

	def test_lex_quoted_string(self) -> None:
		str_type = CodeType.StrCodeType('s', 's')
		self.assertEqual(str_type.lex(make_parse_context('"hello"')), 'hello')

	def test_lex_unquoted_single_token_in_parens(self) -> None:
		# An unquoted single-word string parameter inside parens must capture
		# that word.
		str_type = CodeType.StrCodeType('s', 's')
		context = make_parse_context('word)')
		context.command_in_parens = True
		self.assertEqual(str_type.lex(context), 'word')

	def test_lex_unquoted_open_string_keeps_all_words(self) -> None:
		# An unquoted multi-word string parameter inside parens must keep every
		# word, including the first one.
		str_type = CodeType.StrCodeType('s', 's')
		context = make_parse_context('hello world)')
		context.command_in_parens = True
		self.assertEqual(str_type.lex(context), 'hello world')


class Test_EnumCodeType(unittest.TestCase):
	def make(self, **kwargs) -> CodeType.EnumCodeType:
		return CodeType.EnumCodeType('e', 'e', Struct.l_u8, {'alpha': 1, 'beta': 2}, **kwargs)

	def test_list_cases_are_enumerated(self) -> None:
		enum = CodeType.EnumCodeType('e', 'e', Struct.l_u8, ['zero', 'one', 'two'])
		self.assertEqual(enum.lex(make_parse_context('two')), 2)

	def test_lex_valid_case(self) -> None:
		self.assertEqual(self.make().lex(make_parse_context('beta')), 2)

	def test_lex_invalid_case_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.make().lex(make_parse_context('gamma'))

	def test_lex_integer_when_allowed(self) -> None:
		self.assertEqual(self.make(allow_integer=True).lex(make_parse_context('2')), 2)

	def test_lex_integer_rejected_when_not_allowed(self) -> None:
		with self.assertRaises(PyMSError):
			self.make().lex(make_parse_context('2'))

	def test_serialize_value_to_name(self) -> None:
		self.assertEqual(self.make().serialize(1, serialize_context()), 'alpha')

	def test_serialize_unknown_value_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.make().serialize_basic(99)

	def test_decompile_valid_value(self) -> None:
		enum = self.make()
		scanner = BytesScanner(b'\x02')
		context = DecompileContext(b'\x02', make_language())
		self.assertEqual(enum.decompile(scanner, context), 2)

	def test_keywords(self) -> None:
		self.assertEqual(set(self.make().keywords()), {'alpha', 'beta'})

	def test_decompiled_value_can_be_serialized(self) -> None:
		# Any value the binary field can hold should decompile into something
		# that can be serialized back out, rather than producing a value that
		# later crashes serialization.
		enum = self.make()
		scanner = BytesScanner(b'\x05')
		context = DecompileContext(b'\x05', make_language())
		value = enum.decompile(scanner, context)
		enum.serialize(value, serialize_context())  # must not raise


class Test_BooleanCodeType(unittest.TestCase):
	def make(self) -> CodeType.BooleanCodeType:
		return CodeType.BooleanCodeType('b', 'b', Struct.l_u8)

	def test_lex_true(self) -> None:
		self.assertEqual(self.make().lex(make_parse_context('true')), True)

	def test_lex_false(self) -> None:
		self.assertEqual(self.make().lex(make_parse_context('false')), False)

	def test_lex_one(self) -> None:
		self.assertEqual(self.make().lex(make_parse_context('1')), True)

	def test_lex_zero(self) -> None:
		self.assertEqual(self.make().lex(make_parse_context('0')), False)

	def test_lex_invalid_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.make().lex(make_parse_context('maybe'))

	def test_keywords(self) -> None:
		self.assertEqual(set(self.make().keywords()), {'true', 'false'})

	def test_limits_are_zero_to_one(self) -> None:
		self.assertEqual(self.make().get_limits(make_parse_context('')), (0, 1))

	def test_compile_true_packs_one(self) -> None:
		builder = ByteCodeCompiler()
		self.make().compile(True, builder)
		self.assertEqual(builder.data, b'\x01')


class Test_FlagsCodeType(unittest.TestCase):
	def make(self, **kwargs) -> CodeType.FlagsCodeType:
		return CodeType.FlagsCodeType('f', 'f', Struct.l_u8, {'red': 0x01, 'green': 0x02, 'blue': 0x04}, **kwargs)

	def test_serialize_single_flag(self) -> None:
		self.assertEqual(self.make().serialize(0x02, serialize_context()), 'green')

	def test_serialize_multiple_flags(self) -> None:
		self.assertEqual(self.make().serialize(0x03, serialize_context()), 'red | green')

	def test_serialize_zero_is_empty_value(self) -> None:
		self.assertEqual(self.make().serialize(0, serialize_context()), '0')

	def test_serialize_unknown_bit_as_hex(self) -> None:
		flags = CodeType.FlagsCodeType('f', 'f', Struct.l_u8, {'red': 0x01})
		self.assertEqual(flags.serialize(0x80, serialize_context()), '0x80')

	def test_lex_single_flag(self) -> None:
		context = make_parse_context('red)')
		context.command_in_parens = True
		self.assertEqual(self.make().lex(context), 0x01)

	def test_lex_combined_flags(self) -> None:
		context = make_parse_context('red | blue)')
		context.command_in_parens = True
		self.assertEqual(self.make().lex(context), 0x05)

	def test_lex_empty_is_zero(self) -> None:
		# An empty parameter (immediately closing paren) means no flags.
		context = make_parse_context(')')
		context.command_in_parens = True
		self.assertEqual(self.make().lex(context), 0)

	def test_lex_invalid_flag_name_raises(self) -> None:
		context = make_parse_context('purple)')
		context.command_in_parens = True
		with self.assertRaises(PyMSError):
			self.make().lex(context)

	def test_lex_raw_hex_matching_known_flag(self) -> None:
		# A raw value whose bits all map to known flags is accepted without warning.
		context = make_parse_context('0x04)')
		context.command_in_parens = True
		self.assertEqual(self.make().lex(context), 0x04)
		self.assertEqual(context.warnings, [])

	def test_lex_raw_too_large_raises(self) -> None:
		context = make_parse_context('0x1FF)')
		context.command_in_parens = True
		with self.assertRaises(PyMSError):
			self.make().lex(context)

	def test_lex_raw_unknown_bit_warns(self) -> None:
		# A raw value with a bit that matches no known flag is still accepted, but warns.
		context = make_parse_context('0x80)')
		context.command_in_parens = True
		self.assertEqual(self.make().lex(context), 0x80)
		self.assertEqual(len(context.warnings), 1)

	def test_lex_case_insensitive_when_configured(self) -> None:
		flags = CodeType.FlagsCodeType('f', 'f', Struct.l_u8, {'alpha': 0x01, 'beta': 0x02}, case_sensitive=False)
		context = make_parse_context('ALPHA | BETA)')
		context.command_in_parens = True
		self.assertEqual(flags.lex(context), 0x03)

	def test_keywords(self) -> None:
		self.assertEqual(set(self.make().keywords()), {'red', 'green', 'blue'})

	def test_unknown_bit_round_trips_through_serialize_and_parse(self) -> None:
		# A value with a bit that has no name still serializes (as hex) and must
		# parse back to the same value, keeping decompile->compile stable.
		flags = CodeType.FlagsCodeType('f', 'f', Struct.l_u8, {'red': 0x01})
		text = flags.serialize(0x80, serialize_context())
		context = make_parse_context(text + ')')
		context.command_in_parens = True
		self.assertEqual(flags.lex(context), 0x80)


if __name__ == '__main__':
	unittest.main()
