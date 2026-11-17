
from __future__ import annotations

from .GraftTab import GraftTab
from ..GraftData import ButtonsGraftData
from ..JumpTarget import JumpTarget

from ...FileFormats.Graft import ButtonCard
from ...FileFormats.Graft.CodeHandlers.CodeTypes import ConnectedUnitCodeType

from ...Utilities import UIKit as UI
from ...Utilities import Assets

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
		self.connected_unit = UI.IntegerVar(ConnectedUnitCodeType.NONE_VALUE, [0, ConnectedUnitCodeType.NONE_VALUE])

		frame = UI.LabelFrame(self, text='Button Card')
		# The field's tooltip is on its own frame, so it doesn't also show over the Jump To button beside it
		f = UI.Frame(frame)
		field = UI.Frame(f)
		UI.Label(field, text='Button Set:', width=13, anchor=UI.E).pack(side=UI.LEFT)
		self.button_set_dropdown = UI.DropDown(field, self.button_set, ['None'], self.button_set_changed, width=30)
		self.button_set_dropdown.pack(side=UI.LEFT, padx=2)
		GraftTab.tip(field, 'Button Set', 'The set of buttons the button card shows, or None for no buttons.')
		field.pack(side=UI.LEFT)
		self.button_set_jump_button = UI.Button(f, image=Assets.get_image('jump'), command=self.jump_to_button_set, width=20, height=20)
		self.button_set_jump_button.pack(side=UI.LEFT, padx=2)
		UI.Tooltip(self.button_set_jump_button, JumpTarget.button_sets.tooltip)
		f.pack(fill=UI.X, pady=2)
		f = UI.Frame(frame)
		field = UI.Frame(f)
		UI.Label(field, text='Connected Unit:', width=13, anchor=UI.E).pack(side=UI.LEFT)
		# There is no catch-all entry, so only units and None can be entered
		self.connected_unit_dropdown = UI.EntryDropDown(field, self.connected_unit, [('None', ConnectedUnitCodeType.NONE_VALUE)], entry_width=10, dropdown_width=30, callback=self.connected_unit_changed)
		self.connected_unit_dropdown.pack(side=UI.LEFT, padx=2)
		GraftTab.tip(field, 'Connected Unit', f"When units with this button card are selected together with the connected unit (such as Kerrigan connected to the Ghost), the group uses the connected unit's button card instead of the generic group card, or None ({ConnectedUnitCodeType.NONE_VALUE}).")
		field.pack(side=UI.LEFT)
		self.connected_unit_jump_button = UI.Button(f, image=Assets.get_image('jump'), command=self.jump_to_connected_unit, width=20, height=20)
		self.connected_unit_jump_button.pack(side=UI.LEFT, padx=2)
		UI.Tooltip(self.connected_unit_jump_button, JumpTarget.button_cards.tooltip)
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
		entries = [*((name, unit_id) for unit_id, name in enumerate(self.delegate.data_context.unit_display_names())), ('None', ConnectedUnitCodeType.NONE_VALUE)]
		# A connected unit past the loaded units gets its own entry, so loading it doesn't change it
		if connected_unit != ConnectedUnitCodeType.NONE_VALUE and connected_unit >= len(entries) - 1:
			entries.append((f'Unit {connected_unit}', connected_unit))
		if entries != self.connected_unit_entries:
			self.connected_unit_entries = entries
			self.connected_unit_dropdown.set_entries(entries)

	def load_selected(self) -> None:
		button_card = self.selected_button_card()
		connected_unit = ConnectedUnitCodeType.to_value(button_card.connected_unit) if button_card else ConnectedUnitCodeType.NONE_VALUE
		self.loading = True
		try:
			self.update_button_set_names()
			self.update_connected_unit_entries(connected_unit)
			state = UI.NORMAL if button_card else UI.DISABLED
			self.button_set_dropdown['state'] = state
			self.connected_unit_dropdown.entry['state'] = state
			self.connected_unit_dropdown.dropdown['state'] = state
			if button_card:
				self.button_set.set(0 if button_card.button_set is None else button_card.button_set + 1)
				self.connected_unit.set(connected_unit)
		finally:
			self.loading = False
		self.update_jump_buttons()

	def update_jump_buttons(self) -> None:
		# Each jump is only enabled while its field references an entry
		button_card = self.selected_button_card()
		button_set = button_card.button_set if button_card else None
		can_jump_button_set = button_set is not None and self.delegate.can_jump(JumpTarget.button_sets, button_set)
		self.button_set_jump_button['state'] = UI.NORMAL if can_jump_button_set else UI.DISABLED
		connected_unit = ConnectedUnitCodeType.to_value(button_card.connected_unit) if button_card else ConnectedUnitCodeType.NONE_VALUE
		can_jump_connected_unit = connected_unit != ConnectedUnitCodeType.NONE_VALUE and self.delegate.can_jump(JumpTarget.button_cards, connected_unit)
		self.connected_unit_jump_button['state'] = UI.NORMAL if can_jump_connected_unit else UI.DISABLED

	def jump_to_button_set(self) -> None:
		button_card = self.selected_button_card()
		if button_card and button_card.button_set is not None:
			self.delegate.jump(JumpTarget.button_sets, button_card.button_set)

	def jump_to_connected_unit(self) -> None:
		button_card = self.selected_button_card()
		if button_card is None:
			return
		connected_unit = ConnectedUnitCodeType.to_value(button_card.connected_unit)
		if connected_unit != ConnectedUnitCodeType.NONE_VALUE:
			self.delegate.jump(JumpTarget.button_cards, connected_unit)

	def mark_edited(self) -> None:
		self.graft_data.edited = True
		self.delegate.update_status_bar()

	def button_set_changed(self, index: int) -> None:
		button_set = None if index == 0 else index - 1
		button_card = self.selected_button_card()
		if not self.loading and button_card and button_card.button_set != button_set:
			button_card.button_set = button_set
			self.mark_edited()
			self.update_jump_buttons()

	def connected_unit_changed(self, value: int) -> None:
		connected_unit = ConnectedUnitCodeType.from_value(value)
		button_card = self.selected_button_card()
		if not self.loading and button_card and button_card.connected_unit != connected_unit:
			button_card.connected_unit = connected_unit
			self.mark_edited()
			self.update_jump_buttons()
