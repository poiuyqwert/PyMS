
from ..FileFormats import AIBIN
from ..FileFormats import TBL

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.ScrolledListbox import ScrolledListbox

class FindDialog(PyMSDialog):
	def __init__(self, parent, findstr=False):
		self.findstr = findstr
		self.results = False
		self.id = StringVar()
		self.bw = IntVar()
		self.flags = StringVar()
		self.stringid = StringVar()
		self.string = StringVar()
		self.casesens = IntVar()
		self.regex = IntVar()

		self.reset = None

		self.ai = parent.ai
		self.tbl = parent.tbl
		self.settings = parent.settings
		self.edittbl = parent.edittbl
		self.stattxt = parent.stattxt
		self.strings = parent.strings
		self.resort = parent.resort
	
		PyMSDialog.__init__(self, parent, ['Find a Script','Find a String'][findstr])

	def widgetize(self):
		self.bind(Ctrl.a, self.selectall)

		if self.findstr:
			data = [
				('String ID', self.stringid, 'stringidentry', True),
				('String', self.string, 'stringentry'),
			]
		else:
			data = [
				('AI ID', self.id, 'identry'),
				[
					('aiscript.bin', 1),
					('bwscript.bin', 2),
					('Either', 0),
				],
				('Flags', self.flags, 'flagsentry'),
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
		if self.findstr:
			self.minsize(300,150)
		else:
			self.minsize(300,325)
		self.parent.settings.windows.find.load_window_size(['script','string'][self.findstr], self)

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
		if s.result != None:
			self.stringid.set(s.result)

	def find(self, _=None):
		self.updatecolor()
		self.listbox.delete(0,END)
		self.select['state'] = DISABLED
		if self.findstr:
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
		else:
			m = []
			for t,e in [(self.id, self.identry), (self.flags, self.flagsentry), (self.stringid, self.stringidentry), (self.string, self.stringentry)]:
				if self.regex.get():
					regex = t.get()
					if not regex.startswith('\\A'):
						regex = '.*' + regex
					if not regex.endswith('\\Z'):
						regex = regex + '.*'
				else:
					regex = t.get()
					regex = '.*%s.*' % re.escape(regex)
				try:
					m.append(re.compile(regex, [re.I,0][self.casesens.get()]))
				except:
					e.c = e['bg']
					e['bg'] = '#FFB4B4'
					self.reset = e
					self.resettimer = self.after(1000, self.updatecolor)
					return
			for id,ai in self.ai.ais.iteritems():
				flags = AIBIN.convflags(ai[2])
				string = TBL.decompile_string(self.tbl.strings[ai[1]])
				if m[0].match(id) and (not self.bw.get() or min(ai[0],1) != self.bw.get()-1) and m[1].match(flags) and m[2].match(str(ai[1])) and m[3].match(string):
					self.listbox.insert(END,'%s     %s     %s     %s' % (id, ['BW','  '][min(ai[0],1)], flags, string))

	def select_item(self):
		if self.findstr:
			index = re.split(r'\s+', self.listbox.get(self.listbox.curselection()[0]).strip())[0]
			self.parent.listbox.select_clear(0,END)
			self.parent.listbox.select_set(index)
			self.parent.listbox.see(index)
		else:
			indexs = self.listbox.curselection()
			ids = []
			for index in indexs:
				ids.append(self.listbox.get(index)[:4])
			self.parent.listbox.select_clear(0,END)
			see = True
			for index in range(self.parent.listbox.size()):
				if self.parent.listbox.get(index)[:4] in ids:
					self.parent.listbox.select_set(index)
					if see:
						self.parent.listbox.see(index)
						see = False
		self.ok()

	def dismiss(self):
		self.parent.settings.windows.find.save_window_size(['script','string'][self.findstr], self)
		PyMSDialog.dismiss(self)