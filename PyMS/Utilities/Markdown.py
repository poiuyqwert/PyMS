
import re

# Based on githubs GFM: https://github.github.com/gfm/
# This is not a complete implementation, it is a simplified implementation, mainly enough to satisfy my current use cases
#  - setext heading is not supported
#  - Raw HTML is not supported
#  - Block detection may not match spec 100% in all cases
#  - Inline detection may not match spec 100% in all cases
#  - Reference links are not supported
#  - Autolinks are not supported

class _Scanner(object):
	RE_BLANK = re.compile(r'^[ \t]*$')

	def __init__(self):
		self.line = None # type: str
		self.offset = 0
		self.length = 0
		self.owned = False

	def set_line(self, line): # type: (str) -> None
		self.line = line
		self.offset = 0
		self.length = len(self.line)
		self.owned = False

	def lcut(self, char_count): # type: (int) -> None
		self.offset += char_count

	def rcut(self, char_count): # type: (int) -> None
		self.length -= char_count

	def is_empty(self):
		return not self.line or self.length == 0

	def is_done(self):
		return self.is_empty() or self.owned

	def is_blank(self):
		return _Scanner.RE_BLANK.match(self.line) != None

	def end(self):
		self.offset = len(self.line)-1
		self.length = 0

	def own(self):
		self.owned = True

	def remainder(self):
		if not self.line:
			return ''
		return self.line[self.offset:self.offset+self.length]

	def search(self, pattern): # type: (re.Pattern[str]) -> (re.Match[str] | None)
		return pattern.search(self.line, self.offset, self.length)

	def match(self, pattern): # type: (re.Pattern[str]) -> (re.Match[str] | None)
		return pattern.match(self.line, self.offset, self.length)

# Block content
class Block(object):
	def __init__(self): # type () -> Block
		self.open = True
		self.parent = None # type: Block
		# self.children = [] # type: list[Block]

	@staticmethod
	def start(scanner): # type: (_Scanner) -> (Block | None)
		return None

	def is_continued(self, scanner): # type: (_Scanner) -> bool
		return False

	def close(self):
		self.open = False

	def repr_params(self):
		return None

	def __repr__(self):
		info = '-> ' if self.open else '   '
		info += self.__class__.__name__
		repr_params = self.repr_params()
		if repr_params:
			info += ' (%s)' % repr_params
		return info

class ContainerBlock(Block):
	def __init__(self): # type: () -> ContainerBlock
		Block.__init__(self)
		self.children = []

	def add_child(self, block): # type: (Block) -> None
		self.children.append(block)
		block.parent = self
		if not self.open:
			block.close()

	def get_open_child(self): # type: () -> (Block | None)
		if not self.children:
			return None
		child = self.children[-1]
		if not child.open:
			return None
		return child

	def close_children(self):
		open_child = self.get_open_child()
		if open_child:
			open_child.close()

	def close(self):
		Block.close(self)
		self.close_children()

	def __repr__(self):
		info = Block.__repr__(self)
		for child in self.children:
			info += '\r\n  ' + repr(child).replace('\r\n', '\r\n  ')
		return info

class LeafBlock(Block):
	pass

class ContentBlock(LeafBlock):
	def __init__(self, span=None): # type: (str | Span) -> ContentBlock
		LeafBlock.__init__(self)
		self.spans = [] # type: list[Span]
		if span != None:
			if not isinstance(span, Span):
				span = Span(span)
			self.spans.append(span)

	def add_span(self, span): # type: (str | Span) -> None
		if not isinstance(span, Span):
			span = Span(span)
		self.spans.append(span)

	def __repr__(self):
		info = Block.__repr__(self)
		# TODO: Update
		for span in self.spans:
			info += '\r\n     ' + repr(span).replace('\r\n', '\r\n  ')
		return info

class ThematicBreak(LeafBlock):
	RE_MARKER = re.compile(r' {0,3}(-|_|\*)+? *\1+? *\1+?(?: *\1+?)* *$')

	@staticmethod
	def start(scanner): # type: (_Scanner) -> (ThematicBreak | None)
		match = scanner.match(ThematicBreak.RE_MARKER)
		if not match:
			return None
		scanner.end()
		return ThematicBreak()

class ATXHeading(ContentBlock):
	RE_MARKER = re.compile(r'( {0,3})(#{1,6})(?:( +).+?( +#+ *)?)?$')
	RE_ANCHOR_CLEAN = re.compile(r'[^a-zA-Z ]')

	def __init__(self, level): # type: (int) -> ATXHeading
		ContentBlock.__init__(self)
		self.level = level
		self.open = False

	@staticmethod
	def start(scanner): # type: (_Scanner) -> (ATXHeading | None)
		match = scanner.match(ATXHeading.RE_MARKER)
		if not match:
			return None
		scanner.lcut(len(match.group(1)) + len(match.group(2)))
		if match.group(3):
			scanner.lcut(len(match.group(3)))
		if match.group(4):
			scanner.rcut(len(match.group(4)))
		return ATXHeading(len(match.group(2)))

	def repr_params(self):
		return 'level=%d' % self.level

	def anchor(self):
		def collapse(items): # type: (list[Span | str]) -> None
			anchor = ''
			for item in items:
				if isinstance(item, Span):
					anchor += collapse(item.contents)
				elif isinstance(item, str):
					anchor += ATXHeading.RE_ANCHOR_CLEAN.sub('', item).lower().replace(' ', '-')
			return anchor
		return collapse(self.spans)

class IndentedCodeBlock(ContentBlock):
	RE_MARKER = re.compile(r' {4}.+')

	@staticmethod
	def start(scanner): # type: (_Scanner) -> (IndentedCodeBlock | None)
		match = scanner.match(IndentedCodeBlock.RE_MARKER)
		if not match:
			return None
		scanner.lcut(4)
		scanner.own()
		return IndentedCodeBlock()

	def is_continued(self, scanner): # type: (_Scanner) -> bool
		match = scanner.match(IndentedCodeBlock.RE_MARKER)
		if not match:
			return False
		scanner.lcut(4)
		scanner.own()
		return True

class FencedCodeBlock(ContentBlock):
	RE_MARKER = re.compile(r'( {0,3})(`{3,}|~{3,})([^`~][^`~]*?)?\s*$')
	
	def __init__(self, indent, fence, info_string):
		ContentBlock.__init__(self)
		self.indent = indent
		self._re_closing = re.compile(' {0,3}%s+\\s*$' % fence)
		self.info_string = info_string

	@staticmethod
	def start(scanner): # type: (_Scanner) -> (FencedCodeBlock | None)
		match = scanner.match(FencedCodeBlock.RE_MARKER)
		if not match:
			return None
		scanner.end()
		return FencedCodeBlock(len(match.group(1)), match.group(2), match.group(3))

	def is_continued(self, scanner): # type: (_Scanner) -> bool
		if not scanner.match(self._re_closing):
			return True
		scanner.end()
		self.close()
		return False

class Paragraph(ContentBlock):
	RE_NOT_BLANK = re.compile(r'[^ \t]')

	# @staticmethod
	# def start(scanner): # type: (_Scanner) -> (Paragraph | None)
	# 	if not scanner.search(Paragraph.RE_NOT_BLANK):
	# 		return None
	# 	line = scanner.remainder().strip(' \t')
	# 	scanner.end()
	# 	return Paragraph(line)

class BlockQuote(ContainerBlock):
	RE_MARKER = re.compile(r'( {0,3}>)(?:( )|$)')

	@staticmethod
	def start(scanner): # type: (_Scanner) -> (BlockQuote | None)
		match = scanner.match(BlockQuote.RE_MARKER)
		if not match:
			return None
		scanner.lcut(len(match.group(1)))
		if match.group(2):
			scanner.lcut(len(match.group(2)))
		return BlockQuote()

class ListBlock(ContainerBlock):
	MARKER_BULLET = '-'
	MARKER_NUMERIC = '#'

	def __init__(self, marker, level): # type: (str, int) -> ListBlock
		ContainerBlock.__init__(self)
		self.marker = marker
		self.level = level

	def is_continued(self, scanner): # type: (_Scanner) -> bool
		match = scanner.match(ListItemBlock.RE_LEVEL)
		if match and len(match.group(0)) >= self.level:
			return True
		match = scanner.match(ListItemBlock.RE_MARKER)
		if match:
			if match.group(2) in '-+*':
				marker = ListBlock.MARKER_BULLET
			else:
				marker = ListBlock.MARKER_NUMERIC
			if marker == self.marker:
				return True
		return False

	def repr_params(self): # type: () -> str
		return "marker='%s', level=%d" % (self.marker, self.level)

class ListItemBlock(ContainerBlock):
	RE_MARKER = re.compile(r'( {0,3})([-+*]|[0-9]{1,9}[.)])(?:( {1,4})(?:[^ ]|$)|( )(?:[^ ]|$)|$)')
	RE_LEVEL = re.compile(r' +')

	@staticmethod
	def start(scanner): # type: (_Scanner) -> (ListBlock | None)
		match = scanner.match(ListItemBlock.RE_MARKER)
		if not match:
			return None
		level = len(match.group(1)) + len(match.group(2))
		scanner.lcut(level)
		if match.group(3):
			indent = len(match.group(3))
			scanner.lcut(indent)
			level += indent
		if match.group(4):
			scanner.lcut(1)
			level += 1
		if match.group(2) in '-+*':
			marker = ListBlock.MARKER_BULLET
		else:
			marker = ListBlock.MARKER_NUMERIC
		list = ListBlock(marker, level)
		list.add_child(ListItemBlock())
		return list

	def is_continued(self, scanner): # type: (_Scanner) -> bool
		match = scanner.match(ListItemBlock.RE_LEVEL)
		parent = self.parent # type: ListBlock
		if not match or len(match.group(0)) < parent.level:
			return False
		scanner.lcut(parent.level)
		return True

# Inline content
class Span(object):
	def __init__(self, text): # type: (str) -> Span
		self.contents = [] # type: list[Span | str]
		if text:
			self.contents.append(text)

	@staticmethod
	def apply(text): # type: (str) -> (tuple[int, int, Span] | None)
		return None

	def scan(self, span_type): # type: (type[Span]) -> bool
		if span_type == self.__class__:
			return False
		found = False
		index = 0
		while index < len(self.contents):
			item = self.contents[index]
			if isinstance(item, Span):
				found |= item.scan(span_type)
			elif isinstance(item, str):
				match = span_type.apply(item)
				if match:
					found = True
					start_index,end_index,span = match
					self.contents[index] = item[:start_index]
					self.contents.insert(index+1, span)
					self.contents.insert(index+2, item[end_index:])
					index += 1
			index += 1
		return found

	def repr_params(self): # type: () -> (str | None)
		return None

	def __repr__(self):
		result = '<%s' % self.__class__.__name__
		repr_params = self.repr_params()
		if repr_params:
			result += ' ' + repr_params
		result += '>'
		for item in self.contents:
			if isinstance(item, Span):
				result += repr(item)
			elif isinstance(item, str):
				result += item
		result += '</%s>' % self.__class__.__name__
		return result

class CodeSpan(Span):
	RE_MARKER = re.compile(r'(`{1,3})(.+?)\1')

	@staticmethod
	def apply(text): # type: (str) -> (tuple[int, int, CodeSpan] | None)
		match = CodeSpan.RE_MARKER.search(text)
		if not match:
			return None
		return (match.start(), match.end(), CodeSpan(match.group(2)))

	def scan(self, span_type): # type: (type[Span]) -> bool
		return False

class Bold(Span):
	RE_MARKER = re.compile(r'([*_]{2,3})(.+?)\1')

	@staticmethod
	def apply(text): # type: (str) -> (tuple[int, int, Bold] | None)
		match = Bold.RE_MARKER.search(text)
		if not match:
			return None
		return (match.start(), match.end(), Bold(match.group(2)))

class Italic(Span):
	RE_MARKER = re.compile(r'([*_])(.+?)\1')

	@staticmethod
	def apply(text): # type: (str) -> (tuple[int, int, Italic] | None)
		match = Italic.RE_MARKER.search(text)
		if not match:
			return None
		return (match.start(), match.end(), Italic(match.group(2)))

class Strikethrough(Span):
	RE_MARKER = re.compile(r'~~(.+?)~~')

	@staticmethod
	def apply(text): # type: (str) -> (tuple[int, int, Strikethrough] | None)
		match = Strikethrough.RE_MARKER.search(text)
		if not match:
			return None
		return (match.start(), match.end(), Strikethrough(match.group(1)))

class Link(Span):
	RE_MARKER = re.compile(r'(?<!!)\[(.+?)\]\((\S+?|<.+?>)(?: ([\'"])(.+?)\3)?\)')

	def __init__(self, text, link, title): # type: (str, str, str | None) -> Link
		Span.__init__(self, text)
		self.link = link
		self.title = title

	@staticmethod
	def apply(text): # type: (str) -> (tuple[int, int, Link] | None)
		match = Link.RE_MARKER.search(text)
		if not match:
			return None
		text = match.group(1)
		link = match.group(2)
		if link.startswith('<') and link.endswith('>'):
			link = link[1:-1]
		title = match.group(4)
		return (match.start(), match.end(), Link(text, link, title))

	def repr_params(self): # type () -> (str | None)
		result = 'link="%s"' % self.link
		if self.title:
			result += ' title="%s"' % self.title
		return result

class Image(Span):
	RE_MARKER = re.compile(r'!\[(.+?)\]\((\S+|<.+?>)(?: ([\'"])(.+?)\3)?\)')

	def __init__(self, alt_text, link, title): # type: (str, str, str | None) -> Image
		Span.__init__(self, None)
		self.alt_text = alt_text
		self.link = link
		self.title = title

	@staticmethod
	def apply(text): # type: (str) -> (tuple[int, int, Image] | None)
		match = Image.RE_MARKER.search(text)
		if not match:
			return None
		alt_text = match.group(1)
		link = match.group(2)
		if link.startswith('<') and link.endswith('>'):
			link = link[1:-1]
		title = match.group(4)
		return (match.start(), match.end(), Image(alt_text, link, title))

	def repr_params(self): # type () -> (str | None)
		result = 'link="%s" alt_text="%s"' % (self.link, self.alt_text)
		if self.title:
			result += ' title="%s"' % self.title
		return result

class Document(ContainerBlock):
	RE_NEWLINE = re.compile(r'\r?\n')
	BLOCK_PRIORITY = (
		ThematicBreak,
		ATXHeading,
		# SetextHeading,
		IndentedCodeBlock,
		FencedCodeBlock,
		ListItemBlock,
		BlockQuote,
		# Paragraph
	)
	SPAN_PRIORITY = (
		CodeSpan,
		Link,
		Image,
		Bold,
		Italic,
		Strikethrough
	)

	@staticmethod
	def parse(markdown): # type: (str) -> Document
		document = Document()
		scanner = _Scanner()
		lines = Document.RE_NEWLINE.split(markdown)
		# Phase 1. Build block structure
		for line in lines:
			scanner.set_line(line)
			# print('\r\n' + repr(document))
			# 1. Check for continuations
			working_block = document
			open_block = document
			while True:
				next_block = open_block.get_open_child() if isinstance(open_block, ContainerBlock) else None
				if not next_block:
					break
				if working_block == open_block and next_block.is_continued(scanner):
					working_block = next_block
				open_block = next_block
			# 2. Check for new blocks
			found_block = True
			while found_block and not scanner.is_done():
				for block_type in Document.BLOCK_PRIORITY:
					block = block_type.start(scanner)
					if block:
						if isinstance(block, ListBlock) and isinstance(working_block, ListBlock) and block.marker == working_block.marker:
							block = block.children[-1]
						working_block.close_children()
						working_block.add_child(block)
						# print('\r\n' + repr(document))
						open_block = block
						while isinstance(open_block, ContainerBlock) and open_block.children:
							open_block = open_block.children[-1]
						break
				else:
					found_block = False
			# 3. Incorporate remaining text
			if not scanner.is_empty():
				if isinstance(open_block, ContentBlock):
					open_block.add_span(scanner.remainder())
				else:
					if isinstance(open_block, ListItemBlock) and open_block.children and working_block != open_block:
						open_block.parent.close()
						open_block = open_block.parent.parent
					content_block = Paragraph(scanner.remainder())
					open_block.add_child(content_block)
			elif scanner.is_blank() and isinstance(open_block, ContentBlock):
				open_block.close()
		# print('\r\n' + repr(document))
		# Phase 2. Parse inline structure
		def parse_spans(block):
			if isinstance(block, IndentedCodeBlock) or isinstance(block, FencedCodeBlock):
				return
			if isinstance(block, ContentBlock):
				for span_type in Document.SPAN_PRIORITY:
					for span in block.spans:
						span.scan(span_type)
			if isinstance(block, ContainerBlock):
				for child in block.children:
					parse_spans(child)
		parse_spans(document)
		return document

	def is_continued(self, scanner): # type: (_Scanner) -> bool
		return True

	def close(self):
		self.close_children()
