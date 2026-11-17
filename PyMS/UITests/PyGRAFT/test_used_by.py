from .utils import PyGRAFTTestCase

from ...PyGRAFT.PyGRAFT import PyGRAFT
from ...PyGRAFT.Tabs import ButtonSetsTab, GraftTab

from typing import cast

class Test_PyGRAFT_used_by(PyGRAFTTestCase):
	def open_button_sets(self) -> tuple[PyGRAFT, ButtonSetsTab]:
		gui = self.open_pygraft()
		tab = cast(ButtonSetsTab, self.display_tab(gui, 'Button Sets'))
		return gui, tab

	def rows(self, tab: ButtonSetsTab) -> list[str]:
		return [str(row) for row in tab.used_by.listbox.get(0, 'end')]

	def test_lists_the_button_cards_using_the_set(self) -> None:
		gui, tab = self.open_button_sets()
		for set_id in (0, 5):
			self.select_in_list(gui, set_id)
			card_ids = gui.buttons_data.graft.button_cards_using_button_set(set_id)
			self.assertTrue(card_ids)
			self.assertEqual(self.rows(tab), [f'Button Card {card_id}: {gui.data_context.button_card_name(card_id)}' for card_id in card_ids])
			self.assertEqual(tab.used_by.header_text.get(), f'Used By ({len(card_ids)}):')

	def test_unused_set_lists_nothing(self) -> None:
		gui, tab = self.open_button_sets()
		for card in gui.buttons_data.graft.button_cards:
			if card.button_set == 0:
				card.button_set = None
		tab.refresh()
		self.pump(gui)
		self.assertEqual(self.rows(tab), [])
		self.assertEqual(tab.used_by.header_text.get(), 'Used By (0):')

	def test_shown_in_both_modes(self) -> None:
		gui, tab = self.open_button_sets()
		self.assertTrue(tab.used_by.winfo_ismapped())
		tab.editor.notebook.display('Script')
		self.pump(gui)
		self.assertTrue(tab.used_by.winfo_ismapped())
		self.assertTrue(tab.used_by.listbox.winfo_ismapped())

	def test_collapsing_hides_the_list_and_is_remembered(self) -> None:
		gui, tab = self.open_button_sets()
		count = len(self.rows(tab))
		self.assertTrue(gui.config_.show_used_by.value)
		tab.used_by.collapse_button.invoke()
		self.pump(gui)
		self.assertFalse(gui.config_.show_used_by.value)
		self.assertFalse(tab.used_by.listbox.winfo_ismapped())
		self.assertEqual(tab.used_by.header_text.get(), f'Used By ({count})')
		tab.used_by.collapse_button.invoke()
		self.pump(gui)
		self.assertTrue(gui.config_.show_used_by.value)
		self.assertTrue(tab.used_by.listbox.winfo_ismapped())

	def test_double_click_jumps_to_the_button_card(self) -> None:
		gui, tab = self.open_button_sets()
		self.select_in_list(gui, 5)
		card_ids = gui.buttons_data.graft.button_cards_using_button_set(5)
		listbox = tab.used_by.listbox
		listbox.select_set(len(card_ids) - 1)
		tab.used_by.jump_to_selected()
		self.pump(gui)
		cards_tab = cast(GraftTab, gui.notebook.pages['Button Cards'][0])
		self.assertIs(gui.active_tab(), cards_tab)
		self.assertEqual(cards_tab.selected, card_ids[-1])
		self.assertEqual(self.list_selection(gui), [card_ids[-1]])
