
from __future__ import annotations

from .GraftTab import GraftTab
from ..GraftData import ButtonsGraftData

from ...FileFormats.Graft import ButtonCard
from ...FileFormats.Graft.CodeHandlers.CodeTypes import ConnectedUnitCodeType
from ...FileFormats.Graft.Definitions import NO_CONNECTED_UNIT

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# Tab for the button cards of Buttons.graft (one per unit, followed by the special cards)
class ButtonCardsTab(GraftTab):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ButtonsGraftData) -> None:
		self.graft_data = graft_data
		# The entries the dropdowns were last filled with
		self.button_set_names: list[str] | None = None
		self.connected_unit_entries: list[tuple[str, int]] | None = None
		# Set while the selected button card is loaded into the editor, so updating the widgets doesn't edit it
		self.loading = False
		super().__init__(parent, delegate)

	def build_editor(self) -> None:
		# Index 0 is no button set, and index `n` is button set `n - 1`
		self.button_set = UI.IntVar()
		self.connected_unit = UI.IntegerVar(NO_CONNECTED_UNIT, [0, NO_CONNECTED_UNIT])

		frame = UI.LabelFrame(self, text='Button Card')
		f = UI.Frame(frame)
		UI.Label(f, text='Button Set:', width=13, anchor=UI.E).pack(side=UI.LEFT)
		self.button_set_dropdown = UI.DropDown(f, self.button_set, ['None'], self.button_set_changed, width=30)
		self.button_set_dropdown.pack(side=UI.LEFT, padx=2)
		GraftTab.tip(f, 'Button Set', 'The set of buttons the button card shows, or None for no buttons.')
		f.pack(fill=UI.X, pady=2)
		f = UI.Frame(frame)
		UI.Label(f, text='Connected Unit:', width=13, anchor=UI.E).pack(side=UI.LEFT)
		# There is no catch-all entry, so only units and None can be entered
		self.connected_unit_dropdown = UI.EntryDropDown(f, self.connected_unit, [('None', NO_CONNECTED_UNIT)], entry_width=10, dropdown_width=30, callback=self.connected_unit_changed)
		self.connected_unit_dropdown.pack(side=UI.LEFT, padx=2)
		GraftTab.tip(f, 'Connected Unit', f"When units with this button card are selected together with this unit, the group uses this unit's button card instead of the generic group card (such as Kerrigan connected to the Ghost), or None ({NO_CONNECTED_UNIT}). Choose a unit, or enter its ID.")
		f.pack(fill=UI.X, pady=2)
		frame.pack(anchor=UI.W, padx=5, pady=5)

	def get_graft_data(self) -> ButtonsGraftData:
		return self.graft_data

	def entry_names(self) -> list[str]:
		max_id = len(self.graft_data.graft.button_cards) - 1
		return [GraftTab.format_entry(card_id, max_id, self.delegate.data_context.button_card_name(card_id) or f'Button Card {card_id}') for card_id in range(len(self.graft_data.graft.button_cards))]

	def selected_button_card(self) -> ButtonCard | None:
		button_cards = self.graft_data.graft.button_cards
		if 0 <= self.selected < len(button_cards):
			return button_cards[self.selected]
		return None

	def update_button_set_names(self) -> None:
		set_count = len(self.graft_data.graft.button_sets)
		names = ['None', *(GraftTab.format_entry(set_id, set_count - 1, self.delegate.data_context.button_set_name(set_id) or f'Button Set {set_id}') for set_id in range(set_count))]
		if names != self.button_set_names:
			self.button_set_names = names
			if self.button_set.get() >= len(names):
				self.button_set.set(0)
			self.button_set_dropdown.setentries(names)

	def update_connected_unit_entries(self, connected_unit: int) -> None:
		entries = [*((name, unit_id) for unit_id, name in enumerate(self.delegate.data_context.unit_display_names())), ('None', NO_CONNECTED_UNIT)]
		# A connected unit past the loaded units gets its own entry, so loading it doesn't change it
		if connected_unit != NO_CONNECTED_UNIT and connected_unit >= len(entries) - 1:
			entries.append((f'Unit {connected_unit}', connected_unit))
		if entries != self.connected_unit_entries:
			self.connected_unit_entries = entries
			self.connected_unit_dropdown.set_entries(entries)

	def load_selected(self) -> None:
		button_card = self.selected_button_card()
		connected_unit = ConnectedUnitCodeType.to_value(button_card.connected_unit) if button_card else NO_CONNECTED_UNIT
		self.loading = True
		try:
			self.update_button_set_names()
			self.update_connected_unit_entries(connected_unit)
			state = UI.NORMAL if button_card else UI.DISABLED
			self.button_set_dropdown['state'] = state
			self.connected_unit_dropdown.entry['state'] = state
			self.connected_unit_dropdown.dropdown['state'] = state
			if not button_card:
				return
			self.button_set.set(0 if button_card.button_set is None else button_card.button_set + 1)
			self.connected_unit.set(connected_unit)
		finally:
			self.loading = False

	def mark_edited(self) -> None:
		self.graft_data.edited = True
		self.delegate.update_status_bar()

	def button_set_changed(self, index: int) -> None:
		button_set = None if index == 0 else index - 1
		button_card = self.selected_button_card()
		if not self.loading and button_card and button_card.button_set != button_set:
			button_card.button_set = button_set
			self.mark_edited()

	def connected_unit_changed(self, value: int) -> None:
		connected_unit = ConnectedUnitCodeType.from_value(value)
		button_card = self.selected_button_card()
		if not self.loading and button_card and button_card.connected_unit != connected_unit:
			button_card.connected_unit = connected_unit
			self.mark_edited()
