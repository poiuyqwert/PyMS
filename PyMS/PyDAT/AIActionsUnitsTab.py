
from .DATUnitsTab import DATUnitsTab
from .DataID import DATID

from ..FileFormats.DAT.UnitsDAT import Unit

from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.TextTooltip import TextTooltip
from ..Utilities.UIKit import *
from ..Utilities.ScrollView import ScrollView
from ..Utilities import Assets

from math import floor, sqrt

FORCETYPE_GROUND = 0
FORCETYPE_AIR = 1

class AIActionsUnitsTab(DATUnitsTab):
	def __init__(self, parent, toplevel, parent_tab):
		DATUnitsTab.__init__(self, parent, toplevel, parent_tab)
		self.toplevel = toplevel
		scrollview = ScrollView(self)

		self.computeridleentry = IntegerVar(0,[0,189])
		self.computeridle = IntVar()
		self.humanidleentry = IntegerVar(0,[0,189])
		self.humanidle = IntVar()
		self.returntoidleentry = IntegerVar(0,[0,189])
		self.returntoidle = IntVar()
		self.attackunitentry = IntegerVar(0,[0,189])
		self.attackunit = IntVar()
		self.attackmoveentry = IntegerVar(0,[0,189])
		self.attackmove = IntVar()
		self.rightclick = IntVar()
		self.AI_NoSuicide = IntVar()
		self.AI_NoGuard = IntVar()

		l = LabelFrame(scrollview.content_view, text='AI Actions:')
		s = Frame(l)
		def add_dropdown(title, entry_variable, dropdown_variable, hint_name):
			f = Frame(s)
			Label(f, text=title + ':', width=16, anchor=E).pack(side=LEFT)
			Entry(f, textvariable=entry_variable, font=Font.fixed(), width=3).pack(side=LEFT)
			Label(f, text='=').pack(side=LEFT)
			dropdown = DropDown(f, dropdown_variable, [], entry_variable, width=30)
			dropdown.pack(side=LEFT, fill=X, expand=1, padx=2)
			Button(f, text='Jump ->', command=lambda variable=dropdown_variable: self.jump(DATID.orders, variable.get())).pack(side=LEFT)
			self.tip(f, title, hint_name)
			f.pack(fill=X)
			return dropdown
		self.computeridle_ddw = add_dropdown('Computer Idle', self.computeridleentry, self.computeridle, 'UnitAICompIdle')
		self.humanidle_ddw = add_dropdown('Human Idle', self.humanidleentry, self.humanidle, 'UnitAIHumanIdle')
		self.returntoidle_ddw = add_dropdown('Return to Idle', self.returntoidleentry, self.returntoidle, 'UnitAIReturn')
		self.attackunit_ddw = add_dropdown('Attack Unit', self.attackunitentry, self.attackunit, 'UnitAIAttackUnit')
		self.attackmove_ddw = add_dropdown('Attack Move', self.attackmoveentry, self.attackmove, 'UnitAIAttackMove')
		f = Frame(s)
		Label(f, text='Right-Click Action:', width=16, anchor=E).pack(side=LEFT)
		DropDown(f, self.rightclick, Assets.data_cache(Assets.DataReference.Rightclick), width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Right-Click Action', 'UnitAIRightClick')
		f.pack(fill=X, pady=5)

		f = Frame(s)
		# AI Flags
		self.makeCheckbox(f, self.AI_NoSuicide, 'Ignore Strategic Suicide missions', 'UnitAINoSuicide').pack(side=LEFT)
		self.makeCheckbox(f, self.AI_NoGuard, 'Don\'t become a guard', 'UnitAINoGuard').pack(side=LEFT)
		
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=(0,5))
		l.pack(fill=X, side=TOP)

		l = LabelFrame(scrollview.content_view, text='AI Force Values:')
		self.force_value_text = Text(l, state=DISABLED, height=11, font=Font.fixed())
		self.force_value_text.pack(fill=BOTH, padx=5,pady=5)
		l.pack(fill=X, side=TOP)

		def show_hand_cursor(*_):
			self.force_value_text.config(cursor='hand2')
		def show_arrow_cursor(*_):
			self.force_value_text.config(cursor='arrow')
		def view_ground_weapon(*_):
			_,weapon_id = self.force_weapon_id(FORCETYPE_GROUND)
			if weapon_id != 130:
				self.toplevel.dattabs.display('Weapons')
				self.toplevel.changeid(weapon_id)
		def view_air_weapon(*_):
			_,weapon_id = self.force_weapon_id(FORCETYPE_AIR)
			if weapon_id != 130:
				self.toplevel.dattabs.display('Weapons')
				self.toplevel.changeid(weapon_id)
		def view_basic_unit(*_):
			self.parent_tab.dattabs.display('Basic')
		def view_weapon_override_unit(force_type):
			unit_id,_ = self.force_weapon_id(force_type)
			if unit_id == None:
				return
			self.parent_tab.dattabs.display('Basic')
			self.toplevel.changeid(unit_id)

		bold = Font.fixed().bolded()
		self.force_value_text.tag_configure('force_type', underline=1)
		values = (
			('force_value', '#000000', '#E8E8E8', None, 'Used to calculate the strength of a force of units'),
			('ground_range', '#911EB4', '#EBD6F1', view_ground_weapon, 'Ground Weapon Range'),
			('air_range', '#911EB4', '#EBD6F1', view_air_weapon, 'Air Weapon Range'),
			('ground_cooldown', '#F58231', '#FDE8DA', view_ground_weapon, 'Ground Weapon Cooldown'),
			('air_cooldown', '#F58231', '#FDE8DA', view_air_weapon, 'Air Weapon Cooldown'),
			('ground_factor', '#AA6E28', '#F0E5D8', view_ground_weapon, 'Ground Weapon Factor'),
			('air_factor', '#AA6E28', '#F0E5D8', view_air_weapon, 'Air Weapon Factor'),
			('ground_damage', '#E6194B', '#FAD5DE', view_ground_weapon, 'Ground Weapon Damage'),
			('air_damage', '#E6194B', '#FAD5DE', view_air_weapon, 'Air Weapon Damage'),
			('hp', '#3CB44B', '#DCF1DE', view_basic_unit, 'Health'),
			('shields', '#0082C8', '#D1E8F5', view_basic_unit, 'Shields'),
			('reduction', '#F032E6', '#FCDAFA', None, \
"""Unit Specific Adjustments:
  - SCV/Drone/Probe: 0.25
  - Spider Mine/Interceptor/Scarab: 0
  - Firebat/Mutalisk/Zealot: 2
  - Scourge/Infested Terran: 1/16
  - Reaver: 0.1
  - Everything Else: 1"""
  			),
  			('ground_weapon_override', '#000000', '#F3F3F3', lambda *args: view_weapon_override_unit(FORCETYPE_GROUND), \
"""Weapons Override:
  - Carrier/Gantrithor: Uses Interceptor weapons
  - Reaver/Warbringer: Uses Scarab weapons
  - Has a subunit: Uses subunit weapons"""
			),
  			('air_weapon_override', '#000000', '#F3F3F3', lambda *args: view_weapon_override_unit(FORCETYPE_AIR), \
"""Weapons Override:
  - Carrier/Gantrithor: Uses Interceptor weapons
  - Reaver/Warbringer: Uses Scarab weapons
  - Has a subunit: Uses subunit weapons"""
			)
		)
		for tag,fg,bg,action,tooltip in values:
			self.force_value_text.tag_configure(tag, foreground=fg, background=bg, font=bold)
			TextTooltip(self.force_value_text, tag, text=tooltip)
			if action:
				self.force_value_text.tag_bind(tag, Cursor.Enter, show_hand_cursor, '+')
				self.force_value_text.tag_bind(tag, Cursor.Leave, show_arrow_cursor, '+')
				self.force_value_text.tag_bind(tag, Mouse.Click_Left, action)

		scrollview.pack(fill=BOTH, expand=1)

	def copy(self):
		text = self.toplevel.data_context.units.dat.export_entry(self.parent_tab.id, export_properties=[
			Unit.Property.comp_ai_idle,
			Unit.Property.human_ai_idle,
			Unit.Property.return_to_idle,
			Unit.Property.attack_unit,
			Unit.Property.attack_move,
			Unit.Property.right_click_action,
			Unit.Property.ai_internal,
		])
		self.clipboard_set(text)

	def updated_pointer_entries(self, ids):
		if not DATID.orders in ids:
			return

		# TODO: None for expanded dat?
		names = self.toplevel.data_context.orders.names + ('None',)
		self.computeridle_ddw.setentries(names)
		self.humanidle_ddw.setentries(names)
		self.returntoidle_ddw.setentries(names)
		self.attackunit_ddw.setentries(names)
		self.attackmove_ddw.setentries(names)

		count = 255
		if self.toplevel.data_context.settings.settings.get('reference_limits', True):
			count = self.toplevel.data_context.orders.entry_count()
		self.computeridleentry.range[1] = count
		self.humanidleentry.range[1] = count
		self.returntoidleentry.range[1] = count
		self.attackunitentry.range[1] = count
		self.attackmoveentry.range[1] = count

	def force_weapon_id(self, force_type):
		unit_id = self.parent_tab.id
		if unit_id == 72 or unit_id == 82: # Carrier/Gantrithor
			unit_id = 73 # Intercepter
		elif unit_id == 81 or unit_id == 83: # Reaver/Warbringer
			unit_id = 85 # Scarab
		else:
			entry = self.toplevel.data_context.units.dat.get_entry(unit_id)
			if entry.subunit1 != 228:
				unit_id = entry.subunit1
		entry = self.toplevel.data_context.units.dat.get_entry(unit_id)
		if force_type == FORCETYPE_AIR:
			weapon_id = entry.air_weapon
		else:
			weapon_id = entry.ground_weapon
		return (unit_id if unit_id != self.parent_tab.id else None, weapon_id)

	def build_force_value(self, force_type):
		force_type_name = ('Ground','Air')[force_type]

		unit_id = self.parent_tab.id
		reductions = {
			7: 0.25, # SCV
			41: 0.25, # Drone
			64: 0.25, # Probe

			13: 0.0, # Spider Mine
			73: 0.0, # Interceptor
			85: 0.0, # Scarab

			32: 2.0, # Firebat
			43: 2.0, # Mutalisk
			65: 2.0, # Zealot

			47: 1/16.0, # Scourge
			50: 1/16.0, # Infested Terran

			83: 0.1, # Reaver
		}

		override_unit_id,weapon_id = self.force_weapon_id(force_type)

		attack_range = 0
		cooldown = 1
		factor = 0
		damage = 0
		if weapon_id != 130:
			weapon = self.toplevel.data_context.weapons.dat.get_entry(weapon_id)
			attack_range = weapon.maximum_range
			cooldown = weapon.weapon_cooldown
			factor = weapon.damage_factor
			damage = weapon.damage_amount
		unit = self.toplevel.data_context.units.dat.get_entry(unit_id)
		hp = unit.hit_points.whole
		shields = unit.shield_amount if unit.shield_enabled else 0
		reduction = reductions.get(unit_id, 1.0)
		force_value = int(floor(sqrt(floor(floor(attack_range / cooldown) * factor * damage + (floor((factor * damage * 2048) / cooldown) * (hp + shields)) / 256)) * 7.58) * reduction)

		def fstr(f):
			return ('%f' % f).rstrip('0').rstrip('.')
		text = self.force_value_text
		text.insert(END, force_type_name, ('force_type',))
		text.insert(END, '\n = ')
		text.insert(END, fstr(force_value), ('force_value',))
		text.insert(END, '\n = floor(floor(sqrt(floor(floor(')
		tp = force_type_name.lower()
		text.insert(END, '%d' % attack_range, ('%s_range' % tp,))
		text.insert(END, ' / ')
		text.insert(END, '%d' % cooldown, ('%s_cooldown' % tp,))
		text.insert(END, ') * ')
		text.insert(END, '%d' % factor, ('%s_factor' % tp,))
		text.insert(END, ' * ')
		text.insert(END, '%d' % damage, ('%s_damage' % tp,))
		text.insert(END, ' + (floor((')
		text.insert(END, '%d' % factor, ('%s_factor' % tp,))
		text.insert(END, ' * ')
		text.insert(END, '%d' % damage, ('%s_damage' % tp,))
		text.insert(END, ' * 2048) / ')
		text.insert(END, '%d' % cooldown, ('%s_cooldown' % tp,))
		text.insert(END, ') * (')
		text.insert(END, '%d' % hp, ('hp',))
		text.insert(END, ' + ')
		text.insert(END, '%d' % shields, ('shields',))
		text.insert(END, ')) / 256)) * 7.58) * ')
		text.insert(END, fstr(reduction), ('reduction',))
		text.insert(END, ')')
		if force_type == FORCETYPE_AIR and override_unit_id != None:
			text.insert(END, '\n\nUsing weapons from Unit: ')
			text.insert(END, '%d' % override_unit_id, ('%s_weapon_override' % tp,))

	def build_force_values(self):
		text = self.force_value_text
		text["state"] = NORMAL
		text.delete('1.0', END)
		self.build_force_value(FORCETYPE_GROUND)
		text.insert(END, '\n\n')
		self.build_force_value(FORCETYPE_AIR)
		text["state"] = DISABLED

	def load_data(self, entry):
		self.computeridle.set(entry.comp_ai_idle)
		self.humanidle.set(entry.human_ai_idle)
		self.returntoidle.set(entry.return_to_idle)
		self.attackunit.set(entry.attack_unit)
		self.attackmove.set(entry.attack_move)
		self.rightclick.set(entry.right_click_action)
		self.AI_NoSuicide.set(entry.ai_internal & Unit.AIInternalFlag.no_suicide == Unit.AIInternalFlag.no_suicide)
		self.AI_NoGuard.set(entry.ai_internal & Unit.AIInternalFlag.no_guard == Unit.AIInternalFlag.no_guard)
		self.build_force_values()

	def save_data(self, entry):
		edited = False
		if self.computeridle.get() != entry.comp_ai_idle:
			entry.comp_ai_idle = self.computeridle.get()
			edited = True
		if self.humanidle.get() != entry.human_ai_idle:
			entry.human_ai_idle = self.humanidle.get()
			edited = True
		if self.returntoidle.get() != entry.return_to_idle:
			entry.return_to_idle = self.returntoidle.get()
			edited = True
		if self.attackunit.get() != entry.attack_unit:
			entry.attack_unit = self.attackunit.get()
			edited = True
		if self.attackmove.get() != entry.attack_move:
			entry.attack_move = self.attackmove.get()
			edited = True
		if self.rightclick.get() != entry.right_click_action:
			entry.right_click_action = self.rightclick.get()
			edited = True

		ai_internal = entry.ai_internal & ~Unit.AIInternalFlag.ALL_FLAGS
		if self.AI_NoSuicide.get():
			ai_internal |= Unit.AIInternalFlag.no_suicide
		if self.AI_NoGuard.get():
			ai_internal |= Unit.AIInternalFlag.no_guard
		if ai_internal != entry.ai_internal:
			entry.ai_internal = ai_internal
			edited = True

		return edited
