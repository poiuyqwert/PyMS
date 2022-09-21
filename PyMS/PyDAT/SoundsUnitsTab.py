
from .DATUnitsTab import DATUnitsTab
from .DataID import DATID

from ..FileFormats.DAT.UnitsDAT import Unit

from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.UIKit import *
from ..Utilities.ScrollView import ScrollView

class SoundsUnitsTab(DATUnitsTab):
	def __init__(self, parent, toplevel, parent_tab):
		DATUnitsTab.__init__(self, parent, toplevel, parent_tab)
		self.toplevel = toplevel
		scrollview = ScrollView(self)
		
		self.ready_sound = IntegerVar(0, [0,0])
		self.ready_sound_dropdown = IntVar()
		self.yes_sound_start = IntegerVar(0, [0,0])
		self.yes_sounds_start_dropdown = IntVar()
		self.yes_sound_end = IntegerVar(0, [0,0])
		self.lastyesdd = IntVar()
		self.what_sound_start = IntegerVar(0, [0,0])
		self.what_sound_start_dropdown = IntVar()
		self.what_sound_end = IntegerVar(0, [0,0])
		self.what_sound_end_dropdown = IntVar()
		self.pissed_sound_start = IntegerVar(0, [0,0])
		self.pissed_sound_start_dropdown = IntVar()
		self.pissed_sound_end = IntegerVar(0, [0,0])
		self.pissed_sound_end_dropdown = IntVar()

		l = LabelFrame(scrollview.content_view, text='Sounds:')
		s = Frame(l)

		f = Frame(s)
		Label(f, text='Ready:', width=13, anchor=E).pack(side=LEFT)
		self.ready_sound_entry_widget = Entry(f, textvariable=self.ready_sound, font=Font.fixed(), width=5)
		self.ready_sound_entry_widget.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.ready_sound_dropdown_widget = DropDown(f, self.ready_sound_dropdown, [], self.ready_sound, width=30)
		self.ready_sound_dropdown_widget.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.ready_sound_button_widget = Button(f, text='Jump ->', command=lambda: self.jump(DATID.sfxdata, self.ready_sound_dropdown.get()))
		self.ready_sound_button_widget.pack(side=LEFT)
		self.tip(f, 'Ready', 'UnitSndReady')
		f.pack(fill=X)

		f = Frame(s)
		Label(f, text='Yes (First):', width=13, anchor=E).pack(side=LEFT)
		self.yes_sound_start_entry_widget = Entry(f, textvariable=self.yes_sound_start, font=Font.fixed(), width=5)
		self.yes_sound_start_entry_widget.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.yes_sound_start_dropdown_widget = DropDown(f, self.yes_sounds_start_dropdown, [], self.yes_sound_start, width=30)
		self.yes_sound_start_dropdown_widget.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.yes_sound_start_button_widget = Button(f, text='Jump ->', command=lambda: self.jump(DATID.sfxdata, self.yes_sounds_start_dropdown.get()))
		self.yes_sound_start_button_widget.pack(side=LEFT)
		self.tip(f, 'Yes (First)', 'UnitSndYesStart')
		f.pack(fill=X)

		f = Frame(s)
		Label(f, text='Yes (Last):', width=13, anchor=E).pack(side=LEFT)
		self.yes_sound_end_entry_widget = Entry(f, textvariable=self.yes_sound_end, font=Font.fixed(), width=5)
		self.yes_sound_end_entry_widget.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.yes_sound_end_dropdown_widget = DropDown(f, self.lastyesdd, [], self.yes_sound_end, width=30)
		self.yes_sound_end_dropdown_widget.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.yes_sound_end_button_widget = Button(f, text='Jump ->', command=lambda: self.jump(DATID.sfxdata, self.lastyesdd.get()))
		self.yes_sound_end_button_widget.pack(side=LEFT)
		self.tip(f, 'Yes (Last)', 'UnitSndYesEnd')
		f.pack(fill=X)

		f = Frame(s)
		Label(f, text='What (First):', width=13, anchor=E).pack(side=LEFT)
		self.what_sound_start_entry_widget = Entry(f, textvariable=self.what_sound_start, font=Font.fixed(), width=5)
		self.what_sound_start_entry_widget.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.what_sound_start_dropdown_widget = DropDown(f, self.what_sound_start_dropdown, [], self.what_sound_start, width=30)
		self.what_sound_start_dropdown_widget.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.what_sound_start_button_widget = Button(f, text='Jump ->', command=lambda: self.jump(DATID.sfxdata, self.what_sound_start_dropdown.get()))
		self.what_sound_start_button_widget.pack(side=LEFT)
		self.tip(f, 'What (First)', 'UnitSndWhatStart')
		f.pack(fill=X)

		f = Frame(s)
		Label(f, text='What (Last):', width=13, anchor=E).pack(side=LEFT)
		self.what_sound_end_entry_widget = Entry(f, textvariable=self.what_sound_end, font=Font.fixed(), width=5)
		self.what_sound_end_entry_widget.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.what_sound_end_dropdown_widget = DropDown(f, self.what_sound_end_dropdown, [], self.what_sound_end, width=30)
		self.what_sound_end_dropdown_widget.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.what_sound_end_button_widget = Button(f, text='Jump ->', command=lambda: self.jump(DATID.sfxdata, self.what_sound_end_dropdown.get()))
		self.what_sound_end_button_widget.pack(side=LEFT)
		self.tip(f, 'What (Last)', 'UnitSndWhatEnd')
		f.pack(fill=X)

		f = Frame(s)
		Label(f, text='Annoyed (First):', width=13, anchor=E).pack(side=LEFT)
		self.pissed_sound_start_entry_widget = Entry(f, textvariable=self.pissed_sound_start, font=Font.fixed(), width=5)
		self.pissed_sound_start_entry_widget.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.pissed_sound_start_dropdown_widget = DropDown(f, self.pissed_sound_start_dropdown, [], self.pissed_sound_start, width=30)
		self.pissed_sound_start_dropdown_widget.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.pissed_sound_start_button_widget = Button(f, text='Jump ->', command=lambda: self.jump(DATID.sfxdata, self.pissed_sound_start_dropdown.get()))
		self.pissed_sound_start_button_widget.pack(side=LEFT)
		self.tip(f, 'Annoyed (First)', 'UnitSndAnnStart')
		f.pack(fill=X)

		f = Frame(s)
		Label(f, text='Annoyed (Last):', width=13, anchor=E).pack(side=LEFT)
		self.pissed_sound_end_entry_widget = Entry(f, textvariable=self.pissed_sound_end, font=Font.fixed(), width=5)
		self.pissed_sound_end_entry_widget.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.pissed_sound_end_dropdown_widget = DropDown(f, self.pissed_sound_end_dropdown, [], self.pissed_sound_end, width=30)
		self.pissed_sound_end_dropdown_widget.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.pissed_sound_end_button_widget = Button(f, text='Jump ->', command=lambda: self.jump(DATID.sfxdata, self.pissed_sound_end_dropdown.get()))
		self.pissed_sound_end_button_widget.pack(side=LEFT)
		self.tip(f, 'Annoyed (Last)', 'UnitSndAnnEnd')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		scrollview.pack(fill=BOTH, expand=1)

	def copy(self):
		text = self.toplevel.data_context.units.dat.export_entry(self.parent_tab.id, export_properties=[
			Unit.Property.ready_sound,
			Unit.Property.what_sound_start,
			Unit.Property.what_sound_end,
			Unit.Property.pissed_sound_start,
			Unit.Property.pissed_sound_end,
			Unit.Property.yes_sound_start,
			Unit.Property.yes_sound_end,
		])
		self.clipboard_set(text)

	def updated_pointer_entries(self, ids):
		if not DATID.sfxdata in ids:
			return

		names = self.toplevel.data_context.sounds.names
		dropdowns = (
			self.ready_sound_dropdown_widget,
			self.yes_sound_start_dropdown_widget,
			self.yes_sound_end_dropdown_widget,
			self.what_sound_start_dropdown_widget,
			self.what_sound_end_dropdown_widget,
			self.pissed_sound_start_dropdown_widget,
			self.pissed_sound_end_dropdown_widget
		)
		for dropdown in dropdowns:
			dropdown.setentries(names)

		limit = 65535
		if self.toplevel.data_context.settings.settings.get('reference_limits', True):
			limit = self.toplevel.data_context.sounds.entry_count() - 1
		variables = (
			self.ready_sound,
			self.yes_sound_start,
			self.yes_sound_end,
			self.what_sound_start,
			self.what_sound_end,
			self.pissed_sound_start,
			self.pissed_sound_end
		)
		for variable in variables:
			variable.range[1] = limit

	def load_data(self, entry):
		fields = (
			(entry.ready_sound, self.ready_sound, (self.ready_sound_entry_widget, self.ready_sound_dropdown_widget, self.ready_sound_button_widget)),

			(entry.what_sound_start, self.what_sound_start, (self.what_sound_start_entry_widget, self.what_sound_start_dropdown_widget, self.what_sound_start_button_widget)),
			(entry.what_sound_end, self.what_sound_end, (self.what_sound_end_entry_widget, self.what_sound_end_dropdown_widget, self.what_sound_end_button_widget)),

			(entry.pissed_sound_start, self.pissed_sound_start, (self.pissed_sound_start_entry_widget, self.pissed_sound_start_dropdown_widget, self.pissed_sound_start_button_widget)),
			(entry.pissed_sound_end, self.pissed_sound_end, (self.pissed_sound_end_entry_widget, self.pissed_sound_end_dropdown_widget, self.pissed_sound_end_button_widget)),

			(entry.yes_sound_start, self.yes_sound_start, (self.yes_sound_start_entry_widget, self.yes_sound_start_dropdown_widget, self.yes_sound_start_button_widget)),
			(entry.yes_sound_end, self.yes_sound_end, (self.yes_sound_end_entry_widget, self.yes_sound_end_dropdown_widget, self.yes_sound_end_button_widget))
		)
		for (sound, variable, widgets) in fields:
			has_sound = sound != None
			variable.set(sound if has_sound else 0)
			state = NORMAL if has_sound else DISABLED
			for widget in widgets:
				widget['state'] = state

	def save_data(self, entry):
		edited = False
		if entry.ready_sound != None and self.ready_sound.get() != entry.ready_sound:
			entry.ready_sound = self.ready_sound.get()
			edited = True

		if entry.what_sound_start != None and self.what_sound_start.get() != entry.what_sound_start:
			entry.what_sound_start = self.what_sound_start.get()
			edited = True
		if entry.what_sound_end != None and self.what_sound_end.get() != entry.what_sound_end:
			entry.what_sound_end = self.what_sound_end.get()
			edited = True

		if entry.pissed_sound_start != None and self.pissed_sound_start.get() != entry.pissed_sound_start:
			entry.pissed_sound_start = self.pissed_sound_start.get()
			edited = True
		if entry.pissed_sound_end != None and self.pissed_sound_end.get() != entry.pissed_sound_end:
			entry.pissed_sound_end = self.pissed_sound_end.get()
			edited = True

		if entry.yes_sound_start != None and self.yes_sound_start.get() != entry.yes_sound_start:
			entry.yes_sound_start = self.yes_sound_start.get()
			edited = True
		if entry.yes_sound_end != None and self.yes_sound_end.get() != entry.yes_sound_end:
			entry.yes_sound_end = self.yes_sound_end.get()
			edited = True

		return edited
