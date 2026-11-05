from __future__ import annotations

from .Definitions import OPCODE_MIN, END_OF_LIST
from .CodeHandlers import RequirementCodeCommands
from .CodeHandlers.GraftLanguage import GraftLanguage
from ...Utilities.DataContext import DataContext
from .CodeHandlers.GraftParseContext import GraftParseContext
from .CodeHandlers.GraftSerializeContext import GraftSerializeContext
from .CodeHandlers import SourceParsing

from ...Utilities.CodeHandlers.CodeCommand import CodeCommand
from ...Utilities.CodeHandlers import Tokens
from ...Utilities.BytesScanner import BytesScanner
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities import Struct
from ...Utilities import Assets
from ...Utilities import IO

from collections import OrderedDict
import os

from typing import TYPE_CHECKING, Iterable
if TYPE_CHECKING:
	from .FGP import FGP

MAX_SCRIPT_ID = END_OF_LIST - 1

def _scan_word(scanner: BytesScanner) -> int:
	if scanner.remaining_len() < Struct.l_u16.size:
		raise PyMSError('Scan', 'the data ends before its end of list marker')
	return scanner.scan(Struct.l_u16)

class ReqScript:
	def __init__(self, entry_id: int, commands: list[CodeCommand] | None = None) -> None:
		self.entry_id = entry_id
		self.commands = commands if commands is not None else []

# Abstract class for the requirement script .graft files.
# They all share the same structure: a header word, then each ID followed by its 0xFFFF terminated script, ending with an ID of 0xFFFF.
class AbstractReqGraft:
	# Default filename for the file
	FILE_NAME: str
	# Path the Graft Hook loads the file from in an MPQ
	MPQ_PATH: str
	# What the file's scripts are the requirements for
	DESCRIPTION: str
	# Keyword for the header of each script in the source code
	HEADER_KEYWORD: str
	# The language of the file's scripts (which has the requirement opcodes that are available for the file)
	LANGUAGE: type[GraftLanguage]

	def __init__(self) -> None:
		# The first word of the file (always 0 in vanilla, unknown purpose)
		self.header_word = 0
		self._scripts: OrderedDict[int, ReqScript] = OrderedDict()

	@staticmethod
	def entry_name(data_context: DataContext, entry_id: int) -> str | None:
		# The name of what the script with ID `entry_id` is for
		raise NotImplementedError()

	@classmethod
	def default_path(cls) -> str:
		return Assets.data_file_path(os.path.join('Graft', cls.FILE_NAME))

	def new(self) -> None:
		# The vanilla StarCraft requirements
		self.load(self.default_path())

	@classmethod
	def _decode_script(cls, scanner: BytesScanner, entry_id: int) -> list[CodeCommand]:
		# Reads words up to (and including) the script's terminating 0xFFFF
		commands: list[CodeCommand] = []
		in_sublist = False
		while True:
			word = _scan_word(scanner)
			if word == END_OF_LIST:
				if not in_sublist:
					break
				in_sublist = False
				commands.append(CodeCommand(RequirementCodeCommands.EndSublist, []))
			elif word < OPCODE_MIN:
				commands.append(CodeCommand(RequirementCodeCommands.Has, [word]))
			elif cmd_def := cls.LANGUAGE.lookup_opcode(word):
				params = [_scan_word(scanner) for _ in cmd_def.param_types]
				commands.append(CodeCommand(cmd_def, params))
				if cmd_def in RequirementCodeCommands.sublist_commands:
					in_sublist = True
			else:
				raise PyMSError('Scan', f'script {entry_id} has the word 0x{word:04X}, which is not an opcode for {cls.DESCRIPTION.lower()}')
		return commands

	@classmethod
	def validate_script(cls, script: ReqScript) -> None:
		in_sublist = False
		for command in script.commands:
			definition = command.definition
			if not cls.LANGUAGE.has_command(definition):
				raise PyMSError('Validate', f'`{definition.name}` is not available for {cls.DESCRIPTION.lower()} in script {script.entry_id}')
			if definition == RequirementCodeCommands.EndSublist:
				if not in_sublist:
					raise PyMSError('Validate', f'`end_sublist` used outside of an `upgrade_level_1` or `upgrade_level_2` sub-list in script {script.entry_id}')
				in_sublist = False
			elif definition == RequirementCodeCommands.Has:
				if command.params[0] >= OPCODE_MIN:
					raise PyMSError('Validate', f'`has` unit ID {command.params[0]} is too large (must be below {OPCODE_MIN}) in script {script.entry_id}')
			elif definition in RequirementCodeCommands.sublist_commands:
				in_sublist = True
		if in_sublist:
			raise PyMSError('Validate', f'An `upgrade_level_1` or `upgrade_level_2` sub-list is not ended with `end_sublist` in script {script.entry_id}')

	@classmethod
	def _encode_script(cls, script: ReqScript) -> bytes:
		# The script's words including its terminating 0xFFFF (but not its ID)
		cls.validate_script(script)
		words: list[int] = []
		for command in script.commands:
			definition = command.definition
			if definition == RequirementCodeCommands.EndSublist:
				words.append(END_OF_LIST)
			elif definition == RequirementCodeCommands.Has:
				words.append(command.params[0])
			else:
				assert definition.byte_code_id is not None
				words.append(definition.byte_code_id)
				words.extend(command.params)
		words.append(END_OF_LIST)
		return Struct.l_au16(len(words)).pack(words)

	def load(self, any_input: IO.AnyInputBytes) -> list[PyMSWarning]:
		with IO.InputBytes(any_input) as f:
			data = f.read()
		warnings: list[PyMSWarning] = []
		scripts: OrderedDict[int, ReqScript] = OrderedDict()
		scanner = BytesScanner(data)
		try:
			header_word = _scan_word(scanner)
			while True:
				entry_id = _scan_word(scanner)
				if entry_id == END_OF_LIST:
					break
				commands = self._decode_script(scanner, entry_id)
				if entry_id in scripts:
					# The game uses the last script for an ID
					warnings.append(PyMSWarning(warn_type='Load', warning=f'Script {entry_id} is defined multiple times, only the last definition is kept'))
					del scripts[entry_id]
				scripts[entry_id] = ReqScript(entry_id, commands)
		except PyMSError as e:
			raise PyMSError('Load', f'Unsupported {self.FILE_NAME} file, {e.error}') from e
		except Exception as exc:
			raise PyMSError('Load', f'Unsupported {self.FILE_NAME} file, could possibly be invalid or corrupt') from exc
		if not scanner.at_end():
			warnings.append(PyMSWarning(warn_type='Load', warning=f'{scanner.remaining_len()} bytes of unused data after the end of the file will be discarded'))
		self.header_word = header_word
		self._scripts = scripts
		return warnings

	def save(self, output: IO.AnyOutputBytes) -> None:
		data = bytearray(Struct.l_u16.pack(self.header_word))
		for script in self._scripts.values():
			data += Struct.l_u16.pack(script.entry_id)
			try:
				data += self._encode_script(script)
			except PyMSError as e:
				raise PyMSError('Save', e.error) from e
		data += Struct.l_u16.pack(END_OF_LIST)
		with IO.OutputBytes(output) as f:
			f.write(bytes(data))

	def list_ids(self) -> list[int]:
		return list(self._scripts.keys())

	def get_script(self, entry_id: int) -> ReqScript | None:
		return self._scripts.get(entry_id)

	def set_script(self, script: ReqScript, allow_replace: bool = True) -> None:
		if script.entry_id < 0 or script.entry_id > MAX_SCRIPT_ID:
			raise PyMSError('Internal', f'Script ID {script.entry_id} is out of range (must be 0 to {MAX_SCRIPT_ID})')
		if script.entry_id in self._scripts:
			if not allow_replace:
				raise PyMSError('Internal', f'Script {script.entry_id} already exists')
			# Replace in place to keep the file order
			self._scripts[script.entry_id] = script
			return
		# New scripts are inserted in ID order
		scripts: OrderedDict[int, ReqScript] = OrderedDict()
		inserted = False
		for entry_id, existing in self._scripts.items():
			if not inserted and entry_id > script.entry_id:
				scripts[script.entry_id] = script
				inserted = True
			scripts[entry_id] = existing
		if not inserted:
			scripts[script.entry_id] = script
		self._scripts = scripts

	def set_scripts(self, scripts: Iterable[ReqScript]) -> None:
		for script in scripts:
			self.set_script(script)

	def replace_scripts(self, scripts: Iterable[ReqScript]) -> None:
		# Replaces all scripts, keeping their order (the file order of the vanilla scripts is not sorted)
		new_scripts: OrderedDict[int, ReqScript] = OrderedDict()
		for script in scripts:
			if script.entry_id in new_scripts:
				raise PyMSError('Internal', f'Script {script.entry_id} is included multiple times')
			if script.entry_id < 0 or script.entry_id > MAX_SCRIPT_ID:
				raise PyMSError('Internal', f'Script ID {script.entry_id} is out of range (must be 0 to {MAX_SCRIPT_ID})')
			new_scripts[script.entry_id] = script
		self._scripts = new_scripts

	def remove_script(self, entry_id: int) -> ReqScript | None:
		return self._scripts.pop(entry_id, None)

	def decompile(self, serialize_context: GraftSerializeContext, entry_ids: Iterable[int] | None = None) -> None:
		if entry_ids is None:
			entry_ids = self._scripts.keys()
		data_context = serialize_context.data_context
		first = True
		for entry_id in entry_ids:
			script = self._scripts.get(entry_id)
			if script is None:
				raise PyMSError('Decompile', f'There is no script with ID {entry_id}')
			if not first:
				serialize_context.write('\n')
			first = False
			serialize_context.write(f'{self.HEADER_KEYWORD} {entry_id}:')
			if data_context and (name := self.entry_name(data_context, entry_id)):
				serialize_context.write(serialize_context.formatters.comment.serialize([name]))
			serialize_context.write('\n')
			serialize_context.indent()
			# Sub-list commands and their `end_sublist` are indented an extra level, as is the rest of the script after `upgrade_level_3`
			in_sublist = False
			for command in script.commands:
				command.serialize(serialize_context)
				if (command.definition in RequirementCodeCommands.sublist_commands or command.definition is RequirementCodeCommands.UpgradeLevel3) and not in_sublist:
					serialize_context.indent()
					in_sublist = True
				elif command.definition is RequirementCodeCommands.EndSublist and in_sublist:
					serialize_context.dedent()
					in_sublist = False
			serialize_context.dedent(2 if in_sublist else 1)

	@classmethod
	def compile(cls, parse_context: GraftParseContext) -> list[ReqScript]:
		if not isinstance(parse_context.language, cls.LANGUAGE):
			raise PyMSError('Internal', f'{cls.__name__} scripts must be compiled with a parse context using `{cls.LANGUAGE.__name__}`')
		keyword = cls.HEADER_KEYWORD
		scripts: OrderedDict[int, ReqScript] = OrderedDict()
		script_lines: dict[int, int] = {}
		script: ReqScript | None = None
		while True:
			token = SourceParsing.next_line_token(parse_context)
			if isinstance(token, Tokens.EOFToken):
				break
			if not isinstance(token, Tokens.IdentifierToken):
				raise parse_context.error('Parse', f'Unexpected token `{token.raw_value}` (expected `{keyword}` header or a command)')
			if token.raw_value == keyword:
				line = parse_context.lexer.state.token_line
				entry_id = SourceParsing.parse_header_id(parse_context, keyword, MAX_SCRIPT_ID)
				if entry_id in scripts:
					raise parse_context.error('Parse', f'{keyword} {entry_id} is already defined on line {script_lines[entry_id] + 1}', line=line)
				script = ReqScript(entry_id)
				scripts[entry_id] = script
				script_lines[entry_id] = line
				continue
			cmd_def = parse_context.language.lookup_command(token.raw_value, parse_context.language_context)
			if cmd_def is None:
				if any(other.name == token.raw_value for other in RequirementCodeCommands.all_opcode_commands + [RequirementCodeCommands.EndSublist]):
					raise parse_context.error('Parse', f'`{token.raw_value}` is not available for {cls.DESCRIPTION.lower()}')
				raise parse_context.error('Parse', f'Unknown command `{token.raw_value}`')
			if script is None:
				raise parse_context.error('Parse', f'Command `{token.raw_value}` is not inside a `{keyword}` script')
			try:
				script.commands.append(cmd_def.parse(parse_context))
			except PyMSError as e:
				parse_context.attribute_error(e)
				raise
		for entry_id, script in scripts.items():
			try:
				cls.validate_script(script)
			except PyMSError as e:
				raise PyMSError('Parse', e.error, line=script_lines[entry_id], code=parse_context.lexer.get_line_of_code(script_lines[entry_id])) from e
		parse_context.finalize()
		return list(scripts.values())

	def import_fgp(self, fgp: FGP) -> list[PyMSWarning]:
		# Lays the FireGraft project's requirements over the current scripts.
		# All scripts are decoded first, so nothing is changed if any of them are invalid.
		warnings: list[PyMSWarning] = []
		changes: list[tuple[int, ReqScript | None]] = []
		for entry_id, words in fgp.requirements.get(type(self), {}).items():
			if words is None:
				changes.append((entry_id, None))
				continue
			if not words or words[-1] != END_OF_LIST:
				words = words + [END_OF_LIST]
			scanner = BytesScanner(Struct.l_au16(len(words)).pack(words))
			try:
				commands = self._decode_script(scanner, entry_id)
			except PyMSError as e:
				raise PyMSError('Import', f'Invalid FireGraft {self.DESCRIPTION.lower()}, {e.error}') from e
			if not scanner.at_end():
				warnings.append(PyMSWarning(warn_type='Import', warning=f'FireGraft script {entry_id} has data after its end of list, which was discarded'))
			changes.append((entry_id, ReqScript(entry_id, commands)))
		for entry_id, script in changes:
			if script is None:
				self.remove_script(entry_id)
			else:
				self.set_script(script)
		return warnings
