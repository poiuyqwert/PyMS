
from __future__ import annotations

from ..PyMSError import PyMSError
from ..PyMSWarning import PyMSWarning

from dataclasses import dataclass

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .CodeBlock import CodeBlock
	from .CodeCommand import CodeCommand
	from .DefinitionsHandler import DefinitionsHandler
	from .CodeDirective import CodeDirective
	from .Lexer import Lexer

class BlockReferenceResolver(object):
	def __init__(self, source_line: int | None) -> None:
		self.source_line = source_line

	def block_defined(self, block: CodeBlock) -> None:
		raise NotImplementedError(self.__class__.__name__ + '.block_defined()')

class CommandParamBlockReferenceResolver(BlockReferenceResolver):
	def __init__(self, cmd: CodeCommand, param_index: int, source_line: int | None) -> None:
		BlockReferenceResolver.__init__(self, source_line)
		self.cmd = cmd
		self.param_index = param_index

	def block_defined(self, block: CodeBlock) -> None:
		self.cmd.params[self.param_index] = block

@dataclass
class BlockMetadata:
	name: str
	source_line: int

class ParseContext(object):
	def __init__(self, lexer: Lexer, definitions: DefinitionsHandler | None = None) -> None:
		self.lexer = lexer
		self.definitions = definitions

		self.active_block: CodeBlock | None = None
		self.command_in_parens = False
		self.warnings: list[PyMSWarning] = []
		self.block_metadata: dict[CodeBlock, BlockMetadata] = {}
		self.missing_blocks: dict[str, list[BlockReferenceResolver]] = {}
		self.defined_blocks: dict[str, CodeBlock] = {}
		self.unused_blocks: set[str] = set()
		self.suppress_warnings: list[str] = []
		self.suppress_warnings_next_line: list[str] = []

	def lookup_block(self, name: str, use: bool = True) -> CodeBlock | None:
		block = self.defined_blocks.get(name)
		if not block:
			return None
		if use and name in self.unused_blocks:
			self.unused_blocks.remove(name)
		return block

	def lookup_block_metadata(self, block: CodeBlock) -> BlockMetadata | None:
		return self.block_metadata.get(block)

	def lookup_block_metadata_by_name(self, name: str) -> BlockMetadata | None:
		if block := self.lookup_block(name):
			return self.lookup_block_metadata(block)
		return None

	def define_block(self, block: CodeBlock, metadata: BlockMetadata) -> None:
		if metadata.name in self.defined_blocks:
			raise PyMSError('Parse', "Block with name '%s' is already defined" % metadata.name)
		self.block_metadata[block] = metadata
		self.defined_blocks[metadata.name] = block
		if metadata.name in self.missing_blocks:
			for resolver in self.missing_blocks[metadata.name]:
				resolver.block_defined(block)
			del self.missing_blocks[metadata.name]
		else:
			self.unused_blocks.add(metadata.name)

	def missing_block(self, name: str, reference_resolver: BlockReferenceResolver) -> None:
		if name in self.defined_blocks:
			raise PyMSError('Internal', "Block with name '%s' is being set as missing but is already defined" % name, line=reference_resolver.source_line)
		if not name in self.missing_blocks:
			self.missing_blocks[name] = []
		self.missing_blocks[name].append(reference_resolver)

	def finalize(self) -> None:
		for block_name in self.unused_blocks:
			block = self.defined_blocks[block_name]
			block_metadata = self.block_metadata[block]
			self.add_warning(PyMSWarning('Parse', "Block with name '%s' is unused and will be discarded" % block_name, line=block_metadata.source_line, id='block_unused'))
		if self.active_block:
			block_metadata = self.block_metadata[self.active_block]
			raise self.error('Parse', "The last block (named '%s') does not end" % block_metadata.name, line=block_metadata.source_line)
		self.unused_blocks.clear()
		if self.missing_blocks:
			earliest_line = None
			earliest_block_name = None
			for block_name,resolvers in self.missing_blocks.items():
				for resolver in resolvers:
					if earliest_line is None or (resolver.source_line is not None and resolver.source_line < earliest_line):
						earliest_line = resolver.source_line
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
			error.line = self.lexer.state.line
		error.code = self.lexer.get_line_of_code(error.line)

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
