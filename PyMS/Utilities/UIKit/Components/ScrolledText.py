
from ..Widgets import *

class ScrolledText(Frame):
	def __init__(self, *args, **kwargs):
		if not 'relief' in kwargs:
			kwargs['relief'] = SUNKEN
			if not 'bd' in kwargs and not 'borderwidth' in kwargs:
				kwargs['bd'] = 2
		Frame.__init__(self, *args, **kwargs)

		hscroll = Scrollbar(self, orient=HORIZONTAL)
		vscroll = Scrollbar(self)
		self.textview = Text(self, bd=0, wrap=WORD, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0)
		self.textview.grid(column=0,row=0, sticky=NSEW)
		vscroll.grid(column=1,row=0, sticky=NS)
		vscroll.config(command=self.textview.yview)
		hscroll.grid(column=0,row=1, sticky=EW)
		hscroll.config(command=self.textview.xview)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		self._read_only = False
		self._insertontime = None
		self.textview._original_w = self.textview._w + '_original'
		self.tk.call('rename', self.textview._w, self.textview._original_w)
		self.tk.createcommand(self.textview._w, self.dispatch)

	def dispatch(self, cmd, *args):
		if self._read_only and (cmd == 'insert' or cmd == 'delete'):
			return ""
		try:
			return self.tk.call((self.textview._original_w, cmd) + args)
		except TclError:
			return ""

	def set_read_only(self, read_only):
		self._read_only = read_only
		if read_only:
			self._insertontime = self.textview.cget('insertontime')
			self.textview.configure(insertontime=0)
		elif self._insertontime != None:
			self.textview.configure(insertontime=self._insertontime)

	def insert(self, at_index, text, *tags):
		read_only = self._read_only
		self._read_only = False
		self.textview.insert(at_index, text, *tags)
		self._read_only = read_only

	def delete(self, start_index, end_index):
		read_only = self._read_only
		self._read_only = False
		self.textview.delete(start_index, end_index)
		self._read_only = read_only
