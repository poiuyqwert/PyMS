from .utils import PyGRAFTTestCase

from ...PyGRAFT.PyGRAFT import PyGRAFT
from ...PyGRAFT.Tabs import GraftTab, StatInfoTab
from ...FileFormats.Graft.CodeHandlers import StatInfoCodeCommands
from ...FileFormats.Graft.Definitions import STAT_PRESETS
from ...Utilities import UIKit as UI

from typing import cast

class Test_PyGRAFT_stat_info_tab(PyGRAFTTestCase):
	def open_stat_info(self) -> tuple[PyGRAFT, StatInfoTab]:
		gui = self.open_pygraft()
		tab = cast(StatInfoTab, self.display_tab(gui, 'Unit Stat Info'))
		return gui, tab

	def test_dropdowns_list_the_functions(self) -> None:
		_, tab = self.open_stat_info()
		self.assertEqual(tab.status_dropdown.entries, [command.display_name for command in StatInfoCodeCommands.status_function_commands])
		self.assertEqual(tab.display_dropdown.entries, [command.display_name for command in StatInfoCodeCommands.display_function_commands])

	def test_selecting_unit_loads_its_stat_info(self) -> None:
		gui, tab = self.open_stat_info()
		for unit_id in (0, 7, 106):
			self.select_in_list(gui, unit_id)
			stat_info = gui.buttons_data.graft.stat_info[unit_id]
			self.assertEqual(tab.status_function.get(), stat_info.status_function)
			self.assertEqual(tab.display_function.get(), stat_info.display_function)
			self.assertEqual(tab.debug_unit_id.get(), stat_info.debug_unit_id)
			self.assertEqual(tab.status_dropdown.text.get(), StatInfoCodeCommands.status_function_commands[stat_info.status_function].display_name)
		self.assertFalse(gui.buttons_data.edited)

	def test_changing_functions_edits_selected_unit(self) -> None:
		gui, tab = self.open_stat_info()
		self.select_in_list(gui, 3)
		stat_info = gui.buttons_data.graft.stat_info[3]
		other = gui.buttons_data.graft.stat_info[4].pack()
		new_status = (stat_info.status_function + 1) % len(StatInfoCodeCommands.status_function_commands)
		tab.status_dropdown.set(new_status)
		self.assertEqual(stat_info.status_function, new_status)
		self.assertTrue(gui.buttons_data.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)
		new_display = (stat_info.display_function + 1) % len(StatInfoCodeCommands.display_function_commands)
		tab.display_dropdown.set(new_display)
		self.assertEqual(stat_info.display_function, new_display)
		self.assertEqual(gui.buttons_data.graft.stat_info[4].pack(), other)

	def test_presets_menu_lists_presets(self) -> None:
		_, tab = self.open_stat_info()
		labels = [tab.presets_menu.entrycget(index, 'label') for index in range(len(STAT_PRESETS))]
		self.assertEqual(labels, [preset.name for preset in STAT_PRESETS])
		self.assertEqual(tab.presets_menu.index('end'), len(STAT_PRESETS) - 1)

	def test_applying_preset_sets_both_functions(self) -> None:
		gui, tab = self.open_stat_info()
		self.select_in_list(gui, 5)
		stat_info = gui.buttons_data.graft.stat_info[5]
		for index, preset in enumerate(STAT_PRESETS):
			tab.presets_menu.invoke(index)
			self.assertEqual((stat_info.status_function, stat_info.display_function), (preset.status_function, preset.display_function))
			self.assertEqual((tab.status_function.get(), tab.display_function.get()), (preset.status_function, preset.display_function))

	def test_choosing_debug_unit_sets_entry(self) -> None:
		gui, tab = self.open_stat_info()
		self.select_in_list(gui, 0)
		tab.debug_unit_dropdown.dropdown.set(12)
		self.assertEqual(tab.debug_unit_id.get(), 12)
		self.assertEqual(gui.buttons_data.graft.stat_info[0].debug_unit_id, 12)
		self.assertTrue(gui.buttons_data.edited)

	def test_debug_unit_id_can_be_any_number(self) -> None:
		gui, tab = self.open_stat_info()
		self.select_in_list(gui, 0)
		tab.debug_unit_id.set(5000)
		self.assertEqual(tab.debug_unit_id.get(), 5000)
		self.assertEqual(gui.buttons_data.graft.stat_info[0].debug_unit_id, 5000)
		self.assertEqual(tab.debug_unit_dropdown.dropdown.text.get(), 'Unknown')
		self.select_in_list(gui, 1)
		self.select_in_list(gui, 0)
		self.assertEqual(tab.debug_unit_id.get(), 5000)

	def test_fields_and_presets_have_tooltips(self) -> None:
		_, tab = self.open_stat_info()
		tooltip_widgets = (tab.status_dropdown.master, tab.display_dropdown.master, tab.presets_button, tab.debug_unit_dropdown.master)
		for widget, name in zip(tooltip_widgets, ('Status Func.', 'Display Func.', 'Presets', 'Unit ID')):
			self.assertTrue(getattr(widget, '_tooltip_Tooltip').text.startswith(f'{name}:\n'))

	def test_help_tooltips_show_chosen_functions_help(self) -> None:
		gui, tab = self.open_stat_info()
		self.select_in_list(gui, 0)
		stat_info = gui.buttons_data.graft.stat_info[0]
		def assert_help(status_function: int, display_function: int) -> None:
			status_command = StatInfoCodeCommands.status_function_commands[status_function]
			display_command = StatInfoCodeCommands.display_function_commands[display_function]
			self.assertEqual(tab.status_help.text, GraftTab.tip_text(status_command.display_name, status_command.help_text))
			self.assertEqual(tab.display_help.text, GraftTab.tip_text(display_command.display_name, display_command.help_text))
		assert_help(stat_info.status_function, stat_info.display_function)
		tab.status_dropdown.set(4)
		tab.display_dropdown.set(8)
		assert_help(4, 8)
		self.assertEqual(tab.status_help.parent.cget('text'), '?')
