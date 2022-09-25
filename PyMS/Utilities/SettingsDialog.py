
from . import Assets
from .PyMSDialog import PyMSDialog
from .Notebook import Notebook
from .MPQSettings import MPQSettings
from .SettingsPanel import SettingsPanel
from .ErrorDialog import ErrorDialog
from .UIKit import *

import copy

class SettingsDialog(PyMSDialog):
	def __init__(self, parent, data, min_size, err=None, settings=None, mpqhandler=None):
		self.min_size = min_size
		self.data = data
		self.pages = []
		self.err = err
		self.mpqhandler = mpqhandler
		self.edited = False
		self.settings = parent.settings if settings == None else settings
		PyMSDialog.__init__(self, parent, 'Settings')

	def widgetize(self):
		if self.data:
			self.tabs = Notebook(self)
			if self.mpqhandler:
				self.mpqsettings = MPQSettings(self.tabs, self.mpqhandler.mpq_paths(), self.settings)
				self.tabs.add_tab(self.mpqsettings, 'MPQ Settings')
			for d in self.data:
				if isinstance(d[1],list):
					self.pages.append(SettingsPanel(self.tabs, d[1], self.settings, self.mpqhandler))
				else:
					self.pages.append(d[1](self.tabs))
				self.tabs.add_tab(self.pages[-1], d[0])
			self.tabs.pack(fill=BOTH, expand=1, padx=5, pady=5)
		else:
			self.mpqsettings = MPQSettings(self, self.mpqhandler.mpq_paths(), self.settings, self)
			self.mpqsettings.pack(fill=BOTH, expand=1, padx=5, pady=5)
		btns = Frame(self)
		ok = Button(btns, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(btns, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		btns.pack()
		if self.err:
			self.after(1, self.showerr)
		return ok

	def setup_complete(self):
		self.minsize(*self.min_size)
		self.settings.windows.settings.load_window_size('main', self)

	def showerr(self):
		ErrorDialog(self, self.err)

	def cancel(self):
		if self.err:
			if MessageBox.askyesno(parent=self, title='Exit?', message="One or more files required for this program can not be found and must be chosen. Canceling will close the program, do you wish to continue?"):
				self.parent.after(1, self.parent.exit)
				PyMSDialog.ok(self)
			else:
				pass
		elif not self.edited or MessageBox.askyesno(parent=self, title='Cancel?', message="Are you sure you want to cancel?\nAll unsaved changes will be lost."):
			PyMSDialog.ok(self)

	def save_settings(self):
		if self.mpqhandler:
			self.mpqhandler.set_mpqs(self.mpqsettings.mpqs)
		if self.data:
			for page,page_data in zip(self.pages,self.data):
				page.save(page_data,Assets.mpq_file_path(''),self.settings)

	def ok(self):
		if self.edited:
			old_mpqs = None
			old_settings = copy.deepcopy(self.settings)
			self.save_settings()
			if hasattr(self.parent, 'open_files'):
				e = self.parent.open_files()
				if e:
					if old_mpqs != None:
						self.mpqhandler.set_mpqs(old_mpqs)
					self.settings.update(old_settings, set=True)
					ErrorDialog(self, e)
					return
			if self.mpqhandler:
				self.settings.settings.mpqs = self.mpqhandler.mpq_paths()
		PyMSDialog.ok(self)

	def dismiss(self):
		self.settings.windows.settings.save_window_size('main', self)
		PyMSDialog.dismiss(self)
