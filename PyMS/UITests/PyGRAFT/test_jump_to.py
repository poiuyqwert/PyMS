from .utils import PyGRAFTTestCase, ASK_YES_NO_CANCEL

from ...PyGRAFT.PyGRAFT import PyGRAFT
from ...PyGRAFT.JumpTarget import JumpTarget
from ...PyGRAFT.Tabs import GraftTab, ButtonCardsTab, ButtonSetsTab, ReqGraftTab
from ...PyGRAFT.ButtonSetEditor.ButtonSetBuilderView import ButtonSetBuilderView
from ...FileFormats.Graft import Button
from ...FileFormats.Graft.CodeHandlers import ButtonCodeCommands, RequirementCodeCommands
from ...FileFormats.Graft.CodeHandlers.CodeTypes import ConnectedUnitCodeType
from ...Utilities import UIKit as UI

from unittest import mock

from typing import cast

class Test_PyGRAFT_jump_to(PyGRAFTTestCase):
	def assert_selected(self, gui: PyGRAFT, tab_title: str, index: int) -> None:
		tab = cast(GraftTab, gui.notebook.pages[tab_title][0])
		self.assertIs(gui.active_tab(), tab)
		self.assertEqual(tab.selected, index)
		self.assertEqual(self.list_selection(gui), [index])

	def invoke_button(self, button: UI.Button) -> None:
		button.invoke()
		self.pump(button)

	# Main window

	def test_can_jump_checks_the_entry_exists(self) -> None:
		gui = self.open_pygraft()
		self.assertTrue(gui.can_jump(JumpTarget.button_sets, 0))
		self.assertFalse(gui.can_jump(JumpTarget.button_sets, len(gui.buttons_data.graft.button_sets)))
		self.assertTrue(gui.can_jump(JumpTarget.button_cards, len(gui.buttons_data.graft.button_cards) - 1))
		self.assertFalse(gui.can_jump(JumpTarget.unit_reqs, -1))
		self.assertTrue(gui.can_jump(JumpTarget.unit_reqs, 0))
		self.assertFalse(gui.can_jump(JumpTarget.unit_reqs, 100000))

	def test_jump_to_another_tab_selects_the_entry(self) -> None:
		gui = self.open_pygraft()
		gui.jump(JumpTarget.research_reqs, 3)
		self.pump(gui)
		tab = cast(ReqGraftTab, gui.notebook.pages['Tech Research Reqs.'][0])
		index = tab.index_of_entry(3)
		assert index is not None
		self.assert_selected(gui, 'Tech Research Reqs.', index)
		self.assertEqual(tab.editor.builder_view.entry_id, 3)

	def test_jump_to_missing_entry_does_nothing(self) -> None:
		gui = self.open_pygraft()
		with mock.patch.object(gui, 'bell') as bell:
			gui.jump(JumpTarget.button_sets, len(gui.buttons_data.graft.button_sets))
		bell.assert_called_once()
		self.assert_selected(gui, 'Button Sets', 0)

	# Button Cards

	def test_button_set_jump(self) -> None:
		gui = self.open_pygraft()
		tab = cast(ButtonCardsTab, self.display_tab(gui, 'Button Cards'))
		self.select_in_list(gui, 3)
		tab.button_set_dropdown.set(6)
		self.assertEqual(str(tab.button_set_jump_button['state']), UI.NORMAL)
		self.invoke_button(tab.button_set_jump_button)
		self.assert_selected(gui, 'Button Sets', 5)

	def test_button_set_jump_disabled_for_none(self) -> None:
		gui = self.open_pygraft()
		tab = cast(ButtonCardsTab, self.display_tab(gui, 'Button Cards'))
		card_id = next(card_id for card_id, card in enumerate(gui.buttons_data.graft.button_cards) if card.button_set is None)
		self.select_in_list(gui, card_id)
		self.assertEqual(str(tab.button_set_jump_button['state']), UI.DISABLED)

	def test_connected_unit_jump(self) -> None:
		gui = self.open_pygraft()
		tab = cast(ButtonCardsTab, self.display_tab(gui, 'Button Cards'))
		self.select_in_list(gui, 16)
		self.assertEqual(str(tab.connected_unit_jump_button['state']), UI.NORMAL)
		self.invoke_button(tab.connected_unit_jump_button)
		self.assert_selected(gui, 'Button Cards', 1)
		self.assertEqual(tab.connected_unit.get(), ConnectedUnitCodeType.NONE_VALUE if gui.buttons_data.graft.button_cards[1].connected_unit is None else gui.buttons_data.graft.button_cards[1].connected_unit)
		tab.connected_unit.set(ConnectedUnitCodeType.NONE_VALUE)
		self.assertEqual(str(tab.connected_unit_jump_button['state']), UI.DISABLED)

	def test_jump_buttons_have_tooltips(self) -> None:
		gui = self.open_pygraft()
		tab = cast(ButtonCardsTab, self.display_tab(gui, 'Button Cards'))
		self.assertEqual(getattr(tab.button_set_jump_button, '_tooltip_Tooltip').text, 'Jump To Button Set')
		self.assertEqual(getattr(tab.connected_unit_jump_button, '_tooltip_Tooltip').text, 'Jump To Button Card')

	# Button Set Builder

	def open_builder(self, buttons: list[Button]) -> tuple[PyGRAFT, ButtonSetBuilderView]:
		gui = self.open_pygraft()
		tab = cast(ButtonSetsTab, self.display_tab(gui, 'Button Sets'))
		view = tab.editor.builder_view
		gui.buttons_data.graft.button_sets[0].buttons = buttons
		view.load(0, view.entry_name)
		self.pump(view)
		return gui, view

	def test_action_param_jump(self) -> None:
		gui, view = self.open_builder([Button(condition=ButtonCodeCommands.Always.function_index, action=ButtonCodeCommands.Train.function_index, action_param=7)])
		editor = view.settings_view.action_editor
		self.assertTrue(editor.jump_button.winfo_ismapped())
		self.assertEqual(editor.jump_tooltip.text, 'Jump To Unit Training Reqs.')
		self.invoke_button(editor.jump_button)
		tab = cast(ReqGraftTab, gui.notebook.pages['Unit Training Reqs.'][0])
		self.assert_selected(gui, 'Unit Training Reqs.', cast(int, tab.index_of_entry(7)))

	def test_condition_param_jump(self) -> None:
		gui, view = self.open_builder([Button(condition=ButtonCodeCommands.CanPlayerUseTech.function_index, condition_param=2, action=ButtonCodeCommands.Nothing.function_index)])
		editor = view.settings_view.condition_editor
		self.assertEqual(editor.jump_tooltip.text, 'Jump To Tech Usage Reqs.')
		self.invoke_button(editor.jump_button)
		tab = cast(ReqGraftTab, gui.notebook.pages['Tech Usage Reqs.'][0])
		self.assert_selected(gui, 'Tech Usage Reqs.', cast(int, tab.index_of_entry(2)))

	def test_show_button_card_jump(self) -> None:
		gui, view = self.open_builder([Button(condition=ButtonCodeCommands.Always.function_index, action=ButtonCodeCommands.ShowButtonCard.function_index, action_param=230)])
		self.invoke_button(view.settings_view.action_editor.jump_button)
		self.assert_selected(gui, 'Button Cards', 230)

	def test_unused_or_missing_param_has_no_jump(self) -> None:
		_, view = self.open_builder([Button(condition=ButtonCodeCommands.Always.function_index, action=ButtonCodeCommands.Siege.function_index)])
		self.assertFalse(view.settings_view.action_editor.jump_button.winfo_ismapped())
		self.assertFalse(view.settings_view.condition_editor.jump_button.winfo_ismapped())

	def test_changing_function_shows_the_jump(self) -> None:
		_, view = self.open_builder([Button(condition=ButtonCodeCommands.Always.function_index, action=ButtonCodeCommands.Nothing.function_index)])
		editor = view.settings_view.action_editor
		self.assertFalse(editor.jump_button.winfo_ismapped())
		editor.function.set(ButtonCodeCommands.Upgrade.function_index)
		self.pump(view)
		self.assertTrue(editor.jump_button.winfo_ismapped())
		self.assertEqual(editor.jump_tooltip.text, 'Jump To Upgrade Research Reqs.')

	def test_jump_disabled_without_button(self) -> None:
		_, view = self.open_builder([])
		editor = view.settings_view.condition_editor
		editor.load(ButtonCodeCommands.CanUpgrade.function_index, 0)
		editor.set_enabled(False)
		self.assertEqual(str(editor.jump_button['state']), UI.DISABLED)

	# Requirements Builder

	def test_opcode_param_jump(self) -> None:
		gui = self.open_pygraft()
		tab = cast(ReqGraftTab, self.display_tab(gui, 'Upgrade Research Reqs.'))
		view = tab.editor.builder_view
		row = next(row for row in view.rows if row.cmd_def is RequirementCodeCommands.CurrentUnitIs)
		self.assertTrue(row.jump_button.winfo_ismapped())
		unit_id = row.params[0]
		self.invoke_button(row.jump_button)
		units_tab = cast(ReqGraftTab, gui.notebook.pages['Unit Training Reqs.'][0])
		self.assert_selected(gui, 'Unit Training Reqs.', cast(int, units_tab.index_of_entry(unit_id)))

	def test_opcode_without_param_has_no_jump(self) -> None:
		gui = self.open_pygraft()
		tab = cast(ReqGraftTab, self.display_tab(gui, 'Unit Training Reqs.'))
		row = next(row for row in tab.editor.builder_view.rows if not row.params)
		self.assertFalse(row.jump_button.winfo_ismapped())

	def test_jump_with_unapplied_changes_asks_first(self) -> None:
		gui = self.open_pygraft()
		tab = cast(ReqGraftTab, self.display_tab(gui, 'Upgrade Research Reqs.'))
		view = tab.editor.builder_view
		view.add_opcode()
		self.pump(view)
		self.assertTrue(view.is_edited())
		row = next(row for row in view.rows if row.cmd_def is RequirementCodeCommands.CurrentUnitIs)
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None) as ask:
			self.invoke_button(row.jump_button)
		ask.assert_called_once()
		self.assert_selected(gui, 'Upgrade Research Reqs.', 0)
		self.assertTrue(view.is_edited())
		with mock.patch(ASK_YES_NO_CANCEL, return_value=False):
			self.invoke_button(row.jump_button)
		self.assertEqual(gui.active_tab().get_graft_data(), gui.units_data)
		self.assertFalse(view.is_edited())
