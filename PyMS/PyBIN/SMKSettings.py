
from ..FileFormats import DialogBIN

from ..Utilities.UIKit import *
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.DropDown import DropDown
from ..Utilities.MPQSelect import MPQSelect
from ..Utilities import Assets

class SMKSettings(PyMSDialog):
	def __init__(self, parent, smk, widget=None, window_pos=False):
		self.widget = (widget if widget else parent)
		self.smk = smk
		self.window_pos = window_pos
		self.settings = parent.settings

		self.filename = StringVar()
		self.overlay_smk = IntVar()
		self.overlay_x = IntegerVar(range=[0,65535])
		self.overlay_y = IntegerVar(range=[0,65535])

		self.flag_fadein = BooleanVar()
		self.flag_dark = BooleanVar()
		self.flag_repeat = BooleanVar()
		self.flag_hover = BooleanVar()
		self.flag_unk1 = BooleanVar()
		self.flag_unk2 = BooleanVar()
		self.flag_unk3 = BooleanVar()
		self.flag_unk4 = BooleanVar()

		PyMSDialog.__init__(self, parent, 'Edit SMK', center=False, resizable=(True, False))

	def widgetize(self):
		textframe = Frame(self)
		Label(textframe, text='Filename:').pack(side=LEFT)
		Entry(textframe, textvariable=self.filename, font=Font.fixed()).pack(side=LEFT, fill=X, expand=1)
		button = Button(textframe, image=Assets.get_image('find'), width=20, height=20, command=self.find_smk)
		button.pack(side=LEFT)
		textframe.grid(row=0,column=0, padx=2,pady=2, sticky=NSEW)

		overlayframe = LabelFrame(self, text='Overlay SMK')
		smkframe = Frame(overlayframe)
		self.smks_dropdown = DropDown(smkframe, self.overlay_smk, ['None'], stay_right=False)
		self.smks_dropdown.pack(side=LEFT, fill=X, expand=1)
		button = Button(smkframe, image=Assets.get_image('edit'), width=20, height=20, command=self.edit_smk)
		button.pack(side=LEFT)
		button = Button(smkframe, image=Assets.get_image('add'), width=20, height=20, command=self.add_smk)
		button.pack(side=LEFT)
		smkframe.pack(side=TOP, fill=X, expand=1)
		offsetframe = Frame(overlayframe)
		Label(offsetframe, text='Offset X:').pack(side=LEFT)
		Entry(offsetframe, textvariable=self.overlay_x, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(offsetframe, text='Offset Y:').pack(side=LEFT)
		Entry(offsetframe, textvariable=self.overlay_y, font=Font.fixed(), width=5).pack(side=LEFT)
		offsetframe.pack(side=TOP, fill=X, expand=1)
		overlayframe.grid(row=1,column=0, padx=5,pady=0, sticky=NSEW)

		flagsframe = LabelFrame(self, text='Flags')
		Checkbutton(flagsframe, text='Fade In', variable=self.flag_fadein).grid(row=0,column=0, sticky=W)
		Checkbutton(flagsframe, text='Dark', variable=self.flag_dark).grid(row=1,column=0, sticky=W)
		Checkbutton(flagsframe, text='Repeat Forever', variable=self.flag_repeat).grid(row=2,column=0, sticky=W)
		Checkbutton(flagsframe, text='Show on Hover', variable=self.flag_hover).grid(row=3,column=0, sticky=W)
		Checkbutton(flagsframe, text='4', variable=self.flag_unk1).grid(row=0,column=1, sticky=W)
		Checkbutton(flagsframe, text='5', variable=self.flag_unk2).grid(row=1,column=1, sticky=W)
		Checkbutton(flagsframe, text='6', variable=self.flag_unk3).grid(row=2,column=1, sticky=W)
		Checkbutton(flagsframe, text='7', variable=self.flag_unk4).grid(row=3,column=1, sticky=W)
		flagsframe.grid(row=0,column=1, rowspan=2, padx=2,pady=2, sticky=S)

		bottom = Frame(self)
		ok = Button(bottom, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=1, pady=3)
		Button(bottom, text='Update Preview', width=15, command=self.update_preview).pack(side=RIGHT, padx=3, pady=3)
		bottom.grid(row=2,column=0, columnspan=2, pady=3, padx=3, sticky=EW)

		self.grid_columnconfigure(0, weight=1)

	def setup_complete(self):
		self.minsize(400,160)
		self.maxsize(9999,160)
		self.load_settings()
		self.load_properties()

	def load_settings(self):
		self.settings.windows.edit.load_window_size('smk', self)
	def save_settings(self):
		self.settings.windows.edit.save_window_size('smk', self)

	def load_property_smk(self):
		smks = ['None']
		for smk in self.widget.parent.bin.smks:
			name = smk.filename
			if smk.overlay_smk:
				name += " (Overlay: %s)" % smk.overlay_smk.filename
			smks.append(name)
		self.smks_dropdown.setentries(smks)

		self.overlay_smk.set(0 if not self.smk.overlay_smk else self.widget.parent.bin.smks.index(self.smk.overlay_smk)+1)
	def load_properties(self):
		self.filename.set(self.smk.filename)
		self.load_property_smk()
		self.overlay_x.set(self.smk.offset_x)
		self.overlay_y.set(self.smk.offset_y)

		self.flag_fadein.set((self.smk.flags & DialogBIN.BINSMK.FLAG_FADE_IN == DialogBIN.BINSMK.FLAG_FADE_IN))
		self.flag_dark.set((self.smk.flags & DialogBIN.BINSMK.FLAG_DARK == DialogBIN.BINSMK.FLAG_DARK))
		self.flag_repeat.set((self.smk.flags & DialogBIN.BINSMK.FLAG_REPEATS == DialogBIN.BINSMK.FLAG_REPEATS))
		self.flag_hover.set((self.smk.flags & DialogBIN.BINSMK.FLAG_SHOW_ON_HOVER == DialogBIN.BINSMK.FLAG_SHOW_ON_HOVER))
		self.flag_unk1.set((self.smk.flags & DialogBIN.BINSMK.FLAG_UNK1 == DialogBIN.BINSMK.FLAG_UNK1))
		self.flag_unk2.set((self.smk.flags & DialogBIN.BINSMK.FLAG_UNK2 == DialogBIN.BINSMK.FLAG_UNK2))
		self.flag_unk3.set((self.smk.flags & DialogBIN.BINSMK.FLAG_UNK3 == DialogBIN.BINSMK.FLAG_UNK3))
		self.flag_unk4.set((self.smk.flags & DialogBIN.BINSMK.FLAG_UNK4 == DialogBIN.BINSMK.FLAG_UNK4))

	def save_property_smk(self):
		edited = False
		index = self.overlay_smk.get()-1
		smk = (None if index == -1 else self.widget.parent.bin.smks[index])
		if smk != self.smk.overlay_smk:
			self.smk.overlay_smk = smk
			edited = True
		return edited
	def save_properties(self):
		edited = False
		if self.filename.get() != self.smk.filename:
			self.smk.filename = self.filename.get()
			edited = True
		edited = edited or self.save_property_smk()
		if self.overlay_x.get() != self.smk.offset_x:
			self.smk.offset_x = self.overlay_x.get()
			edited = True
		if self.overlay_y.get() != self.smk.offset_y:
			self.smk.offset_y = self.overlay_y.get()
			edited = True

		flags = 0
		flags |= self.flag_fadein.get() * DialogBIN.BINSMK.FLAG_FADE_IN
		flags |= self.flag_dark.get() * DialogBIN.BINSMK.FLAG_DARK
		flags |= self.flag_repeat.get() * DialogBIN.BINSMK.FLAG_REPEATS
		flags |= self.flag_hover.get() * DialogBIN.BINSMK.FLAG_SHOW_ON_HOVER
		flags |= self.flag_unk1.get() * DialogBIN.BINSMK.FLAG_UNK1
		flags |= self.flag_unk2.get() * DialogBIN.BINSMK.FLAG_UNK2
		flags |= self.flag_unk3.get() * DialogBIN.BINSMK.FLAG_UNK3
		flags |= self.flag_unk4.get() * DialogBIN.BINSMK.FLAG_UNK4
		if flags != self.smk.flags:
			self.smk.flags = flags
			edited = True
		
		if edited:
			self.mark_edited()

	def update_preview(self):
		self.save_properties()
		self.update_smks()
		self.widget.parent.reload_canvas()

	def find_smk(self):
		m = MPQSelect(self, self.widget.parent.mpqhandler, 'SMK', '*.smk', self.settings, 'Select')
		if m.file and m.file.startswith('MPQ:'):
			self.filename.set(m.file[4:])

	def edit_smk(self):
		if self.overlay_smk.get():
			_,_,x,y,_ = parse_geometry(self.winfo_geometry())
			SMKSettings(self, self.widget.parent.bin.smks[self.overlay_smk.get()-1], self.widget, (x+20,y+20))

	def add_smk(self):
		smk = DialogBIN.BINSMK()
		self.widget.parent.bin.smks.append(smk)
		self.smk.overlay_smk = smk
		self.update_smks()
		self.edit_smk()
		self.mark_edited()

	def update_smks(self):
		self.load_property_smk()
		self.parent.update_smks()

	def mark_edited(self):
		self.parent.mark_edited()

	def ok(self):
		self.update_preview()
		PyMSDialog.ok(self)

	def cancel(self):
		self.ok()

	def dismiss(self):
		self.save_settings()
		PyMSDialog.dismiss(self)
