
from .DATTab import DATTab
from .DataID import DATID, UnitsTabID
from .DATRef import DATRefs, DATRef

from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.FloatVar import FloatVar
from ..Utilities.DropDown import DropDown
from ..Utilities.UIKit import *
from ..Utilities.ScrollView import ScrollView
from ..Utilities import Assets

class FlingyTab(DATTab):
	DAT_ID = DATID.flingy

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		scrollview = ScrollView(self)

		self.spriteentry = IntegerVar(0, [0,516])
		self.spritedd = IntVar()
		self.topspeed = IntegerVar(0, [0,4294967294], callback=lambda n,i=0: self.updatespeed(n,i))
		self.speed = FloatVar(1, [0,40265318.381], callback=lambda n,i=1: self.updatespeed(n,i), precision=3)
		self.acceleration = IntegerVar(0, [0,65535])
		self.haltdistance = IntegerVar(0, [0,4294967294], callback=lambda n,i=0: self.updatehalt(n,i))
		self.halt = FloatVar(1, [0,16777215.9921], callback=lambda n,i=1: self.updatehalt(n,i), precision=4)
		self.turnradius = IntegerVar(0, [0,255])
		self.movecontrol = IntVar()
		self.unused = IntegerVar(0, [0,255])

		l = LabelFrame(scrollview.content_view, text='Flingy Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Sprite:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.spriteentry, font=Font.fixed(), width=10).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.sprite_ddw = DropDown(f, self.spritedd, [], self.spriteentry, width=30)
		self.sprite_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda: self.jump(DATID.sprites, self.spritedd.get())).pack(side=LEFT, padx=2)
		self.tip(f, 'Sprite', 'FlingySprite')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Top Speed:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.topspeed, font=Font.fixed(), width=10).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.speed, font=Font.fixed(), width=12).pack(side=LEFT, padx=2)
		Label(f, text='pixels/frame').pack(side=LEFT)
		self.tip(f, 'Top Speed', 'FlingySpeed')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Acceleration:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.acceleration, font=Font.fixed(), width=10).pack(side=LEFT, padx=2)
		self.tip(f, 'Acceleration', 'FlingyAcceleration')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Halt Distance:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.haltdistance, font=Font.fixed(), width=10).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.halt, font=Font.fixed(), width=14).pack(side=LEFT, padx=2)
		Label(f, text='pixels').pack(side=LEFT)
		self.tip(f, 'Halt Distance', 'FlingyHaltDist')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Turn Radius:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.turnradius, font=Font.fixed(), width=10).pack(side=LEFT, padx=2)
		self.tip(f, 'Turn Radius', 'FlingyTurnRad')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Move Control:', width=12, anchor=E).pack(side=LEFT)
		DropDown(f, self.movecontrol, Assets.data_cache(Assets.DataReference.FlingyControl), width=20).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Move Control', 'FlingyMoveControl')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='IScript Mask:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.unused, font=Font.fixed(), width=10).pack(side=LEFT, padx=2)
		self.tip(f, 'IScript Mask', 'FlingyUnused')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)
		scrollview.pack(fill=BOTH, expand=1)

		self.setup_used_by((
			DATRefs(DATID.units, lambda unit: (
				DATRef('Graphics', unit.graphics, dat_sub_tab=UnitsTabID.graphics),
			)),
			DATRefs(DATID.weapons, lambda weapon: (
				DATRef('Graphics', weapon.graphics),
			)),
		))

	def updated_pointer_entries(self, ids):
		if (DATID.units in ids or DATID.weapons in ids) and self.toplevel.dattabs.active == self:
			self.check_used_by_references()
		if DATID.sprites in ids:
			self.sprite_ddw.setentries(self.toplevel.data_context.sprites.names)
			if self.toplevel.data_context.settings.settings.get('reference_limits', True):
				self.spriteentry.range[1] = self.toplevel.data_context.sprites.entry_count() - 1
			else:
				self.spriteentry.range[1] = 65535

	def updatespeed(self, num, type):
		if type:
			self.topspeed.check = False
			self.topspeed.set(int((float(num) * 320 / 3.0)))
		else:
			self.speed.check = False
			s = str(int(num) * 3 / 320.0)
			if s.endswith('.0'):
				s = s[:-2]
			elif len(s.split('.')[1]) > 3:
				s = s[:s.index('.')+4]
			self.speed.set(s)

	def updatehalt(self, num, type):
		if type:
			self.haltdistance.check = False
			self.haltdistance.set(int((float(num) * 256)))
		else:
			self.halt.check = False
			s = str(int(num) / 256.0)
			if s.endswith('.0'):
				s = s[:-2]
			elif len(s.split('.')[1]) > 4:
				s = s[:s.index('.')+5]
			self.halt.set(s)

	def load_entry(self, entry):
		self.spriteentry.set(entry.sprite)
		self.topspeed.set(entry.speed)
		self.acceleration.set(entry.acceleration)
		self.haltdistance.set(entry.halt_distance)
		self.turnradius.set(entry.turn_radius)
		self.unused.set(entry.iscript_mask)
		self.movecontrol.set(entry.movement_control)

	def save_entry(self, entry):
		if self.spriteentry.get() != entry.sprite:
			entry.sprite = self.spriteentry.get()
			self.edited = True
		if self.topspeed.get() != entry.speed:
			entry.speed = self.topspeed.get()
			self.edited = True
		if self.acceleration.get() != entry.acceleration:
			entry.acceleration = self.acceleration.get()
			self.edited = True
		if self.haltdistance.get() != entry.halt_distance:
			entry.halt_distance = self.haltdistance.get()
			self.edited = True
		if self.turnradius.get() != entry.turn_radius:
			entry.turn_radius = self.turnradius.get()
			self.edited = True
		if self.unused.get() != entry.iscript_mask:
			entry.iscript_mask = self.unused.get()
			self.edited = True
		if self.movecontrol.get() != entry.movement_control:
			entry.movement_control = self.movecontrol.get()
			self.edited = True
