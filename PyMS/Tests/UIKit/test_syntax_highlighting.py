
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


class Test_NestedPatterns(unittest.TestCase):
	def _highlighting(self) -> tuple[SyntaxHighlighting, HighlightComponent, HighlightComponent, HighlightComponent]:
		string = _component('String')
		tbl = _component('TBL')
		number = _component('Number')
		highlighting = SyntaxHighlighting(
			syntax_components=[
				SyntaxComponent([HighlightPattern(string, r'"[^"]*"', nested=[HighlightPattern(tbl, r'<\d+>')])]),
				SyntaxComponent([r'\b', HighlightPattern(number, r'\d+'), r'\b']),
			],
			highlight_components=[],
		)
		return (highlighting, string, tbl, number)

	def test_highlight_components_include_nested_after_parent(self) -> None:
		highlighting, string, tbl, number = self._highlighting()
		self.assertEqual(highlighting.all_highlight_components(), [string, tbl, number])

	def test_nested_patterns_keyed_by_parent_tag(self) -> None:
		highlighting, _, _, _ = self._highlighting()
		self.assertEqual(list(highlighting.nested_patterns.keys()), ['String'])
		self.assertEqual(highlighting.nested_patterns['String'].pattern, r'(?P<TBL><\d+>)')

	def test_highlight_spans_plain(self) -> None:
		highlighting, _, _, _ = self._highlighting()
		self.assertEqual(list(highlighting.highlight_spans('a 12 b 3')), [('Number', 2, 4), ('Number', 7, 8)])

	def test_highlight_spans_nested_offsets(self) -> None:
		highlighting, _, _, _ = self._highlighting()
		self.assertEqual(list(highlighting.highlight_spans('x "a<0>b 7" 5')), [
			('String', 2, 11),
			('TBL', 4, 7),
			('Number', 12, 13),
		])

	def test_nested_not_matched_outside_parent(self) -> None:
		highlighting, _, _, _ = self._highlighting()
		self.assertEqual(list(highlighting.highlight_spans('<0>')), [('Number', 1, 2)])
