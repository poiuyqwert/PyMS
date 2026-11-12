
from ..Widgets import Tk
from ..Widgets.Extensions import WindowExtensions

from typing import Any

class MainWindow(Tk, WindowExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		Tk.__init__(self, *args, **kwargs)
		# Stay invisible until `startup()` so the window doesn't flash at the
		# OS-chosen position/size before its config geometry is loaded.
		self.conceal()

	def initialize(self) -> None:
		pass

	def startup(self) -> None:
		self.reveal()
		self.lift()
		self.call('wm', 'attributes', '.', '-topmost', True)
		self.after_idle(self.call, 'wm', 'attributes', '.', '-topmost', False)
		self.focus_force()
		# On Mac the main window doesn't get focused, so we use Cocoa to focus it
		try:
			from os import getpid
			from Cocoa import NSRunningApplication, NSApplicationActivateIgnoringOtherApps # type: ignore[import] # pylint: disable=import-error

			app = NSRunningApplication.runningApplicationWithProcessIdentifier_(getpid())
			app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
		except Exception:
			pass
		self.after_managed(1, self.initialize)
		self.mainloop()

	def set_icon(self, name: str) -> None:
		from ... import Assets  # pylint: disable=cyclic-import
		# `wm iconphoto` raises when given no images, so a program without its own icons falls back to the PyMS icons
		try:
			self.wm_iconphoto(True, *Assets.lookup_icons(name))
		except Exception:
			try:
				self.wm_iconphoto(True, *Assets.lookup_icons('PyMS'))
			except Exception:
				from ... import trace  # pylint: disable=cyclic-import
				if tracer := trace.get_tracer():
					tracer.trace_error()

	def destroy(self) -> None:
		from ... import Assets  # pylint: disable=cyclic-import
		# Cleared after destroying, since widgets' callbacks while being destroyed (e.g. resizing) can get images, which would be cached for the destroyed window
		Tk.destroy(self)
		Assets.clear_image_cache()
