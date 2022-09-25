
from . import Assets
from .PyMSDialog import PyMSDialog
from .Hotlink import Hotlink
from .UIKit import *

import traceback

class InternalErrorDialog(PyMSDialog):
	CAPTURE_NONE = 0
	CAPTURE_PRINT = 1
	CAPTURE_DIALOG = 2
	@staticmethod
	def capture(parent, prog, debug=0):
		trace = ''.join(traceback.format_exception(*sys.exc_info()))
		if debug == InternalErrorDialog.CAPTURE_DIALOG:
			InternalErrorDialog(parent, prog, txt=trace)
		elif debug == InternalErrorDialog.CAPTURE_PRINT:
			print(trace)

	def __init__(self, parent, prog, txt=None):
		self.prog = prog
		self.txt = txt
		PyMSDialog.__init__(self, parent, 'PyMS Internal Error!', grabwait=False)

	def widgetize(self):
		self.bind(Ctrl.a, self.selectall)
		Label(self, text='The PyMS program "%s" has encountered an unknown internal error.\nThe program will attempt to continue, but may cause problems or crash once you press Ok.\nPlease contact poiuy_qwert and send him this traceback with any relivant information, see the Issues/Feedback section in the Readme for details.' % self.prog, justify=LEFT).pack(side=TOP, padx=2, pady=2, fill=X)
		r = Frame(self)
		Hotlink(r, 'Readme (Local)', 'file:///%s' % Assets.readme_file_path).pack(side=RIGHT, padx=10, pady=2)
		Hotlink(r, 'Readme (Online)', 'https://github.com/poiuyqwert/PyMS#issuesfeedback').pack(side=RIGHT, padx=10, pady=2)
		r.pack(fill=X)
		frame = Frame(self, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(frame, orient=HORIZONTAL)
		vscroll = Scrollbar(frame)
		self.text = Text(frame, bd=0, highlightthickness=0, width=70, height=10, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, wrap=NONE, exportselection=0, state=DISABLED)
		if self.txt:
			self.text['state'] = NORMAL
			self.text.insert(END, self.txt)
			self.text['state'] = DISABLED
		self.text.grid(sticky=NSEW)
		hscroll.config(command=self.text.xview)
		hscroll.grid(sticky=EW)
		vscroll.config(command=self.text.yview)
		vscroll.grid(sticky=NS, row=0, column=1)
		frame.grid_rowconfigure(0, weight=1)
		frame.grid_columnconfigure(0, weight=1)
		frame.pack(fill=BOTH, pady=2, padx=2, expand=1)
		buttonbar = Frame(self)
		ok = Button(buttonbar, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3)
		buttonbar.pack(side=BOTTOM, pady=10)
		return ok

	def selectall(self, key=None):
		self.text.focus_set()
		self.text.tag_add(SEL, 1.0, END)

	def add_text(self, text):
		self.text['state'] = NORMAL
		self.text.insert(END, text)
		self.text['state'] = DISABLED
