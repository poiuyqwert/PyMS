
from __future__ import annotations

class PyMSWarning(Exception):
	def __init__(self, warn_type: str, warning: str, line: int | None = None, code: str | None = None, level: int = 0, warn_id: str | None = None, sub_warnings: list[PyMSWarning] | None = None) -> None:
		self.type = warn_type
		self.warning = warning
		self.line = line
		if self.line is not None:
			self.line += 1
		self.code = code
		self.level = level
		self.id = warn_id
		self.sub_warnings = sub_warnings or []

	def repr(self) -> str:
		from .utils import fit
		r = fit(f'{self.type} Warning{f" ({self.id})" if self.id else ""}: ', self.warning, end=True)
		if self.line and self.code:
			r += fit(f'    Line {self.line}: ', self.code, end=True)
		for w in self.sub_warnings:
			r += w.repr()
		return r

	def __repr__(self) -> str:
		from .utils import fit
		r = fit(f'{self.type} Warning{f" ({self.id})" if self.id else ""}: ', self.warning)
		if self.line and self.code:
			r += fit(f'    Line {self.line}: ', self.code)
		for w in self.sub_warnings:
			r += repr(w)
		return r[:-1]

class PyMSWarnList(Exception):
	def __init__(self, warnings: list[PyMSWarning]) -> None:
		self.warnings = warnings

	def __repr__(self) -> str:
		r = ''
		for w in self.warnings:
			r += repr(w)
		return r[:-1]
