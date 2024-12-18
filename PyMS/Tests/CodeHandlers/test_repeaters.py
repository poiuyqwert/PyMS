
from ...Utilities.CodeHandlers import CodeType
from ...Utilities.CodeHandlers import CodeCommand
from ...Utilities.CodeHandlers import LanguageDefinition
from ...Utilities.CodeHandlers.SerializeContext import SerializeContext
from ...Utilities.CodeHandlers.SourceCodeParser import CommandSourceCodeParser
from ...Utilities.CodeHandlers.ParseContext import ParseContext
from ...Utilities.CodeHandlers.Lexer import Lexer
from ...Utilities.CodeHandlers import Tokens
from ...Utilities.CodeHandlers.CodeBlock import CodeBlock
from ...Utilities.CodeHandlers.ByteCodeCompiler import ByteCodeCompiler
from ...Utilities.CodeHandlers.DecompileContext import DecompileContext
from ...Utilities import Struct
from ...Utilities.BytesScanner import BytesScanner

import unittest, io

RepeaterType = CodeType.IntCodeType('repeater', 'repeater', Struct.l_u8, param_repeater=True)
IntType = CodeType.IntCodeType('int', 'int', Struct.l_u16)

BasicCommand = CodeCommand.CodeCommandDefinition('basic', 'basic', 0, [RepeaterType, IntType])
AdvCommand = CodeCommand.CodeCommandDefinition('adv', 'adv', 1, [IntType, RepeaterType, IntType, IntType])


basic_command = CodeCommand.CodeCommand(BasicCommand, [0x02, 0x2000, 0x2100])
basic_code = 'basic 2 8192 8448'
basic_bytecode = b'\x00\x02\x00\x20\x00\x21'

adv_command = CodeCommand.CodeCommand(AdvCommand, [0x1000, 0x02, 0x2000, 0x2100, 0x1100])
adv_code = 'adv 4096 2 8192 8448 4352'
adv_bytecode = b'\x01\x00\x10\x02\x00\x20\x00\x21\x00\x11'

language = LanguageDefinition.LanguageDefinition([
	LanguageDefinition.LanguagePlugin(
		LanguageDefinition.LanguagePlugin.CORE_ID,
		[
			BasicCommand,
			AdvCommand
		],
		[
			RepeaterType,
			IntType
		]
	)
])

class Test_Repeaters(unittest.TestCase):
	def test_repeater_decompile_basic(self) -> None:
		scanner = BytesScanner(basic_bytecode, 1)
		context = DecompileContext(basic_bytecode, language)
		command = BasicCommand.decompile(scanner, context)
		self.assertEqual(command.params, basic_command.params)

	def test_repeater_serialize_basic(self) -> None:
		code = io.StringIO()
		context = SerializeContext(code)
		basic_command.serialize(context)
		self.assertEqual(code.getvalue(), basic_code + '\n')

	def test_repeater_parse_basic(self) -> None:
		lexer = Lexer(basic_code)
		lexer.register_token_type(Tokens.WhitespaceToken, skip=True)
		lexer.register_token_type(Tokens.IdentifierToken)
		lexer.register_token_type(Tokens.IntegerToken)
		context = ParseContext(lexer, language)
		context.active_block = CodeBlock()
		parser = CommandSourceCodeParser()
		parser.parse(context)
		self.assertEqual(context.active_block.commands[-1].params, basic_command.params)

	def test_repeater_compile_basic(self) -> None:
		builder = ByteCodeCompiler()
		basic_command.compile(builder)
		self.assertEqual(builder.data, basic_bytecode)

	def test_repeater_decompile_adv(self) -> None:
		scanner = BytesScanner(adv_bytecode, 1)
		context = DecompileContext(adv_bytecode, language)
		command = AdvCommand.decompile(scanner, context)
		self.assertEqual(command.params, adv_command.params)

	def test_repeater_serialize_adv(self) -> None:
		code = io.StringIO()
		context = SerializeContext(code)
		adv_command.serialize(context)
		self.assertEqual(code.getvalue(), adv_code + '\n')

	def test_repeater_parse_adv(self) -> None:
		lexer = Lexer(adv_code)
		lexer.register_token_type(Tokens.WhitespaceToken, skip=True)
		lexer.register_token_type(Tokens.IdentifierToken)
		lexer.register_token_type(Tokens.IntegerToken)
		context = ParseContext(lexer, language)
		context.active_block = CodeBlock()
		parser = CommandSourceCodeParser()
		parser.parse(context)
		self.assertEqual(context.active_block.commands[-1].params, adv_command.params)

	def test_repeater_compile_adv(self) -> None:
		builder = ByteCodeCompiler()
		adv_command.compile(builder)
		self.assertEqual(builder.data, adv_bytecode)
