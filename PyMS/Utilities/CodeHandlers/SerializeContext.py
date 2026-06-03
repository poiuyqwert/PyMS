
from __future__ import annotations

from .Formatters import Formatters
from .DecompileStrategy import DecompileStrategy

import re

from typing import TYPE_CHECKING, IO
if TYPE_CHECKING:
	from .DefinitionsHandler import DefinitionsHandler

class SerializeContext:
	def __init__(self, output: IO[str], definitions: DefinitionsHandler | None = None, formatters: Formatters | None = None) -> None:
		self._output = output
		self.definitions = definitions
		self.formatters = formatters if formatters is not None else Formatters()
		self.strategy = DecompileStrategy.empty()
		self._indent_level = 0
		self._indent_next = False

	RE_INDENT_NEWLINE = re.compile(r'\n(?=\s*\S)')
	def write(self, text: str, force_indent: bool = False) -> None:
		indent = self.formatters.indent * self._indent_level
		if force_indent or (self._indent_next and self._indent_level):
			self._output.write(indent)
		if self._indent_level:
			text = SerializeContext.RE_INDENT_NEWLINE.sub('\n' + indent, text)
		self._output.write(text)
		self._indent_next = text.endswith('\n')

	def indent(self, levels: int = 1) -> None:
		self._indent_level += levels

	def dedent(self, levels: int = 1) -> None:
		self._indent_level = max(0, self._indent_level - levels)
		self._indent_next = False # Should this be cleared or not?
