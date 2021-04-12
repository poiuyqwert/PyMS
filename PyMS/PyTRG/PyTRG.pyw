from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs import TRG,TBL,AIBIN
from Libs.analytics import *
# def customs(trg):
	# trg.dynamic_actions[1] = ['MySetLocationTo',[TRG.new_location,TRG.new_x1,TRG.new_y1,TRG.new_x2,TRG.new_y2,TRG.new_flags,TRG.new_properties]]
	# trg.dynamic_actions[2] = ['MySetLocationFromDeaths',[TRG.new_location,TRG.action_tunit]]
	# trg.dynamic_actions[3] = ['MyRemoveUnit',[TRG.action_player,TRG.action_tunit,TRG.action_location]]
	# trg.dynamic_actions[255] = ['StickUnit',[]]
# TRG.REGISTER.append(customs)

from Tkinter import *
from tkMessageBox import *
import tkFileDialog,tkColorChooser

from thread import start_new_thread
import optparse, os, webbrowser, sys

LONG_VERSION = 'v%s' % VERSIONS['PyTRG']

CONDITIONS_HELP = {
	'NoCondition':'No condition.',
	'CountdownTimer':'Countdown timer is Comparison(1) Number(1) game seconds.',
	'Command':'Player(1) commands Comparison(1) Number(1) TUnit(1).',
	'Bring':'Player(1) brings Comparison(1) Number(1) TUnit(1) to Location(1).',
	'Accumulate':'Player(1) accumulates Comparison(1) Number(1) ResType(1).',
	'Kill':'Player(1) kills Comparison(1) Number(1) TUnit(1).',
	'CommandTheMost':'Current player commands the most TUnit(1).',
	'CommandsTheMostAt':'Current player commands the most TUnit(1) at Location(1).',
	'MostKills':'Current player has most kills of TUnit(1).',
	'HighestScore':'Current player has highest ScoreType(1).',
	'MostResources':'Current player has most ResType(1).',
	'Switch':'Switch(1) is Set(1).',
	'ElapsedTime':'Elapsed scenario time is Comparison(1) Number(1) game seconds.',
	'Opponents':'Player(1) has Comparison(1) Number(1) opponents remaining in the game.',
	'Deaths':'Player(1) has suffered Comparison(1) Number(1) deaths of TUnit(1).',
	'CommandTheLeast':'Current player commands the least TUnit(1).',
	'CommandTheLeastAt':'Current player commands the least TUnit(1) at Location(1).',
	'LeastKills':'Current player has least kills of TUnit(1).',
	'LowestScore':'Current player has lowest ScoreType(1).',
	'LeastResources':'Current player has least ResType(1).',
	'Score':'Player(1) ScoreType(1) score is Comparison(1) Number(1).',
	'Always':'Always.',
	'Never':'Never.',
}
ACTIONS_HELP = {
	'NoAction':'No action',
	'Victory':'End scenario in victory for current player.',
	'Defeat':'End scenario in defeat for current player.',
	'PreserveTrigger':'Preserve trigger.',
	'Wait':'Wait for Number(1) milliseconds.',
	'PauseGame':'Pause the game.',
	'UnpauseGame':'Unpause the game.',
	'Transmission':'Send transmission to current player from Unit(1) at Location(1). Play WAV(1). Modify transmission duration: Modifier(1) Number(1) milliseconds. Display String(1).',
	'PlayWAV':'Player WAV(1).',
	'DisplayTextMessage':'Display(1) String(1) for current player.',
	'CenterView':'Center view for current player at Location(1).',
	'CreateUnitWithProperties':'Create Number(1) Unit(1) at Location(1) for Player(1). Apply Property(1).',
	'SetMissionObjectives':'Set mission objectives to String(1).',
	'SetSwitch':'SwitchAction(1) Switch(1.)',
	'SetCountdownTimer':'Modify countdown timer: Modifier(1) Number(1) seconds.',
	'RunAIScript':'Execute AI Script AIScript(1).',
	'RunAIScriptAtLocation':'Execute AI Script AIScript(1) at Location(1).',
	'LeaderBoardControl':'Show Leader Board for most control of TUnit(1). Display label String(1).',
	'LeaderBoardControlAtLocation':'Show Leader Board for most control of TUnit(1) at Location(1). Display label String(1).',
	'LeaderBoardResources':'Show Leader Board for accumulation of most ResType(1). Display label String(1).',
	'LeaderBoardKills':'Show Leader Board for player closest to Number(1) kills of TUnit(1). Display label String(1).',
	'LeaderBoardPoints':'Show Leader Board for player closest to Number(1) of ScoreType(1). Display label String(1).',
	'KillUnit':'Kill all TUnit(1) for Player(1).',
	'KillUnitsAtLocation':'Kill QNumber(1) TUnit(1) for Player(1) at Location(1).',
	'RemoveUnit':'Remove all TUnit(1) for Player(1).',
	'RemoveUnitAtLocation':'Remove QNumber(1) TUnit(1) for Player(1) at Location(1).',
	'SetResources':'Modify resources for Player(1): Modifier(1) Number(1) of ResType(1).',
	'SetScore':'Modify score for Player(1): Modifier(1) Number(1) of ScoreType(1).',
	'MinimapPing':'Show minimap ping for current player at Location(1).',
	'TalkingPortrait':'Show Unit(1) talking to current player for Number(1) milliseconds.',
	'MuteUnitSpeech':'Mute all non-trigger unit sounds for current player.',
	'UnmuteUnitSpeech':'Unmute all non-trigger unit sounds for current player.',
	'LeaderboardComputerPlayers':'Set use of computer players in leaderboard calculations to State(1).',
	'LeaderboardGoalControl':'Show Leader Board for player closest to control of Number(1) of TUnit(1). Display label String(1).',
	'LeaderboardGoalControlAtLocation':'Show Leader Board for player closest to control of Number(1) of TUnit(1) at Location(1). Display label String(1).',
	'LeaderboardGoalResources':'Show Leader Board for player closest to accumulation of Number(1) ResType(1). Display label String(1)',
	'LeaderboardGoalKills':'Show Leader Board for player closest to Number(1) kills of TUnit(1). Display label String(1).',
	'LeaderboardGoalPoints':'Show Leader Board for player closest to Number(1) of ScoreType(1). Display label String(1).',
	'MoveLocation':'Center location DestLocation(1) on TUnit(1) owned by Player(1) at Location(1).',
	'MoveUnit':'Move QNumber(1) Unit(1) for Player(1) at Location(1) to DestLocation(1).',
	'LeaderboardGreed':'Show Greed Leader Board for player closest to accumulation of Number(1) ore and gas.',
	'SetNextScenario':'Load scenario String(1) after completion of current game.',
	'SetDoodadState':'Set doodad state for Unit(1) for Player(1) at Location(1) to State(1).',
	'SetInvincibility':'Set invincibility for Unit(1) owned by Player(1) at Location(1) to State(1).',
	'CreateUnit':'Create Number(1) Unit(1) at Location(1) for Player(1).',
	'SetDeaths':'Modify death counts for Player(1): Modifier(1) Number(1) for Unit(1).',
	'Order':'Issue order to all TUnit(1) owned by Player(1) at Location(1): Order(1) to DestLocation(1).',
	'Comment':'Comment: String(1).',
	'GiveUnitstoPlayer':'Give QNumber(1) TUnit(1) owned by Player(1) at Location(1) to DestPlayer(1).',
	'ModifyUnitHitPoints':'Set hit points for QNumber(1) TUnit(1) owned by Player(1) at Location(1) to Percentage(1).',
	'ModifyUnitEnergy':'Set energy points for QNumber(1) TUnit(1) owned by Player(1) at Location(1) to Percentage(1).',
	'ModifyUnitShieldPoints':'Set shield points for QNumber(1) Unit(1) owned by Player(1) at Location(1) to Percentage(1)',
	'ModifyUnitResourceAmount':'Set resource amount for QNumber(1) resource sources owned by Player(1) at Location(1) to Number(1).',
	'ModifyUnitHangerCount':'Add at most Number(1) to hangar for QNumber(1) TUnit(1) at Location(1) owned by Player(1).',
	'PauseTimer':'Pause the countdown timer.',
	'UnpauseTimer':'Unpause the countdown timer.',
	'Draw':'End the scenario in a draw for all players.',
	'SetAllianceStatus':'Set Player(1) to AllyStatus(1).',
	'DisableDebugMode':'Disable debug mode (does nothing?).',
	'EnableDebugMode':'Enable debug mode (does nothing?).',
}
NEW_ACTIONS_HELP = {
	'SetMemoryLocation':'Modify MemoryLocation(1): Modifier(1) NewValue(1).',
	'SetDuoMemoryLocation':'Modify MemoryLocationEnd(1): Modifier(1) MemoryLocation(1)',
	'SetLocationTo':'Modify LocationProps(1) for Location(1): Top left corner to (NewX1,NewY1) and top right corner to (NewX2,NewY2) and elevations LocationFlags(1).',
	'SetLocationFromDeath':'Modifier(1) LocationProps(1) for Location(1) from deaths of Unit(1) owned by Player(1).',
	'DCMath':'Do Math(1) to death count of DestUnit(1) owned by DestPlayer(1) with death count of Unit(1) owned by Player(1).',
	'DisplayStatTxtString':'Display stat_txt.tbl string StringID(1).',
	'SetGameSpeed':'Set game speed to Speed(1) Multiplier(1).',
	'SetSupplyValue':'Modify SupplyType(1) for Player(1): Modifier(1) NewValue(1).',
	'SendUnitOrder':'Modify order of TUnit(1) owned by Player(1) in Location(1) to OrderID(1).',
	'SetUnitTargetToUnit':'Modify order target of TUnit(1) owned by Player(1) in Location(1) to TUnitEnd(1) owned by PlayerEnd(1) in EndLocation(1).',
	'SetUnitTargetToLocation':'Modify order target of TUnit(1) owned by Player(1) in Location(1) to EndLocation(1).',
	'SetUnitTargetToCoords':'Modify order target of TUnit(1) owned by Player(1) in Location(1) to (NewX,NewY).',
	'SetUnitHP':'Modify hit points of TUnit(1) owned by Player(1) in Location(1): Modifier(1) Number(1)',
	'SetUnitShields':'Modify shield points of TUnit(1) owned by Player(1) in Location(1): Modifier(1) Number(1)',
	'SetPlayerVision':'Set Player(1) vision of PlayerEnd(1) to Vision(1)',
}

class Decompile:
	def __init__(self):
		self.text = ''

	def write(self, text):
		self.text += text

	def close(self):
		pass

class CodeTooltip(Tooltip):
	tag = ''

	def setupbinds(self, press):
		if self.tag:
			self.widget.tag_bind(self.tag, '<Enter>', self.enter, '+')
			self.widget.tag_bind(self.tag, '<Leave>', self.leave, '+')
			self.widget.tag_bind(self.tag, '<Motion>', self.motion, '+')
			self.widget.tag_bind(self.tag, '<Button-1>', self.leave, '+')
			self.widget.tag_bind(self.tag, '<ButtonPress>', self.leave)

	def showtip(self):
		if self.tip:
			return
		t = ''
		if self.tag:
			pos = list(self.widget.winfo_pointerxy())
			head,tail = self.widget.tag_prevrange(self.tag,self.widget.index('@%s,%s+1c' % (pos[0] - self.widget.winfo_rootx(),pos[1] - self.widget.winfo_rooty())))
			t = self.widget.get(head,tail)
		try:
			t = self.gettext(t)
			self.tip = Toplevel(self.widget, relief=SOLID, borderwidth=1)
			self.tip.wm_overrideredirect(1)
			frame = Frame(self.tip, background='#FFFFC8', borderwidth=0)
			Label(frame, text=t, justify=LEFT, font=self.font, background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1)
			frame.pack()
			pos = list(self.widget.winfo_pointerxy())
			self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
			self.tip.update_idletasks()
			move = False
			if pos[0] + self.tip.winfo_reqwidth() > self.tip.winfo_screenwidth():
				move = True
				pos[0] = self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth()
			if pos[1] + self.tip.winfo_reqheight() + 22 > self.tip.winfo_screenheight():
				move = True
				pos[1] -= self.tip.winfo_reqheight() + 44
			if move:
				self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
		except:
			if self.tip:
				try:
					self.tip.destroy()
				except:
					pass
				self.tip = None
			return

	def gettext(self, t):
		# Overload to specify tooltip text
		return ''

class ConditionsTooltip(CodeTooltip):
	tag = 'Conditions'

	def gettext(self, condition):
		text = 'Condition:\n  %s(' % condition
		if condition == 'RawCond':
			text += """Long, Long, Long, Short, Byte, Byte, Byte, Byte)
    Create a condition from raw values

  Long: Any number in the range 0 to 4294967295
  Short: Any number in the range 0 to 65535
  Byte: Any number in the range 0 to 255"""
			return text
		params = self.widget.toplevel.trg.condition_parameters[self.widget.toplevel.trg.conditions.index(condition)]
		pinfo = ''
		if params:
			pinfo = '\n\n'
			done = []
			for p in params:
				t = p.__doc__.split(' ',1)[0]
				text += t + ', '
				if not t in done:
					pinfo += fit('  %s: ' % t, TRG.TYPE_HELP[t], end=True, indent=4)
					done.append(t)
			text = text[:-2]
		text += ')'
		return text + '\n' + fit('    ', CONDITIONS_HELP[condition], end=True)[:-1] + pinfo[:-1]

class ActionsTooltip(CodeTooltip):
	tag = 'Actions'

	def gettext(self, action):
		text = 'Action:\n  %s(' % action
		if action == 'RawAct':
			text += """Long, Long, Long, Long, Long, Long, Short, Byte, Byte)
    Create an action from raw values

  Long: Any number in the range 0 to 4294967295
  Short: Any number in the range 0 to 65535
  Byte: Any number in the range 0 to 255"""
			return text
		params = self.widget.toplevel.trg.action_parameters[self.widget.toplevel.trg.actions.index(action)]
		pinfo = ''
		if params:
			pinfo = '\n\n'
			done = []
			for p in params:
				t = p.__doc__.split(' ',1)[0]
				text += t + ', '
				if not t in done:
					pinfo += fit('  %s: ' % t, TRG.TYPE_HELP[t], end=True, indent=4)
					done.append(t)
			text = text[:-2]
		return text + ')\n' + fit('    ', ACTIONS_HELP[action], end=True)[:-1] + pinfo[:-1]

class TrigPlugActionsTooltip(CodeTooltip):
	tag = 'TrigPlugActions'

	def gettext(self, action):
		text = 'TrigPlug Action:\n  %s(' % action
		params = self.widget.toplevel.trg.new_action_parameters[self.widget.toplevel.trg.new_actions.index(action)]
		pinfo = ''
		if params:
			pinfo = '\n\n'
			done = []
			for p in params:
				t = p.__doc__.split(' ',1)[0]
				text += t + ', '
				if not t in done:
					pinfo += fit('  %s: ' % t, TRG.TYPE_HELP[t], end=True, indent=4)
					done.append(t)
			text = text[:-2]
		text += ')'
		return text + '\n' + fit('    ', NEW_ACTIONS_HELP[action], end=True)[:-1] + pinfo[:-1]

class FindReplaceDialog(PyMSDialog):
	def __init__(self, parent):
		self.resettimer = None
		PyMSDialog.__init__(self, parent, 'Find/Replace', grabwait=False, resizable=(True, False))

	def widgetize(self):
		self.find = StringVar()
		self.replacewith = StringVar()
		self.replace = IntVar()
		self.inselection = IntVar()
		self.casesens = IntVar()
		self.regex = IntVar()
		self.multiline = IntVar()
		self.updown = IntVar()
		self.updown.set(1)

		l = Frame(self)
		f = Frame(l)
		s = Frame(f)
		Label(s, text='Find:', anchor=E, width=12).pack(side=LEFT)
		self.findentry = TextDropDown(s, self.find, self.parent.findhistory, 30)
		self.findentry.c = self.findentry['bg']
		self.findentry.pack(fill=X)
		self.findentry.entry.selection_range(0, END)
		self.findentry.focus_set()
		s.pack(fill=X)
		s = Frame(f)
		Label(s, text='Replace With:', anchor=E, width=12).pack(side=LEFT)
		self.replaceentry = TextDropDown(s, self.replacewith, self.parent.replacehistory, 30)
		self.replaceentry.pack(fill=X)
		s.pack(fill=X)
		f.pack(side=TOP, fill=X, pady=2)
		f = Frame(l)
		self.selectcheck = Checkbutton(f, text='In Selection', variable=self.inselection, anchor=W)
		self.selectcheck.pack(fill=X)
		Checkbutton(f, text='Case Sensitive', variable=self.casesens, anchor=W).pack(fill=X)
		Checkbutton(f, text='Regular Expression', variable=self.regex, anchor=W, command=lambda i=1: self.check(i)).pack(fill=X)
		self.multicheck = Checkbutton(f, text='Multi-Line', variable=self.multiline, anchor=W, state=DISABLED, command=lambda i=2: self.check(i))
		self.multicheck.pack(fill=X)
		f.pack(side=LEFT, fill=BOTH)
		f = Frame(l)
		lf = LabelFrame(f, text='Direction')
		self.up = Radiobutton(lf, text='Up', variable=self.updown, value=0, anchor=W)
		self.up.pack(fill=X)
		self.down = Radiobutton(lf, text='Down', variable=self.updown, value=1, anchor=W)
		self.down.pack()
		lf.pack()
		f.pack(side=RIGHT, fill=Y)
		l.pack(side=LEFT, fill=BOTH, pady=2, expand=1)

		l = Frame(self)
		Button(l, text='Find Next', command=self.findnext, default=NORMAL).pack(fill=X, pady=1)
		Button(l, text='Count', command=self.count).pack(fill=X, pady=1)
		self.replacebtn = Button(l, text='Replace', command=lambda i=1: self.findnext(replace=i))
		self.replacebtn.pack(fill=X, pady=1)
		self.repallbtn = Button(l, text='Replace All', command=self.replaceall)
		self.repallbtn.pack(fill=X, pady=1)
		Button(l, text='Close', command=self.ok).pack(fill=X, pady=4)
		l.pack(side=LEFT, fill=Y, padx=2)

		self.bind('<Return>', self.findnext)

		self.bind('<FocusIn>', lambda e,i=3: self.check(i))

		if 'findreplacewindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'findreplacewindow')

		return self.findentry

	def check(self, i):
		if i == 1:
			if self.regex.get():
				self.multicheck['state'] = NORMAL
			else:
				self.multicheck['state'] = DISABLED
				self.multiline.set(0)
		if i in [1,2]:
			s = [NORMAL,DISABLED][self.multiline.get()]
			self.up['state'] = s
			self.down['state'] = s
			if s == DISABLED:
				self.updown.set(1)
		elif i == 3:
			if self.parent.text.tag_ranges('Selection'):
				self.selectcheck['state'] = NORMAL
			else:
				self.selectcheck['state'] = DISABLED
				self.inselection.set(0)

	def findnext(self, key=None, replace=0):
		f = self.find.get()
		if not f in self.parent.findhistory:
			self.parent.findhistory.append(f)
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			if replace:
				rep = self.replacewith.get()
				if not rep in self.parent.replacehistory:
					self.parent.replacehistory.append(rep)
				item = self.parent.text.tag_ranges('Selection')
				if item and r.match(self.parent.text.get(*item)):
					ins = r.sub(rep, self.parent.text.get(*item))
					self.parent.text.delete(*item)
					self.parent.text.insert(item[0], ins)
					self.parent.text.update_range(item[0])
			if self.multiline.get():
				m = r.search(self.parent.text.get(INSERT, END))
				if m:
					self.parent.text.tag_remove('Selection', '1.0', END)
					s,e = '%s +%sc' % (INSERT, m.start(0)),'%s +%sc' % (INSERT,m.end(0))
					self.parent.text.tag_add('Selection', s, e)
					self.parent.text.mark_set(INSERT, e)
					self.parent.text.see(s)
					self.check(3)
				else:
					p = self
					if key and key.keycode == 13:
						p = self.parent
					askquestion(parent=p, title='Find', message="Can't find text.", type=OK)
			else:
				u = self.updown.get()
				s,lse,rlse,e = ['-','+'][u],['lineend','linestart'][u],['linestart','lineend'][u],[self.parent.text.index('1.0 lineend'),self.parent.text.index(END)][u]
				i = self.parent.text.index(INSERT)
				if i == e:
					return
				if i == self.parent.text.index('%s %s' % (INSERT, rlse)):
					i = self.parent.text.index('%s %s1lines %s' % (INSERT, s, lse))
				n = -1
				while not u or i != e:
					if u:
						m = r.search(self.parent.text.get(i, '%s %s' % (i, rlse)))
					else:
						m = None
						a = r.finditer(self.parent.text.get('%s %s' % (i, rlse), i))
						c = 0
						for x,f in enumerate(a):
							if x == n or n == -1:
								m = f
								c = x
						n = c - 1
					if m:
						self.parent.text.tag_remove('Selection', '1.0', END)
						if u:
							s,e = '%s +%sc' % (i,m.start(0)),'%s +%sc' % (i,m.end(0))
							self.parent.text.mark_set(INSERT, e)
						else:
							s,e = '%s linestart +%sc' % (i,m.start(0)),'%s linestart +%sc' % (i,m.end(0))
							self.parent.text.mark_set(INSERT, s)
						self.parent.text.tag_add('Selection', s, e)
						self.parent.text.see(s)
						self.check(3)
						break
					if (not u and n == -1 and self.parent.text.index('%s lineend' % i) == e) or i == e:
						p = self
						if key and key.keycode == 13:
							p = self.parent
						askquestion(parent=p, title='Find', message="Can't find text.", type=OK)
						break
					i = self.parent.text.index('%s %s1lines %s' % (i, s, lse))
				else:
					p = self
					if key and key.keycode == 13:
						p = self.parent
					askquestion(parent=p, title='Find', message="Can't find text.", type=OK)

	def count(self):
		f = self.find.get()
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			askquestion(parent=self, title='Count', message='%s matches found.' % len(r.findall(self.parent.text.get('1.0', END))), type=OK)

	def replaceall(self):
		f = self.find.get()
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			text = r.subn(self.replacewith.get(), self.parent.text.get('1.0', END))
			if text[1]:
				self.parent.text.delete('1.0', END)
				self.parent.text.insert('1.0', text[0].rstrip('\n'))
				self.parent.text.update_range('1.0')
			askquestion(parent=self, title='Replace Complete', message='%s matches replaced.' % text[1], type=OK)

	def updatecolor(self):
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry.c

	def destroy(self):
		self.parent.settings['findreplacewindow'] = self.winfo_geometry()
		PyMSDialog.withdraw(self)

class CodeColors(PyMSDialog):
	def __init__(self, parent):
		self.cont = False
		self.tags = dict(parent.text.tags)
		self.info = odict()
		self.info['Comment'] = 'The color of a comment.'
		self.info['Headers'] = 'The color of any header.'
		self.info['Conditions'] = 'All Condition names'
		self.info['Actions'] = 'All Action names'
		self.info['TrigPlug Actions'] = 'All TrigPlug Action names'
		self.info['Dynamic Conditions'] = 'All the names of the Conditions created by plugins'
		self.info['Dynamic Actions'] = 'All the names of the Actions created by plugins'
		self.info['Constants'] = ['The color of constants.','ConstDef']
		self.info['Keywords'] = 'All keywords'
		self.info['Number'] = 'The color of all numbers.'
		self.info['TBL Format'] = 'The color of TBL formatted characters, like null: <0>'
		self.info['Operators'] = 'The color of the operators:\n    ( ) , :'
		self.info['Error'] = 'The color of an error when testing.'
		self.info['Warning'] = 'The color of a warning when testing.'
		self.info['Selection'] = 'The color of selected text in the editor.'
		PyMSDialog.__init__(self, parent, 'Color Settings', resizable=(False, False))

	def widgetize(self):
		self.listbox = Listbox(self, font=couriernew, width=20, height=16, exportselection=0, activestyle=DOTBOX)
		self.listbox.bind('<ButtonRelease-1>', self.select)
		for t in self.info.keys():
			if isinstance(t, list):
				self.listbox.insert(END, t[0])
			else:
				self.listbox.insert(END, t)
		self.listbox.select_set(0)
		self.listbox.pack(side=LEFT, fill=Y, padx=2, pady=2)

		self.fg = IntVar()
		self.bg = IntVar()
		self.bold = IntVar()
		self.infotext = StringVar()

		r = Frame(self)
		opt = LabelFrame(r, text='Style:', padx=5, pady=5)
		f = Frame(opt)
		c = Checkbutton(f, text='Foreground', variable=self.fg, width=20, anchor=W)
		c.bind('<ButtonRelease-1>', lambda e,i=0: self.select(e,i))
		c.grid(sticky=W)
		c = Checkbutton(f, text='Background', variable=self.bg)
		c.bind('<ButtonRelease-1>', lambda e,i=1: self.select(e,i))
		c.grid(sticky=W)
		c = Checkbutton(f, text='Bold', variable=self.bold)
		c.bind('<ButtonRelease-1>', lambda e,i=2: self.select(e,i))
		c.grid(sticky=W)
		self.fgcanvas = Canvas(f, width=32, height=32, background='#000000')
		self.fgcanvas.bind('<Button-1>', lambda e,i=0: self.colorselect(e, i))
		self.fgcanvas.grid(column=1, row=0)
		self.bgcanvas = Canvas(f, width=32, height=32, background='#000000')
		self.bgcanvas.bind('<Button-1>', lambda e,i=1: self.colorselect(e, i))
		self.bgcanvas.grid(column=1, row=1)
		f.pack(side=TOP)
		Label(opt, textvariable=self.infotext, height=6, justify=LEFT).pack(side=BOTTOM, fill=X)
		opt.pack(side=TOP, fill=Y, expand=1, padx=2, pady=2)
		f = Frame(r)
		ok = Button(f, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3)
		Button(f, text='Cancel', width=10, command=self.cancel).pack(side=LEFT)
		f.pack(side=BOTTOM, pady=2)
		r.pack(side=LEFT, fill=Y)

		self.select()

		return ok

	def select(self, e=None, n=None):
		i = self.info.getkey(int(self.listbox.curselection()[0]))
		s = self.tags[i.replace(' ', '')]
		if n == None:
			if isinstance(self.info[i], list):
				t = self.info[i][0].split('\n')
			else:
				t = self.info[i].split('\n')
			text = ''
			if len(t) == 2:
				d = '  '
				text = t[0] + '\n'
			else:
				d = ''
			text += fit(d, t[-1], 35, True)[:-1]
			self.infotext.set(text)
			if s['foreground'] == None:
				self.fg.set(0)
				self.fgcanvas['background'] = '#000000'
			else:
				self.fg.set(1)
				self.fgcanvas['background'] = s['foreground']
			if s['background'] == None:
				self.bg.set(0)
				self.bgcanvas['background'] = '#000000'
			else:
				self.bg.set(1)
				self.bgcanvas['background'] = s['background']
			self.bold.set(s['font'] != None)
		else:
			v = [self.fg,self.bg,self.bold][n].get()
			if n == 2:
				s['font'] = [self.parent.text.boldfont,couriernew][v]
			else:
				s[['foreground','background'][n]] = ['#000000',None][v]
				if v:
					[self.fgcanvas,self.bgcanvas][n]['background'] = '#000000'

	def colorselect(self, e, i):
		if [self.fg,self.bg][i].get():
			v = [self.fgcanvas,self.bgcanvas][i]
			g = ['foreground','background'][i]
			c = tkColorChooser.askcolor(parent=self, initialcolor=v['background'], title='Select %s color' % g)
			if c[1]:
				v['background'] = c[1]
				k = self.info.getkey(int(self.listbox.curselection()[0])).replace(' ','')
				self.tags[k][g] = c[1]
				if isinstance(self.info[k], list):
					self.tags[self.info[k][1]][g] = c[1]
			self.focus_set()

	def ok(self):
		self.cont = self.tags
		PyMSDialog.ok(self)

	def cancel(self):
		self.cont = False
		PyMSDialog.ok(self)

class TRGCodeText(CodeText):
	def __init__(self, parent, ecallback=None, highlights=None, state=NORMAL):
		self.toplevel = parent
		self.boldfont = ('Courier New', -11, 'bold')
		self.re = None
		if highlights:
			self.highlights = highlights
		else:
			self.highlights = {
				'Comment':{'foreground':'#008000','background':None,'font':None},
				'Headers':{'foreground':'#FF00FF','background':None,'font':self.boldfont},
				'Conditions':{'foreground':'#000000','background':'#EBEBEB','font':None},
				'Actions':{'foreground':'#000000','background':'#E1E1E1','font':None},
				#'TrigPlugConditions':{'foreground':'#000000','background':'#EBEBFF','font':None},
				'TrigPlugActions':{'foreground':'#000000','background':'#E1E1FF','font':None},
				'DynamicConditions':{'foreground':'#000000','background':'#FFEBEB','font':None},
				'DynamicActions':{'foreground':'#000000','background':'#FFE1E1','font':None},
				'Constants':{'foreground':'#FF963C','background':None,'font':None},
				'ConstDef':{'foreground':'#FF963C','background':None,'font':None},
				'Keywords':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Number':{'foreground':'#FF0000','background':None,'font':None},
				'TBLFormat':{'foreground':None,'background':'#E6E6E6','font':None},
				'Operators':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Newline':{'foreground':None,'background':None,'font':None},
				'Error':{'foreground':None,'background':'#FF8C8C','font':None},
				'Warning':{'foreground':None,'background':'#FFC8C8','font':None},
			}
		CodeText.__init__(self, parent, ecallback, state=state)

	def setedit(self):
		if self.ecallback != None:
			self.ecallback()
		self.edited = True

	def setupparser(self):
		comment = '(?P<Comment>#[^\\n]*$)'
		header = '^[ \\t]*(?P<Headers>Trigger(?=\\([^\\n]+\\):)|Conditions(?=(?: \\w+)?:)|Actions(?=(?: \\w+)?:)|Constant(?= \\w+:)|String(?= \\d+:)|Property(?= \\d+:))'
		conditions = '\\b(?P<Conditions>%s)\\b' % '|'.join([x for x in TRG.TRG.conditions if x != None])
		actions = '\\b(?P<Actions>%s)\\b' % '|'.join([x for x in TRG.TRG.actions if x != None])
		#trigplugconditions = '\\b(?P<TrigPlugConditions>%s)\\b' % '|'.join([x for x in AIBIN.AIBIN.short_labels if x != None])
		trigplugactions = '\\b(?P<TrigPlugActions>%s)\\b' % '|'.join([x for x in TRG.TRG.new_actions if x != None])
		constants = '(?P<Constants>\\{\\w+\\})'
		constdef = '(?<=Constant )(?P<ConstDef>\\w+)(?=:)'
		keywords = '\\b(?P<Keywords>%s)(?=[ \\),])' % '|'.join(TRG.keywords)
		tblformat = '(?P<TBLFormat><0*(?:25[0-5]|2[0-4]\d|1?\d?\d)?>)'
		num = '\\b(?P<Number>\\d+|x(?:2|4|8|16|32)|0x[0-9a-fA-F]+)\\b'
		operators = '(?P<Operators>[():,\\-])'
		self.basic = '|'.join((comment, header, keywords, conditions, actions, trigplugactions, constants, constdef, tblformat, num, operators))
		self.tooltips = [ConditionsTooltip(self),ActionsTooltip(self),TrigPlugActionsTooltip(self)]
		self.tags = dict(self.highlights)

	def dynamic(self):
		dyn = '|'
		if self.toplevel.trg:
			if self.toplevel.trg.dynamic_conditions:
				dyn += '\\b(?P<DynamicConditions>%s)\\b|' % '|'.join([n[0] for n in self.toplevel.trg.dynamic_conditions.values()])
			if self.toplevel.trg.dynamic_actions:
				dyn += '\\b(?P<DynamicActions>%s)\\b|' % '|'.join([n[0] for n in self.toplevel.trg.dynamic_actions.values()])
		self.re = re.compile(''.join((self.basic,dyn,'(?P<Newline>\\n)')), re.M)

	def colorize(self):
		if not self.re:
			self.dynamic()
		next = '1.0'
		while True:
			item = self.tag_nextrange("Update", next)
			if not item:
				break
			head, tail = item
			self.tag_remove('Newline', head, tail)
			item = self.tag_prevrange('Newline', head)
			if item:
				head = item[1] + ' linestart'
			else:
				head = "1.0"
			chars = ""
			next = head
			lines_to_get = 1
			ok = False
			while not ok:
				mark = next
				next = self.index(mark + '+%d lines linestart' % lines_to_get)
				lines_to_get = min(lines_to_get * 2, 100)
				ok = 'Newline' in self.tag_names(next + '-1c')
				line = self.get(mark, next)
				if not line:
					return
				for tag in self.tags.keys():
					if tag != 'Selection':
						self.tag_remove(tag, mark, next)
				chars = chars + line
				m = self.re.search(chars)
				while m:
					for key, value in m.groupdict().items():
						if value != None:
							a, b = m.span(key)
							self.tag_add(key, head + '+%dc' % a, head + '+%dc' % b)
					m = self.re.search(chars, m.end())
				if 'Newline' in self.tag_names(next + '-1c'):
					head = next
					chars = ''
				else:
					ok = False
				if not ok:
					self.tag_add('Update', next)
				self.update()
				if not self.coloring:
					return

class PyTRG(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyTRG',
			{
				'stat_txt':'MPQ:rez\\stat_txt.tbl',
				'aiscript':'MPQ:scripts\\aiscript.bin',
			}
		)
		# Remove later (currently 2.5)
		if 'tblbinwindow' in self.settings:
			del self.settings['tblbinwindow']

		#Window
		Tk.__init__(self)
		self.title('PyTRG %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyTRG.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyTRG.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyTRG', VERSIONS['PyTRG'])
		ga.track(GAScreen('PyTRG'))
		setup_trace(self, 'PyTRG')

		self.trg = None
		self.file = None
		self.edited = False
		self.tbl = None
		self.aibin = None
		self.findhistory = []
		self.replacehistory = []
		self.findwindow = None

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			2,
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('import', self.iimport, 'Import TRG (Ctrl+I)', NORMAL, 'Ctrl+I'),
			2,
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('savegottrg', self.savegottrg, 'Save *.got Compatable *.trg (Ctrl+G)', DISABLED, 'Ctrl+G'),
			('export', self.export, 'Export TRG (Ctrl+E)', DISABLED, 'Ctrl+E'),
			('test', self.test, 'Test Code (Ctrl+T)', DISABLED, '<Control-t>'),
			2,
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			10,
			('find', self.find, 'Find/Replace (Ctrl+F)', DISABLED, 'Ctrl+F'),
			10,
			('colors', self.colors, 'Color Settings (Ctrl+Alt+C)', NORMAL, 'Ctrl+Alt+C'),
			2,
			('asc3topyai', self.tblbin, 'Manage stat_txt.tbl and aiscript.bin files (Ctrl+M)', NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default *.trg editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyTRG', NORMAL, ''),
			10,
			('exit', self.exit, 'Exit (Alt+F4)', NORMAL, 'Alt+F4'),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2])
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
				a = btn[4]
				if a:
					if not a.startswith('F'):
						self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					else:
						self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.completing = False
		self.complete = [None, 0]
		self.autocomptext = list(TRG.keywords) + ['Trigger','Conditions','Actions']

		# Text editor
		self.text = TRGCodeText(self, self.edit, highlights=self.settings.get('highlights'), state=DISABLED)
		self.text.pack(fill=BOTH, expand=1, padx=1, pady=1)
		self.text.icallback = self.statusupdate
		self.text.scallback = self.statusupdate
		self.text.acallback = self.autocomplete

		#Statusbar
		self.status = StringVar()
		self.codestatus = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.codestatus, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a TRG.')
		self.codestatus.set('Line: 1  Column: 0  Selected: 0')
		statusbar.pack(side=BOTTOM, fill=X)

		if 'window' in self.settings:
			loadsize(self, self.settings, 'window', True)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings['mpqs'] = self.mpqhandler.mpqs
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self, 'PyTRG'))

		if e:
			self.tblbin(err=e)

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			tbl = TBL.TBL()
			aibin = AIBIN.AIBIN()
			tbl.load_file(self.mpqhandler.get_file(self.settings['stat_txt']))
			aibin.load_file(self.mpqhandler.get_file(self.settings['aiscript']))
		except PyMSError, e:
			err = e
		else:
			self.tbl = tbl
			self.aibin = aibin
		self.mpqhandler.close_mpqs()
		return err

	def unsaved(self):
		if self.trg and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.trg'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.trg', filetypes=[('StarCraft TRG','*.trg'),('All Files','*')], parent=None):
		if parent == None:
			parent = self
		path = self.settings.get('lastpath', BASE_DIR)
		parent._pyms__window_blocking = True
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=parent, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		parent._pyms__window_blocking = False
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		file = [NORMAL,DISABLED][not self.trg]
		for btn in ['save','saveas','savegottrg','export','test','close','find']:
			self.buttons[btn]['state'] = file
		self.text['state'] = file

	def statusupdate(self):
		if not self.completing:
			self.text.taboverride = False
			self.complete = [None, 0]
		i = self.text.index(INSERT).split('.') + [0]
		item = self.text.tag_ranges('Selection')
		if item:
			i[2] = len(self.text.get(*item))
		self.codestatus.set('Line: %s  Column: %s  Selected: %s' % tuple(i))

	def edit(self):
		if not self.completing:
			self.text.taboverride = False
			self.complete = [None, 0]
		self.editstatus['state'] = NORMAL

	def new(self, key=None):
		if not self.unsaved():
			self.text.re = None
			self.trg = TRG.TRG(self.tbl,self.aibin)
			self.file = None
			self.status.set('Editing new TRG.')
			self.title('PyTRG %s (Unnamed.trg)' % LONG_VERSION)
			self.action_states()
			self.text.delete('1.0', END)
			self.edited = False
			self.editstatus['state'] = DISABLED

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.select_file('Open TRG')
				if not file:
					return
			trg = TRG.TRG()
			d = Decompile()
			try:
				trg.load_file(file)
				trg.decompile(d)
			except PyMSError, e:
				d.text = ''
				try:
					trg.load_file(file, True)
					trg.decompile(d)
				except PyMSError, e:
					ErrorDialog(self, e)
					return
			self.text.re = None
			self.trg = trg
			self.title('PyTRG %s (%s)' % (LONG_VERSION,file))
			self.file = file
			self.status.set('Load Successful!')
			self.action_states()
			self.text.delete('1.0', END)
			self.text.insert('1.0', d.text.rstrip('\n'))
			self.text.edit_reset()
			self.text.see('1.0')
			self.edited = False
			self.editstatus['state'] = DISABLED

	def iimport(self, key=None):
		if not self.unsaved():
			file = self.select_file('Import TXT', True, '*.txt', [('Text Files','*.txt'),('All Files','*')])
			if not file:
				return
			try:
				text = open(file,'r').read()
			except:
				ErrorDialog(self, PyMSError('Import','Could not open file "%s"' % file))
				return
			self.text.re = None
			self.trg = TRG.TRG()
			self.title('PyTRG %s (%s)' % (LONG_VERSION,file))
			self.file = file
			self.status.set('Import Successful!')
			self.action_states()
			self.text.delete('1.0', END)
			self.text.insert('1.0', text.rstrip('\n'))
			self.text.edit_reset()
			self.edited = False
			self.editstatus['state'] = DISABLED

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.trg.interpret(self.text)
			self.trg.compile(self.file)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		self.status.set('Save Successful!')
		self.edited = False
		self.editstatus['state'] = DISABLED

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.select_file('Save TRG As', False)
		if not file:
			return True
		self.file = file
		self.save()

	def savegottrg(self, key=None):
		if key and self.buttons['savegottrg']['state'] != NORMAL:
			return
		file = self.select_file('Save *.got Compatable *.trg As', False)
		if not file:
			return True
		try:
			self.trg.interpret(self.text)
			self.trg.compile(file, True)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		self.status.set('*.got Compatable *.trg Saved Successfully!')

	def export(self, key=None):
		if key and self.buttons['export']['state'] != NORMAL:
			return
		file = self.select_file('Export TXT', False, '*.txt', [('Text Files','*.txt'),('All Files','*')])
		if not file:
			return True
		try:
			f = open(file,'w')
			f.write(self.text.get('1.0',END))
			f.close()
			self.status.set('Export Successful!')
		except PyMSError, e:
			ErrorDialog(self, e)

	def test(self, key=None):
		i = TRG.TRG()
		try:
			warnings = i.interpret(self)
		except PyMSError, e:
			if e.line != None:
				self.text.see('%s.0' % e.line)
				self.text.tag_add('Error', '%s.0' % e.line, '%s.end' % e.line)
			if e.warnings:
				for w in e.warnings:
					if w.line != None:
						self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			ErrorDialog(self, e)
			return
		if warnings:
			c = False
			for w in warnings:
				if w.line != None:
					if not c:
						self.text.see('%s.0' % w.line)
						c = True
					self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			WarningDialog(self, warnings, True)
		else:
			askquestion(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.', type=OK)

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.trg = None
			self.title('PyTRG %s' % LONG_VERSION)
			self.file = None
			self.status.set('Load or create a TRG.')
			self.text.delete('1.0', END)
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()

	def find(self, key=None):
		if key and self.buttons['find']['state'] != NORMAL:
			return
		if not self.findwindow:
			self.findwindow = FindReplaceDialog(self)
			self.bind('<F3>', self.findwindow.findnext)
		elif self.findwindow.state() == 'withdrawn':
			self.findwindow.deiconify()
		self.findwindow.focus_set()

	def colors(self, key=None):
		c = CodeColors(self)
		if c.cont:
			self.text.setup(c.cont)
			self.highlights = c.cont

	def tblbin(self, key=None, err=None):
		data = [
			('File Settings',[
				('stat_txt.tbl', 'Contains Unit and AI Script names', 'stat_txt', 'TBL'),
				('aiscript.bin', "Contains AI ID's and references to names in stat_txt.tbl", 'aiscript', 'AIBIN'),
			])
		]
		SettingsDialog(self, data, (340,215), err, mpqhandler=self.mpqhandler)

	def register(self, e=None):
		try:
			register_registry('PyTRG','','trg',os.path.join(BASE_DIR, 'PyTRG.pyw'),os.path.join(BASE_DIR,'Images','PyTRG.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open(os.path.join(BASE_DIR, 'Docs', 'PyTRG.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyTRG', LONG_VERSION, [('FaRTy1billion','For creating TrigPlug and giving me the specs!')])

	def exit(self, e=None):
		if not self.unsaved():
			savesize(self, self.settings)
			self.settings['highlights'] = self.text.highlights
			savesettings('PyTRG', self.settings)
			self.destroy()

	def readlines(self):
		return self.text.get('1.0', END).split('\n')

	def autocomplete(self):
		i = self.text.tag_ranges('Selection')
		if i and '\n' in self.text.get(*i):
			return False
		self.completing = True
		self.text.taboverride = ' (,):'
		def docomplete(s, e, v, t):
			ss = '%s+%sc' % (s,len(t))
			se = '%s+%sc' % (s,len(v))
			self.text.delete(s, ss)
			self.text.insert(s, v)
			self.text.tag_remove('Selection', '1.0', END)
			self.text.tag_add('Selection', ss, se)
			if self.complete[0] == None:
				self.complete = [t, 1, s, se]
			else:
				self.complete[1] += 1
				self.complete[3] = se
		if self.complete[0] != None:
			t,f,s,e = self.complete
		else:
			s,e = self.text.index('%s -1c wordstart' % INSERT),self.text.index('%s -1c wordend' % INSERT)
			t,f = self.text.get(s,e),0
		if t and t[0].lower() in 'abcdefghijklmnopqrstuvwxyz{':
			ac = list(self.autocomptext)
			m = re.match('\\A\\s*[a-z\\{]+\\Z',t)
			if not m:
				ac.extend(list(TRG.TRG.conditions) + list(TRG.TRG.actions) + list(TRG.TRG.new_actions))
			for id,ai in self.aibin.ais.iteritems():
				if not id in ac:
					ac.append(id)
				cs = TBL.decompile_string(self.tbl.strings[ai[1]][:-1], '\x0A\x28\x29\x2C')
				if not cs in ac:
					ac.append(cs)
			for ns in self.tbl.strings[:228]:
				cs = ns.split('\x00')
				if cs[1] != '*':
					cs = TBL.decompile_string('\x00'.join(cs[:2]), '\x0A\x28\x29\x2C')
				else:
					cs = TBL.decompile_string(cs[0], '\x0A\x28\x29\x2C')
				if not cs in ac:
					ac.append(cs)
			head = '1.0'
			while True:
				item = self.text.tag_nextrange('ConstDef', head)
				if not item:
					break
				var = '{%s}' % self.text.get(*item)
				if not var in ac:
					ac.append(var)
				head = item[1]
			ac.sort()
			if m:
				x = list(TRG.TRG.conditions) + list(TRG.TRG.actions) + list(TRG.TRG.new_actions)
				x.sort()
				ac = x + ac
			r = False
			matches = []
			for v in ac:
				if v and v.lower().startswith(t.lower()):
					matches.append(v)
			if matches:
				if f < len(matches):
					docomplete(s,e,matches[f],t)
					self.text.taboverride = ' (,):'
				elif self.complete[0] != None:
					docomplete(s,e,t,t)
					self.complete[1] = 0
				r = True
			self.after(1, self.completed)
			return r

	def completed(self):
		self.completing = False

	def destroy(self):
		if self.findwindow:
			Toplevel.destroy(self.findwindow)
		Tk.destroy(self)

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pytrg.py','pytrg.pyw','pytrg.exe']):
		gui = PyTRG()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyTRG [options] <inp> [out]', version='PyTRG %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a TRG file [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a TRG file")
		p.add_option('-t', '--trig', action='store_true', help="Used to decompile/compile a GOT compatable TRG", default=False)
		p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for parameter types, conditions and actions with parameter lists, and AIScripts [default: Off]", default=False)
		p.add_option('-s', '--stattxt',  help="Used to signify the stat_txt.tbl file to use [default: Libs\\MPQ\\rez\\stat_txt.tbl]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez', 'stat_txt.tbl'))
		p.add_option('-a', '--aiscript', help="Used to signify the aiscript.bin file to use [default: Libs\\MPQ\\scripts\\aiscript.bin]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'scripts', 'aiscript.bin'))
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyTRG(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			trg = TRG.TRG()
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'trg'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			try:
				if opt.convert:
					if opt.trig:
						print "Reading GOT compatable TRG '%s'..." % args[0]
					else:
						print "Reading TRG '%s'..." % args[0]
					trg.load_file(args[0], opt.trig)
					print " - '%s' read successfully\nDecompiling TRG file '%s'..." % (args[0],args[0])
					trg.decompile(args[1], opt.reference)
					print " - '%s' written succesfully" % args[1]
				else:
					print "Interpreting file '%s'..." % args[0]
					trg.interpret(args[0])
					print " - '%s' read successfully" % args[0]
					if opt.trig:
						print "Compiling file '%s' to GOT compatable TRG format..." % args[0]
					else:
						print "Compiling file '%s' to TRG format..." % args[0]
					trg.compile(args[1], opt.trig)
					print " - '%s' written succesfully" % args[1]
			except PyMSError, e:
				print repr(e)

if __name__ == '__main__':
	main()