
from .Config import PyGOTConfig
from .SettingsDialog import SettingsDialog

from ..FileFormats import GOT
from ..FileFormats.TRG import TRG

from ..Utilities import registry
from ..Utilities import UIKit as UI
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.CheckSaved import CheckSaved
from ..Utilities.SponsorDialog import SponsorDialog

from typing import Any

LONG_VERSION = 'v' + Assets.version('PyGOT')

class PyGOT(UI.MainWindow):
	def __init__(self, guifile: str | None = None) -> None:
		#Window
		UI.MainWindow.__init__(self)
		self.set_icon('PyGOT')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyGOT', Assets.version('PyGOT'))
		ga.track(GAScreen('PyGOT'))
		setup_trace('PyGOT', self)

		self.config_ = PyGOTConfig()
		UI.Theme.load_theme(self.config_.theme.value, self)
		self.resizable(False, False)

		self.got: GOT.GOT | None = None
		self.file: str | None = None
		self.edited = False

		self.update_title()

		#Toolbar
		self.toolbar = UI.Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', UI.Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', UI.Ctrl.o)
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Game Template', UI.Ctrl.i)
		self.toolbar.add_gap()
		def save() -> None:
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', UI.Ctrl.s, enabled=False, tags='file_open')
		def saveas() -> None:
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), saveas, 'Save As', UI.Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export Game Template', UI.Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', UI.Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('codeedit'), lambda: self.trg(TRG.Format.got), 'Convert *.trg to GOT compatable', UI.Ctrl.t)
		self.toolbar.add_button(Assets.get_image('insert'), lambda: self.trg(TRG.Format.normal), 'Revert GOT compatable *.trg', UI.Ctrl.Alt.t)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.sets, "Manage Settings", UI.Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.got editor (Windows Only)', enabled=registry.IS_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', UI.Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyGOT')
		self.toolbar.add_button(Assets.get_image('money'), self.sponsor, 'Donate')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', UI.Shortcut.Exit)
		self.toolbar.pack(side=UI.TOP, padx=1, pady=1, fill=UI.X)

		def edited(*_: Any) -> None:
			if not self.got:
				return
			self.mark_edited()
			self.action_states()
		self.name = UI.SStringVar(length=32, callback=edited)
		self.gametype_id = UI.IntegerVar(0,[0,31], callback=edited)
		self.league_id = UI.IntegerVar(0, [0,255])
		self.subtype_name = UI.SStringVar(length=32, callback=edited)
		self.subtype_id = UI.IntegerVar(0,[0,7], callback=edited)
		self.subtype_display = UI.IntegerVar(0, [0,56533], callback=edited)
		self.subtype_label = UI.IntegerVar(0, [0,65535], callback=edited)
		self.victory_condition = UI.IntVar(value=0)
		self.victory_condition.trace_add('write', edited)
		self.resources = UI.IntVar(value=0)
		self.resources.trace_add('write', edited)
		self.unit_stats = UI.IntVar(value=0)
		self.unit_stats.trace_add('write', edited)
		self.fog_of_war = UI.IntVar(value=0)
		self.fog_of_war.trace_add('write', edited)
		self.starting_units = UI.IntVar(value=0)
		self.starting_units.trace_add('write', edited)
		self.starting_positions = UI.IntVar(value=0)
		self.starting_positions.trace_add('write', edited)
		self.player_types = UI.IntVar(value=0)
		self.player_types.trace_add('write', edited)
		self.allies = UI.IntVar(value=0)
		self.allies.trace_add('write', edited)
		self.team_mode = UI.IntVar(value=0)
		self.team_mode.trace_add('write', edited)
		self.cheat_codes = UI.IntVar(value=0)
		self.cheat_codes.trace_add('write', edited)
		self.tournament_mode = UI.IntVar(value=0)
		self.tournament_mode.trace_add('write', edited)
		self.victory_condition_value = UI.IntegerVar(0, [0,4294967295], callback=edited)
		self.resources_value = UI.IntegerVar(0, [0,4294967295], callback=edited)
		self.subtype_value = UI.IntegerVar(0, [0,4294967295], callback=edited)

		content = UI.Frame(self)

		l = UI.LabelFrame(content, text='Template Info:', padx=5, pady=5)
		f = UI.Frame(l)
		UI.Label(f, text='Name:').grid(sticky=UI.E)
		self.name_entry = UI.Entry(f, textvariable=self.name, font=UI.Font.fixed(), width=32, state=UI.DISABLED)
		UI.Tooltip(self.name_entry, 'The name of the Game Template listed in StarCraft')
		self.name_entry.grid(row=0, column=1, pady=1, columnspan=3)

		UI.Label(f, text='ID:').grid(sticky=UI.E)
		self.gametype_id_entry = UI.Entry(f, textvariable=self.gametype_id, font=UI.Font.fixed(), width=2, state=UI.DISABLED)
		UI.Tooltip(self.gametype_id_entry, 'An ID used to define the order of the Game Template when its listed in StarCraft')
		self.gametype_id_entry.grid(row=1, column=1, sticky=UI.W, pady=1)

		UI.Label(f, text='League ID:').grid(row=1, column=2, sticky=UI.E)
		self.league_id_entry = UI.Entry(f, textvariable=self.league_id, font=UI.Font.fixed(), width=10, state=UI.DISABLED)
		# tip(self.league_id_entry, 'subid')
		self.league_id_entry.grid(row=1, column=3, sticky=UI.W, pady=1)
		f.pack(anchor=UI.W)
		f.grid_columnconfigure(2, weight=1)
		l.pack(pady=(0, 5), fill=UI.X, expand=1)

		l = UI.LabelFrame(content, text='Variation Info:', padx=5, pady=5)
		f = UI.Frame(l)
		UI.Label(f, text='Name:').grid(sticky=UI.E)
		self.subtype_name_entry = UI.Entry(f, textvariable=self.subtype_name, font=UI.Font.fixed(), width=32, state=UI.DISABLED)
		UI.Tooltip(self.subtype_name_entry, 'The label for the variation (ie, the one to set greed amount)\nThis should be the same for each variation of a tempalte')
		self.subtype_name_entry.grid(row=0, column=1, pady=1, columnspan=3)

		UI.Label(f, text='Display:').grid(sticky=UI.E)
		self.subtype_display_entry = UI.Entry(f, textvariable=self.subtype_display, font=UI.Font.fixed(), width=10, state=UI.DISABLED)
		UI.Tooltip(self.subtype_display_entry, 'The value defining the variation amount (for example mineral count for greed or amount of teams for Team Vs)')
		self.subtype_display_entry.grid(row=1, column=1, sticky=UI.W, pady=1)

		UI.Label(f, text='ID:').grid(sticky=UI.E)
		self.subtype_id_entry = UI.Entry(f, textvariable=self.subtype_id, font=UI.Font.fixed(), width=1, state=UI.DISABLED)
		UI.Tooltip(self.subtype_id_entry, 'An ID used to define the order of the variation when its listed in StarCraft')
		self.subtype_id_entry.grid(row=2, column=1, sticky=UI.W, pady=1)

		UI.Label(f, text='Label:').grid(row=1, column=2, sticky=UI.E)
		self.subtype_label_entry = UI.Entry(f, textvariable=self.subtype_label, font=UI.Font.fixed(), width=10, state=UI.DISABLED)
		# tip(self.subtype_label_entry, 'subid')
		self.subtype_label_entry.grid(row=1, column=3, sticky=UI.W, pady=1)

		UI.Label(f, text='Value:').grid(row=2, column=2, sticky=UI.E)
		self.subtype_value_entry = UI.Entry(f, textvariable=self.subtype_value, font=UI.Font.fixed(), width=10, state=UI.DISABLED)
		# tip(self.subtype_value_entry, 'subid')
		self.subtype_value_entry.grid(row=2, column=3, sticky=UI.W, pady=1)
		f.pack(anchor=UI.W)
		f.grid_columnconfigure(2, weight=1)
		l.pack(pady=(0, 5), fill=UI.X, expand=1)

		l = UI.LabelFrame(content, text='Settings', padx=5, pady=5)
		row = 0
		def add_with_value(name: str, option_var: UI.IntVar, options: list[str], value_var: UI.IntegerVar) -> tuple[UI.DropDown, UI.Entry]:
			nonlocal row
			UI.Label(l, text=name + ':', anchor=UI.E).grid(row=row, column=0, sticky=UI.E)
			dropdown = UI.DropDown(l, option_var, options, width=25, state=UI.DISABLED)
			dropdown.grid(row=row, column=1, pady=1)
			entry = UI.Entry(l, textvariable=value_var, font=UI.Font.fixed(), width=10, state=UI.DISABLED)
			entry.grid(row=row, column=2, padx=(5, 0), pady=1)
			row += 1
			return (dropdown, entry)
		def add_without_value(name: str, option_var: UI.IntVar, options: list[str]) -> UI.DropDown:
			nonlocal row
			UI.Label(l, text=name + ':', anchor=UI.E).grid(row=row, column=0, sticky=UI.E)
			dropdown = UI.DropDown(l, option_var, options, width=25, state=UI.DISABLED)
			dropdown.grid(row=row, column=1, pady=1)
			row += 1
			return dropdown

		self.victory_condition_dropdown, self.victory_condition_entry = add_with_value('Victory Conditions', self.victory_condition, list(o.display_name for o in GOT.VictoryCondition.ALL()), self.victory_condition_value)
		self.resources_dropdown, self.resources_entry = add_with_value('Resource Type', self.resources, list(o.display_name for o in GOT.Resources.ALL()), self.resources_value)
		self.unit_stats_dropdown = add_without_value('Unit Stats', self.unit_stats, list(o.display_name for o in GOT.UnitStats.ALL()))
		self.fog_of_war_dropdown = add_without_value('Fog of War', self.fog_of_war, list(o.display_name for o in GOT.FogOfWar.ALL()))
		self.starting_units_dropdown = add_without_value('Starting Units', self.starting_units, list(o.display_name for o in GOT.StartingUnits.ALL()))
		self.starting_positions_dropdown = add_without_value('Starting Positions', self.starting_positions, list(o.display_name for o in GOT.StartingPositions.ALL()))
		self.player_types_dropdown = add_without_value('Player Types', self.player_types, list(o.display_name for o in GOT.PlayerTypes.ALL()))
		self.allies_dropdown = add_without_value('Allies', self.allies, list(o.display_name for o in GOT.Allies.ALL()))
		self.team_mode_dropdown = add_without_value('Team Mode', self.team_mode, list(o.display_name for o in GOT.TeamMode.ALL()))
		self.cheat_codes_dropdown = add_without_value('Cheat Codes', self.cheat_codes, list(o.display_name for o in GOT.CheatCodes.ALL()))
		self.tournament_mode_dropdown = add_without_value('Tournament Mode', self.tournament_mode, list(o.display_name for o in GOT.TournametMode.ALL()))
		l.pack()
		content.pack(padx=5, pady=(0, 5))

		#Statusbar
		self.status = UI.StringVar()
		self.status.set('Load or create a Game Template.')
		statusbar = UI.StatusBar(self)
		statusbar.add_label(self.status, width=35)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_spacer()
		statusbar.pack(side=UI.BOTTOM, fill=UI.X)

		self.config_.windows.main.load_size(self)

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyGOT')

	def check_saved(self) -> CheckSaved:
		if not self.got or not self.edited:
			return CheckSaved.saved
		file = self.file
		if not file:
			file = 'Unnamed.got'
		save = UI.MessageBox.askyesnocancel(parent=self, title='Save Changes?', message=f"Save changes to '{file}'?", default=UI.MessageBox.YES)
		if save is None:
			return CheckSaved.cancelled
		if not save:
			return CheckSaved.saved
		if self.file:
			return self.save()
		return self.saveas()

	def is_file_open(self) -> bool:
		return not not self.got

	def action_states(self) -> None:
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		fields: tuple[UI.Misc, ...] = (
			self.name_entry,
			self.gametype_id_entry,
			self.league_id_entry,
			self.subtype_name_entry,
			self.subtype_display_entry,
			self.subtype_id_entry,
			self.subtype_label_entry,
			self.subtype_value_entry,
			self.victory_condition_dropdown,
			self.resources_dropdown,
			self.unit_stats_dropdown,
			self.fog_of_war_dropdown,
			self.starting_units_dropdown,
			self.starting_positions_dropdown,
			self.player_types_dropdown,
			self.allies_dropdown,
			self.team_mode_dropdown,
			self.cheat_codes_dropdown,
			self.tournament_mode_dropdown
		)
		for field in fields:
			field['state'] = UI.NORMAL if self.is_file_open() else UI.DISABLED
		if self.got:
			victory = GOT.VictoryCondition(self.victory_condition.get())
			self.victory_condition_entry['state'] = UI.NORMAL if victory.requires_value else UI.DISABLED
			resources = GOT.Resources(self.resources.get())
			self.resources_entry['state'] = UI.NORMAL if resources.requires_value else UI.DISABLED

	def reset(self) -> None:
		self.name.check = False
		self.name.set('')
		self.subtype_name.check = False
		self.subtype_name.set('')
		all_vars: list[UI.Variable] = [
			self.gametype_id,
			self.league_id,
			self.subtype_id,
			self.subtype_display,
			self.subtype_label,
			self.victory_condition,
			self.resources,
			self.unit_stats,
			self.fog_of_war,
			self.starting_units,
			self.starting_positions,
			self.player_types,
			self.allies,
			self.team_mode,
			self.cheat_codes,
			self.tournament_mode,
			self.victory_condition_value,
			self.resources_value,
			self.subtype_value
		]
		for var in all_vars:
			var.set(0)

	def update_title(self) -> None:
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.got'
		if not file_path:
			self.title(f'PyGOT {LONG_VERSION}')
		else:
			self.title(f'PyGOT {LONG_VERSION} ({file_path})')

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.editstatus['state'] = UI.NORMAL if edited else UI.DISABLED

	def new(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.got = GOT.GOT()
		self.file = None
		self.status.set('Editing new Game Template.')
		self.update_title()
		self.mark_edited(False)
		self.reset()
		self.action_states()

	def team_mode_to_dropdown_index(self, team_mode: GOT.TeamMode) -> int:
		return GOT.TeamMode.ALL().index(team_mode)

	def team_mode_from_dropdown_index(self, index: int) -> GOT.TeamMode:
		return GOT.TeamMode.ALL()[index]

	def load_values(self) -> None:
		if not self.got:
			self.reset()
			return
		self.name.set(self.got.name)
		self.subtype_name.set(self.got.subtype_name)
		self.gametype_id.set(self.got.gametype_id)
		self.league_id.set(self.got.league_id)
		self.subtype_id.set(self.got.subtype_id)
		self.subtype_display.set(self.got.subtype_display)
		self.subtype_label.set(self.got.subtype_label)
		self.victory_condition.set(self.got.victory_condition.value)
		self.resources.set(self.got.resources.value)
		self.unit_stats.set(self.got.unit_stats.value)
		self.fog_of_war.set(self.got.fog_of_war.value)
		self.starting_units.set(self.got.starting_units.value)
		self.starting_positions.set(self.got.starting_positions.value)
		self.player_types.set(self.got.player_types.value)
		self.allies.set(self.got.allies.value)
		self.team_mode.set(self.team_mode_to_dropdown_index(self.got.team_mode))
		self.cheat_codes.set(self.got.cheat_codes.value)
		self.tournament_mode.set(self.got.tournament_mode.value)
		self.victory_condition_value.set(self.got.victory_condition_value)
		self.resources_value.set(self.got.resources_value)
		self.subtype_value.set(self.got.subtype_value)

	def save_values(self) -> None:
		if not self.got:
			return
		self.got.name = self.name.get()
		self.got.subtype_name = self.subtype_name.get()
		self.got.gametype_id = self.gametype_id.get()
		self.got.league_id = self.league_id.get()
		self.got.subtype_id = self.subtype_id.get()
		self.got.subtype_display = self.subtype_display.get()
		self.got.subtype_label = self.subtype_label.get()
		self.got.victory_condition = GOT.VictoryCondition(self.victory_condition.get())
		self.got.resources = GOT.Resources(self.resources.get())
		self.got.unit_stats = GOT.UnitStats(self.unit_stats.get())
		self.got.fog_of_war = GOT.FogOfWar(self.fog_of_war.get())
		self.got.starting_units = GOT.StartingUnits(self.starting_units.get())
		self.got.starting_positions = GOT.StartingPositions(self.starting_positions.get())
		self.got.player_types = GOT.PlayerTypes(self.player_types.get())
		self.got.allies = GOT.Allies(self.allies.get())
		self.got.team_mode = self.team_mode_from_dropdown_index(self.team_mode.get())
		self.got.cheat_codes = GOT.CheatCodes(self.cheat_codes.get())
		self.got.tournament_mode = GOT.TournametMode(self.tournament_mode.get())
		self.got.victory_condition_value = self.victory_condition_value.get()
		self.got.resources_value = self.resources_value.get()
		self.got.subtype_value = self.subtype_value.get()

	def open(self, file: str | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		if file is None:
			file = self.config_.last_path.got.select_open(self)
			if not file:
				return
		got = GOT.GOT()
		try:
			got.load_file(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.got = got
		self.file = file
		self.update_title()
		self.load_values()
		self.status.set('Load Successful!')
		self.mark_edited(False)
		self.action_states()

	def iimport(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		file = self.config_.last_path.txt.select_open(self)
		if not file:
			return
		got = GOT.GOT()
		try:
			got.interpret(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.got = got
		self.file = file
		self.update_title()
		self.load_values()
		self.status.set('Import Successful!')
		self.mark_edited(False)
		self.action_states()

	def save(self) -> CheckSaved:
		return self.saveas(file_path=self.file)

	def saveas(self, file_path: str | None = None) -> CheckSaved:
		if not self.got:
			return CheckSaved.saved
		if not file_path:
			file_path = self.config_.last_path.got.select_save(self)
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			self.save_values()
			self.got.save_file(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.file = file_path
		self.update_title()
		self.status.set('Save Successful!')
		self.mark_edited(False)
		return CheckSaved.saved

	def export(self) -> None:
		if not self.got:
			return
		file = self.config_.last_path.txt.select_save(self)
		if not file:
			return
		try:
			self.got.decompile(file)
			self.status.set('Export Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def close(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.got = None
		self.file = None
		self.update_title()
		self.status.set('Load or create a Game Template.')
		self.mark_edited(False)
		self.reset()
		self.action_states()

	def trg(self, trg_format: TRG.Format) -> None:
		file = self.config_.last_path.trg.select_open(self)
		if not file:
			return
		trg = TRG.TRG()
		try:
			trg.load(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		file = self.config_.last_path.trg.select_save(self)
		if not file:
			return
		try:
			trg.save(file, trg_format)
		except PyMSError as e:
			ErrorDialog(self, e)

	def register_registry(self) -> None:
		try:
			registry.register('PyGOT', 'got', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def sets(self) -> None:
		SettingsDialog(self, self.config_)

	def help(self) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyGOT.md')

	def about(self) -> None:
		AboutDialog(self, 'PyGOT', LONG_VERSION)

	def sponsor(self) -> None:
		SponsorDialog(self)

	def exit(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.config_.windows.main.save_size(self)
		self.config_.save()
		self.destroy()
