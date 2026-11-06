
from .utils import PyGRAFTTestCase

from ...PyGRAFT.PyGRAFT import PyGRAFT
from ...PyGRAFT.Tabs import GraftTab, ButtonCardsTab
from ...FileFormats.Graft.Definitions import NO_CONNECTED_UNIT

from typing import cast

class Test_PyGRAFT_button_cards_tab(PyGRAFTTestCase):
	def open_button_cards(self) -> tuple[PyGRAFT, ButtonCardsTab]:
		gui = self.open_pygraft()
		tab = cast(ButtonCardsTab, self.display_tab(gui, 'Button Cards'))
		return gui, tab

	def test_button_set_dropdown_lists_none_and_every_button_set(self) -> None:
		gui, tab = self.open_button_cards()
		button_sets = gui.buttons_data.graft.button_sets
		entries = tab.button_set_dropdown.entries
		self.assertEqual(len(entries), len(button_sets) + 1)
		self.assertEqual(entries[0], 'None')
		self.assertEqual(entries[1].strip(), GraftTab.format_entry(0, len(button_sets) - 1, gui.data_context.button_set_name(0) or 'Button Set 0').strip())

	def test_connected_unit_dropdown_lists_every_unit_and_none(self) -> None:
		gui, tab = self.open_button_cards()
		unit_names = gui.data_context.unit_display_names()
		self.assertEqual(tab.connected_unit_dropdown.dropdown.entries, [*unit_names, 'None'])

	def test_selecting_card_loads_its_fields(self) -> None:
		gui, tab = self.open_button_cards()
		for card_id in (0, 16, 227, 240):
			self.select_in_list(gui, card_id)
			card = gui.buttons_data.graft.button_cards[card_id]
			self.assertEqual(tab.button_set.get(), 0 if card.button_set is None else card.button_set + 1)
			self.assertEqual(tab.connected_unit.get(), NO_CONNECTED_UNIT if card.connected_unit is None else card.connected_unit)
		self.select_in_list(gui, 16)
		self.assertEqual(tab.connected_unit_dropdown.dropdown.text.get(), gui.data_context.unit_display_name(1))
		self.select_in_list(gui, 0)
		self.assertEqual(tab.connected_unit_dropdown.dropdown.text.get(), 'None')
		self.assertFalse(gui.buttons_data.edited)

	def test_card_without_button_set_shows_none(self) -> None:
		gui, tab = self.open_button_cards()
		card_id = next(card_id for card_id, card in enumerate(gui.buttons_data.graft.button_cards) if card.button_set is None)
		self.select_in_list(gui, card_id)
		self.assertEqual(tab.button_set.get(), 0)
		self.assertEqual(tab.button_set_dropdown.text.get(), 'None')

	def test_choosing_button_set_edits_selected_card(self) -> None:
		gui, tab = self.open_button_cards()
		self.select_in_list(gui, 3)
		cards = gui.buttons_data.graft.button_cards
		other = (cards[4].button_set, cards[4].connected_unit)
		tab.button_set_dropdown.set(6)
		self.assertEqual(cards[3].button_set, 5)
		self.assertTrue(gui.buttons_data.edited)
		tab.button_set_dropdown.set(0)
		self.assertIsNone(cards[3].button_set)
		self.assertEqual((cards[4].button_set, cards[4].connected_unit), other)

	def test_choosing_connected_unit_edits_selected_card(self) -> None:
		gui, tab = self.open_button_cards()
		self.select_in_list(gui, 3)
		card = gui.buttons_data.graft.button_cards[3]
		tab.connected_unit_dropdown.dropdown.set(12)
		self.assertEqual(tab.connected_unit.get(), 12)
		self.assertEqual(card.connected_unit, 12)
		self.assertTrue(gui.buttons_data.edited)
		tab.connected_unit_dropdown.dropdown.set(len(gui.data_context.unit_display_names()))
		self.assertEqual(tab.connected_unit.get(), NO_CONNECTED_UNIT)
		self.assertIsNone(card.connected_unit)

	def test_entering_connected_unit_id_selects_unit(self) -> None:
		gui, tab = self.open_button_cards()
		self.select_in_list(gui, 3)
		tab.connected_unit.set(7)
		self.assertEqual(gui.buttons_data.graft.button_cards[3].connected_unit, 7)
		self.assertEqual(tab.connected_unit_dropdown.dropdown.text.get(), gui.data_context.unit_display_name(7))
		tab.connected_unit.set(NO_CONNECTED_UNIT)
		self.assertIsNone(gui.buttons_data.graft.button_cards[3].connected_unit)

	def test_connected_unit_entry_only_accepts_units_or_none(self) -> None:
		gui, tab = self.open_button_cards()
		self.select_in_list(gui, 16)
		card = gui.buttons_data.graft.button_cards[16]
		tab.connected_unit.set(len(gui.data_context.unit_display_names()))
		self.assertEqual(tab.connected_unit.get(), 1)
		self.assertEqual(card.connected_unit, 1)
		self.assertFalse(gui.buttons_data.edited)

	def test_loading_unknown_connected_unit_keeps_it(self) -> None:
		gui, tab = self.open_button_cards()
		unit_count = len(gui.data_context.unit_display_names())
		cards = gui.buttons_data.graft.button_cards
		cards[5].connected_unit = unit_count + 10
		self.select_in_list(gui, 5)
		self.assertEqual(tab.connected_unit.get(), unit_count + 10)
		self.assertEqual(tab.connected_unit_dropdown.dropdown.text.get(), f'Unit {unit_count + 10}')
		self.select_in_list(gui, 6)
		self.assertEqual(tab.connected_unit_dropdown.dropdown.entries, [*gui.data_context.unit_display_names(), 'None'])
		self.assertEqual(cards[5].connected_unit, unit_count + 10)
		self.assertIsNone(cards[6].connected_unit)
		self.assertFalse(gui.buttons_data.edited)

	def test_fields_have_tooltips(self) -> None:
		_, tab = self.open_button_cards()
		for widget, name in ((tab.button_set_dropdown.master, 'Button Set'), (tab.connected_unit_dropdown.master, 'Connected Unit')):
			self.assertTrue(getattr(widget, '_tooltip_Tooltip').text.startswith(f'{name}:\n'))
