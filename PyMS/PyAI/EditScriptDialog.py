
from .FlagEditor import FlagEditor
from .StringEditor import StringEditor

from ..FileFormats import TBL

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError

class EditScriptDialog(PyMSDialog):
	def __init__(self, parent, id='MYAI', flags=0, string=0, aiinfo='', title='Edit AI ID, String and Extra Info.', initial=''):
		self.initialid = initial
		self.validid = id
		self.id = StringVar()
		self.id.set(id)
		self.id.trace('w', self.editid)
		self.flags = flags
		self.validstring = string
		self.string = StringVar()
		self.string.set(string)
		self.string.trace('w', self.editstring)
		self.actualstring = StringVar()
		self.actualstring.set(TBL.decompile_string(parent.ai.tbl.strings[string]))
		self.aiinfo = aiinfo

		# TODO: How are these used?
		self.ai = parent.ai
		self.tbl = parent.tbl
		self.settings = parent.settings
		self.edittbl = parent.edittbl
		self.stattxt = parent.stattxt
		self.strings = parent.strings
		self.resort = parent.resort

		PyMSDialog.__init__(self, parent, title)

	def widgetize(self):
		frame = Frame(self)

		##Entries
		entries = Frame(frame)
		id = Frame(entries)
		Label(id, text='AI ID:', width=10, anchor=E).pack(side=LEFT)
		identry = Entry(id, justify=LEFT, textvariable=self.id, width=10, validate='key', vcmd=self.editid).pack(side=LEFT)
		Button(id, text='Flags', width=10, command=self.editflags).pack(side=RIGHT, padx=1, pady=2) 
		id.pack(fill=X)
		string = Frame(entries)
		Label(string, text='String:', width=10, anchor=E).pack(side=LEFT)
		stringid = Entry(string, justify=LEFT, textvariable=self.string, width=10, vcmd=self.editstring)
		stringid.pack(side=LEFT)
		Label(string, textvariable=self.actualstring, anchor=W, width=1).pack(side=LEFT, fill=X, expand=1)
		Button(string, text='Browse...', width=10, command=self.browse).pack(side=RIGHT, padx=1, pady=2) 
		string.pack(fill=X)

		##Extra info
		aiinfo = Frame(entries)
		Label(aiinfo, text='Extra Info:', width=10, anchor=NE).pack(side=LEFT, fill=Y)
		vscroll = Scrollbar(aiinfo)
		self.info = Text(aiinfo, yscrollcommand=vscroll.set, width=1, height=1, wrap=WORD)
		self.info.insert(1.0, self.aiinfo)
		self.info.pack(side=LEFT, fill=BOTH, expand=1)
		vscroll.config(command=self.info.yview)
		vscroll.pack(side=RIGHT, fill=Y)
		aiinfo.pack(fill=BOTH, expand=1)

		entries.pack(side=LEFT, fill=BOTH, expand=1)
		frame.pack(fill=BOTH, expand=1)

		##Buttons
		buttonframe = Frame(self)
		self.okbtn = Button(buttonframe, text='Ok', width=10, command=self.ok)
		self.okbtn.pack(side=LEFT, padx=3, pady=3)
		Button(buttonframe, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		buttonframe.pack()

		return identry

	def setup_complete(self):
		self.minsize(300,200)
		self.parent.settings.windows.load_window_size('script_edit', self)

	def editflags(self):
		f = FlagEditor(self, self.flags)
		if f.flags != None:
			self.flags = f.flags

	def editid(self, *_):
		new = self.id.get()
		if len(new) > 4 or [x for x in ',():' if x in new]:
			self.id.set(self.validid)
		else:
			self.validid = new
		if hasattr(self, 'okbtn'):
			if len(new) < 4:
				self.okbtn['state'] = DISABLED
			elif len(new) == 4:
				self.okbtn['state'] = NORMAL

	def editstring(self, *_):
		s = self.string.get()
		if s:
			try:
				s = int(self.string.get())
				if s < 0:
					raise PyMSError('Internal', 'Invalid string ID')
			except:
				s = self.validstring
			else:
				strs = len(self.ai.tbl.strings)-1
				if s > strs:
					s = strs
			self.string.set(s)
		else:
			s = 0
		self.validstring = s
		self.actualstring.set(TBL.decompile_string(self.ai.tbl.strings[s]))

	def browse(self):
		s = StringEditor(self, 'Select a String', True, self.string.get())
		if s.result != None:
			self.string.set(s.result)

	def ok(self):
		id = self.id.get()
		if self.initialid != id and id in self.parent.ai.ais:
			replace = MessageBox.askquestion(parent=self, title='Replace Script?', message="The script with ID '%s' already exists, replace it?" % id, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if replace == MessageBox.YES:
				if not self.ai.ais[id][0]:
					del self.ai.bwscript.ais[id]
				if id in self.ai.aiinfo:
					del self.ai.aiinfo[id]
			else:
				if replace == MessageBox.NO:
					self.cancel()
				return
		if not self.string.get():
			self.string.set(0)
		self.aiinfo = self.info.get(1.0, END)[:-1]
		PyMSDialog.ok(self)

	def cancel(self):
		self.id.set('')
		PyMSDialog.ok(self)

	def dismiss(self):
		self.parent.settings.windows.save_window_size('script_edit', self)
		PyMSDialog.dismiss(self)
