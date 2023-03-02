
try:
	import Tkinter as _Tk
except:
	import tkinter as _Tk

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

	def after_background(self, callback, background_function, *args, **kwargs):
		from threading import Thread
		from Queue import Queue

		class BackgroundThread(Thread):
			def __init__(self, function, args, kwargs):
				Thread.__init__(self)
				self.queue = Queue()
				self.function = function
				self.args = args
				self.kwargs = kwargs

			def run(self):
				try:
					result = self.function(*args, **kwargs)
				except Exception as exception:
					result = exception
				self.queue.put(result)

		def watch_background_thread(thread): # type: (BackgroundThread) -> None
			result = None
			try:
				result = thread.queue.get(False)
			except:
				pass
			if not thread.is_alive():
				callback(result)
				return
			self.after(200, watch_background_thread, thread)

		thread = BackgroundThread(background_function, args, kwargs)
		thread.start()
		watch_background_thread(thread)
