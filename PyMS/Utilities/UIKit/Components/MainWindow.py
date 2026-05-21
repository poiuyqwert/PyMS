
from ..Widgets import *
from ..Widgets.Extensions import WindowExtensions

class MainWindow(Tk, WindowExtensions):
	def initialize(self) -> None:
		pass

	def startup(self) -> None:
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
		except:
			pass
		self.after_managed(1, self.initialize)
		self.mainloop()

	def set_icon(self, name: str) -> None:
		from ... import Assets
		import os
		try:
			icon = Assets.lookup_image(f'{name}.ico')
			if not icon:
				icon = Assets.lookup_image(name)
			if not icon:
				icon = Assets.lookup_image('PyMS.ico')
			if not icon:
				icon = Assets.lookup_image('PyMS')
			if icon:
				try:
					self.tk.call('wm', 'iconphoto', getattr(self, '_w'), '-default', icon) # Python3: self.wm_iconphoto(True, icon)
					return
				except:
					self.wm_iconbitmap(default=icon)
					return
		except:
			pass
		try:
			icon_path = Assets.image_path(f'{name}.xbm')
			if not os.path.exists(icon_path):
				icon_path = Assets.image_path('PyMS.xbm')
			icon_path = f'@{icon_path}'
			self.wm_iconbitmap(default=icon_path)
		except:
			pass

	def destroy(self) -> None:
		from ... import Assets
		Assets.clear_image_cache()
		return Tk.destroy(self)
