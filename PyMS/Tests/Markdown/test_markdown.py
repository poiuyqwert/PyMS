
from ...Utilities.Markdown import (
	Document, _Scanner,
	ATXHeading, ThematicBreak, IndentedCodeBlock, FencedCodeBlock, BlockQuote, ListBlock, ListItemBlock, Paragraph,
	Span, CodeSpan, Bold, Italic, Strikethrough, Link, Image,
)

import re
import unittest


def _scanner(line: str) -> _Scanner:
	scanner = _Scanner()
	scanner.set_line(line)
	return scanner


class Test_Scanner(unittest.TestCase):
	def test_set_line_initializes(self) -> None:
		scanner = _scanner('hello')
		self.assertEqual(scanner.remainder(), 'hello')
		self.assertEqual(scanner.offset, 0)
		self.assertEqual(scanner.length, 5)

	def test_lcut_advances_remainder(self) -> None:
		scanner = _scanner('hello')
		scanner.lcut(2)
		self.assertEqual(scanner.remainder(), 'llo')

	def test_rcut_trims_remainder(self) -> None:
		scanner = _scanner('hello')
		scanner.rcut(2)
		self.assertEqual(scanner.remainder(), 'hel')

	def test_is_empty(self) -> None:
		self.assertTrue(_scanner('').is_empty())
		self.assertFalse(_scanner('x').is_empty())

	def test_end_empties_scanner(self) -> None:
		scanner = _scanner('hello')
		scanner.end()
		self.assertTrue(scanner.is_empty())
		self.assertEqual(scanner.remainder(), '')
		self.assertEqual(scanner.offset, len('hello'))

	def test_is_blank(self) -> None:
		self.assertTrue(_scanner('   ').is_blank())
		self.assertTrue(_scanner('').is_blank())
		self.assertFalse(_scanner('  x').is_blank())

	def test_own_marks_done(self) -> None:
		scanner = _scanner('x')
		self.assertFalse(scanner.is_done())
		scanner.own()
		self.assertTrue(scanner.is_done())

	def test_match_from_offset(self) -> None:
		scanner = _scanner('   abc')
		match = scanner.match(re.compile(r' +'))
		assert match is not None
		self.assertEqual(match.group(), '   ')

	def test_match_respects_offset(self) -> None:
		scanner = _scanner('   abc')
		scanner.lcut(3)
		match = scanner.match(re.compile(r'[a-z]+'))
		assert match is not None
		self.assertEqual(match.group(), 'abc')

	def test_search_finds_within_line(self) -> None:
		scanner = _scanner('abc123')
		match = scanner.search(re.compile(r'\d+'))
		assert match is not None
		self.assertEqual(match.group(), '123')


class Test_ATXHeading_start(unittest.TestCase):
	def test_level_one(self) -> None:
		scanner = _scanner('# Title')
		heading = ATXHeading.start(scanner)
		assert heading is not None
		self.assertEqual(heading.level, 1)
		self.assertEqual(scanner.remainder(), 'Title')

	def test_level_six(self) -> None:
		heading = ATXHeading.start(_scanner('###### Six'))
		assert heading is not None
		self.assertEqual(heading.level, 6)

	def test_requires_space_after_hashes(self) -> None:
		self.assertIsNone(ATXHeading.start(_scanner('#Foo')))

	def test_seven_hashes_is_not_heading(self) -> None:
		self.assertIsNone(ATXHeading.start(_scanner('####### Seven')))

	def test_non_heading(self) -> None:
		self.assertIsNone(ATXHeading.start(_scanner('not a heading')))

	def test_strips_closing_hashes(self) -> None:
		scanner = _scanner('# Foo #')
		heading = ATXHeading.start(scanner)
		assert heading is not None
		self.assertEqual(scanner.remainder(), 'Foo')

	def test_strips_multiple_closing_hashes(self) -> None:
		scanner = _scanner('## Bar ###')
		ATXHeading.start(scanner)
		self.assertEqual(scanner.remainder(), 'Bar')


class Test_ATXHeading_anchor(unittest.TestCase):
	def test_lowercases_and_dashes_spaces(self) -> None:
		heading = ATXHeading(1)
		heading.add_span('Hello World')
		self.assertEqual(heading.anchor(), 'hello-world')

	def test_strips_non_alpha(self) -> None:
		heading = ATXHeading(1)
		heading.add_span('Hello, World!')
		self.assertEqual(heading.anchor(), 'hello-world')


class Test_ThematicBreak_start(unittest.TestCase):
	def test_dashes(self) -> None:
		self.assertIsInstance(ThematicBreak.start(_scanner('---')), ThematicBreak)

	def test_asterisks(self) -> None:
		self.assertIsInstance(ThematicBreak.start(_scanner('***')), ThematicBreak)

	def test_underscores(self) -> None:
		self.assertIsInstance(ThematicBreak.start(_scanner('___')), ThematicBreak)

	def test_spaced_markers(self) -> None:
		self.assertIsInstance(ThematicBreak.start(_scanner('- - -')), ThematicBreak)

	def test_two_markers_is_not_break(self) -> None:
		self.assertIsNone(ThematicBreak.start(_scanner('--')))

	def test_text_is_not_break(self) -> None:
		self.assertIsNone(ThematicBreak.start(_scanner('abc')))


class Test_IndentedCodeBlock(unittest.TestCase):
	def test_start_requires_four_spaces(self) -> None:
		scanner = _scanner('    code')
		block = IndentedCodeBlock.start(scanner)
		self.assertIsInstance(block, IndentedCodeBlock)
		self.assertEqual(scanner.remainder(), 'code')

	def test_start_rejects_three_spaces(self) -> None:
		self.assertIsNone(IndentedCodeBlock.start(_scanner('   code')))

	def test_is_continued_on_indented_line(self) -> None:
		block = IndentedCodeBlock()
		scanner = _scanner('    more')
		self.assertTrue(block.is_continued(scanner))
		self.assertEqual(scanner.remainder(), 'more')

	def test_is_not_continued_on_unindented_line(self) -> None:
		block = IndentedCodeBlock()
		self.assertFalse(block.is_continued(_scanner('not indented')))


class Test_FencedCodeBlock_start(unittest.TestCase):
	def test_backtick_fence(self) -> None:
		block = FencedCodeBlock.start(_scanner('```'))
		assert block is not None
		self.assertIsNone(block.info_string)

	def test_info_string(self) -> None:
		block = FencedCodeBlock.start(_scanner('```python'))
		assert block is not None
		self.assertEqual(block.info_string, 'python')

	def test_tilde_fence(self) -> None:
		self.assertIsInstance(FencedCodeBlock.start(_scanner('~~~')), FencedCodeBlock)

	def test_two_backticks_is_not_fence(self) -> None:
		self.assertIsNone(FencedCodeBlock.start(_scanner('``')))

	def test_content_line_continues_block(self) -> None:
		block = FencedCodeBlock.start(_scanner('```'))
		assert block is not None
		self.assertTrue(block.is_continued(_scanner('some code')))

	def test_closing_fence_ends_block(self) -> None:
		block = FencedCodeBlock.start(_scanner('```'))
		assert block is not None
		self.assertFalse(block.is_continued(_scanner('```')))
		self.assertFalse(block.open)

	def test_closing_fence_with_trailing_whitespace(self) -> None:
		block = FencedCodeBlock.start(_scanner('```'))
		assert block is not None
		self.assertFalse(block.is_continued(_scanner('```   ')))


class Test_BlockQuote_start(unittest.TestCase):
	def test_with_space(self) -> None:
		scanner = _scanner('> quote')
		block = BlockQuote.start(scanner)
		self.assertIsInstance(block, BlockQuote)
		self.assertEqual(scanner.remainder(), 'quote')

	def test_marker_only(self) -> None:
		self.assertIsInstance(BlockQuote.start(_scanner('>')), BlockQuote)

	def test_requires_marker(self) -> None:
		self.assertIsNone(BlockQuote.start(_scanner('not a quote')))


class Test_ListItemBlock_start(unittest.TestCase):
	def test_bullet_markers(self) -> None:
		for marker in ('- item', '* item', '+ item'):
			with self.subTest(marker=marker):
				block = ListItemBlock.start(_scanner(marker))
				self.assertIsInstance(block, ListBlock)
				assert isinstance(block, ListBlock)
				self.assertEqual(block.marker, ListBlock.MARKER_BULLET)

	def test_numeric_markers(self) -> None:
		for marker in ('1. item', '1) item'):
			with self.subTest(marker=marker):
				block = ListItemBlock.start(_scanner(marker))
				assert isinstance(block, ListBlock)
				self.assertEqual(block.marker, ListBlock.MARKER_NUMERIC)

	def test_creates_list_item_child(self) -> None:
		block = ListItemBlock.start(_scanner('- item'))
		assert isinstance(block, ListBlock)
		self.assertEqual([type(child).__name__ for child in block.children], ['ListItemBlock'])

	def test_non_list(self) -> None:
		self.assertIsNone(ListItemBlock.start(_scanner('item')))


class Test_inline_apply(unittest.TestCase):
	def test_code_span(self) -> None:
		result = CodeSpan.apply('a `code` b')
		assert result is not None
		start, end, span = result
		self.assertEqual((start, end), (2, 8))
		self.assertEqual(span.contents, ['code'])

	def test_code_span_none(self) -> None:
		self.assertIsNone(CodeSpan.apply('no code here'))

	def test_bold(self) -> None:
		result = Bold.apply('a **bold** b')
		assert result is not None
		start, end, span = result
		self.assertEqual((start, end), (2, 10))
		self.assertEqual(span.contents, ['bold'])

	def test_italic(self) -> None:
		result = Italic.apply('a *it* b')
		assert result is not None
		_, _, span = result
		self.assertEqual(span.contents, ['it'])

	def test_strikethrough(self) -> None:
		result = Strikethrough.apply('a ~~s~~ b')
		assert result is not None
		_, _, span = result
		self.assertEqual(span.contents, ['s'])

	def test_link(self) -> None:
		result = Link.apply('[text](url)')
		assert result is not None
		_, _, span = result
		self.assertEqual(span.link, 'url')
		self.assertIsNone(span.title)
		self.assertEqual(span.contents, ['text'])

	def test_link_with_title(self) -> None:
		result = Link.apply('[t](url "ti")')
		assert result is not None
		_, _, span = result
		self.assertEqual(span.link, 'url')
		self.assertEqual(span.title, 'ti')

	def test_link_strips_angle_brackets(self) -> None:
		result = Link.apply('[t](<my url>)')
		assert result is not None
		_, _, span = result
		self.assertEqual(span.link, 'my url')

	def test_link_does_not_match_image(self) -> None:
		self.assertIsNone(Link.apply('![alt](img.png)'))

	def test_image(self) -> None:
		result = Image.apply('![alt](img.png)')
		assert result is not None
		_, _, span = result
		self.assertEqual(span.alt_text, 'alt')
		self.assertEqual(span.link, 'img.png')

	def test_image_requires_bang(self) -> None:
		self.assertIsNone(Image.apply('[text](url)'))


class Test_Span_scan(unittest.TestCase):
	def test_splits_string_into_span(self) -> None:
		span = Span('a **b** c')
		found = span.scan(Bold)
		self.assertTrue(found)
		self.assertEqual(len(span.contents), 3)
		self.assertEqual(span.contents[0], 'a ')
		self.assertEqual(span.contents[2], ' c')
		bold = span.contents[1]
		assert isinstance(bold, Bold)
		self.assertEqual(bold.contents, ['b'])

	def test_no_match_returns_false(self) -> None:
		span = Span('plain text')
		self.assertFalse(span.scan(Bold))
		self.assertEqual(span.contents, ['plain text'])

	def test_code_span_never_rescans(self) -> None:
		self.assertFalse(CodeSpan('**not bold**').scan(Bold))

	def test_skips_same_span_type(self) -> None:
		self.assertFalse(Bold('text').scan(Bold))


class Test_Document_parse(unittest.TestCase):
	def test_heading(self) -> None:
		heading = Document.parse('# Title').children[0]
		self.assertIsInstance(heading, ATXHeading)
		assert isinstance(heading, ATXHeading)
		self.assertEqual(heading.level, 1)
		self.assertEqual(heading.spans[0].contents, ['Title'])

	def test_heading_anchor(self) -> None:
		heading = Document.parse('## Hello World').children[0]
		assert isinstance(heading, ATXHeading)
		self.assertEqual(heading.anchor(), 'hello-world')

	def test_paragraph(self) -> None:
		self.assertIsInstance(Document.parse('hello world').children[0], Paragraph)

	def test_thematic_break(self) -> None:
		self.assertIsInstance(Document.parse('---').children[0], ThematicBreak)

	def test_indented_code_block(self) -> None:
		self.assertIsInstance(Document.parse('    code').children[0], IndentedCodeBlock)

	def test_block_quote(self) -> None:
		quote = Document.parse('> quote').children[0]
		assert isinstance(quote, BlockQuote)
		self.assertIsInstance(quote.children[0], Paragraph)

	def test_list(self) -> None:
		block = Document.parse('- a\n- b').children[0]
		assert isinstance(block, ListBlock)
		self.assertEqual(block.marker, ListBlock.MARKER_BULLET)
		self.assertEqual([type(child).__name__ for child in block.children], ['ListItemBlock', 'ListItemBlock'])

	def test_inline_parsing_in_paragraph(self) -> None:
		paragraph = Document.parse('a **bold** c').children[0]
		assert isinstance(paragraph, Paragraph)
		contents = paragraph.spans[0].contents
		self.assertEqual(contents[0], 'a ')
		bold = contents[1]
		assert isinstance(bold, Bold)
		self.assertEqual(bold.contents, ['bold'])

	def test_heading_strips_closing_hashes(self) -> None:
		heading = Document.parse('# Title #').children[0]
		assert isinstance(heading, ATXHeading)
		self.assertEqual(heading.spans[0].contents, ['Title'])

	def test_fenced_code_block_closes_before_following_text(self) -> None:
		document = Document.parse('```\ncode line\n```\nafter')
		self.assertEqual([type(child).__name__ for child in document.children], ['FencedCodeBlock', 'Paragraph'])
		fenced = document.children[0]
		assert isinstance(fenced, FencedCodeBlock)
		self.assertEqual([span.contents for span in fenced.spans], [['code line']])
