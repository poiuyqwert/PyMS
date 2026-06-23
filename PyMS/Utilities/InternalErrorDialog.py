
from . import Assets
from .PyMSDialog import PyMSDialog
from . import UIKit as UI

import traceback, sys, platform

class InternalErrorDialog(PyMSDialog):
	CAPTURE_NONE = 0
	CAPTURE_PRINT = 1
	CAPTURE_DIALOG = 2
	@staticmethod
	def capture(parent: UI.Misc, prog: str, exception: BaseException | None = None, debug: int = CAPTURE_DIALOG) -> None:
		if exception is not None:
			trace = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
		else:
			trace = ''.join(traceback.format_exception(*sys.exc_info()))
		if debug == InternalErrorDialog.CAPTURE_DIALOG:
			InternalErrorDialog(parent, prog, txt=trace)
		elif debug == InternalErrorDialog.CAPTURE_PRINT:
			print(trace)

	def __init__(self, parent: UI.Misc, prog: str, txt: str | None = None) -> None:
		self.prog = prog
		self.txt = txt
		PyMSDialog.__init__(self, parent, 'PyMS Internal Error!', grabwait=False)

	def widgetize(self) -> UI.Misc | None:
		self.bind(UI.Ctrl.a(), self.selectall)
		UI.Label(self, text=f'The PyMS program "{self.prog}" has encountered an unknown internal error.\nThe program will attempt to continue, but may cause problems or crash once you press Ok.\nPlease contact poiuy_qwert and send him this traceback with any relivant information, see the Issues/Feedback section in the Readme for details.', justify=UI.LEFT).pack(side=UI.TOP, padx=2, pady=2, fill=UI.X)
		r = UI.Frame(self)
		UI.Hotlink(r, 'Readme (Local)', f'file:///{Assets.readme_file_path}').pack(side=UI.RIGHT, padx=10, pady=2)
		UI.Hotlink(r, 'Readme (Online)', 'https://github.com/poiuyqwert/PyMS#issuesfeedback').pack(side=UI.RIGHT, padx=10, pady=2)
		r.pack(fill=UI.X)
		frame = UI.Frame(self, bd=2, relief=UI.SUNKEN)
		hscroll = UI.Scrollbar(frame, orient=UI.HORIZONTAL)
		vscroll = UI.Scrollbar(frame)
		self.text = UI.Text(frame, bd=0, highlightthickness=0, width=70, height=10, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, wrap=UI.NONE, exportselection=False, state=UI.DISABLED)
		self.add_text(f'PyMS: {Assets.version("PyMS")}')
		self.add_text(f'{self.prog}: {Assets.version(self.prog)}')
		self.add_text(f'Python: {sys.version}')
		try:
			self.add_text(f'Tcl/Tk: {UI.Tcl().call("info", "patchlevel")}')
		except Exception:
			pass
		self.add_text(f'Platform: {platform.system()}')
		if self.txt:
			self.add_text(self.txt)
		self.text.grid(sticky=UI.NSEW)
		hscroll.config(command=self.text.xview)
		hscroll.grid(sticky=UI.EW)
		vscroll.config(command=self.text.yview)
		vscroll.grid(sticky=UI.NS, row=0, column=1)
		frame.grid_rowconfigure(0, weight=1)
		frame.grid_columnconfigure(0, weight=1)
		frame.pack(fill=UI.BOTH, pady=2, padx=2, expand=1)
		buttonbar = UI.Frame(self)
		ok = UI.Button(buttonbar, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=3)
		buttonbar.pack(side=UI.BOTTOM, pady=10)
		return ok

	def selectall(self, _event: UI.Event | None = None) -> None:
		self.text.focus_set()
		self.text.tag_add(UI.SEL, '1.0', UI.END)

	def add_text(self, text: str, newline: bool = True) -> None:
		self.text['state'] = UI.NORMAL
		self.text.insert(UI.END, text)
		if newline:
			self.text.insert(UI.END, '\n')
		self.text['state'] = UI.DISABLED
