
from __future__ import annotations

from .CodeBlock import CodeBlock
from . import Tokens

from ..PyMSError import PyMSError
from ..PyMSWarning import PyMSWarning

from dataclasses import dataclass

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from .CodeHeader import CodeHeader
	from .DefinitionsHandler import DefinitionsHandler
	from .CodeDirective import CodeDirective
	from .Lexer import Lexer
	from .CodeType import CodeType
	from .LanguageDefinition import LanguageDefinition

@dataclass
class BlockMetadata:
	name: str
	definition_line: int | None
	uses: list[CodeHeader]

	def merge(self, other: BlockMetadata):
		self.definition_line = other.definition_line
		for use in other.uses:
			if not use in self.uses:
				self.uses.append(use)

class ParseContext(object):
	def __init__(self, lexer: Lexer, language: LanguageDefinition, definitions: DefinitionsHandler | None = None) -> None:
		from .LanguageDefinition import LanguageContext
		self.lexer = lexer
		self.language = language
		self.language_context = LanguageContext()
		self.definitions = definitions

		self.active_block: CodeBlock | None = None
		self.command_in_parens = False
		self.warnings: list[PyMSWarning] = []
		self.block_metadata: dict[CodeBlock, BlockMetadata] = {}
		self.missing_blocks: dict[str, list[int]] = {}
		self.blocks: dict[str, CodeBlock] = {}
		self.unused_blocks: set[str] = set()
		self.suppress_warnings: list[str] = []
		self.suppress_warnings_next_line: list[str] = []

	def get_block(self, name: str) -> CodeBlock:
		block = self.blocks.get(name)
		if not block:
			block = CodeBlock()
			self.blocks[name] = block
			self.block_metadata[block] = BlockMetadata(name, None, [])
			self.missing_block(name, self.lexer.state.line)
		elif name in self.unused_blocks:
			self.unused_blocks.remove(name)
		return block

	def lookup_block_metadata(self, block: CodeBlock) -> BlockMetadata | None:
		return self.block_metadata.get(block)

	def lookup_block_metadata_by_name(self, name: str) -> BlockMetadata | None:
		if block := self.blocks.get(name):
			return self.lookup_block_metadata(block)
		return None

	def define_block(self, name: str, line: int) -> CodeBlock:
		metadata = self.lookup_block_metadata_by_name(name)
		if metadata is not None and metadata.definition_line is not None:
			raise self.error('Parse', "A block named '%s' is already defined on line %d" % (name, metadata.definition_line))
		block = self.get_block(name)
		self.block_metadata[block].definition_line = line
		if name in self.missing_blocks:
			del self.missing_blocks[name]
		else:
			self.unused_blocks.add(name)
		return block

	def add_block_owner(self, block: CodeBlock, owner: CodeHeader) -> None:
		block.owners.append(owner)
		self.add_block_use(block, owner)

	def add_block_use(self, block: CodeBlock, use: CodeHeader) -> None:
		if use in self.block_metadata[block].uses:
			return
		self.block_metadata[block].uses.append(use)
		if block.next_block is not None:
			self.add_block_use(block.next_block, use)
		for ref_block in block.ref_blocks:
			self.add_block_use(ref_block, use)

	def add_block_use_block(self, block: CodeBlock, use_block: CodeBlock) -> None:
		metadata = self.block_metadata[use_block]
		for use in metadata.uses:
			self.add_block_use(block, use)

	def missing_block(self, name: str, source_line: int) -> None:
		block_metadata = self.lookup_block_metadata_by_name(name)
		if block_metadata and block_metadata.definition_line is not None:
			raise PyMSError('Internal', "Block with name '%s' is being set as missing but is already defined" % name, line=source_line)
		if not name in self.missing_blocks:
			self.missing_blocks[name] = []
		self.missing_blocks[name].append(source_line)

	def finalize(self) -> None:
		for block_name in self.unused_blocks:
			block = self.blocks[block_name]
			block_metadata = self.block_metadata[block]
			self.add_warning(PyMSWarning('Parse', "Block with name '%s' is unused and will be discarded" % block_name, line=block_metadata.definition_line, id='block_unused'))
		if self.active_block:
			block_metadata = self.block_metadata[self.active_block]
			raise self.error('Parse', "The last block (named '%s') does not end" % block_metadata.name, line=block_metadata.definition_line)
		self.unused_blocks.clear()
		if self.missing_blocks:
			earliest_line = None
			earliest_block_name = None
			for block_name,lines in self.missing_blocks.items():
				first_line = min(lines)
				if earliest_line is None or first_line < earliest_line:
					earliest_line = first_line
					earliest_block_name = block_name
			raise PyMSError('Parse', "Block with name '%s' is not defined" % earliest_block_name, line=earliest_line)
		self.warnings = list(warning for warning in self.warnings if warning.id not in self.suppress_warnings)

	def handle_directive(self, directive: CodeDirective) -> None:
		pass

	def error(self, type: str, error: str, line: int | None = None, level=1) -> PyMSError:
		if line is None:
			line = self.lexer.state.line
		return PyMSError(type, error, line, self.lexer.get_line_of_code(line), level=level)

	def attribute_error(self, error: PyMSError) -> None:
		if error.line is None:
			error.line = self.lexer.state.line + 1
		if error.code is None:
			error.code = self.lexer.get_line_of_code(error.line - 1)

	def warning(self, type: str, warning: str, line: int | None = None, level: int = 0, id: str | None = None) -> PyMSWarning:
		if line is None:
			line = self.lexer.state.line
		return PyMSWarning(type, warning, line=line, code=self.lexer.get_line_of_code(line), level=level, id=id)

	def attribute_warning(self, warning: PyMSWarning) -> None:
		if warning.line is None:
			warning.line = self.lexer.state.line
		warning.code = self.lexer.get_line_of_code(warning.line)

	def add_warning(self, warning: PyMSWarning) -> None:
		if warning.id in self.suppress_warnings_next_line:
			return
		self.attribute_warning(warning)
		self.warnings.append(warning)

	def add_supressed_warning_id(self, warning_id: str, next_line: bool = False) -> None:
		if next_line:
			self.suppress_warnings_next_line.append(warning_id)
		else:
			self.suppress_warnings.append(warning_id)

	def next_line(self) -> None:
		self.suppress_warnings_next_line = []

	def lookup_param_value(self, param_type: CodeType) -> Any | None:
		value: Any | None = None
		token = self.lexer.next_token(peek=True)
		# TODO: Should variable resolution be done inside the type?
		if isinstance(token, Tokens.IdentifierToken) and self.definitions:
			variable = self.definitions.get_variable(token.raw_value)
			if variable:
				if not param_type.accepts(variable.type):
					raise self.error('Parse', f"Incorrect type on varaible '{variable.name}'. Excpected '{param_type.name}' but got '{variable.type.name}'")
				value = variable.value
				try:
					param_type.validate(value, self, token.raw_value)
				except PyMSError as e:
					e.warnings.append(PyMSWarning('Variable', f"The variable '{variable.name}' of type '{variable.type.name}' was set to '{variable.value}' when the above error happened"))
					raise
				_ = self.lexer.next_token()
		return value
