from __future__ import annotations

from .CodeHandlers import RequirementCodeCommands
from .CodeHandlers.GraftLanguage import ReqGraftLanguage
from .CodeHandlers.GraftParseContext import GraftParseContext
from .CodeHandlers.GraftSerializeContext import GraftSerializeContext
from .CodeHandlers import SourceParsing

from ...Utilities.CodeHandlers.CodeCommand import CodeCommand, CodeCommandDefinition
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
		# Reads words up to (and including) the script's terminating 0xFFFF.
		# Loadable opcodes the language doesn't have are kept, so the file still loads and `validate` reports them
		commands: list[CodeCommand] = []
		in_sublist = False
		while True:
			word = scanner.scan(Struct.l_u16)
			if word == RequirementCodeCommands.END_OF_LIST:
				if not in_sublist:
					break
				in_sublist = False
				commands.append(CodeCommand(RequirementCodeCommands.EndLevelRequirements, []))
			elif word < RequirementCodeCommands.OPCODE_MIN:
				commands.append(CodeCommand(RequirementCodeCommands.HasCompleted, [word]))
			elif cmd_def := language.LOADABLE_OPCODES.get(word):
				params = [scanner.scan(Struct.l_u16) for _ in cmd_def.param_types]
				commands.append(CodeCommand(cmd_def, params))
				if cmd_def in RequirementCodeCommands.sublist_commands:
					in_sublist = True
			else:
				raise PyMSError('Scan', f'script {entry_id} has the word 0x{word:04X}, which is not an opcode for {language.DESCRIPTION.lower()}')
		return cls(entry_id, commands)

	def find_invalid_command(self, language: type[ReqGraftLanguage]) -> tuple[str, int] | None:
		# The first problem with the script, and the index of the command it's about.
		# Upgrade levels must be laid out the way the game uses them: it checks the commands before `level_1_requires`, then jumps from it to the first
		# `level_N_requires` word for the current upgrade level (searching past the end of the script if it's missing), and checks the commands after that word
		# up to the next 0xFFFF. When indexing the scripts, the game also reads the word after any 0xFFFF as the ID of the next script.
		levels = RequirementCodeCommands.level_commands
		level_indices: dict[CodeCommandDefinition, int] = {}
		# The `level_1_requires` or `level_2_requires` whose sub-list hasn't been ended yet
		sublist_index: int | None = None
		unended_sublist_error = f'A `level_1_requires` or `level_2_requires` sub-list is not ended with `end_level_requirements` in script {self.entry_id}'
		# The level command that must come directly after the last `end_level_requirements`
		expected_level: CodeCommandDefinition | None = None
		for index, command in enumerate(self.commands):
			definition = command.definition
			if not language.has_command(definition):
				return (f'`{definition.name}` is not available for {language.DESCRIPTION.lower()} in script {self.entry_id}', index)
			if expected_level is not None:
				if definition is not expected_level:
					return (f'`end_level_requirements` must be directly followed by `{expected_level.name}` in script {self.entry_id} (the game never checks commands placed between them, and can read them as the start of another script)', index)
				expected_level = None
			if definition == RequirementCodeCommands.HasCompleted:
				if command.params[0] >= RequirementCodeCommands.OPCODE_MIN:
					return (f'`has_completed` unit ID {command.params[0]} is too large (must be below {RequirementCodeCommands.OPCODE_MIN}) in script {self.entry_id}', index)
			elif definition in levels:
				if definition in level_indices:
					return (f'`{definition.name}` is used more than once in script {self.entry_id}', index)
				if sublist_index is not None:
					# The next level can't start until the previous level's sub-list is ended
					return (unended_sublist_error, sublist_index)
				position = levels.index(definition)
				if position and levels[position - 1] not in level_indices:
					if RequirementCodeCommands.Level1Requires not in level_indices:
						return (f'`{definition.name}` is used without a `level_1_requires` before it in script {self.entry_id} (the game only reaches it by jumping from `level_1_requires`)', index)
					return (f'`{definition.name}` must come after `{levels[position - 1].name}` in script {self.entry_id}', index)
				level_indices[definition] = index
				if definition in RequirementCodeCommands.sublist_commands:
					sublist_index = index
			elif definition == RequirementCodeCommands.EndLevelRequirements:
				if sublist_index is None:
					return (f'`end_level_requirements` used outside of a `level_1_requires` or `level_2_requires` sub-list in script {self.entry_id}', index)
				expected_level = levels[levels.index(self.commands[sublist_index].definition) + 1]
				sublist_index = None
			elif definition == RequirementCodeCommands.Or:
				if index and self.commands[index - 1].definition in levels:
					return (f'`or` can\'t directly follow `{self.commands[index - 1].definition.name}` in script {self.entry_id} (the upgrade level always counts as met, so the condition after the `or` would never matter)', index)
				if index + 1 < len(self.commands) and self.commands[index + 1].definition == RequirementCodeCommands.EndLevelRequirements:
					return (f'`or` can\'t directly come before `end_level_requirements` in script {self.entry_id}', index)
			if RequirementCodeCommands.Level1Requires in level_indices and RequirementCodeCommands.Level3Requires not in level_indices:
				for param in command.params:
					if param in (RequirementCodeCommands.Level2Requires.byte_code_id, RequirementCodeCommands.Level3Requires.byte_code_id):
						return (f'`{definition.name}` can\'t use the value 0x{param:04X} after `level_1_requires` in script {self.entry_id} (the game would jump to it as an upgrade level)', index)
		if sublist_index is not None:
			return (unended_sublist_error, sublist_index)
		if RequirementCodeCommands.Level1Requires in level_indices:
			missing = [level.name for level in levels if level not in level_indices]
			if missing:
				missing_text = ' and '.join(f'`{name}`' for name in missing)
				return (f'`level_1_requires` is used without {missing_text} after it in script {self.entry_id} (the game would search past the end of the script for the upgrade level)', level_indices[RequirementCodeCommands.Level1Requires])
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
			if definition == RequirementCodeCommands.EndLevelRequirements:
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
		# Sub-list commands and their `end_level_requirements` are indented an extra level, as is the rest of the script after `level_3_requires`
		in_sublist = False
		for command in self.commands:
			command.serialize(serialize_context)
			if (command.definition in RequirementCodeCommands.sublist_commands or command.definition is RequirementCodeCommands.Level3Requires) and not in_sublist:
				serialize_context.indent()
				in_sublist = True
			elif command.definition is RequirementCodeCommands.EndLevelRequirements and in_sublist:
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
