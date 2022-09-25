
from ..FileFormats import TBL

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

class EditStringDialog(PyMSDialog):
	def __init__(self, parent, string, title='Edit String'):
		self.string = string
		PyMSDialog.__init__(self, parent, title)

	def widgetize(self):
		Label(self, text='String:', anchor=W).pack(fill=X)

		info = Frame(self)
		vscroll = Scrollbar(info)
		self.info = Text(info, yscrollcommand=vscroll.set, width=1, height=1, wrap=WORD)
		self.info.insert(1.0, self.string)
		self.info.pack(side=LEFT, fill=BOTH, expand=1)
		vscroll.config(command=self.info.yview)
		vscroll.pack(side=RIGHT, fill=Y)
		info.pack(fill=BOTH, expand=1)

		buttonframe = Frame(self)
		self.okbtn = Button(buttonframe, text='Ok', width=10, command=self.ok)
		self.okbtn.pack(side=LEFT, padx=3, pady=3)
		Button(buttonframe, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		buttonframe.pack()

		return self.info

	def setup_complete(self):
		self.minsize(300,100)
		self.parent.parent.settings.windows.load_window_size('string_edit', self)

	def ok(self):
		string = TBL.compile_string(self.info.get(1.0, END)[:-1])
		if not string.endswith('\x00'):
			string += '\x00'
		self.string = string
		PyMSDialog.ok(self)

	def cancel(self):
		PyMSDialog.ok(self)

	def dismiss(self):
		self.parent.parent.settings.windows.save_window_size('string_edit', self)
		PyMSDialog.dismiss(self)
