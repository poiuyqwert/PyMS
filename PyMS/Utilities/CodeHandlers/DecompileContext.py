
from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .LanguageDefinition import LanguageDefinition, LanguageContext
	from .CodeBlock import CodeBlock
	from .CodeCommand import CodeCommand

class DecompileContext:
	def __init__(self, data: bytes, language: LanguageDefinition) -> None:
		from .LanguageDefinition import LanguageContext
		self.data = data
		self.block_refs: dict[int, CodeBlock] = {}
		self.cmd_refs: dict[int, tuple[CodeBlock, CodeCommand]] = {}
		self.language = language
		self.language_context = LanguageContext()
