
from .PyMSDialog import PyMSDialog
from .UIKit import *

class WarnDialog(PyMSDialog):
	def __init__(self, parent, message, title='Warning!', show_dont_warn=False):
		self.message = message
		self.dont_warn = IntVar()
		self.show_dont_warn = show_dont_warn
		PyMSDialog.__init__(self, parent, title, resizable=(False, False))

	def widgetize(self):
		Label(self, text=self.message).pack(side=TOP, padx=20,pady=10)
		frame = Frame(self)
		if self.show_dont_warn:
			Checkbutton(frame, text="Don't warn me again", variable=self.dont_warn, anchor=W).pack(side=LEFT, padx=(0,10))
		ok = Button(frame, text='Ok', width=10, command=self.ok)
		ok.pack(side=RIGHT)
		frame.pack(side=BOTTOM, fill=BOTH, padx=20,pady=(0,10))
		return ok

	def setup_complete(self):
		self.minsize(300, 100)
