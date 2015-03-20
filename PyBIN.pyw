from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs.SpecialLists import TreeList
from Libs import DialogBIN

from Tkinter import *

from thread import start_new_thread
import optparse, os, webbrowser, sys

VERSION = (0,1)
LONG_VERSION = 'v%s.%s' % VERSION

class WidgetNode:
	def __init__(self, widget, parent=None):
		self.widget = widget
		self.parent = parent
		self.index = None
		self.children = []

class PyBIN(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyBIN',
			{
				'tfontgam':'MPQ:game\\tfontgam.pcx',
				'font10':'MPQ:font\\font10.fnt',
				'font14':'MPQ:font\\font14.fnt',
				'font16':'MPQ:font\\font16.fnt',
				'font16x':'MPQ:font\\font16x.fnt',
			}
		)

		#Window
		Tk.__init__(self)
		self.title('PyBIN %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyGOT.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyGOT.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		setup_trace(self, 'PyBIN')
		self.minsize(850, 539)
		self.maxsize(1080, 539)
		# self.resizable(True, False)
		if 'window' in self.settings:
			loadsize(self, self.settings, 'window', True)

		self.bin = None
		self.file = None
		self.edited = False

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			2,
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('import', self.iimport, 'Import from TXT (Ctrl+I)', NORMAL, 'Ctrl+I'),
			2,
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('export', self.export, 'Export to TXT (Ctrl+E)', DISABLED, 'Ctrl+E'),
			2,
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			10,
			('asc3topyai', self.mpqsettings, 'Manage Settings (Ctrl+M)', NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default *.bin editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyBIN', NORMAL, ''),
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

		frame = Frame(self)
		leftframe = Frame(frame)
		Label(leftframe, text='Widgets:', anchor=W).pack(side=TOP, fill=X)
		self.widgetTree = TreeList(leftframe)
		self.widgetTree.pack(side=TOP, padx=1, pady=1, fill=BOTH, expand=1)
		leftframe.grid(row=0, column=0, padx=2, pady=2, sticky=NSEW)
		frame.grid_columnconfigure(0, weight=1, minsize=128)

		rightframe = Frame(frame, bd=1, relief=SUNKEN)
		self.widgetCanvas = Canvas(rightframe, background='#000000', highlightthickness=0, width=640, height=480)
		self.widgetCanvas.pack(fill=BOTH)
		rightframe.grid(row=0, column=1, padx=2, pady=2, sticky=NSEW)
		frame.grid_columnconfigure(1, weight=0, minsize=640)
		frame.pack(fill=X)

		#Statusbar
		self.status = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=35, anchor=W).pack(side=LEFT, padx=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a Dialog BIN.')
		statusbar.pack(side=BOTTOM, fill=X)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if not 'mpqs' in self.settings:
			self.mpqhandler.add_defaults()
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self,))

		if e:
			self.mpqsettings(err=e)

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			tfontgam = PCX.PCX()
			font10 = FNT.FNT()
			font14 = FNT.FNT()
			font16 = FNT.FNT()
			font16x = FNT.FNT()
			tfontgam.load_file(self.mpqhandler.get_file(self.settings['tfontgam']))
			try:
				font10.load_file(self.mpqhandler.get_file(self.settings['font10'], False))
			except:
				font10.load_file(self.mpqhandler.get_file(self.settings['font10'], True))
			try:
				font14.load_file(self.mpqhandler.get_file(self.settings['font14'], False))
			except:
				font14.load_file(self.mpqhandler.get_file(self.settings['font14'], True))
			try:
				font16.load_file(self.mpqhandler.get_file(self.settings['font16'], False))
			except:
				font16.load_file(self.mpqhandler.get_file(self.settings['font16'], True))
			try:
				font16x.load_file(self.mpqhandler.get_file(self.settings['font16x'], False))
			except:
				font16x.load_file(self.mpqhandler.get_file(self.settings['font16x'], True))
		except PyMSError, e:
			err = e
		else:
			self.tfontgam = tfontgam
			self.font10 = font10
			self.font14 = font14
			self.font16 = font16
			self.font16x = font16x
		self.mpqhandler.close_mpqs()
		return err

	def mpqsettings(self, key=None, err=None):
		data = [
			('Preview Settings',[
				('tfontgam.pcx','The special palette which holds text colors.','tfontgam','PCX'),
				('font10.fnt','Size 10 font','font10','FNT'),
				('font14.fnt','Size 14 font','font14','FNT'),
				('font16.fnt','Size 16 font','font16','FNT'),
				('font16x.fnt','Size 16x font','font16x','FNT'),
			])
		]
		SettingsDialog(self, data, (340,430), err)

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, listbox, offset):
		index = 0
		if offset == END:
			index = listbox.size()-2
		elif offset not in [0,END] and listbox.curselection():
			print listbox.curselection()
			index = max(min(listbox.size()-1, int(listbox.curselection()[0]) + offset),0)
		listbox.select_clear(0,END)
		listbox.select_set(index)
		listbox.see(index)
		return "break"

	def unsaved(self):
		if self.bin and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.bin'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.bin', filetypes=[('StarCraft Dialogs','*.bin'),('All Files','*')]):
		path = self.settings.get('lastpath', BASE_DIR)
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=self, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		file = [NORMAL,DISABLED][not self.bin]
		for btn in ['save','saveas','export','close']:
			self.buttons[btn]['state'] = file

	def edit(self, n=None):
		self.edited = True
		self.editstatus['state'] = NORMAL
		self.action_states()

	def reload_list(self):
		self.widgetTree.delete(ALL)
		def list_widget(index, widget):
			if type(widget) == DialogBIN.DialogBINGroup:
				name = 'Group'
			else:
				name = DialogBIN.DialogBINWidget.TYPE_NAMES[widget.type]
			group = None
			if widget.children or widget == self.bin.dialog:
				group = True
			result = self.widgetTree.insert(index, name, group)
			for child in widget.children:
				list_widget(result + '.-1', child)
		list_widget('-1', self.bin.dialog)

	def reload_canvas(self):
		self.widgetCanvas.delete(ALL)
		def show_widget(widget):
			x1,y1,x2,y2 = widget.bounding_box()
			self.widgetCanvas.create_rectangle(x1,y1, x2,y2, width=1, outline='#0080ff')
			for child in widget.children:
				show_widget(child)
		show_widget(self.bin.dialog)

	def new(self, key=None):
		if not self.unsaved():
			self.bin = DialogBIN.DialogBIN()
			self.reload_list()
			self.file = None
			self.status.set('Editing new Dialog.')
			self.title('PyBIN %s (Unnamed.bin)' % LONG_VERSION)
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.select_file('Open Dialog BIN')
				if not file:
					return
			dbin = DialogBIN.DialogBIN()
			try:
				dbin.load_file(file)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.bin = dbin
			self.reload_list()
			self.reload_canvas()
			self.title('PyBIN %s (%s)' % (LONG_VERSION,file))
			self.file = file
			self.status.set('Load Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()

	def iimport(self, key=None):
		if not self.unsaved():
			file = self.select_file('Import TXT', True, '*.txt', [('Text Files','*.txt'),('All Files','*')])
			if not file:
				return
			dbin = DialogBIN.DialogBIN()
			try:
				dbin.interpret_file(file)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.bin = abin
			self.title('PyBIN %s (%s)' % (LONG_VERSION,file))
			self.file = file
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
			self.bin.compile_file(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError, e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.select_file('Save Dialog BIN As', False)
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
			self.bin.decompile_file(file)
			self.status.set('Export Successful!')
		except PyMSError, e:
			ErrorDialog(self, e)

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.bin = None
			self.title('PyBIN %s' % LONG_VERSION)
			self.file = None
			self.status.set('Load or create a Dialog BIN.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.reset()
			self.action_states()

	def register(self, e=None):
		try:
			register_registry('PyBIN','','bin',os.path.join(BASE_DIR, 'PyBIN.pyw'),os.path.join(BASE_DIR,'Images','PyGOT.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyBIN.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyBIN', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
			savesize(self, self.settings)
			try:
				f = file(os.path.join(BASE_DIR,'Settings','PyBIN.txt'),'w')
				f.write(pprint(self.settings))
				f.close()
			except:
				pass
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pybin.py','pybin.pyw','pybin.exe']):
		gui = PyBIN()
		gui.mainloop()
	else:
		p = optparse.OptionParser(usage='usage: PyBIN [options] <inp> [out]', version='PyBIN %s' % LONG_VERSION)
		# p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a GOT file [default]", default=True)
		# p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a GOT file")
		# p.add_option('-t', '--trig', help="Used to compile a TRG file to a GOT compatable TRG file")
		# p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for settings at the top of the file [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyBIN(opt.gui)
			gui.mainloop()
		# else:
		# 	if not len(args) in [1,2]:
		# 		p.error('Invalid amount of arguments')
		# 	path = os.path.dirname(args[0])
		# 	if not path:
		# 		path = os.path.abspath('')
		# 	got = GOT.GOT()
		# 	if len(args) == 1:
		# 		if opt.convert:
		# 			ext = 'txt'
		# 		else:
		# 			ext = 'got'
		# 		args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
		# 	try:
		# 		if opt.convert:
		# 			print "Reading GOT '%s'..." % args[0]
		# 			got.load_file(args[0])
		# 			print " - '%s' read successfully\nDecompiling GOT file '%s'..." % (args[0],args[0])
		# 			got.decompile(args[1], opt.reference)
		# 			print " - '%s' written succesfully" % args[1]
		# 		else:
		# 			print "Interpreting file '%s'..." % args[0]
		# 			got.interpret(args[0])
		# 			print " - '%s' read successfully\nCompiling file '%s' to GOT format..." % (args[0],args[0])
		# 			lo.compile(args[1])
		# 			print " - '%s' written succesfully" % args[1]
		# 			if opt.trig:
		# 				print "Reading TRG '%s'..." % args[0]
		# 				trg = TRG.TRG()
		# 				trg.load_file(opt.trig)
		# 				print " - '%s' read successfully" % args[0]
		# 				path = os.path.dirname(opt.trig)
		# 				if not path:
		# 					path = os.path.abspath('')
		# 				file = '%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[1]).split(os.extsep)[:-1])), os.extsep, 'trg')
		# 				print "Compiling file '%s' to GOT compatable TRG..." % file
		# 				trg.compile(file, True)
		# 				print " - '%s' written succesfully" % file
		# 	except PyMSError, e:
		# 		print repr(e)

if __name__ == '__main__':
	main()