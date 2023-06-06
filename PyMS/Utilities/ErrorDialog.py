
from .PyMSDialog import PyMSDialog
from .WarningDialog import WarningDialog
from .InternalErrorDialog import InternalErrorDialog
from .UIKit import *
from .PyMSError import PyMSError
from .trace import get_tracer

import sys, traceback

class ErrorDialog(PyMSDialog):
	def __init__(self, parent, error): # type: (Misc, PyMSError) -> None
		self.error = error
		PyMSDialog.__init__(self, parent, '%s Error!' % error.type, resizable=(False, False))

	def widgetize(self): # type: () -> (Misc | None)
		Label(self, justify=LEFT, anchor=W, text=self.error.repr(), wraplength=640).pack(pady=10, padx=5)
		frame = Frame(self)
		ok = Button(frame, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3)
		w = len(self.error.warnings)
		p = 's'
		if w == 1:
			p = ''
		Button(frame, text='%s Warning%s' % (w, p), width=10, command=self.viewwarnings, state=DISABLED if not self.error.warnings else NORMAL).pack(side=LEFT, padx=3)
		Button(frame, text='Copy', width=10, command=self.copy).pack(side=LEFT, padx=6)
		if self.error.exception:
			Button(frame, text='Internal Error', width=10, command=self.internal).pack(side=LEFT, padx=6)
		frame.pack(pady=10)
		return ok

	def copy(self): # type: () -> None
		self.clipboard_clear()
		self.clipboard_append(self.error.repr())

	def viewwarnings(self): # type: () -> None
		WarningDialog(self, self.error.warnings)

	def internal(self): # type: () -> None
		program_name = 'PyMS'
		if tracer := get_tracer():
			program_name = tracer.program_name
		InternalErrorDialog(self, program_name, txt=''.join(traceback.format_exception(*self.error.exception)))
