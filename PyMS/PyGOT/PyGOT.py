
from ..FileFormats.GOT import GOT
from ..FileFormats.TRG import TRG

from ..Utilities.utils import BASE_DIR, VERSIONS, WIN_REG_AVAILABLE, fit, register_registry, couriernew
from ..Utilities.UIKit import *
from ..Utilities.Tooltip import Tooltip
from ..Utilities.Settings import Settings
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.Toolbar import Toolbar
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.SStringVar import SStringVar
from ..Utilities.DropDown import DropDown
from ..Utilities.StatusBar import StatusBar
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog

import os, webbrowser

LONG_VERSION = 'v%s' % VERSIONS['PyGOT']

HINTS = {
	'name':'The name of the Game Template listed in StarCraft',
	'id':'An ID used to define the order of the Game Template when its listed in StarCraft',
	'sublabel':'The label for the variation (ie, the one to set greed amount)',
	'subvalue':'The value defining the variation amount (for example mineral count for greed or amount of teams for Team Vs)',
	'subid':'An ID used to define the order of the variation when its listed in StarCraft',
}
def tip(o, h):
	o.tooltip = Tooltip(o, fit('', HINTS[h], end=True)[:-1], mouse=True)

def get_info(label):
	if label == 'TeamMode':
		return ['Off','2 Teams','3 Teams','4 Teams']
	if label in GOT.labels:
		return GOT.info[GOT.labels.index(label)]
	return None

class PyGOT(MainWindow):
	def __init__(self, guifile=None):
		self.settings = Settings('PyGOT', '1')

		#Window
		MainWindow.__init__(self)
		self.title('PyGOT %s' % LONG_VERSION)
		self.set_icon('PyGOT')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyGOT', VERSIONS['PyGOT'])
		ga.track(GAScreen('PyGOT'))
		setup_trace(self, 'PyGOT')
		self.resizable(False, False)

		self.got = None
		self.file = None
		self.edited = False

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button('new', self.new, 'New', Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button('open', self.open, 'Open', Ctrl.o)
		self.toolbar.add_button('import', self.iimport, 'Import Game Template', Ctrl.i)
		self.toolbar.add_gap()
		self.toolbar.add_button('save', self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		self.toolbar.add_button('saveas', self.saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button('export', self.export, 'Export Game Template', Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button('close', self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button('codeedit', lambda: self.trg(True), 'Convert *.trg to GOT compatable', Ctrl.t)
		self.toolbar.add_button('insert', lambda: self.trg(False), 'Revert GOT compatable *.trg', Ctrl.Alt.t)
		self.toolbar.add_section()
		self.toolbar.add_button('register', self.register, 'Set as default *.got editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button('help', self.help, 'Help', Key.F1)
		self.toolbar.add_button('about', self.about, 'About PyGOT')
		self.toolbar.add_section()
		self.toolbar.add_button('exit', self.exit, 'Exit', Alt.F4)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.input = {}

		self.name = SStringVar(length=32, callback=self.edit)
		self.id = IntegerVar(0,[0,32], callback=self.edit)
		self.sublabel = SStringVar(length=32, callback=self.edit)
		self.subvalue = IntegerVar(0, [0,4294967295], callback=self.edit)
		self.subid = IntegerVar(0,[0,8], callback=self.edit)

		top = Frame(self)
		left = Frame(top)
		l = LabelFrame(left, text='Template Info:', padx=2, pady=2)
		Label(l, text='Name:').grid(sticky=E)
		self.input['name'] = Entry(l, textvariable=self.name, font=couriernew, width=20, state=DISABLED)
		tip(self.input['name'], 'name')
		self.input['name'].grid(row=0, column=1, pady=1)
		Label(l, text='ID:').grid(sticky=E)
		self.input['id'] = Entry(l, textvariable=self.id, font=couriernew, width=2, state=DISABLED)
		tip(self.input['id'], 'id')
		self.input['id'].grid(row=1, column=1, sticky=W, pady=1)
		l.pack(padx=1)
		left.pack(side=LEFT, fill=Y)
		l = LabelFrame(top, text='Variation Info:', padx=2, pady=2)
		Label(l, text='Label:').grid(sticky=E)
		self.input['sublabel'] = Entry(l, textvariable=self.sublabel, font=couriernew, width=20, state=DISABLED)
		tip(self.input['sublabel'], 'sublabel')
		self.input['sublabel'].grid(row=0, column=1, pady=1)
		Label(l, text='Value:').grid(sticky=E)
		self.input['subvalue'] = Entry(l, textvariable=self.subvalue, font=couriernew, width=10, state=DISABLED)
		tip(self.input['subvalue'], 'subvalue')
		self.input['subvalue'].grid(row=1, column=1, sticky=W, pady=1)
		Label(l, text='ID:').grid(sticky=E)
		self.input['subid'] = Entry(l, textvariable=self.subid, font=couriernew, width=1, state=DISABLED)
		tip(self.input['subid'], 'subid')
		self.input['subid'].grid(row=2, column=1, sticky=W, pady=1)
		l.pack()
		top.pack(padx=1, pady=2)

		self.victory = IntegerVar(0, callback=self.edit)
		self.victoryvalue = IntegerVar(0, [0,4294967295])
		self.resource = IntegerVar(0, callback=self.edit)
		self.resourcevalue = IntegerVar(0, [0,4294967295])
		self.stats = IntegerVar(0, callback=self.edit)
		self.fog = IntegerVar(0, callback=self.edit)
		self.units = IntegerVar(0, callback=self.edit)
		self.start = IntegerVar(0, callback=self.edit)
		self.players = IntegerVar(0, callback=self.edit)
		self.allies = IntegerVar(0, callback=self.edit)
		self.teams = IntegerVar(0, callback=self.edit)
		self.cheats = IntegerVar(0, callback=self.edit)
		self.tourny = IntegerVar(0, callback=self.edit)

		b = Frame(self)
		options = [
			('Victory Conditions', 'victory', self.victory, 'victoryvalue', self.victoryvalue),
			('Resource Type', 'resource', self.resource, 'resourcevalue', self.resourcevalue),
			('Unit Stats', 'stats', self.stats),
			('Fog Of War', 'fog', self.fog),
			('Starting Units', 'units', self.units),
			('Starting Positions', 'start', self.start),
			('Player Types', 'players', self.players),
			('Allies', 'allies', self.allies),
			('Team Mode', 'teams', self.teams),
			('Cheat Codes', 'cheats', self.cheats),
			('Tournament Mode', 'tourny', self.tourny),
		]
		for row,option in enumerate(options):
			c = None
			if len(option) > 3:
				c = lambda n,i=row: self.dropchange(n,i)
			Label(b, text='%s:' % option[0], anchor=E).grid(sticky=E)
			self.input[option[1]] = DropDown(b, option[2], get_info(option[0].replace(' ','')), c, width=25, state=DISABLED)
			self.input[option[1]].grid(row=row, column=1, pady=1)
			if len(option) > 3:
				self.input[option[3]] = Entry(b, textvariable=option[4], font=couriernew, width=10, state=DISABLED)
				self.input[option[3]].grid(row=row, column=2, pady=1)
		b.pack()

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a Game Template.')
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, width=35)
		self.editstatus = statusbar.add_icon(PhotoImage(file=os.path.join(BASE_DIR, 'PyMS', 'Images', 'save.gif')))
		statusbar.add_spacer()
		statusbar.pack(side=BOTTOM, fill=X)

		self.values = [
			self.name,
			self.sublabel,
			self.id,
			self.subid,
			self.subvalue,
			self.victory,
			self.resource,
			self.stats,
			self.fog,
			self.units,
			self.start,
			self.players,
			self.allies,
			self.teams,
			self.cheats,
			self.tourny,
			self.victoryvalue,
			self.resourcevalue,
		]

		self.settings.windows.load_window_size('main', self)

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyGOT')

	def unsaved(self):
		if self.got and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.got'
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	# def select_file(self, title, open=True, ext='.got', filetypes=[('StarCraft Game Templates','*.got'),('All Files','*')]):
	# 	path = self.settings.get('lastpath', BASE_DIR)
	# 	self._pyms__window_blocking = True
	# 	file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=self, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
	# 	self._pyms__window_blocking = False
	# 	if file:
	# 		self.settings['lastpath'] = os.path.dirname(file)
	# 	return file

	def is_file_open(self):
		return not not self.got

	def action_states(self):
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		for inp in ['name','id','sublabel','subvalue','subid','victory','resource','stats','fog','units','start','players','allies','teams','cheats','tourny']:
			self.input[inp]['state'] = self.is_file_open()
		if self.got:
			self.input['victoryvalue']['state'] = [DISABLED,NORMAL][self.victory.get() > 0 and not self.victory.get() % 3]
			self.input['resourcevalue']['state'] = [DISABLED,NORMAL][self.resource.get() % 4 == 1]

	def dropchange(self, n, i):
		self.input[['victoryvalue','resourcevalue'][i]]['state'] = [DISABLED,NORMAL][[n > 0 and not n % 3,n % 4 == 1][i]]

	def edit(self, n=None):
		self.edited = True
		self.editstatus['state'] = NORMAL

	def reset(self):
		self.name.check = False
		self.name.set('')
		self.sublabel.check = False
		self.sublabel.set('')
		vars = [
			self.id,
			self.subid,
			self.subvalue,
			self.victory,
			self.resource,
			self.stats,
			self.fog,
			self.units,
			self.start,
			self.players,
			self.allies,
			self.teams,
			self.cheats,
			self.tourny,
			self.victoryvalue,
			self.resourcevalue,
		]
		for var in vars:
			var.check = False
			var.set(0)

	def new(self, key=None):
		if not self.unsaved():
			self.got = GOT()
			self.file = None
			self.status.set('Editing new Game Template.')
			self.title('PyGOT %s (Unnamed.got)' % LONG_VERSION)
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.reset()
			self.action_states()

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.settings.lastpath.got.select_file('open', self, 'Open GOT', '.got', [('StarCraft Game Templates','*.got'),('All Files','*')])
				if not file:
					return
			got = GOT()
			try:
				got.load_file(file)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.got = got
			self.title('PyGOT %s (%s)' % (LONG_VERSION,file))
			self.file = file
			for var,val in zip(self.values,self.got.template):
				if var == self.teams and val > 1:
					val -= 1
				var.set(val)
			self.status.set('Load Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()

	def iimport(self, key=None):
		if not self.unsaved():
			file = self.settings.lastpath.txt.select_file('import', self, 'Import TXT', '.txt', [('Text Files','*.txt'),('All Files','*')])
			if not file:
				return
			got = GOT()
			try:
				got.interpret(file)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.got = got
			self.title('PyGOT %s (%s)' % (LONG_VERSION,file))
			self.file = file
			for var,val in zip(self.values,self.got.template):
				if var == self.teams and val > 1:
					val -= 1
				var.set(val)
			self.status.set('Import Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			for n,var in enumerate(self.values):
				val = var.get()
				if var == self.teams and val > 0:
					val += 1
				self.got.template[n] = val
			self.got.compile(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError, e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.settings.lastpath.got.select_file('save', self, 'Save GOT As', '.got', [('StarCraft Game Templates','*.got'),('All Files','*')], save=True)
		if not file:
			return True
		self.file = file
		self.save()

	def export(self, key=None):
		if key and self.buttons['export']['state'] != NORMAL:
			return
		file = self.settings.lastpath.txt.select_file('export', self, 'Export TXT', '.txt', [('Text Files','*.txt'),('All Files','*')], save=True)
		if not file:
			return True
		try:
			self.got.decompile(file)
			self.status.set('Export Successful!')
		except PyMSError, e:
			ErrorDialog(self, e)

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.got = None
			self.title('PyGOT %s' % LONG_VERSION)
			self.file = None
			self.status.set('Load or create a Game Template.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.reset()
			self.action_states()

	def trg(self, e=None, t=0):
		file = self.settings.lastpath.trg.select_file('open', self, 'Open TRG', '.trg', [('StarCraft Triggers','*.trg'),('All Files','*')])
		if not file:
			return
		trg = TRG()
		try:
			trg.load_file(file)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		file = self.settings.lastpath.trg.select_file('save', self, 'Save TRG', '.trgg', [('StarCraft Triggers','*.trg'),('All Files','*')])
		if not file:
			return True
		try:
			trg.compile(file, t)
		except PyMSError, e:
			ErrorDialog(self, e)

	def register(self, e=None):
		try:
			register_registry('PyGOT','','got',os.path.join(BASE_DIR, 'PyGOT.pyw'),os.path.join(BASE_DIR, 'PyMS', 'Images', 'PyGOT.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyGOT.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyGOT', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
			self.settings.windows.save_window_size('main', self)
			self.settings.save()
			self.destroy()
