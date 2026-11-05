
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
		self._at_line_start = True

	# Blank (or whitespace-only) lines are never indented
	RE_CONTENT_LINE = re.compile(r'[^\S\n]*\S')
	RE_INDENT_NEWLINE = re.compile(r'\n(?=[^\S\n]*\S)')
	def write(self, text: str) -> None:
		if not text:
			return
		if self._indent_level:
			indent = self.formatters.indent * self._indent_level
			if self._at_line_start and SerializeContext.RE_CONTENT_LINE.match(text):
				self._output.write(indent)
			text = SerializeContext.RE_INDENT_NEWLINE.sub('\n' + indent, text)
		self._output.write(text)
		self._at_line_start = text.endswith('\n')

	def indent(self, levels: int = 1) -> None:
		self._indent_level += levels

	def dedent(self, levels: int = 1) -> None:
		self._indent_level = max(0, self._indent_level - levels)
