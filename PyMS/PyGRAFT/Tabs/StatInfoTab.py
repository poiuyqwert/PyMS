from __future__ import annotations

from .GraftTab import GraftTab
from ..GraftData import ButtonsGraftData

from ...FileFormats.Graft import StatInfo
from ...FileFormats.Graft.CodeHandlers import StatInfoCodeCommands
from ...FileFormats.Graft.CodeHandlers.GraftCommandDefinition import GraftCommandDefinition

from ...Utilities import UIKit as UI
from ...Utilities import Struct

from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

@dataclass(frozen=True)
class StatPreset:
	name: str
	status_function: GraftCommandDefinition
	display_function: GraftCommandDefinition

# Most units use one of these status/display function pairs, though not all of them do
STAT_PRESETS: tuple[StatPreset, ...] = (
	StatPreset('Building', StatInfoCodeCommands.ChangedBuilding, StatInfoCodeCommands.DrawBuilding),
	StatPreset('Normal Unit', StatInfoCodeCommands.ChangedUnit, StatInfoCodeCommands.DrawUnit),
	StatPreset('Unit w/ Subunits', StatInfoCodeCommands.ChangedHangar, StatInfoCodeCommands.DrawHangar),
	StatPreset('Transport', StatInfoCodeCommands.ChangedTransport, StatInfoCodeCommands.DrawTransport),
	StatPreset('Transport w/ Supply', StatInfoCodeCommands.ChangedSupplyTransport, StatInfoCodeCommands.DrawSupplyTransport),
	StatPreset('Powerup', StatInfoCodeCommands.ChangedPowerup, StatInfoCodeCommands.DrawPowerup),
	StatPreset('Morph Unit', StatInfoCodeCommands.ChangedMorph, StatInfoCodeCommands.DrawMorph),
	StatPreset('Merge Unit', StatInfoCodeCommands.ChangedSummon, StatInfoCodeCommands.DrawSummon),
	StatPreset('Unselectable', StatInfoCodeCommands.ChangedNever, StatInfoCodeCommands.DrawNone),
)

# Tab for the unit stat info of Buttons.graft (one per unit)
class StatInfoTab(GraftTab):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ButtonsGraftData) -> None:
		self.graft_data = graft_data
		# The unit names the debug unit dropdown was last filled with
		self.unit_names: tuple[str, ...] | None = None
		super().__init__(parent, delegate)

	def build_editor(self) -> None:
		self.status_function = UI.IntVar()
		self.display_function = UI.IntVar()
		self.debug_unit_id = UI.IntegerVar(0, [0, Struct.l_u32.max])

		frame = UI.LabelFrame(self, text='Status Information')
		f = UI.Frame(frame)
		field = UI.Frame(f)
		UI.Label(field, text='Status Func.:', width=13, anchor=UI.E).pack(side=UI.LEFT)
		self.status_dropdown = UI.DropDown(field, self.status_function, [command.display_name for command in StatInfoCodeCommands.status_function_commands], self.status_function_changed, width=30)
		self.status_dropdown.pack(side=UI.LEFT, padx=2)
		GraftTab.tip(field, 'Status Func.', "Checks whether what the unit's stat panel shows has changed, and redraws it when it has.")
		field.pack(side=UI.LEFT)
		help_label = UI.Label(f, text='?')
		help_label.pack(side=UI.LEFT, padx=2)
		self.status_help = UI.Tooltip(help_label) # Shows the help of the chosen function
		f.pack(fill=UI.X, pady=2)
		f = UI.Frame(frame)
		field = UI.Frame(f)
		UI.Label(field, text='Display Func.:', width=13, anchor=UI.E).pack(side=UI.LEFT)
		self.display_dropdown = UI.DropDown(field, self.display_function, [command.display_name for command in StatInfoCodeCommands.display_function_commands], self.display_function_changed, width=30)
		self.display_dropdown.pack(side=UI.LEFT, padx=2)
		GraftTab.tip(field, 'Display Func.', "Draws the unit's stat panel.")
		field.pack(side=UI.LEFT)
		help_label = UI.Label(f, text='?')
		help_label.pack(side=UI.LEFT, padx=2)
		self.display_help = UI.Tooltip(help_label) # Shows the help of the chosen function
		f.pack(fill=UI.X, pady=2)
		self.presets_button = UI.Button(frame, text='Presets', command=self.show_presets)
		self.presets_button.pack(side=UI.RIGHT, padx=2, pady=2)
		GraftTab.tip(self.presets_button, 'Presets', 'Sets the Status and Display functions to one of the pairs most units use.')
		self.presets_menu = UI.Menu(self, tearoff=0)
		for preset in STAT_PRESETS:
			self.presets_menu.add_command(label=preset.name, command=partial(self.apply_preset, preset))
		frame.pack(anchor=UI.W, padx=5, pady=5)

		frame = UI.LabelFrame(self, text='Debug')
		f = UI.Frame(frame)
		UI.Label(f, text='Unit ID:', width=13, anchor=UI.E).pack(side=UI.LEFT)
		self.debug_unit_dropdown = UI.EntryDropDown(f, self.debug_unit_id, [('Unknown', None)], entry_width=10, dropdown_width=30, callback=self.debug_unit_id_changed)
		self.debug_unit_dropdown.pack(side=UI.LEFT, padx=2)
		GraftTab.tip(f, 'Unit ID', 'A debug unit ID, unused by the game (defaults to the unit itself). Choose a unit, or enter any number.')
		f.pack(fill=UI.X, pady=2)
		frame.pack(anchor=UI.W, padx=5, pady=5)

	def get_graft_data(self) -> ButtonsGraftData:
		return self.graft_data

	def entry_names(self) -> list[str]:
		max_id = len(self.graft_data.graft.stat_info) - 1
		return [GraftTab.format_entry(unit_id, max_id, self.delegate.data_context.unit_display_name(unit_id) or f'Unit {unit_id}') for unit_id in range(len(self.graft_data.graft.stat_info))]

	def selected_stat_info(self) -> StatInfo | None:
		stat_info = self.graft_data.graft.stat_info
		if 0 <= self.selected < len(stat_info):
			return stat_info[self.selected]
		return None

	def load_selected(self) -> None:
		unit_names = self.delegate.data_context.unit_display_names()
		if unit_names is not self.unit_names:
			self.unit_names = unit_names
			# Any ID can be entered, so IDs without a unit show the catch-all entry
			self.debug_unit_dropdown.set_entries([*((name, unit_id) for unit_id, name in enumerate(unit_names)), ('Unknown', None)])
		stat_info = self.selected_stat_info()
		state = UI.NORMAL if stat_info else UI.DISABLED
		self.status_dropdown['state'] = state
		self.display_dropdown['state'] = state
		self.presets_button['state'] = state
		self.debug_unit_dropdown.entry['state'] = state
		self.debug_unit_dropdown.dropdown['state'] = state
		if not stat_info:
			return
		self.status_function.set(stat_info.status_function)
		self.display_function.set(stat_info.display_function)
		self.debug_unit_id.set(stat_info.debug_unit_id)

	def mark_edited(self) -> None:
		self.graft_data.edited = True
		self.delegate.update_status_bar()

	def status_function_changed(self, status_function: int) -> None:
		command = StatInfoCodeCommands.status_function_commands[status_function]
		self.status_help.text = GraftTab.tip_text(command.display_name, command.help_text)
		stat_info = self.selected_stat_info()
		if stat_info and stat_info.status_function != status_function:
			stat_info.status_function = status_function
			self.mark_edited()

	def display_function_changed(self, display_function: int) -> None:
		command = StatInfoCodeCommands.display_function_commands[display_function]
		self.display_help.text = GraftTab.tip_text(command.display_name, command.help_text)
		stat_info = self.selected_stat_info()
		if stat_info and stat_info.display_function != display_function:
			stat_info.display_function = display_function
			self.mark_edited()

	def debug_unit_id_changed(self, debug_unit_id: int) -> None:
		stat_info = self.selected_stat_info()
		if stat_info and stat_info.debug_unit_id != debug_unit_id:
			stat_info.debug_unit_id = debug_unit_id
			self.mark_edited()

	def show_presets(self) -> None:
		self.presets_menu.post(self.presets_button.winfo_rootx(), self.presets_button.winfo_rooty() + self.presets_button.winfo_height())

	def apply_preset(self, preset: StatPreset) -> None:
		self.status_function.set(preset.status_function.function_index)
		self.display_function.set(preset.display_function.function_index)
