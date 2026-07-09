
from .PyMSDialog import PyMSDialog
from . import UIKit as UI
from .PyMSWarning import PyMSWarning

class WarningDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, warnings: list[PyMSWarning], cont: bool = False) -> None:
		self.warnings = warnings
		self.cont = cont
		PyMSDialog.__init__(self, parent, 'Warning!', resizable=(False, False))

	def widgetize(self) -> UI.Misc | None:
		self.bind(UI.Ctrl.a(), self.selectall)
		frame = UI.Frame(self, bd=2, relief=UI.SUNKEN)
		hscroll = UI.Scrollbar(frame, orient=UI.HORIZONTAL)
		vscroll = UI.Scrollbar(frame)
		self.warntext = UI.Text(frame, bd=0, highlightthickness=0, width=60, height=10, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, wrap=UI.NONE, exportselection=False)
		self.warntext.tag_config('highlevel', foreground='#960000')
		self.warntext.grid()
		hscroll.config(command=self.warntext.xview)
		hscroll.grid(sticky=UI.EW)
		vscroll.config(command=self.warntext.yview)
		vscroll.grid(sticky=UI.NS, row=0, column=1)
		for warning in self.warnings:
			if warning.level:
				self.warntext.insert(UI.END, repr(warning) + '\n', 'highlevel')
			else:
				self.warntext.insert(UI.END, repr(warning) + '\n')
		self.warntext['state'] = UI.DISABLED
		frame.pack(side=UI.TOP, pady=2, padx=2)
		buttonbar = UI.Frame(self)
		ok = UI.Button(buttonbar, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=3)
		if self.cont:
			UI.Button(buttonbar, text='Cancel', width=10, command=self.cancel).pack(side=UI.LEFT)
		buttonbar.pack(pady=10)
		return ok

	def selectall(self, _event: UI.Event | None = None) -> None:
		self.warntext.focus_set()
		self.warntext.tag_add(UI.SEL, 1.0, UI.END)

	def ok(self, _: UI.Event | None = None) -> None:
		self.cont = True
		PyMSDialog.ok(self)

	def cancel(self, _: UI.Event | None = None) -> None:
		self.cont = False
		PyMSDialog.ok(self)
