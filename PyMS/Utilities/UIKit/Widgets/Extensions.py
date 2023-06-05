
try:
	import tkinter as _Tk
except:
	import tkinter as _Tk

from typing import TYPE_CHECKING, Callable, Literal
if TYPE_CHECKING:
	from ..EventPattern import EventPattern

class Extensions(_Tk.Misc):
	def remove_bind(self, sequence, funcid): # type: (str, str) -> None
		"""Unbind for this widget for event SEQUENCE  the
		function identified with FUNCID."""
		bound = ''
		if funcid:
			self.deletecommand(funcid)
			funcs = self.tk.call('bind', self._w, sequence, None).split('\n')
			bound = '\n'.join([f for f in funcs if not f.startswith('if {{"[{0}'.format(funcid))])
		self.tk.call('bind', self._w, sequence, bound)

	def apply_cursor(self, cursors): # type: (list[str]) -> (str | None)
		for cursor in reversed(cursors):
			try:
				self.config(cursor=cursor)
				return cursor
			except:
				pass

	def clipboard_set(self, text):
		self.clipboard_clear()
		self.clipboard_append(text)
