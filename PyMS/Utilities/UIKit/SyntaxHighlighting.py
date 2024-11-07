
from __future__ import annotations

import re

from dataclasses import dataclass

from typing import TYPE_CHECKING, Sequence
if TYPE_CHECKING:
	from ..Config import HighlightStyle

@dataclass
class HighlightComponent:
	name: str
	description: str
	highlight_style: HighlightStyle
	tag: str | None = None

	@property
	def tag_name(self) -> str:
		return self.tag or self.name.replace(' ', '')

@dataclass
class HighlightPattern:
	highlight: HighlightComponent
	pattern: str

	@property
	def full_pattern(self) -> str:
		return f'(?P<{self.highlight.tag_name}>{self.pattern})'

@dataclass
class SyntaxComponent:
	patterns: Sequence[HighlightPattern | str]

	@property
	def full_pattern(self) -> str:
		full_pattern = ''
		for pattern in self.patterns:
			if isinstance(pattern, HighlightPattern):
				full_pattern += pattern.full_pattern
			else:
				full_pattern += pattern
		return full_pattern

	def highlight_components(self) -> Sequence[HighlightComponent]:
		return [pattern.highlight for pattern in self.patterns if isinstance(pattern, HighlightPattern)]

@dataclass
class SyntaxHighlighting:
	syntax_components: Sequence[SyntaxComponent]
	highlight_components: Sequence[HighlightComponent]

	@property
	def full_pattern(self) -> str:
		return '|'.join(component.full_pattern for component in self.syntax_components)

	@property
	def re_pattern(self) -> re.Pattern:
		return re.compile(self.full_pattern)

	def all_highlight_components(self) -> Sequence[HighlightComponent]:
		highlight_components: list[HighlightComponent] = []
		for syntax_component in self.syntax_components:
			highlight_components.extend(syntax_component.highlight_components())
		highlight_components.extend(self.highlight_components)
		return highlight_components
