
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.UIKit import *
from ..Utilities.TextDropDown import TextDropDown

class GotoDialog(PyMSDialog):
	def __init__(self, parent):
		self.goto = IntegerVar(range=(0,65535), allow_hex=True)
		PyMSDialog.__init__(self, parent, 'Goto', grabwait=False, escape=True, resizable=(False,False))

	def widgetize(self):
		f = Frame(self)
		Label(f, text='Index:').grid(row=0,column=0)
		self.gotoentry = TextDropDown(f, self.goto, self.parent.gotohistory, 5)
		self.gotoentry.entry.selection_range(0, END)
		self.gotoentry.grid(row=0,column=1)

		Button(f, text='Goto', command=self.jump).grid(row=0,column=2, padx=(4,0))
		f.pack(padx=4,pady=4)

		self.bind(Key.Return, self.jump)

		return self.gotoentry

	def setup_complete(self):
		self.parent.settings.windows.load_window_size('goto', self)

	def jump(self, event=None):
		s = self.goto.get(True)
		if not s in self.parent.gotohistory:
			self.parent.gotohistory.insert(0, s)
		i = min(self.goto.get(), len(self.parent.tbl.strings)-1)
		self.parent.listbox.select_clear(0,END)
		self.parent.listbox.select_set(i)
		self.parent.listbox.see(i)
		self.parent.update()

	def dismiss(self):
		self.parent.settings.windows.save_window_size('goto', self)
		PyMSDialog.dismiss(self)
