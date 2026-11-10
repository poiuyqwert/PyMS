from __future__ import annotations

from .CodeHandlers import RequirementCodeCommands
from .CodeHandlers.GraftLanguage import ReqGraftLanguage
from .CodeHandlers.GraftParseContext import GraftParseContext
from .CodeHandlers.GraftSerializeContext import GraftSerializeContext
from .CodeHandlers import SourceParsing

from ...Utilities.CodeHandlers.CodeCommand import CodeCommand
from ...Utilities.CodeHandlers import Tokens
from ...Utilities.BytesScanner import BytesScanner
from ...Utilities.PyMSError import PyMSError
from ...Utilities import Struct

# A requirement script. Whether it is valid depends on the language of the file it is for.
class ReqScript:
	def __init__(self, entry_id: int, commands: list[CodeCommand] | None = None) -> None:
		self.entry_id = entry_id
		self.commands = commands if commands is not None else []

	@classmethod
	def decode(cls, scanner: BytesScanner, entry_id: int, language: type[ReqGraftLanguage]) -> ReqScript:
		# Reads words up to (and including) the script's terminating 0xFFFF
		commands: list[CodeCommand] = []
		in_sublist = False
		while True:
			word = scanner.scan(Struct.l_u16)
			if word == RequirementCodeCommands.END_OF_LIST:
				if not in_sublist:
					break
				in_sublist = False
				commands.append(CodeCommand(RequirementCodeCommands.EndSublist, []))
			elif word < RequirementCodeCommands.OPCODE_MIN:
				commands.append(CodeCommand(RequirementCodeCommands.HasCompleted, [word]))
			elif cmd_def := language.lookup_opcode(word):
				params = [scanner.scan(Struct.l_u16) for _ in cmd_def.param_types]
				commands.append(CodeCommand(cmd_def, params))
				if cmd_def in RequirementCodeCommands.sublist_commands:
					in_sublist = True
			else:
				raise PyMSError('Scan', f'script {entry_id} has the word 0x{word:04X}, which is not an opcode for {language.DESCRIPTION.lower()}')
		return cls(entry_id, commands)

	def find_invalid_command(self, language: type[ReqGraftLanguage]) -> tuple[str, int] | None:
		# The first problem with the script, and the index of the command it's about
		sublist_index: int | None = None
		for index, command in enumerate(self.commands):
			definition = command.definition
			if not language.has_command(definition):
				return (f'`{definition.name}` is not available for {language.DESCRIPTION.lower()} in script {self.entry_id}', index)
			if definition == RequirementCodeCommands.EndSublist:
				if sublist_index is None:
					return (f'`end_sublist` used outside of an `upgrade_level_1` or `upgrade_level_2` sub-list in script {self.entry_id}', index)
				sublist_index = None
			elif definition == RequirementCodeCommands.HasCompleted:
				if command.params[0] >= RequirementCodeCommands.OPCODE_MIN:
					return (f'`has_completed` unit ID {command.params[0]} is too large (must be below {RequirementCodeCommands.OPCODE_MIN}) in script {self.entry_id}', index)
			elif definition in RequirementCodeCommands.sublist_commands:
				sublist_index = index
		if sublist_index is not None:
			return (f'An `upgrade_level_1` or `upgrade_level_2` sub-list is not ended with `end_sublist` in script {self.entry_id}', sublist_index)
		return None

	def validate(self, language: type[ReqGraftLanguage]) -> None:
		if invalid := self.find_invalid_command(language):
			raise PyMSError('Validate', invalid[0])

	def encode(self, language: type[ReqGraftLanguage]) -> bytes:
		# The script's words including its terminating 0xFFFF (but not its ID)
		self.validate(language)
		words: list[int] = []
		for command in self.commands:
			definition = command.definition
			if definition == RequirementCodeCommands.EndSublist:
				words.append(RequirementCodeCommands.END_OF_LIST)
			elif definition == RequirementCodeCommands.HasCompleted:
				words.append(command.params[0])
			else:
				assert definition.byte_code_id is not None
				words.append(definition.byte_code_id)
				words.extend(command.params)
		words.append(RequirementCodeCommands.END_OF_LIST)
		return Struct.l_au16(len(words)).pack(words)

	def serialize(self, serialize_context: GraftSerializeContext) -> None:
		# Sub-list commands and their `end_sublist` are indented an extra level, as is the rest of the script after `upgrade_level_3`
		in_sublist = False
		for command in self.commands:
			command.serialize(serialize_context)
			if (command.definition in RequirementCodeCommands.sublist_commands or command.definition is RequirementCodeCommands.UpgradeLevel3) and not in_sublist:
				serialize_context.indent()
				in_sublist = True
			elif command.definition is RequirementCodeCommands.EndSublist and in_sublist:
				serialize_context.dedent()
				in_sublist = False
		if in_sublist:
			serialize_context.dedent()

	@staticmethod
	def check_language(parse_context: GraftParseContext, language: type[ReqGraftLanguage]) -> None:
		if not isinstance(parse_context.language, language):
			raise PyMSError('Internal', f'{language.DESCRIPTION} scripts must be compiled with a parse context using `{language.__name__}`')

	@staticmethod
	def parse_command(parse_context: GraftParseContext, token: Tokens.Token, language: type[ReqGraftLanguage]) -> CodeCommand:
		# Parses the command that starts with `token` (the first token of its line)
		cmd_def = parse_context.language.lookup_command(token.raw_value, parse_context.language_context)
		if cmd_def is None:
			if any(other.name == token.raw_value for other in RequirementCodeCommands.all_req_commands):
				raise parse_context.error('Parse', f'`{token.raw_value}` is not available for {language.DESCRIPTION.lower()}')
			raise parse_context.error('Parse', f'Unknown command `{token.raw_value}`')
		try:
			return cmd_def.parse(parse_context)
		except PyMSError as e:
			parse_context.attribute_error(e)
			raise

	@classmethod
	def compile(cls, parse_context: GraftParseContext, entry_id: int, language: type[ReqGraftLanguage]) -> ReqScript:
		# Compiles only a script's commands (no header) into the script for `entry_id`
		cls.check_language(parse_context, language)
		keyword = language.HEADER_KEYWORD
		script = cls(entry_id)
		command_lines: list[int] = []
		while True:
			token = SourceParsing.next_line_token(parse_context)
			if isinstance(token, Tokens.EOFToken):
				break
			if not isinstance(token, Tokens.IdentifierToken):
				raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected a command)')
			if token.raw_value == keyword:
				raise parse_context.error('Parse', f'`{keyword}` headers are not allowed, the code is only the commands of {keyword.lower()} {entry_id}')
			line = parse_context.lexer.state.token_line
			script.commands.append(cls.parse_command(parse_context, token, language))
			command_lines.append(line)
		if invalid := script.find_invalid_command(language):
			error, index = invalid
			line = command_lines[index]
			raise PyMSError('Parse', error, line=line, code=parse_context.lexer.get_line_of_code(line))
		parse_context.finalize()
		return script
