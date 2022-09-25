
from .LocaleDialog import LOCALE_CHOICES

from ..Utilities.UIKit import *
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.EntryDropDown import EntryDropDown

class GeneralSettings(Frame):
	def __init__(self, parent, setdlg=None):
		if setdlg == None:
			self.setdlg = parent.parent
		else:
			self.setdlg = setdlg
		Frame.__init__(self, parent)

		self.maxfiles = IntegerVar(1,[1,65535])
		self.maxfiles.set(self.setdlg.settings.settings.defaults.get('maxfiles'))
		self.maxfiles.trace('w', self.changed)

		self.blocksize = IntegerVar(1,[1,23])
		self.blocksize.set(self.setdlg.settings.settings.defaults.get('blocksize'))
		self.blocksize.trace('w', self.changed)

		f = Frame(self)
		Label(f, text='Max Files', font=Font.default().bolded(), anchor=W).pack(fill=X, expand=1)
		Label(f, text='Max file capacity for new archives (cannot be changed for an existing archive)', anchor=W).pack(fill=X, expand=1)
		Entry(f, textvariable=self.maxfiles, width=5).pack(side=LEFT)
		f.pack(side=TOP, fill=X)

		f = Frame(self)
		Label(f, text='Block Size', font=Font.default().bolded(), anchor=W).pack(fill=X, expand=1)
		Label(f, text='Block size for new archives (default is 3)', anchor=W).pack(fill=X, expand=1)
		Entry(f, textvariable=self.blocksize, width=2).pack(side=LEFT)
		f.pack(side=TOP, fill=X)

	def changed(self, *_):
		self.setdlg.edited = True

	def save(self, page_data, mpq_dir, settings):
		settings.settings.defaults.maxfiles = self.maxfiles.get()
		settings.settings.defaults.blocksize = self.blocksize.get()
