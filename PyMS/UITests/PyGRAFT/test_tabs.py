
from .utils import PyGRAFTTestCase, TAB_TITLES, SELECT_OPEN, ASK_YES_NO_CANCEL

from ...PyGRAFT.PyGRAFT import PyGRAFT
from ...PyGRAFT.GraftData import AnyGraftData
from ...PyGRAFT.Tabs import ReqGraftTab, ButtonCardsTab, ButtonSetsTab, StatInfoTab
from ...FileFormats.Graft import ButtonsGraft, UnitsGraft, UpgradesGraft, ResearchGraft, TechGraft, OrdersGraft, Button, ButtonSet, FGP
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities import UIKit as UI

import io

from unittest import mock

ASK_YES_NO = 'tkinter.messagebox.askyesno'
SHOW_ERROR = 'tkinter.messagebox.showerror'
WARNING_DIALOG = 'PyMS.PyGRAFT.PyGRAFT.WarningDialog'

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
		assert isinstance(tab, ButtonSetsTab)
		self.assertEqual(tab.editor.builder_view.entry_id, 7)
		self.assertEqual(tab.editor.builder_view.entry_name, self.list_entries(gui)[7].strip())

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

	def import_fgp(self, gui: PyGRAFT, fgp_contents: FGP, *, continue_import: bool = False) -> dict[str, mock.MagicMock]:
		def load(fgp: FGP, _path: str) -> list[PyMSWarning]:
			fgp.requirements = fgp_contents.requirements
			fgp.button_sets = fgp_contents.button_sets
			fgp.units = fgp_contents.units
			return []
		with mock.patch(SELECT_OPEN, return_value='project.fgp'), \
				mock.patch.object(FGP, 'load', autospec=True, side_effect=load), \
				mock.patch(ASK_YES_NO, return_value=continue_import) as ask_yes_no, \
				mock.patch(SHOW_ERROR) as show_error, \
				mock.patch(WARNING_DIALOG) as warning_dialog:
			gui.import_fgp()
		self.pump(gui)
		return {'ask_yes_no': ask_yes_no, 'show_error': show_error, 'warning_dialog': warning_dialog}

	def assert_unchanged(self, gui: PyGRAFT, before: dict[str, bytes], *, skip: AnyGraftData | None = None) -> None:
		for graft_data in gui.all_graft_data():
			if graft_data is not skip:
				self.assertFalse(graft_data.edited, graft_data.file_name)
				self.assertEqual(graft_data.save_bytes(), before[graft_data.file_name], graft_data.file_name)

	def test_import_fgp_marks_only_changed_files_edited(self) -> None:
		gui = self.open_pygraft()
		fgp = FGP()
		fgp.requirements[UnitsGraft] = {0: [0xFF11, 0xFFFF]}
		before = {graft_data.file_name: graft_data.save_bytes() for graft_data in gui.all_graft_data()}
		dialogs = self.import_fgp(gui, fgp)
		for dialog in dialogs.values():
			dialog.assert_not_called()
		self.assertTrue(gui.units_data.edited)
		self.assertNotEqual(gui.units_data.save_bytes(), before['Units.graft'])
		self.assert_unchanged(gui, before, skip=gui.units_data)

	def invalid_buttons_fgp(self) -> FGP:
		fgp = FGP()
		fgp.requirements[UnitsGraft] = {0: [0xFF11, 0xFFFF]}
		fgp.button_sets = {0: ButtonSet([Button(condition=3, action=600)])}
		return fgp

	def test_import_fgp_with_failed_files_asks_to_continue(self) -> None:
		gui = self.open_pygraft()
		dialogs = self.import_fgp(gui, self.invalid_buttons_fgp())
		dialogs['ask_yes_no'].assert_called_once()
		message = dialogs['ask_yes_no'].call_args.kwargs['message']
		self.assertIn('Buttons.graft: Button set 0 uses unknown button action 600', message)
		self.assertNotIn('Units.graft', message)

	def test_aborted_import_fgp_changes_no_files(self) -> None:
		gui = self.open_pygraft()
		before = {graft_data.file_name: graft_data.save_bytes() for graft_data in gui.all_graft_data()}
		self.import_fgp(gui, self.invalid_buttons_fgp(), continue_import=False)
		self.assert_unchanged(gui, before)

	def test_continued_import_fgp_applies_the_other_files(self) -> None:
		gui = self.open_pygraft()
		before = {graft_data.file_name: graft_data.save_bytes() for graft_data in gui.all_graft_data()}
		self.import_fgp(gui, self.invalid_buttons_fgp(), continue_import=True)
		self.assertTrue(gui.units_data.edited)
		self.assertNotEqual(gui.units_data.save_bytes(), before['Units.graft'])
		self.assert_unchanged(gui, before, skip=gui.units_data)

	def test_import_fgp_with_every_file_failed_is_an_error(self) -> None:
		gui = self.open_pygraft()
		fgp = FGP()
		for graft_type in (UnitsGraft, UpgradesGraft, ResearchGraft, TechGraft, OrdersGraft):
			fgp.requirements[graft_type] = {0: [0xFF1F, 0xFFFF]}
		fgp.button_sets = {0: ButtonSet([Button(condition=3, action=600)])}
		before = {graft_data.file_name: graft_data.save_bytes() for graft_data in gui.all_graft_data()}
		dialogs = self.import_fgp(gui, fgp)
		dialogs['ask_yes_no'].assert_not_called()
		dialogs['show_error'].assert_called_once()
		message = dialogs['show_error'].call_args.kwargs['message']
		self.assertIn('None of the files could be imported', message)
		for graft_data in gui.all_graft_data():
			self.assertIn(f'{graft_data.file_name}: ', message)
		self.assert_unchanged(gui, before)

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
