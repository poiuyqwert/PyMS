
from ..FileFormats import IScriptBIN
from ..FileFormats import TBL
from ..FileFormats.MPQ.MPQ import MPQ
from ..FileFormats import DAT

from ..Utilities.utils import play_sound
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.DropDown import DropDown
from ..Utilities import Assets

class SoundDialog(PyMSDialog):
	def __init__(self, parent, id=0):
		self.toplevel = parent.parent
		self.id = IntVar()
		self.id.set(id)
		PyMSDialog.__init__(self, parent, "Sound Insert/Preview", grabwait=False, resizable=(False, False))

	def widgetize(self):
		f = Frame(self)
		self.dd = DropDown(f, self.id, ['%03s %s' % (n,TBL.decompile_string(self.toplevel.sfxdatatbl.strings[self.toplevel.soundsdat.get_entry(n).sound_file-1][:-1])) for n in range(self.toplevel.soundsdat.entry_count())], width=30)
		self.dd.pack(side=LEFT, padx=1)
		b = Button(f, image=Assets.get_image('fwp'), width=20, height=20, command=self.play, state=NORMAL if (play_sound and MPQ.supported()) else DISABLED)
		b.pack(side=LEFT, padx=1)
		f.pack(padx=5,pady=5)

		self.overwrite = IntVar()
		self.closeafter = IntVar()
		self.closeafter.set(self.toplevel.settings.sounds.get('closeafter',0))

		btns = Frame(self)
		lf = LabelFrame(btns, text='Insert/Overwrite')
		b = Frame(lf)
		Checkbutton(b, text='Overwrite', variable=self.overwrite).pack(side=LEFT)
		Checkbutton(b, text='Close after', variable=self.closeafter).pack(side=LEFT)
		b.pack()
		b = Frame(lf)
		Button(b, text='ID', width=10, command=self.doid).pack(side=LEFT)
		Button(b, text='Command', width=10, command=self.docmd).pack(side=LEFT)
		b.pack(padx=5, pady=5)
		lf.pack(side=LEFT)
		r = Frame(btns)
		ok = Button(r, text='Ok', width=10, command=self.ok)
		ok.pack(side=BOTTOM)
		r.pack(side=RIGHT, fill=Y)
		btns.pack(fill=X, padx=5, pady=5)

		return ok

	def play(self):
		f = self.parent.parent.mpqhandler.get_file('MPQ:sound\\' + self.toplevel.sfxdatatbl.strings[self.toplevel.soundsdat.get_entry(self.id.get()).sound_file-1][:-1])
		if f:
			play_sound(f.read())

	def doid(self):
		if self.overwrite.get():
			s = self.parent.text.index('%s linestart' % INSERT)
			m = re.match('(\\s*)(\\S+)(\\s+)([^\\s#]+)(\\s+.*)?', self.parent.text.get(s,'%s lineend' % INSERT))
			if m and m.group(2) == 'playsnd':
				self.parent.text.delete(s,'%s lineend' % INSERT)
				self.parent.text.insert(s, m.group(1)+m.group(2)+m.group(3)+str(self.id.get())+m.group(5))
		else:
			self.parent.text.insert(INSERT, self.id.get())
		if self.closeafter.get():
			self.destroy()

	def docmd(self):
		s = self.parent.text.index('%s linestart' % INSERT)
		i = IScriptBIN.type_soundid(1, self.toplevel.ibin, self.id.get())
		longest_opcode = max([len(o[0][0]) for o in IScriptBIN.OPCODES] + [13]) + 1
		t = '\tplaysnd%s\t%s' % (' ' * (longest_opcode-7),i[0])
		if i[1]:
			t += ' # ' + i[1]
		if self.overwrite.get():
			self.parent.text.delete(s,'%s lineend' % INSERT)
		else:
			t += '\n'
		self.parent.text.insert(s, t)
		if self.closeafter.get():
			self.destroy()

	def destroy(self):
		self.toplevel.settings.sounds.closeafter = self.closeafter.get()
		PyMSDialog.withdraw(self)
