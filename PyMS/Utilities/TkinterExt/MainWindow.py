
import Tkinter as Tk

class MainWindow(Tk.Tk):
	def startup(self):
		self.lift()
		self.call('wm', 'attributes', '.', '-topmost', True)
		self.after_idle(self.call, 'wm', 'attributes', '.', '-topmost', False)
		self.focus_force()
		# On Mac the main window doesn't get focused, so we use Cocoa to focus it
		try:
			import os
			from Cocoa import NSRunningApplication, NSApplicationActivateIgnoringOtherApps

			app = NSRunningApplication.runningApplicationWithProcessIdentifier_(os.getpid())
			app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
		except:
			pass
		self.mainloop()

	def set_icon(self, name):
		from ..utils import BASE_DIR
		import os
		try:
			self.icon = os.path.join(BASE_DIR, 'PyMS','Images','%s.ico' % name)
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'PyMS','Images','%s.xbm' % name)
			self.wm_iconbitmap(self.icon)
