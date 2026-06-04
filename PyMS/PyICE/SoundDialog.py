
from .Delegates import MainDelegate
from .Config import PyICEConfig

from ..FileFormats.IScriptBIN.CodeHandlers import CodeCommands
from ..FileFormats.MPQ.MPQ import MPQ

from ..Utilities.utils import play_sound
from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Assets
from ..Utilities.CodeHandlers.CodeCommand import CodeCommand

import re, io

class SoundDialog(PyMSDialog):
	def __init__(self, *, parent: UI.Misc, delegate: MainDelegate, config: PyICEConfig.Sounds, text: UI.CodeText, sound_id: int = 0) -> None:
		self.delegate = delegate
		self.config_ = config
		self.text = text
		self.id = UI.IntVar()
		self.id.set(sound_id)
		PyMSDialog.__init__(self, parent, "Sound Insert/Preview", grabwait=False, resizable=(False, False))

	def widgetize(self) -> UI.Misc | None:
		f = UI.Frame(self)
		# TODO: Missing soundsdat?
		sounds_dat = self.delegate.get_data_context().sounds_dat
		assert sounds_dat is not None
		self.dd = UI.DropDown(f, self.id, [f'{n:03} {self.delegate.get_data_context().sound_name(n)}' for n in range(self.delegate.get_data_context().sounds_entry_count)], width=30)
		self.dd.pack(side=UI.LEFT, padx=1)
		UI.Button(f, image=Assets.get_image('fwp'), width=20, height=20, command=self.play, state=UI.NORMAL if MPQ.supported() else UI.DISABLED).pack(side=UI.LEFT, padx=1)
		f.pack(padx=5,pady=5)

		self.overwrite = UI.BooleanVar(value=self.config_.overwrite.value)
		self.closeafter = UI.BooleanVar(value=self.config_.close_after.value)

		btns = UI.Frame(self)
		lf = UI.LabelFrame(btns, text='Insert/Overwrite')
		r = UI.Frame(lf)
		UI.Checkbutton(r, text='Overwrite', variable=self.overwrite).pack(side=UI.LEFT)
		UI.Checkbutton(r, text='Close after', variable=self.closeafter).pack(side=UI.LEFT)
		r.pack()
		r = UI.Frame(lf)
		UI.Button(r, text='ID', width=10, command=self.doid).pack(side=UI.LEFT)
		UI.Button(r, text='Command', width=10, command=self.docmd).pack(side=UI.LEFT)
		r.pack(padx=5, pady=5)
		lf.pack(side=UI.LEFT)
		r = UI.Frame(btns)
		ok = UI.Button(r, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.BOTTOM)
		r.pack(side=UI.RIGHT, fill=UI.Y)
		btns.pack(fill=UI.X, padx=5, pady=5)

		return ok

	def play(self) -> None:
		if not play_sound:
			return
		sound_path = self.delegate.get_data_context().sound_path(self.id.get())
		if not sound_path:
			return
		f = self.delegate.mpqhandler.get_file('MPQ:sound\\' + sound_path)
		if not f:
			return
		play_sound(f.read())

	def doid(self) -> None:
		if self.overwrite.get():
			s = self.text.index(f'{UI.INSERT} linestart')
			m = re.match('(\\s*)(\\S+)(\\s+)([^\\s#]+)(\\s+.*)?', self.text.get(s,f'{UI.INSERT} lineend'))
			if m and m.group(2) == 'playsnd':
				self.text.delete(s, f'{UI.INSERT} lineend')
				self.text.insert(s, m.group(1)+m.group(2)+m.group(3)+str(self.id.get())+m.group(5))
		else:
			self.text.insert(UI.INSERT, str(self.id.get()))
		if self.closeafter.get():
			self.destroy()

	def docmd(self) -> None:
		s = self.text.index(f'{UI.INSERT} linestart')
		output = io.StringIO()
		serialize_context = self.delegate.get_serialize_context(output)
		serialize_context.indent()
		CodeCommand(CodeCommands.Playsnd, [self.id.get()]).serialize(serialize_context)
		text = output.getvalue()
		with self.text.undo_group():
			if self.overwrite.get():
				self.text.delete(s, f'{UI.INSERT} lineend')
				text = text.rstrip('\n')
			self.text.insert(s, text)
		if self.closeafter.get():
			self.destroy()

	def destroy(self) -> None:
		self.config_.overwrite.value = self.overwrite.get()
		self.config_.close_after.value = self.closeafter.get()
		PyMSDialog.withdraw(self)
