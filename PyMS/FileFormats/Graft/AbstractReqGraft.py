from __future__ import annotations

from .Definitions import END_OF_LIST, MAX_SCRIPT_ID
from .ReqScript import ReqScript
from .CodeHandlers.GraftLanguage import ReqGraftLanguage
from ...Utilities.DataContext import DataContext
from .CodeHandlers.GraftParseContext import GraftParseContext
from .CodeHandlers.GraftSerializeContext import GraftSerializeContext
from .CodeHandlers import SourceParsing

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

# Abstract class for the requirement script .graft files.
# They all share the same structure: a header word, then each ID followed by its 0xFFFF terminated script, ending with an ID of 0xFFFF.
class AbstractReqGraft:
	# Default filename for the file
	FILE_NAME: str
	# Path the Graft Hook loads the file from in an MPQ
	MPQ_PATH: str
	# The language of the file's scripts (which has the requirement opcodes that are available for the file, what they are the requirements for, and their header keyword)
	LANGUAGE: type[ReqGraftLanguage]

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

	def load(self, any_input: IO.AnyInputBytes) -> list[PyMSWarning]:
		with IO.InputBytes(any_input) as f:
			data = f.read()
		warnings: list[PyMSWarning] = []
		scripts: OrderedDict[int, ReqScript] = OrderedDict()
		scanner = BytesScanner(data)
		try:
			header_word = scanner.scan(Struct.l_u16)
			while True:
				entry_id = scanner.scan(Struct.l_u16)
				if entry_id == END_OF_LIST:
					break
				script = ReqScript.decode(scanner, entry_id, self.LANGUAGE)
				if entry_id in scripts:
					# The game uses the last script for an ID
					warnings.append(PyMSWarning(warn_type='Load', warning=f'Script {entry_id} is defined multiple times, only the last definition is kept'))
					del scripts[entry_id]
				scripts[entry_id] = script
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
				data += script.encode(self.LANGUAGE)
			except PyMSError as e:
				raise PyMSError('Save', e.error) from e
		data += Struct.l_u16.pack(END_OF_LIST)
		with IO.OutputBytes(output) as f:
			f.write(bytes(data))

	def list_ids(self) -> list[int]:
		return list(self._scripts.keys())

	def get_script(self, entry_id: int) -> ReqScript | None:
		return self._scripts.get(entry_id)

	@staticmethod
	def _check_entry_id(entry_id: int) -> None:
		if entry_id < 0 or entry_id > MAX_SCRIPT_ID:
			raise PyMSError('Internal', f'Script ID {entry_id} is out of range (must be 0 to {MAX_SCRIPT_ID})')

	def set_script(self, script: ReqScript, allow_replace: bool = True) -> None:
		self._check_entry_id(script.entry_id)
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
			self._check_entry_id(script.entry_id)
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
			serialize_context.write(f'{self.LANGUAGE.HEADER_KEYWORD} {entry_id}:')
			if data_context and (name := self.entry_name(data_context, entry_id)):
				serialize_context.write(serialize_context.formatters.comment.serialize([name]))
			serialize_context.write('\n')
			serialize_context.indent()
			script.serialize(serialize_context)
			serialize_context.dedent()

	def decompile_script(self, serialize_context: GraftSerializeContext, entry_id: int) -> None:
		# Only the script's commands (no header), starting unindented
		script = self._scripts.get(entry_id)
		if script is None:
			raise PyMSError('Decompile', f'There is no script with ID {entry_id}')
		script.serialize(serialize_context)

	@classmethod
	def compile(cls, parse_context: GraftParseContext) -> list[ReqScript]:
		ReqScript.check_language(parse_context, cls.LANGUAGE)
		keyword = cls.LANGUAGE.HEADER_KEYWORD
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
			command = ReqScript.parse_command(parse_context, token, cls.LANGUAGE)
			if script is None:
				raise parse_context.error('Parse', f'Command `{token.raw_value}` is not inside a `{keyword}` script')
			script.commands.append(command)
		for entry_id, script in scripts.items():
			try:
				script.validate(cls.LANGUAGE)
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
				script = ReqScript.decode(scanner, entry_id, self.LANGUAGE)
			except PyMSError as e:
				raise PyMSError('Import', f'Invalid FireGraft {self.LANGUAGE.DESCRIPTION.lower()}, {e.error}') from e
			if not scanner.at_end():
				warnings.append(PyMSWarning(warn_type='Import', warning=f'FireGraft script {entry_id} has data after its end of list, which was discarded'))
			changes.append((entry_id, script))
		for entry_id, change in changes:
			if change is None:
				self.remove_script(entry_id)
			else:
				self.set_script(change)
		return warnings
