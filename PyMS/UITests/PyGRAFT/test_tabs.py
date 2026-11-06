
from .utils import PyGRAFTTestCase, TAB_TITLES, SELECT_OPEN, ASK_YES_NO_CANCEL

from ...PyGRAFT.Tabs import ReqGraftTab, ButtonCardsTab, ButtonSetsTab, StatInfoTab
from ...FileFormats.Graft import ButtonsGraft
from ...Utilities import UIKit as UI

import io

from unittest import mock

class Test_PyGRAFT_tabs(PyGRAFTTestCase):
	def test_tabs_in_order(self) -> None:
		gui = self.open_pygraft()
		self.assertEqual(tuple(sorted(gui.notebook.pages, key=lambda title: gui.notebook.pages[title][1])), TAB_TITLES)

	def test_list_starts_with_button_sets(self) -> None:
		gui = self.open_pygraft()
		self.assertIsInstance(gui.active_tab(), ButtonSetsTab)
		self.assertEqual(len(self.list_entries(gui)), len(gui.buttons_data.graft.button_sets))
		self.assertEqual(self.list_selection(gui), [0])

	def test_list_shows_active_tabs_entries(self) -> None:
		gui = self.open_pygraft()
		tab = self.display_tab(gui, 'Unit Training Reqs.')
		assert isinstance(tab, ReqGraftTab)
		self.assertIs(tab.get_graft_data(), gui.units_data)
		entries = self.list_entries(gui)
		self.assertEqual(len(entries), len(gui.units_data.entry_ids(gui.data_context)))
		self.assertIn('Terran Marine', entries[0])
		self.assertEqual(self.list_selection(gui), [0])

	def test_switching_tabs_repopulates_list(self) -> None:
		gui = self.open_pygraft()
		self.display_tab(gui, 'Button Cards')
		self.assertEqual(len(self.list_entries(gui)), len(gui.buttons_data.graft.button_cards))
		self.display_tab(gui, 'Button Sets')
		self.assertEqual(len(self.list_entries(gui)), len(gui.buttons_data.graft.button_sets))
		self.display_tab(gui, 'Unit Stat Info')
		self.assertEqual(len(self.list_entries(gui)), len(gui.buttons_data.graft.stat_info))
		self.display_tab(gui, 'Order Reqs.')
		self.assertEqual(len(self.list_entries(gui)), len(gui.orders_data.entry_ids(gui.data_context)))

	def test_req_list_shows_every_dat_entry_dimming_ones_without_scripts(self) -> None:
		gui = self.open_pygraft()
		self.display_tab(gui, 'Order Reqs.')
		entry_ids = gui.orders_data.entry_ids(gui.data_context)
		self.assertEqual(entry_ids, list(range(gui.data_context.order_entry_count)))
		self.assertEqual(len(self.list_entries(gui)), len(entry_ids))
		dimmed_foreground = gui.listbox.listbox.cget('disabledforeground')
		for index, entry_id in enumerate(entry_ids):
			foreground = gui.listbox.itemcget(index, 'foreground')
			if gui.orders_data.has_script(entry_id):
				self.assertEqual(foreground, '')
			else:
				self.assertEqual(foreground, dimmed_foreground)
		self.display_tab(gui, 'Button Cards')
		self.assertTrue(all(gui.listbox.itemcget(index, 'foreground') == '' for index in range(len(self.list_entries(gui)))))

	def test_list_selection_selects_entry_in_tab(self) -> None:
		gui = self.open_pygraft()
		tab = self.display_tab(gui, 'Button Sets')
		self.select_in_list(gui, 7)
		self.assertEqual(tab.selected, 7)
		self.assertIn(self.list_entries(gui)[7].strip(), tab.placeholder.get())

	def test_each_tab_keeps_its_selection(self) -> None:
		gui = self.open_pygraft()
		self.select_in_list(gui, 3)
		self.display_tab(gui, 'Unit Stat Info')
		self.assertEqual(self.list_selection(gui), [0])
		self.select_in_list(gui, 12)
		self.display_tab(gui, 'Button Sets')
		self.assertEqual(self.list_selection(gui), [3])
		self.display_tab(gui, 'Unit Stat Info')
		self.assertEqual(self.list_selection(gui), [12])

	def test_buttons_tabs_share_one_file(self) -> None:
		gui = self.open_pygraft()
		buttons_tabs = [tab for tab in gui.tabs if isinstance(tab, (ButtonCardsTab, ButtonSetsTab, StatInfoTab))]
		self.assertEqual(len(buttons_tabs), 3)
		for tab in buttons_tabs:
			self.assertIs(tab.get_graft_data(), gui.buttons_data)
		self.display_tab(gui, 'Button Cards')
		gui.buttons_data.edited = True
		for title in ('Button Sets', 'Unit Stat Info'):
			self.display_tab(gui, title)
			self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)
		self.display_tab(gui, 'Unit Training Reqs.')
		self.assertEqual(str(gui.editstatus['state']), UI.DISABLED)

	def test_open_known_file_name_shows_its_first_tab(self) -> None:
		gui = self.open_pygraft()
		path = ButtonsGraft.default_path()
		with mock.patch(SELECT_OPEN, return_value=path):
			gui.open()
		self.pump(gui)
		self.assertIsInstance(gui.active_tab(), ButtonSetsTab)
		self.assertEqual(gui.buttons_data.file_path, path)
		self.assertEqual(gui.status.get(), path)

	def test_open_unknown_file_name_loads_into_active_tabs_file(self) -> None:
		gui = self.open_pygraft()
		self.display_tab(gui, 'Order Reqs.')
		with mock.patch(SELECT_OPEN, return_value='custom_orders.graft'), \
				mock.patch.object(gui.orders_data, 'load', return_value=[]) as load:
			gui.open()
		load.assert_called_once_with('custom_orders.graft')
		self.assertIs(gui.active_tab().get_graft_data(), gui.orders_data)

	def test_import_text_marks_active_file_edited(self) -> None:
		gui = self.open_pygraft()
		self.display_tab(gui, 'Upgrade Research Reqs.')
		output = io.StringIO()
		gui.upgrades_data.export_text(output, gui.data_context)
		# A path that doesn't exist is read as the code itself
		with mock.patch(SELECT_OPEN, return_value=output.getvalue()):
			gui.iimport()
		self.assertTrue(gui.upgrades_data.edited)
		self.assertIsNone(gui.upgrades_data.file_path)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)
		self.assertFalse(gui.units_data.edited)

	def test_check_saved_only_asks_about_edited_files(self) -> None:
		gui = self.open_pygraft()
		gui.research_data.edited = True
		with mock.patch(ASK_YES_NO_CANCEL, return_value=False) as ask:
			gui.check_saved()
		ask.assert_called_once()
		self.assertIn('Research.graft', ask.call_args.kwargs['message'])

	def test_new_resets_active_file_after_confirming(self) -> None:
		gui = self.open_pygraft()
		self.display_tab(gui, 'Unit Training Reqs.')
		gui.units_data.edited = True
		gui.units_data.file_path = 'mod/Units.graft'
		with mock.patch(ASK_YES_NO_CANCEL, return_value=False):
			gui.new()
		self.assertFalse(gui.units_data.edited)
		self.assertIsNone(gui.units_data.file_path)
		self.assertEqual(gui.status.get(), 'Units.graft')

	def test_status_bar_layout_matches_other_programs(self) -> None:
		gui = self.open_pygraft()
		statusbar = gui.editstatus.master
		assert statusbar is not None
		slaves = sorted(statusbar.grid_slaves(), key=lambda widget: int(widget.grid_info()['column']))
		self.assertEqual(len(slaves), 3)
		self.assertIs(slaves[1], gui.editstatus)
		# The edited icon sits right after the path, not pushed to the far edge
		self.assertEqual(statusbar.grid_columnconfigure(0)['weight'], 60)

	def test_status_bar_shows_active_tabs_entry_count(self) -> None:
		gui = self.open_pygraft()
		self.assertEqual(gui.entry_count.get(), f'{len(gui.buttons_data.graft.button_sets)} entries')
		self.display_tab(gui, 'Button Cards')
		self.assertEqual(gui.entry_count.get(), f'{len(gui.buttons_data.graft.button_cards)} entries')
