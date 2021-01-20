
from DATTab import DATTab

from ..FileFormats.TBL import decompile_string
from ..Utilities.utils import couriernew
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.FloatVar import FloatVar
from ..Utilities.DropDown import DropDown
from ..Utilities.DataCache import DATA_CACHE

from Tkinter import *

class WeaponsTab(DATTab):
	data = 'Weapons.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		self.amount = IntegerVar(0, [0,65535])
		self.type = IntVar()
		self.bonus = IntegerVar(0, [0,65535])
		self.explosion = IntVar()
		self.factor = IntegerVar(0, [0,255])
		self.unused = IntVar()
		self.cooldown = IntegerVar(0, [1,255], callback=lambda n,i=0: self.updatetime(n,i))
		self.seconds = FloatVar(1, [0.06,17], callback=lambda n,i=1: self.updatetime(n,i), precision=2)
		self.upgradeentry = IntegerVar(0,[0,61])
		self.upgrade = IntVar()

		data = Frame(frame)
		left = Frame(data)
		l = LabelFrame(left, text='Damage Properties:')
		s = Frame(l)
		f = Frame(s)
		ls = Frame(f)
		Label(ls, text='Amount:', width=12, anchor=E).pack(side=LEFT)
		Entry(ls, textvariable=self.amount, font=couriernew, width=5).pack(side=LEFT, padx=2)
		self.tip(ls, 'Damage Amount', 'WeapDamageAmount')
		ls.pack(side=LEFT)
		ls = Frame(f)
		Label(ls, text='Type:', width=9, anchor=E).pack(side=LEFT)
		DropDown(ls, self.type, DATA_CACHE['DamTypes.txt'], width=20).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(ls, 'Damage Type', 'WeapDamageType')
		ls.pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		ls = Frame(f)
		Label(ls, text='Bonus:', width=12, anchor=E).pack(side=LEFT)
		Entry(ls, textvariable=self.bonus, font=couriernew, width=5).pack(side=LEFT, padx=2)
		self.tip(ls, 'Damage Bonus', 'WeapDamageBonus')
		ls.pack(side=LEFT)
		ls = Frame(f)
		Label(ls, text='Explosion:', width=9, anchor=E).pack(side=LEFT)
		DropDown(ls, self.explosion, DATA_CACHE['Explosions.txt'], width=20).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(ls, 'Explosion', 'WeapDamageExplosion')
		ls.pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		ls = Frame(f)
		Label(ls, text='Factor:', width=12, anchor=E).pack(side=LEFT)
		Entry(ls, textvariable=self.factor, font=couriernew, width=5).pack(side=LEFT, padx=2)
		self.tip(ls, 'Damage Factor', 'WeapDamageFactor')
		ls.pack(side=LEFT)
		ls = Frame(f)
		Label(ls, text='Unused:', width=9, anchor=E).pack(side=LEFT)
		DropDown(ls, self.unused, DATA_CACHE['Techdata.txt'], width=20).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(ls, 'Unused Technology', 'WeapUnused')
		ls.pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Cooldown:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.cooldown, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.seconds, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='secs.').pack(side=LEFT)
		self.tip(f, 'Cooldown', 'WeapDamageCooldown')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Upgrade:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.upgradeentry, font=couriernew, width=2).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.upgrade, DATA_CACHE['Upgrades.txt'], self.upgradeentry, width=18).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Upgrades',i=self.upgrade: self.jump(t,i)).pack(side=LEFT)
		self.tip(f, 'Damage Upgrade', 'WeapDamageUpgrade')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		stattxt = [] # ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings]
		self.labelentry = IntegerVar(0,[0,len(stattxt)-1])
		self.label = IntVar()
		self.errormsgentry = IntegerVar(0,[0,len(stattxt)-1])
		self.errormsg = IntVar()

		l = LabelFrame(left, text='Weapon Display:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Label:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.labelentry, font=couriernew, width=4).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.labels = DropDown(f, self.label, stattxt, self.labelentry, width=28)
		self.labels.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Label', 'WeapLabel')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Error Msg:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.errormsgentry, font=couriernew, width=4).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.errormsgs = DropDown(f, self.errormsg, stattxt, self.errormsgentry, width=28)
		self.errormsgs.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Error Message', 'WeapError')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.removeafter = IntegerVar(0, [0,255])
		self.behaviour = IntVar()
		self.graphicsentry = IntegerVar(0, [0,208])
		self.graphicsdd = IntVar()
		self.iconentry = IntegerVar(0, [0,389], callback=lambda n:self.selicon(n,1))
		self.icondd = IntVar()
		self.xoffset = IntegerVar(0, [0,255])
		self.yoffset = IntegerVar(0, [0,255])
		self.attackangle = IntegerVar(0, [0,255])
		self.launchspin = IntegerVar(0, [0,255])

		l = LabelFrame(left, text='Weapon Display:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Behaviour:', width=12, anchor=E).pack(side=LEFT)
		DropDown(f, self.behaviour, DATA_CACHE['Behaviours.txt'], width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Behaviour', 'WeapBehaviour')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Remove After:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.removeafter, font=couriernew, width=3).pack(side=LEFT, padx=2)
		self.tip(f, 'Remove After', 'WeapRemoveAfter')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Graphics:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.graphicsentry, font=couriernew, width=3).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.graphicsdd, DATA_CACHE['Flingy.txt'], self.graphicsentry).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Flingy',i=self.graphicsdd: self.jump(t,i)).pack(side=LEFT, padx=2)
		self.tip(f, 'Graphics', 'WeapGraphics')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Icon:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.iconentry, font=couriernew, width=3).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.icondd, DATA_CACHE['Icons.txt'], self.selicon).pack(side=LEFT, fill=X, expand=1, padx=2)
		self.tip(f, 'Icon', 'WeapIcon')
		f.pack(fill=X)
		f = Frame(s)
		ls = Frame(f)
		rs = Frame(ls)
		Label(rs, text='X Offset:', width=12, anchor=E).pack(side=LEFT)
		Entry(rs, textvariable=self.xoffset, font=couriernew, width=3).pack(side=LEFT, padx=2)
		self.tip(rs, 'X Offset', 'WeapOffsetForward')
		rs.pack(side=TOP)
		rs = Frame(ls)
		Label(rs, text='Y Offset:', width=12, anchor=E).pack(side=LEFT)
		Entry(rs, textvariable=self.yoffset, font=couriernew, width=3).pack(side=LEFT, padx=2)
		self.tip(rs, 'Y Offset', 'WeapOffsetUpward')
		rs.pack(side=TOP)
		ls.pack(side=LEFT)
		ls = Frame(f)
		rs = Frame(ls)
		Label(rs, text='Attack Angle:', width=12, anchor=E).pack(side=LEFT)
		Entry(rs, textvariable=self.attackangle, font=couriernew, width=3).pack(side=LEFT, padx=2)
		self.tip(rs, 'Attack Angle', 'WeapAttackAngle')
		rs.pack(side=TOP)
		rs = Frame(ls)
		Label(rs, text='Launch Spin:', width=12, anchor=E).pack(side=LEFT)
		Entry(rs, textvariable=self.launchspin, font=couriernew, width=3).pack(side=LEFT, padx=2)
		self.tip(rs, 'Launch Spin', 'WeapLaunchSpin')
		rs.pack(side=TOP)
		ls.pack(side=LEFT)
		ls = Frame(f, relief=SUNKEN, bd=1)
		self.preview = Canvas(ls, width=34, height=34, background='#000000')
		self.preview.pack()
		ls.pack(side=RIGHT)
		f.pack(fill=X)
		f = Frame(s)
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)
		left.pack(side=LEFT, fill=Y)

		self.minrange = IntegerVar(0, [0,4294967294])
		self.maxrange = IntegerVar(0, [0,4294967294])

		right = Frame(data)
		l = LabelFrame(right, text='Weapon Range:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Min:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.minrange, font=couriernew, width=10).pack(side=LEFT, padx=2)
		self.tip(f, 'Minimum Range', 'WeapRangeMin')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Max:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.maxrange, font=couriernew, width=10).pack(side=LEFT, padx=2)
		self.tip(f, 'Maximum Range', 'WeapRangeMax')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack()

		self.innerradius = IntegerVar(0, [0,65535])
		self.mediumradius = IntegerVar(0, [0,65535])
		self.outerradius = IntegerVar(0, [0,65535])

		l = LabelFrame(right, text='Splash Radii:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Inner:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.innerradius, font=couriernew, width=5).pack(side=LEFT, padx=2)
		self.tip(f, 'Inner Radius', 'WeapSplashInner')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Medium:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.mediumradius, font=couriernew, width=5).pack(side=LEFT, padx=2)
		self.tip(f, 'Medium Radius', 'WeapSplashMed')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Outer:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.outerradius, font=couriernew, width=5).pack(side=LEFT, padx=2)
		self.tip(f, 'Outer Radius', 'WeapSplashOuter')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.air = IntVar()
		self.ground = IntVar()
		self.mechanical = IntVar()
		self.organic = IntVar()
		self.nonbuilding = IntVar()
		self.nonrobotic = IntVar()
		self.terrain = IntVar()
		self.orgormech = IntVar()
		self.own = IntVar()

		l = LabelFrame(right, text='Target Flags:')
		s = Frame(l)
		flags = [
			('Air', self.air, '001'),
			('Ground', self.ground, '002'),
			('Mechanical', self.mechanical, '004'),
			('Organic', self.organic, '008'),
			('Non-Building', self.nonbuilding, '010'),
			('Non-Robotic', self.nonrobotic, '020'),
			('Terrain', self.terrain, '040'),
			('Org. or Mech.', self.orgormech, '080'),
			('Own', self.own, '100'),
		]
		for t,v,h in flags:
			f = Frame(s)
			Checkbutton(f, text=t, variable=v).pack(side=LEFT)
			self.tip(f, t, 'WeapTarget' + h)
			f.pack(side=TOP, fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=BOTH)
		right.pack(side=LEFT)
		data.pack(pady=5)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('units.dat', ['GroundWeapon','AirWeapon']),
			('orders.dat', ['Targeting']),
		]
		self.setuplistbox()

		self.values = {
			'Label':self.label,
			'Graphics':self.graphicsentry,
			'Unused':self.unused,
			'TargetFlags':[self.air, self.ground, self.mechanical, self.organic, self.nonbuilding, self.nonrobotic, self.terrain, self.orgormech, self.own],
			'MinimumRange':self.minrange,
			'MaximumRange':self.maxrange,
			'DamageUpgrade':self.upgrade,
			'WeaponType':self.type,
			'WeaponBehavior':self.behaviour,
			'RemoveAfter':self.removeafter,
			'ExplosionType':self.explosion,
			'InnerSplashRange':self.innerradius,
			'MediumSplashRange':self.mediumradius,
			'OuterSplashRange':self.outerradius,
			'DamageAmount':self.amount,
			'DamageBonus':self.bonus,
			'WeaponCooldown':self.cooldown,
			'DamageFactor':self.factor,
			'AttackAngle':self.attackangle,
			'LaunchSpin':self.launchspin,
			'ForwardOffset':self.xoffset,
			'UpwardOffset':self.yoffset,
			'TargetErrorMessage':self.errormsg,
			'Icon':self.iconentry
		}

	def files_updated(self):
		self.dat = self.toplevel.weapons
		stattxt = ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings]
		self.labelentry.range[1] = len(stattxt)-1
		self.labels.setentries(stattxt)
		self.labelentry.editvalue()
		self.errormsgentry.range[1] = len(stattxt)-1
		self.errormsgs.setentries(stattxt)
		self.errormsgentry.editvalue()

	def updatetime(self, num, type):
		if type:
			self.cooldown.check = False
			self.cooldown.set(int(float(num) * 15))
		else:
			self.seconds.check = False
			s = str(int(num) / 15.0)
			if s.endswith('.0'):
				s = s[:-2]
			elif len(s.split('.')[1]) > 2:
				s = s[:s.index('.')+3]
			self.seconds.set(s)

	def selicon(self, n, t=0):
		if t:
			self.icondd.set(n)
		else:
			self.iconentry.set(n)
		self.drawpreview()

	def drawpreview(self):
		self.preview.delete(ALL)
		if 'Icons' in PALETTES and self.toplevel.cmdicon:
			i = self.iconentry.get()
			if not i in ICON_CACHE:
				image = frame_to_photo(PALETTES['Icons'], self.toplevel.cmdicon, i, True)
				ICON_CACHE[i] = image
			else:
				image = ICON_CACHE[i]
			self.preview.create_image(19-image[1]/2+(image[0].width()-image[2])/2, 19-image[3]/2+(image[0].height()-image[4])/2, image=image[0])

	def load_data(self, id=None):
		DATTab.load_data(self, id)
		if 'Icons' in PALETTES and self.toplevel.cmdicon:
			self.drawpreview()
