
from .PyMSDialog import PyMSDialog
from .WarningDialog import WarningDialog
from .InternalErrorDialog import InternalErrorDialog
from .UIKit import *

import sys, traceback

class ErrorDialog(PyMSDialog):
	def __init__(self, parent, error):
		self.error = error
		PyMSDialog.__init__(self, parent, '%s Error!' % error.type, resizable=(False, False))

	def widgetize(self):
		Label(self, justify=LEFT, anchor=W, text=self.error.repr(), wraplen=640).pack(pady=10, padx=5)
		frame = Frame(self)
		ok = Button(frame, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3)
		w = len(self.error.warnings)
		p = 's'
		if w == 1:
			p = ''
		Button(frame, text='%s Warning%s' % (w, p), width=10, command=self.viewwarnings, state=[NORMAL,DISABLED][not self.error.warnings]).pack(side=LEFT, padx=3)
		Button(frame, text='Copy', width=10, command=self.copy).pack(side=LEFT, padx=6)
		if self.error.exception:
			Button(frame, text='Internal Error', width=10, command=self.internal).pack(side=LEFT, padx=6)
		frame.pack(pady=10)
		return ok

	def copy(self):
		self.clipboard_clear()
		self.clipboard_append(self.error.repr())

	def viewwarnings(self):
		WarningDialog(self, self.error.warnings)

	def internal(self):
		InternalErrorDialog(self, sys.stderr.prog, txt=''.join(traceback.format_exception(*self.error.exception)))
