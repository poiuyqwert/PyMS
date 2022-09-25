# coding=utf-8

from .UIKit import *
from .TextTooltip import TextDynamicTooltip, TextTooltip
from .utils import is_mac
# from AutohideScrollbar import AutohideScrollbar
from . import Markdown
from . import Assets

import webbrowser, re, os

def _em(em=1): # type: (float) -> int
	return int(16 * em)

def _list_numbered(num):
	return '%d. ' % num

def _list_lettered(num):
	result = ''
	while num > 0:
		result += chr(96 + num % 26)
		num -= 26
	return '%s. ' % result

_ROMAN_LOOKUP = (
	(1000, 'm'),
	(900, 'cm'),
	(500, 'd'),
	(400, 'cd'),
	(100, 'c'),
	(90, 'xc'),
	(50, 'l'),
	(40, 'xl'),
	(10, 'x'),
	(9, 'ix'),
	(5, 'v'),
	(4, 'iv'),
	(1, 'i'),
)
def _list_roman(num):
	result = ''
	for (div, roman) in _ROMAN_LOOKUP:
		(count, num) = divmod(num, div)
		result += roman * count
		if not num:
			break
	return '%s. ' % result

class MarkdownView(Frame):
	class _ListDisplay(object):
		def __init__(self, list_block, margin): # type: (Markdown.ListBlock, int) -> MarkdownView._ListDisplay
			self.list_block = list_block
			self.margin = margin
	class _ListItemDisplay(object):
		def __init__(self, marker, size): # type: (str, int) -> MarkdownView._ListItemDisplay
			self.marker = marker
			self.size = size
	class _ListItemTags(object):
		def __init__(self, first_line_tag, subsequent_lines_tag):
			self.first_line_tag = first_line_tag
			self.first_line_used = False
			self.subsequent_lines_tag = subsequent_lines_tag
	_LIST_BULLETS = ('• ', '◦ ', '▪ ')
	_LIST_BULLET_CACHE = None # type: tuple[_ListItemDisplay]
	_LIST_NUMERICS = (_list_numbered, _list_lettered, _list_roman)
	_LIST_NUMERIC_CACHE = ([], [], []) # type: tuple[list[_ListItemDisplay], list[_ListItemDisplay], list[_ListItemDisplay]]

	RE_LINK_HAS_SCHEME = re.compile(r'[a-zA-Z][a-zA-Z0-9+.-]{1,31}:')

	# Specify `link_callback` to handle relative links
	def __init__(self, *args, **kwargs):
		self.link_callback = kwargs.pop('link_callback', None)
		if not 'relief' in kwargs:
			kwargs['relief'] = SUNKEN
			if not 'bd' in kwargs and not 'borderwidth' in kwargs:
				kwargs['bd'] = 2
		Frame.__init__(self, *args, **kwargs)

		hscroll = Scrollbar(self, orient=HORIZONTAL)
		vscroll = Scrollbar(self)
		self.font = Font.default().sized(_em())
		self.textview = Text(self, bd=0, wrap=WORD, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0, font=self.font, insertontime=0)
		self.textview.grid(column=0,row=0, padx=50, sticky=NSEW)
		vscroll.grid(column=1,row=0, sticky=NS)
		vscroll.config(command=self.textview.yview)
		hscroll.grid(column=0,row=1, sticky=EW)
		hscroll.config(command=self.textview.xview)

		self.textview.tag_configure('line_spacing', spacing2=8, spacing3=8)
		self.textview.tag_configure('h1', font=Font.default().sized(_em(2)).bolded(), spacing1=24, spacing3=16)
		self.textview.tag_configure('h2', font=Font.default().sized(_em(1.5)).bolded(), spacing1=24, spacing3=16)
		self.textview.tag_configure('h3', font=Font.default().sized(_em(1.25)).bolded(), spacing1=24, spacing3=16)
		self.textview.tag_configure('h4', font=Font.default().sized(_em()).bolded(), spacing1=24, spacing3=16)
		self.textview.tag_configure('h5', font=Font.default().sized(_em(0.875)).bolded(), spacing1=24, spacing3=16)
		self.textview.tag_configure('h6', font=Font.default().sized(_em(0.85)).bolded(), spacing1=24, spacing3=16)
		self.textview.tag_configure('p', font=Font.default().sized(_em()))
		self.textview.tag_configure('code', font=Font.fixed().sized(_em()), background='#EEEEEE', lmargin1=16,lmargin2=16, rmargin=16, wrap=NONE)
		self.textview.tag_configure('top_spacing', spacing1=16)
		self.textview.tag_configure('bottom_spacing', spacing3=16)
		self.textview.tag_configure('bold', font=Font.default().sized(_em()).bolded())
		self.textview.tag_configure('link', foreground='#6A5EFF', underline=1)
		self.textview.tag_configure('codespan', font=Font.fixed().sized(_em()), background='#EEEEEE')
		self.textview.tag_configure('top_margin', spacing1=64)
		self.textview.tag_raise(SEL)

		self.links = {} # type: dict[str, Markdown.Link]
		self.headers = {} # type: dict[str, str]
		self.images = {} # type: dict[str, Markdown.Image]
		def link_lookup(tags): # type: (tuple[str, ...]) -> (Markdown.Link | None)
			for tag in tags:
				if tag.startswith('link_'):
					link = self.links.get(tag)
					if link:
						return link
			return None
		def link_tooltip_lookup(_, tags): # type: (str, tuple[str, ...]) -> (str | None)
			link = link_lookup(tags)
			if not link:
				return None
			if not MarkdownView.RE_LINK_HAS_SCHEME.match(link.link):
				tooltip = os.path.splitext(link.link)[0].replace('/',' > ')
			else:
				tooltip = link.link
			if link.title:
				tooltip = '%s (%s)' % (link.title, tooltip)
			return tooltip
		TextDynamicTooltip(self.textview, 'link', link_tooltip_lookup, cursor=('hand1','hand2','pointinghand'))

		def image_tooltip_lookup(_, tags): # type: (str, tuple[str, ...]) -> (str | None)
			for tag in tags:
				if tag.startswith('image_'):
					image = self.images.get(tag)
					tooltip = image.alt_text
					if image.title:
						tooltip += ' (%s)' % image.title
					return tooltip
			return None
		TextDynamicTooltip(self.textview, 'image', image_tooltip_lookup)

		def link_click(*_):
			index = self.textview.index('current')
			tags = self.textview.tag_names(index)
			link = link_lookup(tags)
			if not link:
				return
			if MarkdownView.RE_LINK_HAS_SCHEME.match(link.link):
				webbrowser.open(link.link)
			elif link.link.startswith('#'):
				self.view_fragment(link.link[1:].lower())
			elif self.link_callback:
				self.link_callback(link.link)
		self.textview.tag_bind('link', Mouse.Click_Left, link_click)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		self._read_only = True
		self.textview._original_w = self.textview._w + '_original'
		self.tk.call('rename', self.textview._w, self.textview._original_w)
		self.tk.createcommand(self.textview._w, self.dispatch)

	def dispatch(self, cmd, *args):
		if self._read_only and (cmd == 'insert' or cmd == 'delete'):
			return ""
		try:
			return self.tk.call((self.textview._original_w, cmd) + args)
		except TclError:
			return ""

	def view_fragment(self, fragment):
		index = self.headers.get(fragment)
		if index:
			self.textview.see(index)
			dlineinfo = self.textview.dlineinfo(index)
			self.textview.yview_scroll(dlineinfo[1], 'pixels')

	def load_markdown(self, markdown): # type: (str) -> None
		document = Markdown.Document.parse(markdown)

		self.links.clear()
		self.headers.clear()
		self.images.clear()
		self._lists = [] # type: list[MarkdownView._ListDisplay]
		self._lists_margin = 0
		self._list_items_tags = [] # type: list[MarkdownView._ListItemTags]
		self._next_tags = ('top_margin',)

		self._read_only = False
		self.textview.delete('1.0', END)
		self.insert_block(document)
		self.textview.tag_add('line_spacing', '1.0', END)
		self._read_only = True

	def insert_block(self, block): # type: (Markdown.Block) -> None
		tags = ()
		if self._list_items_tags:
			list_item_tags = self._list_items_tags[-1]
			if list_item_tags.first_line_used:
				tags += (list_item_tags.subsequent_lines_tag,)
			else:
				tags += (list_item_tags.first_line_tag,)
				list_item_tags.first_line_used = True
		if self._next_tags and not isinstance(block, Markdown.Document):
			tags += self._next_tags
			self._next_tags = None
		if isinstance(block, Markdown.ATXHeading):
			self.headers[block.anchor()] = self.textview.index('%s -1lines' % END)
			self.insert_content(block, tags + ('h%d' % block.level,))
		elif isinstance(block, Markdown.Paragraph):
			additional_last_line_tags = None
			if \
				not isinstance(block.parent, Markdown.ListItemBlock) or (
					block.parent.children[-1] != block and
					not isinstance(block.parent.children[block.parent.children.index(block)+1], Markdown.ListBlock)
				):
				additional_last_line_tags = ('bottom_spacing',)
			self.insert_content(block, tags, additional_last_line_tags=additional_last_line_tags)
		elif isinstance(block, Markdown.IndentedCodeBlock) or isinstance(block, Markdown.FencedCodeBlock):
			self.insert_content(block, tags + ('code',), additional_first_line_tags=('top_spacing',), additional_last_line_tags=('bottom_spacing',))
			self._next_tags = ('top_spacing',)
		elif isinstance(block, Markdown.ListBlock):
			index = min(len(self._lists), 2)
			if block.marker == Markdown.ListBlock.MARKER_BULLET:
				if not MarkdownView._LIST_BULLET_CACHE:
					MarkdownView._LIST_BULLET_CACHE = tuple(MarkdownView._ListItemDisplay(bullet, self.font.measure(bullet)) for bullet in MarkdownView._LIST_BULLETS)
				margin = MarkdownView._LIST_BULLET_CACHE[index].size
			elif block.marker == Markdown.ListBlock.MARKER_NUMERIC:
				if len(block.children) > len(MarkdownView._LIST_NUMERIC_CACHE[index]):
					for num in range(len(MarkdownView._LIST_NUMERIC_CACHE[index]),len(block.children)):
						marker = MarkdownView._LIST_NUMERICS[index](num+1)
						MarkdownView._LIST_NUMERIC_CACHE[index].append(MarkdownView._ListItemDisplay(marker, self.font.measure(marker)))
				margin = max(display.size for display in MarkdownView._LIST_NUMERIC_CACHE[index][:len(block.children)])
			self._lists.append(MarkdownView._ListDisplay(block, margin))
			self._lists_margin += 10 + margin
		elif isinstance(block, Markdown.ListItemBlock):
			index = min(len(self._lists)-1,2)
			if self._lists[-1].list_block.marker == Markdown.ListBlock.MARKER_BULLET:
				display = MarkdownView._LIST_BULLET_CACHE[index]
			else:
				list_block = block.parent # type: Markdown.ListBlock
				display = MarkdownView._LIST_NUMERIC_CACHE[index][list_block.children.index(block)]
			firts_line_margin = self._lists_margin - display.size
			first_line_tag = 'list_margin%d:%d' % (firts_line_margin, self._lists_margin)
			self.textview.tag_configure(first_line_tag, lmargin1=firts_line_margin, lmargin2=self._lists_margin)
			subsequent_lines_tag = 'list_margin%d' % self._lists_margin
			self.textview.tag_configure(subsequent_lines_tag, lmargin1=self._lists_margin, lmargin2=self._lists_margin)
			self._list_items_tags.append(MarkdownView._ListItemTags(first_line_tag, subsequent_lines_tag))
			self.textview.insert(END, display.marker, tags + (first_line_tag,))
		if isinstance(block, Markdown.ContainerBlock):
			for child in block.children:
				self.insert_block(child)
		if isinstance(block, Markdown.ListBlock):
			display = self._lists.pop()
			self._lists_margin -= 10 + display.margin
			if not self._lists:
				self._next_tags = ('top_spacing',)
		elif isinstance(block, Markdown.ListItemBlock):
			self._list_items_tags.pop()

	RE_KEYBOARD_SHORTCUT = re.compile(r'(?:(?:Shift|Ctrl|Alt)\+)+.+$')
	def insert_content(self, block, tags, additional_first_line_tags=None, additional_last_line_tags=None): # type: (Markdown.ContentBlock, tuple[str], tuple[str], tuple[str]) -> None
		def insert_item(item, tags):
			if isinstance(item, Markdown.CodeSpan):
				tags += ('codespan',)
				# Markdown "Keyboard Shortcut" Extension
				#  - Code spans where the content matches keyboard shortcut format (see RE_KEYBOARD_SHORTCUT) will be updated on Mac to reflect the mac shortcuts
				if is_mac():
					match = MarkdownView.RE_KEYBOARD_SHORTCUT.match(item.contents[0])
					if match:
						item.contents[0] = item.contents[0]\
							.replace('Ctrl+', Modifier.Ctrl.description)\
							.replace('Alt+', Modifier.Alt.description)\
							.replace('Shift+', Modifier.Shift.description)
			elif isinstance(item, Markdown.Bold):
				tags += ('bold',)
			elif isinstance(item, Markdown.Link):
				link_tag = 'link_%d' % len(self.links)
				tags += ('link', link_tag)
				self.links[link_tag] = item
			elif isinstance(item, Markdown.Image):
				# TODO: Move to callback to reduce dependence on PyMS
				image = Assets.help_image(item.link)
				if not image:
					return
				start_index = self.textview.index('%s -1chars' % END)
				self.textview.image_create(END, image=image)
				image_tag = 'image_%d' % len(self.images)
				tags += ('image', image_tag)
				for tag in tags:
					self.textview.tag_add(tag, start_index, END)
				self.images[image_tag] = item
			if isinstance(item, Markdown.Span):
				for sub_item in item.contents:
					insert_item(sub_item, tags)
			elif isinstance(item, str):
				self.textview.insert(END, item, tags)
		end_index = len(block.spans)-1
		for index, span in enumerate(block.spans):
			line_tags = tags
			if index == 0 and additional_first_line_tags:
				line_tags += additional_first_line_tags
			if index == end_index and additional_last_line_tags:
				line_tags += additional_last_line_tags
			insert_item(span, line_tags)
			self.textview.insert(END, '\n', line_tags)
