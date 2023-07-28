
from .Delegates import MainDelegate

from ..FileFormats import IScriptBIN
from ..FileFormats import TBL
from ..FileFormats.MPQ.MPQ import MPQ

from ..Utilities.utils import play_sound
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Assets

import re

class SoundDialog(PyMSDialog):
	def __init__(self, parent: Misc, delegate: MainDelegate, text: Text, id: int = 0) -> None:
		self.delegate = delegate
		self.text = text
		self.id = IntVar()
		self.id.set(id)
		PyMSDialog.__init__(self, parent, "Sound Insert/Preview", grabwait=False, resizable=(False, False))

	def widgetize(self) -> Misc | None:
		f = Frame(self)
		self.dd = DropDown(f, self.id, ['%03s %s' % (n,TBL.decompile_string(self.delegate.sfxdatatbl.strings[self.delegate.soundsdat.get_entry(n).sound_file-1][:-1])) for n in range(self.delegate.soundsdat.entry_count())], width=30)
		self.dd.pack(side=LEFT, padx=1)
		Button(f, image=Assets.get_image('fwp'), width=20, height=20, command=self.play, state=NORMAL if MPQ.supported() else DISABLED).pack(side=LEFT, padx=1)
		f.pack(padx=5,pady=5)

		self.overwrite = IntVar()
		self.closeafter = IntVar()
		self.closeafter.set(self.delegate.settings.sounds.get('closeafter',0))

		btns = Frame(self)
		lf = LabelFrame(btns, text='Insert/Overwrite')
		r = Frame(lf)
		Checkbutton(r, text='Overwrite', variable=self.overwrite).pack(side=LEFT)
		Checkbutton(r, text='Close after', variable=self.closeafter).pack(side=LEFT)
		r.pack()
		r = Frame(lf)
		Button(r, text='ID', width=10, command=self.doid).pack(side=LEFT)
		Button(r, text='Command', width=10, command=self.docmd).pack(side=LEFT)
		r.pack(padx=5, pady=5)
		lf.pack(side=LEFT)
		r = Frame(btns)
		ok = Button(r, text='Ok', width=10, command=self.ok)
		ok.pack(side=BOTTOM)
		r.pack(side=RIGHT, fill=Y)
		btns.pack(fill=X, padx=5, pady=5)

		return ok

	def play(self) -> None:
		if not play_sound:
			return
		f = self.delegate.mpqhandler.get_file('MPQ:sound\\' + self.delegate.sfxdatatbl.strings[self.delegate.soundsdat.get_entry(self.id.get()).sound_file-1][:-1])
		if not f:
			return
		play_sound(f.read())

	def doid(self) -> None:
		if self.overwrite.get():
			s = self.text.index('%s linestart' % INSERT)
			m = re.match('(\\s*)(\\S+)(\\s+)([^\\s#]+)(\\s+.*)?', self.text.get(s,'%s lineend' % INSERT))
			if m and m.group(2) == 'playsnd':
				self.text.delete(s,'%s lineend' % INSERT)
				self.text.insert(s, m.group(1)+m.group(2)+m.group(3)+str(self.id.get())+m.group(5))
		else:
			self.text.insert(INSERT, str(self.id.get()))
		if self.closeafter.get():
			self.destroy()

	def docmd(self) -> None:
		s = self.text.index('%s linestart' % INSERT)
		i = IScriptBIN.type_soundid(1, self.delegate.get_ibin(), self.id.get())
		assert isinstance(i, tuple)
		longest_opcode = max([len(o[0][0]) for o in IScriptBIN.OPCODES] + [13]) + 1
		t = '\tplaysnd%s\t%s' % (' ' * (longest_opcode-7),i[0])
		if i[1]:
			t += ' # ' + i[1]
		if self.overwrite.get():
			self.text.delete(s,'%s lineend' % INSERT)
		else:
			t += '\n'
		self.text.insert(s, t)
		if self.closeafter.get():
			self.destroy()

	def destroy(self):
		self.delegate.settings.sounds.closeafter = self.closeafter.get()
		PyMSDialog.withdraw(self)
