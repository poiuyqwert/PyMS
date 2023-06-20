
from .Tooltip import Tooltip
from ..Widgets import *
from ..EventPattern import *

from typing import Callable

class TextTooltip(Tooltip):
	def __init__(self, parent: Text, tag: str, **kwargs) -> None:
		self.text_widget = parent
		self.tag = tag
		self.cursor = kwargs.pop('cursor', None) # type: (list[str] | None)
		self._old_cursor = None
		kwargs['mouse'] = True
		Tooltip.__init__(self, parent, **kwargs)

	def setupbinds(self, press: bool) -> None:
		self.text_widget.tag_bind(self.tag, Cursor.Enter(), self.enter, '+')
		self.text_widget.tag_bind(self.tag, Cursor.Leave(), self.leave, '+')
		self.text_widget.tag_bind(self.tag, Mouse.Motion(), self.motion, '+')
		self.text_widget.tag_bind(self.tag, Mouse.Click_Left(), self.leave, '+')
		if press:
			self.text_widget.tag_bind(self.tag, Mouse.ButtonPress(), self.leave)

	def enter(self, e: Event | None = None) -> None:
		if self.cursor:
			self._old_cursor = self.parent.cget('cursor')
			self.text_widget.apply_cursor(self.cursor) # type: ignore[attr-defined]
		Tooltip.enter(self)

	def leave(self, e: Event | None = None) -> None:
		if self._old_cursor:
			self.text_widget.config(cursor=self._old_cursor)
		Tooltip.leave(self)

class TextDynamicTooltip(TextTooltip):
	def __init__(self, parent: Text, tag: str, text_lookup: Callable[[str | None, tuple[str, ...]], str | None], **kwargs) -> None:
		self.text_lookup = text_lookup
		TextTooltip.__init__(self, parent, tag, **kwargs)

	def showtip(self):
		index = self.text_widget.index('current')
		tags = self.text_widget.tag_names(index)
		if not self.tag in tags:
			return
		tag_text = None
		tag_range = self.text_widget.tag_prevrange(self.tag, index)
		if tag_range and len(tag_range) == 2:
			tag_text = self.text_widget.get(*tag_range)
		text = self.text_lookup(tag_text, tags)
		if not text:
			return
		self.text = text
		TextTooltip.showtip(self)
