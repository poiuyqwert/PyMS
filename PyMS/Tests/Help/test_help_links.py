
from ...Utilities import Assets
from ...Utilities import Markdown
from ...Utilities.MarkdownView import MarkdownView

import os
import unittest

from collections import Counter


def _collect_anchors(document: Markdown.Document) -> list[str]:
	anchors: list[str] = []
	def walk(block: Markdown.Block) -> None:
		if isinstance(block, Markdown.ATXHeading):
			anchors.append(block.anchor())
		if isinstance(block, Markdown.ContainerBlock):
			for child in block.children:
				walk(child)
	walk(document)
	return anchors

def _collect_spans(document: Markdown.Document, span_type: type) -> list:
	spans: list = []
	def walk_spans(items: list[Markdown.Span | str]) -> None:
		for item in items:
			if isinstance(item, span_type):
				spans.append(item)
			if isinstance(item, Markdown.Span):
				walk_spans(item.contents)
	def walk_blocks(block: Markdown.Block) -> None:
		if isinstance(block, Markdown.ContentBlock):
			walk_spans(list(block.spans))
		if isinstance(block, Markdown.ContainerBlock):
			for child in block.children:
				walk_blocks(child)
	walk_blocks(document)
	return spans


class Test_help_links(unittest.TestCase):
	help_tree: Assets.HelpFolder
	anchors: dict[str, list[str]]
	links: dict[str, list[Markdown.Link]]
	images: dict[str, list[Markdown.Image]]

	@classmethod
	def setUpClass(cls) -> None:
		cls.help_tree = Assets.help_tree(force_update=True)
		cls.anchors = {}
		cls.links = {}
		cls.images = {}
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
					document = Markdown.Document.parse(file.read())
				cls.anchors[page_path] = _collect_anchors(document)
				cls.links[page_path] = _collect_spans(document, Markdown.Link)
				cls.images[page_path] = _collect_spans(document, Markdown.Image)

	def fail_for_violations(self, description: str, violations: list[str]) -> None:
		if violations:
			self.fail(f'{description}:\n' + '\n'.join(violations))

	def test_help_corpus_is_loaded(self) -> None:
		self.assertGreater(len(self.anchors), 0)

	def test_links_are_same_page_root_absolute_or_external(self) -> None:
		# The in-app resolver (`Assets.HelpFolder.index()`) only accepts `/Help/...` paths, and GitHub
		# requires the `.md` extension, so cross-page links must be root-absolute `/Help/....md` (with an
		# optional `#anchor`). File-relative links are silently dead in-app. External links need an
		# explicit scheme or `MarkdownView` treats them as internal pages.
		violations: list[str] = []
		for page_path, links in self.links.items():
			for link in links:
				if link.link.startswith('#'):
					continue
				if MarkdownView.RE_LINK_HAS_SCHEME.match(link.link):
					continue
				if link.link.startswith('/Help/') and link.link.split('#')[0].endswith(os.extsep + 'md'):
					continue
				violations.append(f'{page_path}: ({link.link})')
		self.fail_for_violations('Links that are not same-page `#anchor`, root-absolute `/Help/....md`, or external with a scheme', violations)

	def test_cross_page_links_resolve(self) -> None:
		violations: list[str] = []
		for page_path, links in self.links.items():
			for link in links:
				if not link.link.startswith('/Help/'):
					continue
				if self.help_tree.index(link.link) is None:
					violations.append(f'{page_path}: ({link.link})')
		self.fail_for_violations('Cross-page links to pages missing from the help tree', violations)

	def test_link_anchors_exist(self) -> None:
		violations: list[str] = []
		for page_path, links in self.links.items():
			for link in links:
				if link.link.startswith('#'):
					target_path = page_path
					anchor = link.link[1:]
				elif link.link.startswith('/Help/') and '#' in link.link:
					target_path, anchor = link.link.split('#', 1)
				else:
					continue
				target_anchors = self.anchors.get(target_path)
				if target_anchors is None:
					# Missing target page is reported by `test_cross_page_links_resolve`
					continue
				if anchor not in target_anchors:
					violations.append(f'{page_path}: ({link.link})')
		self.fail_for_violations('Links to anchors with no matching heading in the target page', violations)

	def test_heading_anchors_are_unique_per_page(self) -> None:
		# GitHub deduplicates repeated heading slugs with `-1` suffixes but the in-app viewer does not,
		# so a duplicate anchor makes every link to it ambiguous.
		violations: list[str] = []
		for page_path, anchors in self.anchors.items():
			for anchor, count in Counter(anchors).items():
				if count > 1:
					violations.append(f'{page_path}: (#{anchor}) x{count}')
		self.fail_for_violations('Pages with duplicate heading anchors', violations)

	def test_image_links_resolve(self) -> None:
		# Mirrors `Assets.help_image()`: images resolve under `Help/` and require a file extension.
		violations: list[str] = []
		for page_path, images in self.images.items():
			for image in images:
				if not image.link.startswith('/Help/') or not os.extsep in image.link.split('/')[-1]:
					violations.append(f'{page_path}: ({image.link})')
					continue
				full_path = os.path.join(Assets.help_dir, *image.link.split('/')[2:])
				if not os.path.isfile(full_path):
					violations.append(f'{page_path}: ({image.link})')
		self.fail_for_violations('Image links that are not root-absolute `/Help/...` paths to existing files', violations)
