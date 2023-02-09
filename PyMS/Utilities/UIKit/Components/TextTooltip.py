
from .Tooltip import Tooltip
from ..Widgets import *
from ..EventPattern import *

class TextTooltip(Tooltip):
	def __init__(self, parent, tag, **kwargs): # type: (Text, str, **Any) -> TextTooltip
		self.tag = tag
		self.cursor = kwargs.pop('cursor', None) # type: (list[str] | None)
		self._old_cursor = None
		kwargs['mouse'] = True
		Tooltip.__init__(self, parent, **kwargs)

	def setupbinds(self, press):
		self.parent.tag_bind(self.tag, Cursor.Enter, self.enter, '+')
		self.parent.tag_bind(self.tag, Cursor.Leave, self.leave, '+')
		self.parent.tag_bind(self.tag, Mouse.Motion, self.motion, '+')
		self.parent.tag_bind(self.tag, Mouse.Click_Left, self.leave, '+')
		if press:
			self.parent.tag_bind(self.tag, Mouse.ButtonPress, self.leave)

	def enter(self, _=None):
		if self.cursor:
			self._old_cursor = self.parent.cget('cursor')
			self.parent.apply_cursor(self.cursor)
		Tooltip.enter(self)

	def leave(self, _=None):
		if self._old_cursor:
			self.parent.config(cursor=self._old_cursor)
		Tooltip.leave(self)

class TextDynamicTooltip(TextTooltip):
	def __init__(self, parent, tag, text_lookup, **kwargs): # type: (Text, str, Callable[[str | None, tuple[str, ...]], str], **Any) -> TextDynamicTooltip
		self.text_lookup = text_lookup
		TextTooltip.__init__(self, parent, tag, **kwargs)

	def showtip(self):
		textview = self.parent # type: Text
		index = textview.index('current')
		tags = textview.tag_names(index)
		if not self.tag in tags:
			return
		tag_text = None
		tag_range = textview.tag_prevrange(self.tag, index)
		if tag_range and len(tag_range) == 2:
			tag_text = textview.get(*tag_range)
		text = self.text_lookup(tag_text, tags)
		if not text:
			return
		self.text = text
		TextTooltip.showtip(self)
