
from DATTab import DATTab
from DataID import DATID, DataID, UnitsTabID
from DATRef import DATRefs, DATRef

from ..FileFormats.TBL import decompile_string
from ..FileFormats.MPQ.SFmpq import SFMPQ_LOADED

from ..Utilities.utils import BASE_DIR, couriernew, play_sound
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.DataCache import DATA_CACHE

from Tkinter import *

import os

class SoundsTab(DATTab):
	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		self.soundentry = IntegerVar(0, [0,0])
		self.sounddd = IntVar()

		l = LabelFrame(frame, text='Sound:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Sound File:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.soundentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.sounds = DropDown(f, self.sounddd, [], self.changesound, width=30)
		self.soundentry.callback = self.sounds.set
		self.sounds.pack(side=LEFT, fill=X, expand=1, padx=2)
		i = PhotoImage(file=os.path.join(BASE_DIR, 'PyMS', 'Images', 'fwp.gif'))
		self.playbtn = Button(f, image=i, width=20, height=20, command=self.play)
		self.playbtn.image = i
		self.playbtn.pack(side=LEFT, padx=1)
		self.tip(f, 'Sound File', 'SoundFile')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.unknown1 = IntegerVar(0, [0,255])
		self.flags = IntegerVar(0, [0,255])
		self.race = IntVar()
		self.volume = IntegerVar(0, [0,100])

		m = Frame(frame)
		l = LabelFrame(m, text='General Properties:')
		s = Frame(l)
		
		f = Frame(s)
		Label(f, text='Unknown1:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.unknown1, font=couriernew, width=10).pack(side=LEFT)
		self.tip(f, 'Unknown1', 'SoundUnk1')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Flags:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.flags, font=couriernew, width=10).pack(side=LEFT)
		self.tip(f, 'Flags', 'SoundFlags')
		f.pack(fill=X)
		
		f = Frame(s)
		
		Label(f, text='Race:', width=9, anchor=E).pack(side=LEFT)
		DropDown(f, self.race, DATA_CACHE['Races.txt'], width=10).pack(side=LEFT, fill=X, expand=1)
		self.tip(f, 'Race', 'SoundRace')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Volume %:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.volume, font=couriernew, width=10).pack(side=LEFT)
		self.tip(f, 'Volume %', 'SoundVol')
		f.pack(fill=X)
		
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT)
		m.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)
		self.setup_used_by((
			DATRefs(DATID.units, lambda unit: (
				DATRef('Ready', unit.ready_sound, dat_sub_tab=UnitsTabID.sounds),
				DATRef('What', unit.what_sound_start, unit.what_sound_end, dat_sub_tab=UnitsTabID.sounds),
				DATRef('Annoyed', unit.pissed_sound_start, unit.pissed_sound_end, dat_sub_tab=UnitsTabID.sounds),
				DATRef('Yes', unit.yes_sound_start, unit.yes_sound_end, dat_sub_tab=UnitsTabID.sounds)
			)),
		))

	def get_dat_data(self):
		return self.toplevel.data_context.sounds

	def updated_data_files(self, dataids):
		if DataID.sfxdatatbl in dataids:
			self.sounds.setentries(('None',) + self.toplevel.data_context.sfxdatatbl.strings)
			self.soundentry.range[1] = len(self.toplevel.data_context.sfxdatatbl.strings)

	def updated_entry_names(self, datids):
		if DATID.units in datids and self.toplevel.dattabs.active == self:
			self.check_used_by_references()

	def changesound(self, n=None):
		if n == None:
			n = self.soundentry.get()
		else:
			self.soundentry.set(n)
		self.playbtn['state'] = NORMAL if (play_sound and SFMPQ_LOADED and n > 0) else DISABLED

	def play(self):
		if play_sound:
			f = self.toplevel.data_context.mpqhandler.get_file('MPQ:sound\\' + self.toplevel.data_context.sfxdatatbl.strings[self.soundentry.get()-1])
			if f:
				play_sound(f.read())

	def load_entry(self, entry):
		self.soundentry.set(entry.sound_file)
		self.unknown1.set(entry.priority)
		# TODO: Flags
		self.flags.set(entry.flags)
		# TODO: Length adjust
		self.race.set(entry.length_adjust)
		self.volume.set(entry.minimum_volume)

		self.changesound()

	def save_entry(self, entry):
		if self.soundentry.get() != entry.sound_file:
			entry.sound_file = self.soundentry.get()
			self.edited = True
		if self.unknown1.get() != entry.priority:
			entry.priority = self.unknown1.get()
			self.edited = True
		# TODO: Flags
		if self.flags.get() != entry.flags:
			entry.flags = self.flags.get()
			self.edited = True
		# TODO: Length adjust
		if self.race.get() != entry.length_adjust:
			entry.length_adjust = self.race.get()
			self.edited = True
		if self.volume.get() != entry.minimum_volume:
			entry.minimum_volume = self.volume.get()
			self.edited = True
