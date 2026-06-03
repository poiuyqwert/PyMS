
from ._helpers import make_parse_context, make_language, ByteType

from ...Utilities.CodeHandlers import CodeCommand
from ...Utilities.CodeHandlers.SerializeContext import SerializeContext
from ...Utilities.CodeHandlers.DecompileContext import DecompileContext
from ...Utilities.CodeHandlers.ByteCodeCompiler import ByteCodeCompiler
from ...Utilities.BytesScanner import BytesScanner
from ...Utilities.PyMSError import PyMSError

import unittest, io


IncCommand = CodeCommand.CodeCommandDefinition('inc', 'inc', 0, [ByteType])
PairCommand = CodeCommand.CodeCommandDefinition('pair', 'pair', 1, [ByteType, ByteType])
VirtualCommand = CodeCommand.CodeCommandDefinition('virtual', 'virtual', None, [ByteType])

LANGUAGE = make_language([IncCommand, PairCommand], [ByteType])


def parse_command(definition, code: str):
	# `CodeCommandDefinition.parse` runs after the command name is consumed, so
	# `code` is just the parameter list.
	context = make_parse_context(code, LANGUAGE)
	return definition.parse(context)


class Test_FindByName(unittest.TestCase):
	def test_found(self) -> None:
		self.assertIs(CodeCommand.CodeCommandDefinition.find_by_name('pair', [IncCommand, PairCommand]), PairCommand)

	def test_missing(self) -> None:
		self.assertIsNone(CodeCommand.CodeCommandDefinition.find_by_name('zzz', [IncCommand]))


class Test_Parse(unittest.TestCase):
	def test_flat_single_param(self) -> None:
		command = parse_command(IncCommand, '5')
		self.assertEqual(command.params, [5])

	def test_parens_single_param(self) -> None:
		command = parse_command(IncCommand, '(5)')
		self.assertEqual(command.params, [5])

	def test_parens_multiple_params(self) -> None:
		command = parse_command(PairCommand, '(5, 6)')
		self.assertEqual(command.params, [5, 6])

	def test_flat_multiple_params(self) -> None:
		command = parse_command(PairCommand, '5 6')
		self.assertEqual(command.params, [5, 6])

	def test_trailing_token_is_rejected(self) -> None:
		with self.assertRaises(PyMSError):
			parse_command(IncCommand, '5 6')

	def test_missing_comma_in_parens_rejected(self) -> None:
		with self.assertRaises(PyMSError):
			parse_command(PairCommand, '(5 6)')

	def test_unterminated_parens_rejected(self) -> None:
		with self.assertRaises(PyMSError):
			parse_command(PairCommand, '(5, 6')


class Test_Decompile(unittest.TestCase):
	def test_reads_params_from_bytes(self) -> None:
		data = b'\x05'
		scanner = BytesScanner(data)
		context = DecompileContext(data, LANGUAGE)
		command = IncCommand.decompile(scanner, context)
		self.assertEqual(command.params, [5])


class Test_Compile(unittest.TestCase):
	def test_emits_id_and_params(self) -> None:
		builder = ByteCodeCompiler()
		CodeCommand.CodeCommand(IncCommand, [5]).compile(builder)
		self.assertEqual(builder.data, b'\x00\x05')

	def test_command_without_bytecode_id_raises_clean_error(self) -> None:
		# A parse-only/virtual command has no byte code id; compiling it should
		# surface a proper PyMSError rather than an assertion.
		builder = ByteCodeCompiler()
		with self.assertRaises(PyMSError):
			CodeCommand.CodeCommand(VirtualCommand, [5]).compile(builder)


class Test_Serialize(unittest.TestCase):
	def test_serializes_name_and_params(self) -> None:
		output = io.StringIO()
		context = SerializeContext(output)
		CodeCommand.CodeCommand(IncCommand, [5]).serialize(context)
		self.assertEqual(output.getvalue(), 'inc 5\n')


class Test_IterParams(unittest.TestCase):
	def test_yields_value_and_type_pairs(self) -> None:
		command = CodeCommand.CodeCommand(PairCommand, [5, 6])
		pairs = list(command.iter_params())
		self.assertEqual([value for value, _ in pairs], [5, 6])
		self.assertEqual([code_type for _, code_type in pairs], [ByteType, ByteType])


class Test_FullHelpText(unittest.TestCase):
	def test_placeholder_one_refers_to_first_parameter(self) -> None:
		command = CodeCommand.CodeCommandDefinition('cmd', 'set {1} to value', 0, [ByteType])
		help_text = command.full_help_text()
		self.assertNotIn('{1}', help_text)
		self.assertIn('byte', help_text)

	def test_repeated_param_types_are_numbered(self) -> None:
		command = CodeCommand.CodeCommandDefinition('cmd', 'help', 0, [ByteType, ByteType])
		help_text = command.full_help_text()
		self.assertIn('byte(1)', help_text)
		self.assertIn('byte(2)', help_text)


if __name__ == '__main__':
	unittest.main()
