
from ...Utilities.UIKit.SyntaxHighlighting import HighlightComponent, HighlightPattern, SyntaxComponent, SyntaxHighlighting
from ...Utilities.Config import HighlightStyle, Style

import re
import unittest


def _component(name: str, tag: str | None = None) -> HighlightComponent:
	return HighlightComponent(name=name, description=f'{name} description', highlight_style=HighlightStyle(Style()), tag=tag)


class Test_HighlightComponent_tag_name(unittest.TestCase):
	def test_uses_explicit_tag(self) -> None:
		self.assertEqual(_component('My Name', tag='custom').tag_name, 'custom')

	def test_strips_spaces_from_name(self) -> None:
		self.assertEqual(_component('AI ID').tag_name, 'AIID')

	def test_name_without_spaces_unchanged(self) -> None:
		self.assertEqual(_component('Number').tag_name, 'Number')


class Test_HighlightPattern_full_pattern(unittest.TestCase):
	def test_wraps_pattern_in_named_group(self) -> None:
		pattern = HighlightPattern(_component('Number'), r'\d+')
		self.assertEqual(pattern.full_pattern, r'(?P<Number>\d+)')

	def test_uses_tag_name_with_spaces_stripped(self) -> None:
		pattern = HighlightPattern(_component('AI ID'), r'\w+')
		self.assertEqual(pattern.full_pattern, r'(?P<AIID>\w+)')

	def test_uses_explicit_tag(self) -> None:
		pattern = HighlightPattern(_component('Number', tag='num'), r'\d+')
		self.assertEqual(pattern.full_pattern, r'(?P<num>\d+)')


class Test_SyntaxComponent(unittest.TestCase):
	def test_full_pattern_concatenates_mixed_patterns(self) -> None:
		component = SyntaxComponent([
			HighlightPattern(_component('A'), 'a'),
			'-',
			HighlightPattern(_component('B'), 'b'),
		])
		self.assertEqual(component.full_pattern, '(?P<A>a)-(?P<B>b)')

	def test_full_pattern_of_raw_strings(self) -> None:
		self.assertEqual(SyntaxComponent(['foo', 'bar']).full_pattern, 'foobar')

	def test_full_pattern_empty(self) -> None:
		self.assertEqual(SyntaxComponent([]).full_pattern, '')

	def test_highlight_components_only_from_patterns(self) -> None:
		a = _component('A')
		b = _component('B')
		component = SyntaxComponent([HighlightPattern(a, 'a'), 'raw', HighlightPattern(b, 'b')])
		self.assertEqual(component.highlight_components(), [a, b])

	def test_highlight_components_empty_when_only_raw(self) -> None:
		self.assertEqual(SyntaxComponent(['raw']).highlight_components(), [])


class Test_SyntaxHighlighting(unittest.TestCase):
	def test_full_pattern_joins_components_with_alternation(self) -> None:
		highlighting = SyntaxHighlighting(
			syntax_components=[
				SyntaxComponent([HighlightPattern(_component('Number'), r'\d+')]),
				SyntaxComponent([HighlightPattern(_component('Word'), r'[a-z]+')]),
			],
			highlight_components=[],
		)
		self.assertEqual(highlighting.full_pattern, r'(?P<Number>\d+)|(?P<Word>[a-z]+)')

	def test_re_pattern_compiles_full_pattern(self) -> None:
		highlighting = SyntaxHighlighting(
			syntax_components=[SyntaxComponent([HighlightPattern(_component('Number'), r'\d+')])],
			highlight_components=[],
		)
		self.assertIsInstance(highlighting.re_pattern, re.Pattern)
		self.assertEqual(highlighting.re_pattern.pattern, highlighting.full_pattern)

	def test_re_pattern_captures_named_groups(self) -> None:
		highlighting = SyntaxHighlighting(
			syntax_components=[
				SyntaxComponent([HighlightPattern(_component('Number'), r'\d+')]),
				SyntaxComponent([HighlightPattern(_component('Word'), r'[a-z]+')]),
			],
			highlight_components=[],
		)
		number_match = highlighting.re_pattern.match('123')
		assert number_match is not None
		self.assertEqual(number_match.group('Number'), '123')
		word_match = highlighting.re_pattern.match('abc')
		assert word_match is not None
		self.assertEqual(word_match.group('Word'), 'abc')

	def test_re_pattern_is_cached(self) -> None:
		highlighting = SyntaxHighlighting(
			syntax_components=[SyntaxComponent([HighlightPattern(_component('Number'), r'\d+')])],
			highlight_components=[],
		)
		self.assertIs(highlighting.re_pattern, highlighting.re_pattern)

	def test_all_highlight_components_collects_in_order(self) -> None:
		a = _component('A')
		b = _component('B')
		c = _component('C')
		standalone = _component('D')
		highlighting = SyntaxHighlighting(
			syntax_components=[
				SyntaxComponent([HighlightPattern(a, 'a'), 'raw', HighlightPattern(b, 'b')]),
				SyntaxComponent([HighlightPattern(c, 'c')]),
			],
			highlight_components=[standalone],
		)
		self.assertEqual(highlighting.all_highlight_components(), [a, b, c, standalone])
