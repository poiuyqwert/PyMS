
from ..FileFormats import AIBIN
from ..FileFormats import TBL

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

import re

class FindStringDialog(PyMSDialog):
	def __init__(self, parent: AnyWindow):
		self.results = False
		self.id = StringVar()
		self.bw = IntVar()
		self.flags = StringVar()
		self.stringid = StringVar()
		self.string = StringVar()
		self.casesens = IntVar()
		self.regex = IntVar()

		self.reset = None

		PyMSDialog.__init__(self, parent, 'Find a String')

	def widgetize(self):
		self.bind(Ctrl.a, self.selectall)

		data = [
			('String ID', self.stringid, 'stringidentry', True),
			('String', self.string, 'stringentry'),
		]
		focuson = None
		for d in data:
			if isinstance(d, list):
				frame = Frame(self)
				for rb in d:
					Radiobutton(frame, text=rb[0], variable=self.bw, value=rb[1]).pack(side=LEFT)
				frame.pack(fill=X)
			else:
				Label(self, text=d[0], anchor=W).pack(fill=X)
				if len(d) == 4:
					frame = Frame(self)
					entry = Entry(frame, textvariable=d[1])
					setattr(self, d[2], entry)
					entry.pack(side=LEFT, fill=X, expand=1)
					Button(frame, text='Browse...', width=10, command=self.browse).pack(side=RIGHT)
					frame.pack(fill=X)
					if not focuson:
						focuson = entry
				else:
					entry = Entry(self, textvariable=d[1])
					setattr(self, d[2], entry)
					entry.pack(fill=X)
					if not focuson:
						focuson = entry

		options = Frame(self)
		Checkbutton(options, text='Case Sensitive', variable=self.casesens).pack(side=LEFT, padx=3)
		Checkbutton(options, text='Regular Expressions', variable=self.regex).pack(side=LEFT, padx=3)
		options.pack(pady=3)

		self.listbox = ScrolledListbox(self, selectmode=[EXTENDED,BROWSE][self.findstr], font=Font.fixed(), width=1, height=1)
		self.listbox.pack(fill=BOTH, padx=2, pady=2, expand=1)
		self.listbox.bind(WidgetEvent.Listbox.Select, self.update)

		buttons = Frame(self)
		Button(buttons, text='Find', width=10, command=self.find, default=NORMAL).pack(side=LEFT, padx=3, pady=3)
		self.select = Button(buttons, text='Select', width=10, command=self.select_item, state=DISABLED)
		self.select.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		buttons.pack()

		self.bind(Key.Return, self.find)

		return focuson

	def setup_complete(self):
		self.minsize(300,150)
		self.parent.settings.windows.find.load_window_size('string', self)

	def update(self, e=None):
		self.select['state'] = NORMAL

	def updatecolor(self):
		if self.reset:
			if self.resettimer:
				self.after_cancel(self.resettimer)
				self.resettimer = None
			self.reset['bg'] = self.reset.c
			self.reset = None

	def selectall(self, e=None):
		if self.listbox.size():
			self.listbox.select_set(0, END)
			self.select['state'] = NORMAL

	def browse(self):
		from . import StringEditor
		try:
			s = int(self.stringid.get())
		except:
			s = 0
		s = StringEditor.StringEditor(self, 'Select a String', True, s)
		if s.result is not None:
			self.stringid.set(s.result)

	def find(self, _=None):
		self.updatecolor()
		self.listbox.delete(0,END)
		self.select['state'] = DISABLED

		m = []
		for t,e in [(self.stringid, self.stringidentry), (self.string, self.stringentry)]:
			if self.regex.get():
				regex = t.get()
				if not regex.startswith('\\A'):
					regex = '.*' + regex
				if not regex.endswith('\\Z'):
					regex = regex + '.*'
			else:
				regex = '.*%s.*' % re.escape(t.get())
			try:
				m.append(re.compile(regex, [re.I,0][self.casesens.get()]))
			except:
				e.c = e['bg']
				e['bg'] = '#FFB4B4'
				self.reset = e
				self.resettimer = self.after(1000, self.updatecolor)
				return
		pad = len(str(len(self.tbl.strings)))
		for n,s in enumerate(self.tbl.strings):
			l = TBL.decompile_string(s)
			if m[0].match(str(n)) and m[1].match(l):
				self.listbox.insert(END, '%s%s     %s' % (' ' * (pad - len(str(n))), n, l))

	def select_item(self):
		index = re.split(r'\s+', self.listbox.get(self.listbox.curselection()[0]).strip())[0]
		self.parent.listbox.select_clear(0,END)
		self.parent.listbox.select_set(index)
		self.parent.listbox.see(index)
		self.ok()

	def dismiss(self):
		self.parent.settings.windows.find.save_window_size('string', self)
		PyMSDialog.dismiss(self)
