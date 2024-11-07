
from ..Utils import remove_bind

import tkinter as _Tk

from typing import TypeVar, ParamSpec, Callable

T = TypeVar('T')
P = ParamSpec('P')

class Extensions(_Tk.Misc):
	def remove_bind(self, sequence: str, funcid: str) -> None:
		"""Unbind for this widget for event SEQUENCE  the
		function identified with FUNCID."""
		remove_bind(self, sequence, funcid)

	def apply_cursor(self, cursors: list[str]) -> (str | None):
		for cursor in reversed(cursors):
			try:
				self.configure(cursor=cursor) # type: ignore[call-arg]
				return cursor
			except:
				pass
		return None

	def clipboard_not_empty(self) -> bool:
		return not not self.clipboard_get()

	def clipboard_set(self, text: str) -> None:
		self.clipboard_clear()
		self.clipboard_append(text)

	def after_background(self, callback: Callable[[T | Exception | None], None], background_function: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> None:
		from threading import Thread
		from queue import Queue

		class BackgroundThread(Thread):
			def __init__(self, function: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> None:
				Thread.__init__(self)
				self.queue: Queue[T | Exception] = Queue()
				self.function = function
				self.args = args
				self.kwargs = kwargs

			def run(self) -> None:
				result: T | Exception
				try:
					result = self.function(*args, **kwargs)
				except Exception as exception:
					result = exception
				self.queue.put(result)

		def watch_background_thread(thread: BackgroundThread) -> None:
			result = None
			try:
				result = thread.queue.get(False)
			except:
				pass
			if not thread.is_alive():
				callback(result)
				return
			self.after(200, watch_background_thread, thread)

		thread = BackgroundThread(background_function, *args, **kwargs)
		thread.start()
		watch_background_thread(thread)

class WindowExtensions(_Tk.Misc, _Tk.Wm):
	def maxsize(self, width: int | None = None, height: int | None = None) -> tuple[int, int]: # type: ignore[override]
		if width and height and not hasattr(self, '_initial_max_size'):
			self._initial_max_size: tuple[int, int] | None = _Tk.Toplevel.maxsize(self)
		return _Tk.Toplevel.maxsize(self, width, height) # type: ignore[arg-type]

	# `wm_state` will be `'zoomed'` when `window.size == window.maxsize`, not just when it is maximized
	def is_maximized(self) -> bool:
		is_maximized = (self.wm_state() == 'zoomed')
		if is_maximized and hasattr(self, '_initial_max_size') and self._initial_max_size is not None:
			cur_max_width, cur_max_height = self.maxsize()
			initial_max_width, initial_max_height = self._initial_max_size
			is_maximized = (cur_max_width >= initial_max_width and cur_max_height >= initial_max_height)
		return is_maximized
