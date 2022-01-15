
from IScriptCodeText import IScriptCodeText
from FindReplaceDialog import FindReplaceDialog
from CodeColors import CodeColors
from CodeGeneratorDialog import CodeGeneratorDialog
from PreviewerDialog import PreviewerDialog, PREVIEWER_CMDS
from SoundDialog import SoundDialog

from ..FileFormats import IScriptBIN
from ..FileFormats import GRP

from ..Utilities.utils import BASE_DIR, couriernew
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Tooltip import Tooltip
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.WarningDialog import WarningDialog

import os

class CodeEditDialog(PyMSDialog):
	def __init__(self, parent, ids):
		self.ids = ids
		self.decompile = ''
		self.file = None
		self.autocomptext = IScriptBIN.TYPE_HELP.keys() + ['.headerstart','.headerend']
		for o in IScriptBIN.OPCODES:
			self.autocomptext.extend(o[0])
		for a in IScriptBIN.HEADER:
			self.autocomptext.extend(a)
		self.completing = False
		self.complete = [None, 0]
		t = ''
		if ids:
			t = ', '.join([str(i) for i in ids[:5]])
			if len(ids) > 5:
				t += '...'
			t += ' - '
		t += 'IScript Editor'
		PyMSDialog.__init__(self, parent, t, grabwait=False)
		self.findwindow = None
		self.previewer = None

	def widgetize(self):
		buttons = [
			('save', self.save, 'Save (Ctrl+S)', '<Control-s>'),
			('test', self.test, 'Test Code (Ctrl+T)', '<Control-t>'),
			4,
			('export', self.export, 'Export Code (Ctrl+E)', '<Control-e>'),
			('saveas', self.exportas, 'Export As... (Ctrl+Alt+A)', '<Control-Alt-a>'),
			('import', self.iimport, 'Import Code (Ctrl+I)', '<Control-i>'),
			10,
			('find', self.find, 'Find/Replace (Ctrl+F)', '<Control-f>'),
			10,
			('colors', self.colors, 'Color Settings (Ctrl+Alt+C)', '<Control-Alt-c>'),
			10,
			('debug', self.generate, 'Generate Code (Ctrl+G)', '<Control-g>'),
			('insert', self.preview, 'Insert/Preview Window (Ctrl+W)', '<Control-w>'),
			('fwp', self.sounds, 'Sound Previewer (Ctrl+Q)', '<Control-q>'),
		]
		self.bind('<Alt-Left>', lambda e,i=0: self.gotosection(e,i))
		self.bind('<Alt-Right>', lambda e,i=1: self.gotosection(e,i))
		self.bind('<Alt-Up>', lambda e,i=2: self.gotosection(e,i))
		self.bind('<Alt-Down>', lambda e,i=3: self.gotosection(e,i))
		bar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR, 'PyMS', 'Images','%s.gif' % btn[0]))
				if btn[3] == True:
					button = Checkbutton(bar, image=image, width=20, height=20, indicatoron=0, variable=btn[1])
				else:
					button = Button(bar, image=image, width=20, height=20, command=btn[1])
					self.bind(btn[3], btn[1])
				button.image = image
				button.tooltip = Tooltip(button, btn[2], couriernew)
				button.pack(side=LEFT)
				if button.winfo_reqwidth() > 26:
					button['width'] = 18
				if button.winfo_reqheight() > 26:
					button['height'] = 18
			else:
				Frame(bar, width=btn).pack(side=LEFT)
		bar.pack(fill=X, padx=2, pady=2)

		self.text = IScriptCodeText(self, self.parent.ibin, self.edited, highlights=self.parent.highlights)
		self.text.pack(fill=BOTH, expand=1, padx=1, pady=1)
		self.text.icallback = self.statusupdate
		self.text.scallback = self.statusupdate
		self.text.acallback = self.autocomplete

		self.status = StringVar()
		self.status.set("Origional ID's: " + ', '.join([str(i) for i in self.ids]))
		self.scriptstatus = StringVar()
		self.scriptstatus.set('Line: 1  Column: 0  Selected: 0')

		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		image = PhotoImage(file=os.path.join(BASE_DIR, 'PyMS', 'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.scriptstatus, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		statusbar.pack(side=BOTTOM, fill=X)

		self.after(1, self.load)

		self.parent.settings.windows.load_window_size('codeedit', self)

		return self.text

	def gotosection(self, e, i):
		c = [self.text.tag_prevrange, self.text.tag_nextrange][i % 2]
		t = [('Error','Warning'),('HeaderStart','Block')][i > 1]
		a = c(t[0], INSERT)
		b = c(t[1], INSERT)
		s = None
		if a:
			if not b or self.text.compare(a[0], ['>','<'][i % 2], b[0]):
				s = a
			else:
				s = b
		elif b:
			s = b
		if s:
			self.text.see(s[0])
			self.text.mark_set(INSERT, s[0])

	def autocomplete(self):
		i = self.text.tag_ranges('Selection')
		if i and '\n' in self.text.get(*i):
			return False
		self.completing = True
		self.text.taboverride = ' :'
		def docomplete(s, e, v, t):
			ss = '%s+%sc' % (s,len(t))
			se = '%s+%sc' % (s,len(v))
			self.text.delete(s, ss)
			self.text.insert(s, v)
			self.text.tag_remove('Selection', '1.0', END)
			self.text.tag_add('Selection', ss, se)
			if self.complete[0] == None:
				self.complete = [t, 1, s, se]
			else:
				self.complete[1] += 1
				self.complete[3] = se
		if self.complete[0] != None:
			t,f,s,e = self.complete
		else:
			s,e = self.text.index('%s -1c wordstart' % INSERT),self.text.index('%s -1c wordend' % INSERT)
			t,f = self.text.get(s,e),0
		if t and t[0].lower() in 'abcdefghijklmnopqrstuvwxyz_.':
			ac = list(self.autocomptext)
			head = '1.0'
			while True:
				item = self.text.tag_nextrange('Block', head)
				if not item:
					break
				block = self.text.get(*item)
				if not block in ac:
					ac.append(block)
				head = item[1]
			ac.sort()
			r = False
			matches = []
			for v in ac:
				if v and v.lower().startswith(t.lower()):
					matches.append(v)
			if matches:
				if f < len(matches):
					docomplete(s,e,matches[f],t)
					self.text.taboverride = ' (,):'
				elif self.complete[0] != None:
					docomplete(s,e,t,t)
					self.complete[1] = 0
				r = True
			self.after(1, self.completed)
			return r

	def completed(self):
		self.completing = False

	def statusupdate(self):
		if not self.completing:
			self.text.taboverride = False
			self.complete = [None, 0]
		i = self.text.index(INSERT).split('.') + [0]
		item = self.text.tag_ranges('Selection')
		if item:
			i[2] = len(self.text.get(*item))
		self.scriptstatus.set('Line: %s  Column: %s  Selected: %s' % tuple(i))

	def edited(self):
		if not self.completing:
			self.text.taboverride = False
			self.complete = [None, 0]
		self.editstatus['state'] = NORMAL
		if self.file:
			self.title('IScript Editor [*%s*]' % self.file)

	def cancel(self):
		if self.text.edited:
			save = MessageBox.askquestion(parent=self, title='Save Code?', message="Would you like to save the code?", default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return
				self.save()
		self.ok()

	def save(self, e=None):
		self.parent.iimport(file=self, parent=self)
		self.text.edited = False
		self.editstatus['state'] = DISABLED

	def ok(self):
		self.parent.settings.windows.save_window_size('codeedit', self)
		PyMSDialog.ok(self)

	def checkframes(self, grp):
		if os.path.exists(grp):
			p = grp
		else:
			p = self.parent.mpqhandler.get_file('MPQ:unit\\' + grp)
		try:
			grp = GRP.CacheGRP()
			grp.load_file(p)
		except PyMSError:
			return None
		return grp.frames

	def test(self, e=None):
		i = IScriptBIN.IScriptBIN(self.parent.weaponsdat, self.parent.flingydat, self.parent.imagesdat, self.parent.spritesdat, self.parent.soundsdat, self.parent.tbl, self.parent.imagestbl, self.parent.sfxdatatbl)
		try:
			warnings = i.interpret(self, checkframes=self.checkframes)
		except PyMSError as e:
			if e.line != None:
				self.text.see('%s.0' % e.line)
				self.text.tag_add('Error', '%s.0' % e.line, '%s.end' % e.line)
			if e.warnings:
				for w in e.warnings:
					if w.line != None:
						self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			ErrorDialog(self, e)
			return
		if warnings:
			c = False
			for w in warnings:
				if w.line != None:
					if not c:
						self.text.see('%s.0' % w.line)
						c = True
					self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			WarningDialog(self, warnings, True)
		else:
			MessageBox.askquestion(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.', type=MessageBox.OK)

	def export(self, e=None):
		if not self.file:
			self.exportas()
		else:
			f = open(self.file, 'w')
			f.write(self.text.get('1.0', END))
			f.close()
			self.title('IScript Editor [%s]' % self.file)

	def exportas(self, e=None):
		file = self.parent.select_file('Export Code', False, '.txt', [('Text Files','*.txt'),('All Files','*')], self)
		if not file:
			return
		self.file = file
		self.export()

	def iimport(self, e=None):
		iimport = self.parent.select_file('Import From', True, '.txt', [('Text Files','*.txt'),('All Files','*')], self)
		if iimport:
			try:
				f = open(iimport, 'r')
				self.text.delete('1.0', END)
				self.text.insert('1.0', f.read())
				self.text.edit_reset()
				f.close()
			except:
				ErrorDialog(self, PyMSError('Import','Could not import file "%s"' % iimport))

	def find(self, e=None):
		if not self.findwindow:
			self.findwindow = FindReplaceDialog(self)
			self.bind('<F3>', self.findwindow.findnext)
		elif self.findwindow.state() == 'withdrawn':
			self.findwindow.deiconify()
		self.findwindow.focus_set()

	def colors(self, e=None):
		c = CodeColors(self)
		if c.cont:
			self.text.setup(c.cont)
			self.parent.highlights = c.cont

	def generate(self, *_):
		CodeGeneratorDialog(self)

	def preview(self, e=None):
		if not self.previewer or self.previewer.state() == 'withdrawn':
			if not self.previewer:
				self.previewer = PreviewerDialog(self)
			self.previewer.updatecurrentimages()
			t = re.split('\\s+',self.text.get('%s linestart' % INSERT,'%s lineend' % INSERT).split('#',1)[0].strip())
			if t[0] in PREVIEWER_CMDS[0] and self.previewer.curradio['state'] == NORMAL:
				try:
					f = IScriptBIN.type_frame(2, None, t[1])
				except:
					f = 0
				self.previewer.type.set(0)
				self.previewer.curid.set(0)
				self.previewer.curcmd.set(PREVIEWER_CMDS[0].index(t[0]))
				self.previewer.select(0,0,f)
			elif t[0] in PREVIEWER_CMDS[1]:
				try:
					n = IScriptBIN.type_imageid(2, None, t[1])
				except:
					n = 0
				self.previewer.type.set(1)
				self.previewer.image.set(n)
				self.previewer.imagecmd.set(PREVIEWER_CMDS[1].index(t[0]))
				self.previewer.select(n,1)
			elif t[0] in PREVIEWER_CMDS[2]:
				try:
					n = IScriptBIN.type_spriteid(2, None, t[1])
				except:
					n = 0
				self.previewer.type.set(2)
				self.previewer.sprites.set(n)
				self.previewer.spritescmd.set(PREVIEWER_CMDS[2].index(t[0]))
				self.previewer.select(n,2)
			elif t[0] in PREVIEWER_CMDS[3]:
				try:
					n = IScriptBIN.type_flingyid(2, None, t[1])
				except:
					n = 0
				self.previewer.type.set(3)
				self.previewer.flingy.set(n)
				self.previewer.flingycmd.set(PREVIEWER_CMDS[3].index(t[0]))
				self.previewer.select(n,3)
			else:
				self.previewer.select(0,self.previewer.type.get())
			self.previewer.deiconify()
			self.after(50, self.previewer.updateframes)
		self.previewer.focus_set()

	def sounds(self):
		t = re.split('\\s+',self.text.get('%s linestart' % INSERT,'%s lineend' % INSERT).split('#',1)[0].strip())
		i = 0
		if t[0] == 'playsnd':
			try:
				i = IScriptBIN.type_soundid(2, None, t[1])
			except:
				pass
		SoundDialog(self, i)

	def load(self):
		try:
			warnings = self.parent.ibin.decompile(self, ids=self.ids)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if warnings:
			WarningDialog(self, warnings)

	def write(self, text):
		self.decompile += text

	def readlines(self):
		return self.text.get('1.0', END).split('\n')

	def close(self):
		if self.decompile:
			self.text.insert('1.0', self.decompile.strip())
			self.decompile = ''
			self.text.text.mark_set(INSERT, '1.0')
			self.text.text.see(INSERT)
			self.text.edit_reset()
			self.text.edited = False
			self.editstatus['state'] = DISABLED

	def destroy(self):
		if self.findwindow:
			Toplevel.destroy(self.findwindow)
		if self.previewer:
			Toplevel.destroy(self.previewer)
		Toplevel.destroy(self)
