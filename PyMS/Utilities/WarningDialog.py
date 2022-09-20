
from .PyMSDialog import PyMSDialog
from .UIKit import *

class WarningDialog(PyMSDialog):
	def __init__(self, parent, warnings, cont=False):
		self.warnings = warnings
		self.cont = cont
		PyMSDialog.__init__(self, parent, 'Warning!', resizable=(False, False))

	def widgetize(self):
		self.bind(Ctrl.a, self.selectall)
		frame = Frame(self, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(frame, orient=HORIZONTAL)
		vscroll = Scrollbar(frame)
		self.warntext = Text(frame, bd=0, highlightthickness=0, width=60, height=10, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, wrap=NONE, exportselection=0)
		self.warntext.tag_config('highlevel', foreground='#960000')
		self.warntext.grid()
		hscroll.config(command=self.warntext.xview)
		hscroll.grid(sticky=EW)
		vscroll.config(command=self.warntext.yview)
		vscroll.grid(sticky=NS, row=0, column=1)
		for warning in self.warnings:
			if warning.level:
				self.warntext.insert(END, warning.repr(), 'highlevel')
			else:
				self.warntext.insert(END, warning.repr())
		self.warntext['state'] = DISABLED
		frame.pack(side=TOP, pady=2, padx=2)
		buttonbar = Frame(self)
		ok = Button(buttonbar, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3)
		if self.cont:
			Button(buttonbar, text='Cancel', width=10, command=self.cancel).pack(side=LEFT)
		buttonbar.pack(pady=10)
		return ok

	def selectall(self, key=None):
		self.warntext.focus_set()
		self.warntext.tag_add(SEL, 1.0, END)

	def ok(self):
		self.cont = True
		PyMSDialog.ok(self)

	def cancel(self):
		self.cont = False
		PyMSDialog.ok(self)
