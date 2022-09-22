
from .EditStringDialog import EditStringDialog

from ..FileFormats import TBL

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Toolbar import Toolbar
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.StatusBar import StatusBar
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities import Assets
from ..Utilities.FileType import FileType

class StringEditor(PyMSDialog):
	def __init__(self, parent, title='String Editor', cancel=False, index=0):
		self.result = None
		self.cancelbtn = cancel
		self.index = index

		self.ai = parent.ai
		self.tbl = parent.tbl
		self.settings = parent.settings
		self.edittbl = parent.edittbl
		self.stattxt = parent.stattxt
		self.strings = parent.strings
		self.resort = parent.resort
		PyMSDialog.__init__(self, parent, '%s (%s)' % (title, parent.stattxt()))

	def widgetize(self):
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('opendefault'), self.opendefault, 'Open Default TBL', Ctrl.d)
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s)
		self.toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', Ctrl.Alt.s)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add String', Key.Insert)
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove String', Key.Delete)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('find'), self.find, 'Find String', Ctrl.f)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('edit'), self.edit, 'Edit String', Ctrl.e)
		self.toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

		self.listbox = ScrolledListbox(self, font=Font.fixed())
		self.listbox.pack(fill=BOTH, expand=1)
		self.listbox.bind(ButtonRelease.Click_Right, self.popup)
		self.listbox.bind(Double.Click_Left, self.edit)

		self.listmenu = Menu(self, tearoff=0)
		self.listmenu.add_command(label='Add String', command=self.add, underline=4)
		self.listmenu.add_command(label='Remove String', command=self.remove, underline=0, tags='string_selected')
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Edit String', command=self.edit, underline=8, tags='string_selected')

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		if self.cancelbtn:
			Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		self.status = StringVar()
		statusbar = StatusBar(self)
		statusbar.add_label(self.status)
		statusbar.pack(side=BOTTOM, fill=X)

		self.update()
		self.listbox.select_clear(0,END)
		self.listbox.select_set(self.index)
		self.listbox.see(self.index)

		return ok

	def setup_complete(self):
		self.minsize(300,300)
		self.parent.settings.windows.load_window_size('string_editor', self)

	def action_states(self):
		# TODO: How to determine action states?
		pass

	def popup(self, e):
		string_seleced = not not not self.listbox.curselection()
		self.listmenu.tag_enabled('string_selected', string_seleced)
		self.listmenu.post(e.x_root, e.y_root)

	def find(self, e=None):
		if not self.listbox.size():
			return
		from . import FindDialog
		FindDialog.FindDialog(self, True)

	def ok(self):
		self.result = int(self.listbox.curselection()[0])
		PyMSDialog.ok(self)

	def cancel(self):
		self.result = None
		PyMSDialog.ok(self)

	def dismiss(self):
		self.parent.settings.windows.save_window_size('string_editor', self)
		PyMSDialog.dismiss(self)

	def update(self):
		sel = 0
		if self.listbox.size():
			sel = self.listbox.curselection()[0]
			self.listbox.delete(0, END)
		size = len(self.parent.tbl.strings)
		pad = len(str(size))
		for n,s in enumerate(self.parent.tbl.strings):
			self.listbox.insert(END, '%s%s     %s' % (' ' * (pad - len(str(n))), n, TBL.decompile_string(s)))
		self.listbox.select_set(sel)
		self.listbox.see(sel)
		self.status.set('Strings: %s' % size)

	def open(self, file=None):
		if self.parent.edittbl():
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % self.parent.stattxt(), default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return
				if self.tbl:
					self.save()
				else:
					self.saveas()
		if file == None:
			file = self.settings.lastpath.tbl.select_open_file(self, title='Open stat_txt.tbl', filetypes=[FileType.tbl()])
		if file:
			tbl = TBL.TBL()
			try:
				tbl.load_file(file)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			max = len(tbl.strings)
			ids = {}
			for s,i in self.parent.strings.iteritems():
				if s >= max:
					ids[s] = i
			if ids:
				pass
			if self.parent.ai:
				self.parent.ai.tbl = tbl
			self.parent.tbl = tbl
			self.parent.stattxt(file)
			self.title('String Editor (%s)' % file)
			self.update()
			self.parent.edittbl(False)

	def opendefault(self):
		self.open(Assets.mpq_file_path('rez', 'stat_txt.tbl'))

	def save(self, key=None, file=None):
		if file == None:
			file = self.parent.stattxt()
		try:
			self.tbl.compile(file)
			self.parent.stattxt(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.tbledited = False

	def saveas(self, key=None):
		file = self.settings.lastpath.tbl.select_save_file(self, title='Save stat_txt.tbl', filetypes=[FileType.tbl()])
		if not file:
			return
		self.save(None, file)

	def add(self, key=None):
		e = EditStringDialog(self, '', 'Add String')
		if e.string:
			self.parent.tbl.strings.append(e.string)
			self.update()
			self.listbox.select_clear(0, END)
			self.listbox.select_set(END)
			self.listbox.see(END)
			self.parent.edittbl(True)
			if self.parent.ai:
				self.parent.resort()

	def remove(self, key=None):
		string = int(self.listbox.curselection()[0])
		if self.parent.ai:
			ids = {}
			for s,i in self.parent.strings.iteritems():
				if s > string:
					ids[s] = i
			if ids:
				plural = 0
				i = ''
				e = 0
				for s,x in ids.iteritems():
					if e < 6:
						i += '    '
					comma = False
					for n in x:
						if plural < 2:
							plural += 1
						if e < 6 and comma:
							i += ", "
						else:
							comma = True
						if e < 6:
							i += n
					if e < 6:
						i += ': %s\n' % s
					e += 1
				if e > 5:
					i += 'And %s other scripts. ' % (e-5)
				if plural == 2:
					plural = 1
				if not MessageBox.askquestion(parent=self, title='Remove String?', message="Deleting string '%s' will effect the AI Script%s:\n%sContinue removing string anyway?" % (string, 's' * plural, i), default=MessageBox.YES):
					return
				end = self.listbox.size()-1
				if end in self.parent.strings:
					new = self.listbox.size()-2
					for id in self.parent.strings[end]:
						self.parent.ai.ais[id][1] = new
					if not new in self.parent.strings:
						self.parent.strings[new] = []
					self.parent.strings[new].extend(self.parent.strings[end])
					del self.parent.strings[string]
				if self.parent.ai:
					self.parent.resort()
		del self.parent.tbl.strings[string]
		if string:
			self.listbox.select_set(string-1)
		else:
			self.listbox.select_set(0)
		self.parent.edittbl(True)
		self.update()

	def edit(self, key=None):
		id = int(self.listbox.curselection()[0])
		string = TBL.decompile_string(self.parent.tbl.strings[id])
		e = EditStringDialog(self, string)
		if string != e.string:
			self.parent.edittbl(True)
			self.parent.tbl.strings[id] = e.string
			self.update()
			if self.parent.ai:
				self.parent.resort()
