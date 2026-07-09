
import traceback

from .PyMSDialog import PyMSDialog
from .WarningDialog import WarningDialog
from .InternalErrorDialog import InternalErrorDialog
from . import UIKit as UI
from .PyMSError import PyMSError
from .trace import get_tracer

class ErrorDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, error: PyMSError) -> None:
		self.error = error
		self.chained_exception: BaseException | None = error.__cause__ or error.__context__
		PyMSDialog.__init__(self, parent, f'{error.type} Error!', resizable=(False, False))

	def widgetize(self) -> UI.Misc | None:
		UI.Label(self, justify=UI.LEFT, anchor=UI.W, text=repr(self.error), wraplength=640).pack(pady=10, padx=5)
		frame = UI.Frame(self)
		ok = UI.Button(frame, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=3)
		w = len(self.error.warnings)
		p = 's'
		if w == 1:
			p = ''
		UI.Button(frame, text=f'{w} Warning{p}', width=10, command=self.viewwarnings, state=UI.DISABLED if not self.error.warnings else UI.NORMAL).pack(side=UI.LEFT, padx=3)
		UI.Button(frame, text='Copy', width=10, command=self.copy).pack(side=UI.LEFT, padx=6)
		if self.chained_exception:
			UI.Button(frame, text='Internal Error', width=10, command=self.internal).pack(side=UI.LEFT, padx=6)
		frame.pack(pady=10)
		return ok

	def copy(self) -> None:
		self.clipboard_clear()
		self.clipboard_append(repr(self.error))

	def viewwarnings(self) -> None:
		WarningDialog(self, self.error.warnings)

	def internal(self) -> None:
		program_name = 'PyMS'
		if tracer := get_tracer():
			program_name = tracer.program_name
		assert self.chained_exception is not None
		formatted = traceback.TracebackException.from_exception(self.chained_exception).format()
		InternalErrorDialog(self, program_name, txt=''.join(formatted))
