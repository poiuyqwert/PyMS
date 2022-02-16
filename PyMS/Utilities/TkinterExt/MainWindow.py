
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
