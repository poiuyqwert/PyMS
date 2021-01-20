
from DATTab import DATTab
from ..FileFormats.TBL import decompile_string
from ..FileFormats.MPQ.SFmpq import SFMPQ_LOADED

from ..Utilities.utils import BASE_DIR, couriernew, play_sound
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.DataCache import DATA_CACHE

from Tkinter import *

import os

class SoundsTab(DATTab):
	data = 'Sfxdata.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		sfxdata = [] # ['None'] + [decompile_string(s) for s in self.toplevel.sfxdatatbl.strings]
		self.soundentry = IntegerVar(0, [0,len(sfxdata)-1])
		self.sounddd = IntVar()

		l = LabelFrame(frame, text='Sound:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Sound File:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.soundentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.sounds = DropDown(f, self.sounddd, sfxdata, self.changesound, width=30)
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

		self.usedby = [
			('units.dat', ['ReadySound',('WhatSoundStart','WhatSoundEnd'),('PissSoundStart','PissSoundEnd'),('YesSoundStart','YesSoundEnd')]),
		]
		self.setuplistbox()

		self.values = {
			'SoundFile':self.soundentry,
			'Unknown1':self.unknown1,
			'Flags':self.flags,
			'Race':self.race,
			'Volume':self.volume,
		}

	def files_updated(self):
		self.dat = self.toplevel.sounds
		sfxdata = ['None'] + [decompile_string(s) for s in self.toplevel.sfxdatatbl.strings]
		self.soundentry.range[1] = len(sfxdata)-1
		self.sounds.setentries(sfxdata)
		self.soundentry.editvalue()

	def changesound(self, n=None):
		if n == None:
			n = self.soundentry.get()
		else:
			self.soundentry.set(n)
		self.playbtn['state'] = [DISABLED,NORMAL][play_sound and SFMPQ_LOADED and n > 0]

	def play(self):
		if play_sound:
			f = self.toplevel.mpqhandler.get_file('MPQ:sound\\' + self.toplevel.sfxdatatbl.strings[self.soundentry.get()-1][:-1])
			if f:
				play_sound(f.read())

	def load_data(self, id=None):
		DATTab.load_data(self, id)
		self.changesound()
