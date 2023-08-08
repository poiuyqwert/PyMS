
from __future__ import annotations

from ..PyMSError import PyMSError
from ..PyMSWarning import PyMSWarning

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .CodeBlock import CodeBlock
	from .CodeCommand import CodeCommand
	from .DefinitionsHandler import DefinitionsHandler

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

	def block_defined(self, block): # type: (CodeBlock) -> None
		self.cmd.params[self.param_index] = block

class ParseContext(object):
	def __init__(self, definitions: DefinitionsHandler | None = None) -> None:
		self.definitions = definitions
		self.warnings: list[PyMSWarning] = []
		self.missing_blocks: dict[str, list[BlockReferenceResolver]] = {}
		self.defined_blocks: dict[str, tuple[CodeBlock, int | None]] = {}
		self.unused_blocks: set[str] = set()

	def lookup_block(self, name: str, use: bool = True) -> (CodeBlock | None):
		block_info = self.defined_blocks.get(name)
		if not block_info:
			return None
		if use and name in self.unused_blocks:
			self.unused_blocks.remove(name)
		return block_info[0]

	def lookup_block_source_line(self, name: str) -> int | None:
		block_info = self.defined_blocks.get(name)
		if not block_info:
			return None
		return block_info[1]

	def lookup_block_name(self, lookup_block: CodeBlock) -> str | None:
		for block_name,(block,_) in self.defined_blocks.items():
			if block == lookup_block:
				return block_name
		return None

	def define_block(self, name: str, block: CodeBlock, source_line: int | None) -> None:
		if name in self.defined_blocks:
			raise PyMSError('Parse', "Block with name '%s' is already defined" % name)
		self.defined_blocks[name] = (block, source_line)
		if name in self.missing_blocks:
			for resolver in self.missing_blocks[name]:
				resolver.block_defined(block)
			del self.missing_blocks[name]
		else:
			self.unused_blocks.add(name)

	def missing_block(self, name: str, reference_resolver: BlockReferenceResolver) -> None:
		if name in self.defined_blocks:
			raise PyMSError('Internal', "Block with name '%s' is being set as missing but is already defined" % name)
		if not name in self.missing_blocks:
			self.missing_blocks[name] = []
		self.missing_blocks[name].append(reference_resolver)

	def finalize(self) -> None:
		for block_name in self.unused_blocks:
			_,source_line = self.defined_blocks[block_name]
			self.warnings.append(PyMSWarning('Parse', "Block with name '%s' is unused and will be discarded" % block_name, line=source_line))
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
