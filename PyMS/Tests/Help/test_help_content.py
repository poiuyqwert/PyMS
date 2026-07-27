
from ...Utilities import Assets
from ...Utilities import Markdown

import os
import re
import unittest


# The body lines of every fenced code block, scanned straight from the source text.
# This deliberately duplicates the parsers fence handling rather than reusing it, so it can be
# compared against what the parser actually produced. The fence patterns themselves are shared
# with `FencedCodeBlock` so the scan tracks the parsers definition of a fence.
# Simplification: fences opened inside a list item or a code fence marker appearing inside an
# indented code block are not modelled. Neither occurs in the help pages, and if one is added
# later this fails loudly naming the page rather than passing silently.
def _source_code_blocks(text: str) -> list[list[str]]:
	blocks: list[list[str]] = []
	block: list[str] | None = None
	closing: re.Pattern[str] | None = None
	for line in Markdown.Document.RE_NEWLINE.split(text):
		if block is None or closing is None:
			match = Markdown.FencedCodeBlock.RE_MARKER.match(line)
			if match:
				block = []
				closing = re.compile(r' {0,3}%s+\s*$' % match.group(2))
		elif closing.match(line):
			blocks.append(block)
			block = None
			closing = None
		else:
			block.append(line)
	if block is not None:
		blocks.append(block)
	return blocks

# The body lines of every parsed fenced code block, in document order. Code block spans are
# never inline parsed, so any non-`str` content would itself be a failure of that invariant.
def _parsed_code_blocks(document: Markdown.Document) -> list[list[str]]:
	blocks: list[list[str]] = []
	def walk(block: Markdown.Block) -> None:
		if isinstance(block, Markdown.FencedCodeBlock):
			blocks.append([''.join(content for content in span.contents if isinstance(content, str)) for span in block.spans])
		if isinstance(block, Markdown.ContainerBlock):
			for child in block.children:
				walk(child)
	walk(document)
	return blocks


class Test_help_content(unittest.TestCase):
	source_code_blocks: dict[str, list[list[str]]]
	parsed_code_blocks: dict[str, list[list[str]]]

	@classmethod
	def setUpClass(cls) -> None:
		cls.source_code_blocks = {}
		cls.parsed_code_blocks = {}
		for dir_path, _, filenames in os.walk(Assets.help_dir):
			for filename in filenames:
				if filename.startswith('.'):
					continue
				_, ext = os.path.splitext(filename)
				if ext != os.extsep + 'md':
					continue
				full_path = os.path.join(dir_path, filename)
				page_path = '/Help/' + os.path.relpath(full_path, Assets.help_dir).replace(os.sep, '/')
				with open(full_path, 'r', encoding='utf-8') as file:
					text = file.read()
				cls.source_code_blocks[page_path] = _source_code_blocks(text)
				cls.parsed_code_blocks[page_path] = _parsed_code_blocks(Markdown.Document.parse(text))

	def fail_for_violations(self, description: str, violations: list[str]) -> None:
		if violations:
			self.fail(f'{description}:\n' + '\n'.join(violations))

	def test_help_corpus_is_loaded(self) -> None:
		self.assertGreater(len(self.source_code_blocks), 0)

	def test_help_corpus_has_code_blocks(self) -> None:
		self.assertGreater(sum(len(blocks) for blocks in self.source_code_blocks.values()), 0)

	# Every line of a fenced code block must survive parsing verbatim, in order, in the same
	# block. The in-app viewer renders one line per span, so a line the parser drops is a line
	# missing from a code example that renders correctly on GitHub.
	def test_fenced_code_block_lines_are_preserved(self) -> None:
		violations: list[str] = []
		for page_path, source_blocks in self.source_code_blocks.items():
			parsed_blocks = self.parsed_code_blocks[page_path]
			if len(source_blocks) != len(parsed_blocks):
				violations.append(f'{page_path}: source has {len(source_blocks)} code block(s), parsed has {len(parsed_blocks)}')
				continue
			for index, (source_block, parsed_block) in enumerate(zip(source_blocks, parsed_blocks)):
				if source_block != parsed_block:
					violations.append(f'{page_path}: code block {index + 1} does not match:\n  source: {source_block!r}\n  parsed: {parsed_block!r}')
		self.fail_for_violations('Fenced code block content was lost when parsing', violations)
