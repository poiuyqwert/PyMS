
from .PyMSDialog import PyMSDialog
from .UIKit import *
from .SettingsFile import SettingsFile
from .MPQHandler import MPQHandler

class BaseSettingsDialog(PyMSDialog):
	def __init__(self, parent, settings, mpqhandler=None): # type: (Toplevel, SettingsFile, MPQHandler) -> BaseSettingsDialog
		self.settings = settings
		self.mpqhandler = mpqhandler
		self.edited = False
		self.notebook = None # type: Notebook
		PyMSDialog.__init__(self, parent, 'Settings')

	def widgetize(self):
		self.notebook = Notebook(self)
		self.notebook.pack(fill=BOTH, expand=1, padx=5, pady=5)
		btns = Frame(self)
		ok = Button(btns, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(btns, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		btns.pack()
		return ok
