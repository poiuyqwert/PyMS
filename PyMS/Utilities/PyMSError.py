
from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .PyMSWarning import PyMSWarning

class PyMSError(Exception):
	def __init__(self, err_type: str, error: str, *, line: int | None = None, code: str | None = None, warnings: list[PyMSWarning] | None = None, level: int = 1, cause: BaseException | None = None) -> None:
		self.type = err_type
		self.error = error
		self.line = line
		if self.line is not None:
			self.line += 1
		self.code = code
		self.warnings = warnings or []
		self.level = level
		if cause is not None:
			self.__cause__ = cause

	def __repr__(self) -> str:
		r = f'{self.type} Error: {self.error}'
		if self.line:
			if self.code is not None:
				r += f'\n    Line {self.line}: {self.code}'
			else:
				r += f'\n    Line {self.line}'
		for w in self.warnings:
			r += '\n' + repr(w)
		return r

	def __str__(self) -> str:
		return repr(self)
