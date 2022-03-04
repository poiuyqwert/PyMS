
import Tkinter as Tk

class MainWindow(Tk.Tk):
	def startup(self):
		self.lift()
		self.call('wm', 'attributes', '.', '-topmost', True)
		self.after_idle(self.call, 'wm', 'attributes', '.', '-topmost', False)
		self.focus_force()
		# On Mac the main window doesn't get focused, so we use Cocoa to focus it
		try:
			from os import getpid
			from Cocoa import NSRunningApplication, NSApplicationActivateIgnoringOtherApps # pylint: disable=no-name-in-module

			app = NSRunningApplication.runningApplicationWithProcessIdentifier_(getpid())
			app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
		except:
			pass
		self.mainloop()

	def maxsize(self, width=None, height=None):
		if width and height and not hasattr(self, '_initial_max_size'):
			self._initial_max_size = Tk.Tk.maxsize(self)
		return Tk.Tk.maxsize(self, width, height)

	# `wm_state` will be `'zoomed'` when `window.size == window.maxsize`, not just when it is maximized
	def is_maximized(self):
		is_maximized = (self.wm_state() == 'zoomed')
		if is_maximized and hasattr(self, '_initial_max_size'):
			cur_max_width, cur_max_height = self.maxsize()
			initial_max_width, initial_max_height = self._initial_max_size
			is_maximized = (cur_max_width >= initial_max_width and cur_max_height >= initial_max_height)
		return is_maximized

	def set_icon(self, name):
		from ...Utilities import Assets
		try:
			self.icon = Assets.get_image('%s.ico' % name)
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % Assets.image_path('%s.xbm' % name)
			self.wm_iconbitmap(self.icon)

	def destroy(self):
		from ...Utilities import Assets
		Assets.clear_image_cache()
		return Tk.Tk.destroy(self)
