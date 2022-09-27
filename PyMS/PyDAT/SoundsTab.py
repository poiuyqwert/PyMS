
from .DATTab import DATTab
from .DataID import DATID, DataID, UnitsTabID
from .DATRef import DATRefs, DATRef

from ..FileFormats.DAT.SoundsDAT import Sound
from ..FileFormats.MPQ.MPQ import MPQ

from ..Utilities.utils import play_sound
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.UIKit import *
from ..Utilities.ScrollView import ScrollView
from ..Utilities import Assets

class SoundsTab(DATTab):
	DAT_ID = DATID.sfxdata

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		scrollview = ScrollView(self)

		self.soundentry = IntegerVar(0, [0,0])
		self.sounddd = IntVar()

		l = LabelFrame(scrollview.content_view, text='Sound:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Sound File:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.soundentry, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.sounds = DropDown(f, self.sounddd, [], self.changesound, width=30)
		self.soundentry.callback = self.sounds.set
		self.sounds.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.playbtn = Button(f, image=Assets.get_image('fwp'), width=20, height=20, command=self.play)
		self.playbtn.pack(side=LEFT, padx=1)
		self.tip(f, 'Sound File', 'SoundFile')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.priority = IntegerVar(0, [0,255])
		self.portrait_length_adjust = IntegerVar(0, [0,65535])
		self.minimum_volume = IntegerVar(0, [0,100])

		m = Frame(scrollview.content_view)

		l = LabelFrame(m, text='General Properties:')
		s = Frame(l)
		
		f = Frame(s)
		Label(f, text='Priority:', width=17, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.priority, font=Font.fixed(), width=5).pack(side=LEFT)
		self.tip(f, 'Priority', 'SoundPriority')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Portrait Length Adjust:', width=17, anchor=E).pack(side=LEFT)
		self.tip(f, 'Portrait Length Adjust', 'SoundPortraitLengthAdjust')
		Entry(f, textvariable=self.portrait_length_adjust, font=Font.fixed(), width=5).pack(side=LEFT)
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Minimum Volume %:', width=17, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.minimum_volume, font=Font.fixed(), width=5).pack(side=LEFT)
		self.tip(f, 'Minimum Volume %', 'SoundMinimumVolume')
		f.pack(fill=X)
		
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=Y)

		self.preload = IntVar()
		self.unit_speech = IntVar()
		self.one_at_a_time = IntVar()
		self.never_preempt = IntVar()

		l = LabelFrame(m, text='Flags:')
		s = Frame(l)

		f = Frame(s)
		self.makeCheckbox(f, self.preload, 'Preload', 'SoundPreload').pack(side=LEFT)
		f.pack(side=TOP, fill=X)
		f = Frame(s)
		self.makeCheckbox(f, self.unit_speech, 'Unit Speech', 'SoundUnitSpeech').pack(side=LEFT)
		f.pack(side=TOP, fill=X)
		f = Frame(s)
		self.makeCheckbox(f, self.one_at_a_time, 'One at a Time', 'SoundOneAtATime').pack(side=LEFT)
		f.pack(side=TOP, fill=X)
		f = Frame(s)
		self.makeCheckbox(f, self.never_preempt, 'Never Preempt', 'SoundNeverPreempt').pack(side=LEFT)
		f.pack(side=TOP, fill=X)

		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, padx=2)

		m.pack(fill=X)
		scrollview.pack(fill=BOTH, expand=1)

		self.setup_used_by((
			DATRefs(DATID.units, lambda unit: (
				DATRef('Ready', unit.ready_sound, dat_sub_tab=UnitsTabID.sounds),
				DATRef('What', unit.what_sound_start, unit.what_sound_end, dat_sub_tab=UnitsTabID.sounds),
				DATRef('Annoyed', unit.pissed_sound_start, unit.pissed_sound_end, dat_sub_tab=UnitsTabID.sounds),
				DATRef('Yes', unit.yes_sound_start, unit.yes_sound_end, dat_sub_tab=UnitsTabID.sounds)
			)),
		))

	def updated_pointer_entries(self, ids):
		if DataID.sfxdatatbl in ids:
			self.sounds.setentries(('None',) + self.toplevel.data_context.sfxdatatbl.strings)
			self.soundentry.range[1] = len(self.toplevel.data_context.sfxdatatbl.strings)

		if DATID.units in ids and self.toplevel.dattabs.active == self:
			self.check_used_by_references()

	def changesound(self, n=None):
		if n == None:
			n = self.soundentry.get()
		else:
			self.soundentry.set(n)
		self.playbtn['state'] = NORMAL if (play_sound and MPQ.supported() and n > 0) else DISABLED

	def play(self):
		if play_sound:
			tbl_string = self.toplevel.data_context.sfxdatatbl.strings[self.soundentry.get()-1]
			if tbl_string.endswith('<0>'):
				tbl_string = tbl_string[:-3]
			f = self.toplevel.data_context.mpqhandler.get_file('MPQ:sound\\' + tbl_string)
			if f:
				play_sound(f.read())

	def load_entry(self, entry):
		self.soundentry.set(entry.sound_file)
		self.priority.set(entry.priority)

		flags_fields = (
			(self.preload, Sound.Flag.preload),
			(self.unit_speech, Sound.Flag.unit_speech),
			(self.one_at_a_time, Sound.Flag.one_at_a_time),
			(self.never_preempt, Sound.Flag.never_preempt)
		)
		for (variable, flag) in flags_fields:
			variable.set(entry.flags & flag == flag)

		# TODO: Length adjust
		self.portrait_length_adjust.set(entry.portrait_length_adjust)
		self.minimum_volume.set(entry.minimum_volume)

		self.changesound()

	def save_entry(self, entry):
		if self.soundentry.get() != entry.sound_file:
			entry.sound_file = self.soundentry.get()
			self.edited = True
			if self.toplevel.data_context.settings.settings.get('customlabels'):
				self.toplevel.data_context.dat_data(DATID.sfxdata).update_names()
		if self.priority.get() != entry.priority:
			entry.priority = self.priority.get()
			self.edited = True

		flags = entry.flags & ~Sound.Flag.ALL_FLAGS
		flags_fields = (
			(self.preload, Sound.Flag.preload),
			(self.unit_speech, Sound.Flag.unit_speech),
			(self.one_at_a_time, Sound.Flag.one_at_a_time),
			(self.never_preempt, Sound.Flag.never_preempt)
		)
		for (variable, flag) in flags_fields:
			if variable.get():
				flags |= flag
		if flags != entry.flags:
			entry.flags = flags
			self.edited = True

		# TODO: Length adjust
		if self.portrait_length_adjust.get() != entry.portrait_length_adjust:
			entry.portrait_length_adjust = self.portrait_length_adjust.get()
			self.edited = True
		if self.minimum_volume.get() != entry.minimum_volume:
			entry.minimum_volume = self.minimum_volume.get()
			self.edited = True
