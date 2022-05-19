
from Tooltip import Tooltip

from UIKit import Text
from utils import apply_cursor

class TextTooltip(Tooltip):
	def __init__(self, parent, tag, **kwargs): # type: (Text, str, **Any) -> TextTooltip
		self.tag = tag
		self.cursor = kwargs.pop('cursor', None) # type: (list[str] | None)
		self._old_cursor = None
		kwargs['mouse'] = True
		Tooltip.__init__(self, parent, **kwargs)

	def setupbinds(self, press):
		self.parent.tag_bind(self.tag, '<Enter>', self.enter, '+')
		self.parent.tag_bind(self.tag, '<Leave>', self.leave, '+')
		self.parent.tag_bind(self.tag, '<Motion>', self.motion, '+')
		self.parent.tag_bind(self.tag, '<Button-1>', self.leave, '+')
		if press:
			self.parent.tag_bind(self.tag, '<ButtonPress>', self.leave)

	def enter(self, _=None):
		if self.cursor:
			self._old_cursor = self.parent.cget('cursor')
			apply_cursor(self.parent, self.cursor)
		Tooltip.enter(self)

	def leave(self, _=None):
		if self._old_cursor:
			self.parent.config(cursor=self._old_cursor)
		Tooltip.leave(self)

class TextDynamicTooltip(TextTooltip):
	def __init__(self, parent, tag, text_lookup, **kwargs): # type: (Text, str, Callable[[str, tuple[str, ...]], str], **Any) -> TextDynamicTooltip
		self.text_lookup = text_lookup
		TextTooltip.__init__(self, parent, tag, **kwargs)

	def showtip(self):
		textview = self.parent # type: Text
		index = textview.index('current')
		tags = textview.tag_names(index)
		if not self.tag in tags:
			return
		tag_range = textview.tag_prevrange(self.tag, index)
		if not tag_range or len(tag_range) != 2:
			return
		tag_text = textview.get(*tag_range)
		text = self.text_lookup(tag_text, tags)
		if not text:
			return
		self.text = text
		TextTooltip.showtip(self)
