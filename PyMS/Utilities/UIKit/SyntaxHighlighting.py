
from __future__ import annotations

import re

from dataclasses import dataclass
from functools import cached_property

from typing import TYPE_CHECKING, Iterator, Sequence
if TYPE_CHECKING:
	from ..Config import HighlightStyle

__all__ = [
	'HighlightComponent',
	'HighlightPattern',
	'SyntaxComponent',
	'SyntaxHighlighting',
]

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
	# Patterns highlighted only within the span matched by this pattern
	nested: Sequence[HighlightPattern] = ()

	@property
	def full_pattern(self) -> str:
		return f'(?P<{self.highlight.tag_name}>{self.pattern})'

	def highlight_components(self) -> Sequence[HighlightComponent]:
		highlight_components = [self.highlight]
		for nested in self.nested:
			highlight_components.extend(nested.highlight_components())
		return highlight_components

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

	def highlight_patterns(self) -> Sequence[HighlightPattern]:
		return [pattern for pattern in self.patterns if isinstance(pattern, HighlightPattern)]

	def highlight_components(self) -> Sequence[HighlightComponent]:
		highlight_components: list[HighlightComponent] = []
		for pattern in self.highlight_patterns():
			highlight_components.extend(pattern.highlight_components())
		return highlight_components

@dataclass
class SyntaxHighlighting:
	syntax_components: Sequence[SyntaxComponent]
	highlight_components: Sequence[HighlightComponent]

	@property
	def full_pattern(self) -> str:
		return '|'.join(component.full_pattern for component in self.syntax_components)

	@cached_property
	def re_pattern(self) -> re.Pattern:
		return re.compile(self.full_pattern)

	@cached_property
	def nested_patterns(self) -> dict[str, re.Pattern]:
		nested_patterns: dict[str, re.Pattern] = {}
		def collect(patterns: Sequence[HighlightPattern]) -> None:
			for pattern in patterns:
				if pattern.nested:
					nested_patterns[pattern.highlight.tag_name] = re.compile('|'.join(nested.full_pattern for nested in pattern.nested))
					collect(pattern.nested)
		for syntax_component in self.syntax_components:
			collect(syntax_component.highlight_patterns())
		return nested_patterns

	def highlight_spans(self, line: str) -> Iterator[tuple[str, int, int]]:
		yield from self._highlight_spans(self.re_pattern, line, 0, len(line))

	def _highlight_spans(self, re_pattern: re.Pattern, line: str, start: int, end: int) -> Iterator[tuple[str, int, int]]:
		match = re_pattern.search(line, start, end)
		while match:
			for key, value in match.groupdict().items():
				if value is None:
					continue
				match_head, match_tail = match.span(key)
				yield (key, match_head, match_tail)
				nested_pattern = self.nested_patterns.get(key)
				if nested_pattern is not None:
					yield from self._highlight_spans(nested_pattern, line, match_head, match_tail)
			# Guard against empty matches looping forever
			next_start = match.end() if match.end() > match.start() else match.end() + 1
			if next_start > end:
				break
			match = re_pattern.search(line, next_start, end)

	def all_highlight_components(self) -> Sequence[HighlightComponent]:
		highlight_components: list[HighlightComponent] = []
		for syntax_component in self.syntax_components:
			highlight_components.extend(syntax_component.highlight_components())
		highlight_components.extend(self.highlight_components)
		return highlight_components
