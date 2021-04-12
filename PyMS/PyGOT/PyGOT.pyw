from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs import TRG, GOT
from Libs.analytics import *

from Tkinter import *
from tkMessageBox import *
import tkFileDialog,tkColorChooser

from thread import start_new_thread
import optparse, os, webbrowser, sys

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
	if label in GOT.GOT.labels:
		return GOT.GOT.info[GOT.GOT.labels.index(label)]
	return None

class PyGOT(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyGOT')

		#Window
		Tk.__init__(self)
		self.title('PyGOT %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyGOT.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyGOT.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyGOT', VERSIONS['PyGOT'])
		ga.track(GAScreen('PyGOT'))
		setup_trace(self, 'PyGOT')
		self.resizable(False, False)

		self.got = None
		self.file = None
		self.edited = False

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			2,
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('import', self.iimport, 'Import Game Template (Ctrl+I)', NORMAL, 'Ctrl+I'),
			2,
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('export', self.export, 'Export Game Template (Ctrl+E)', DISABLED, 'Ctrl+E'),
			2,
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			10,
			('codeedit', lambda e=None,t=True: self.trg(e,t), 'Convert *.trg to GOT compatable (Ctrl+T)', NORMAL, 'Ctrl+T'),
			('insert', lambda e=None,t=False: self.trg(e,t), 'Revert GOT compatable *.trg (Ctrl+Alt+T)', NORMAL, 'Ctrl+Alt+T'),
			10,
			('register', self.register, 'Set as default *.got editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyGOT', NORMAL, ''),
			10,
			('exit', self.exit, 'Exit (Alt+F4)', NORMAL, 'Alt+F4'),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2])
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
				a = btn[4]
				if a:
					if not a.startswith('F'):
						self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					else:
						self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

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
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=35, anchor=W).pack(side=LEFT, padx=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a Game Template.')
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

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self, 'PyGOT'))

	def unsaved(self):
		if self.got and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.got'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.got', filetypes=[('StarCraft Game Templates','*.got'),('All Files','*')]):
		path = self.settings.get('lastpath', BASE_DIR)
		self._pyms__window_blocking = True
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=self, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		self._pyms__window_blocking = False
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		file = [NORMAL,DISABLED][not self.got]
		for btn in ['save','saveas','export','close']:
			self.buttons[btn]['state'] = file
		for inp in ['name','id','sublabel','subvalue','subid','victory','resource','stats','fog','units','start','players','allies','teams','cheats','tourny']:
			self.input[inp]['state'] = file
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
			self.got = GOT.GOT()
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
				file = self.select_file('Open GOT')
				if not file:
					return
			got = GOT.GOT()
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
			file = self.select_file('Import TXT', True, '*.txt', [('Text Files','*.txt'),('All Files','*')])
			if not file:
				return
			got = GOT.GOT()
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
		file = self.select_file('Save GOT As', False)
		if not file:
			return True
		self.file = file
		self.save()

	def export(self, key=None):
		if key and self.buttons['export']['state'] != NORMAL:
			return
		file = self.select_file('Export TXT', False, '*.txt', [('Text Files','*.txt'),('All Files','*')])
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
		file = self.select_file('Open TRG', True, '*.trg', [('StarCraft Triggers','*.trg'),('All Files','*')])
		if not file:
			return
		trg = TRG.TRG()
		try:
			trg.load_file(trig)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		file = self.select_file('Save TRG', False, '*.trg', [('StarCraft Triggers','*.trg'),('All Files','*')])
		if not file:
			return True
		try:
			trg.compile(file, t)
		except PyMSError, e:
			ErrorDialog(self, e)

	def register(self, e=None):
		try:
			register_registry('PyGOT','','got',os.path.join(BASE_DIR, 'PyGOT.pyw'),os.path.join(BASE_DIR,'Images','PyGOT.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyGOT.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyGOT', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
			savesettings('PyGOT', self.settings)
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pygot.py','pygot.pyw','pygot.exe']):
		gui = PyGOT()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyGOT [options] <inp> [out]', version='PyGOT %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a GOT file [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a GOT file")
		p.add_option('-t', '--trig', help="Used to compile a TRG file to a GOT compatable TRG file")
		p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for settings at the top of the file [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyGOT(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			got = GOT.GOT()
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'got'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			try:
				if opt.convert:
					print "Reading GOT '%s'..." % args[0]
					got.load_file(args[0])
					print " - '%s' read successfully\nDecompiling GOT file '%s'..." % (args[0],args[0])
					got.decompile(args[1], opt.reference)
					print " - '%s' written succesfully" % args[1]
				else:
					print "Interpreting file '%s'..." % args[0]
					got.interpret(args[0])
					print " - '%s' read successfully\nCompiling file '%s' to GOT format..." % (args[0],args[0])
					lo.compile(args[1])
					print " - '%s' written succesfully" % args[1]
					if opt.trig:
						print "Reading TRG '%s'..." % args[0]
						trg = TRG.TRG()
						trg.load_file(opt.trig)
						print " - '%s' read successfully" % args[0]
						path = os.path.dirname(opt.trig)
						if not path:
							path = os.path.abspath('')
						file = '%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[1]).split(os.extsep)[:-1])), os.extsep, 'trg')
						print "Compiling file '%s' to GOT compatable TRG..." % file
						trg.compile(file, True)
						print " - '%s' written succesfully" % file
			except PyMSError, e:
				print repr(e)

if __name__ == '__main__':
	main()