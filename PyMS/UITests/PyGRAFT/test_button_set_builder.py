from .utils import PyGRAFTTestCase, ASK_YES_NO_CANCEL

from ...PyGRAFT.PyGRAFT import PyGRAFT
from ...PyGRAFT.Tabs import ButtonSetsTab
from ...PyGRAFT.ButtonSetEditor.ButtonSetBuilderView import ButtonSetBuilderView
from ...PyGRAFT.ButtonSetEditor.ButtonRow import ButtonRow
from ...FileFormats.Graft import Button
from ...FileFormats.Graft.CodeHandlers import ButtonCodeCommands
from ...FileFormats.GRP import GRP, CacheGRP
from ...FileFormats.TBL import TBL
from ...Utilities import UIKit as UI
from ...Utilities import IO

from unittest import mock

ICON_SELECT_DIALOG = 'PyMS.PyGRAFT.ButtonSetEditor.ButtonSettingsView.IconSelectDialog'
ERROR_DIALOG = 'PyMS.PyGRAFT.ButtonSetEditor.ButtonSetBuilderView.ErrorDialog'
MOVE_CODE = 'button {\n\tposition TL\n\ticon 228\n\talways\n\tmove\n\tenabled_str 664\n\tdisabled_str 0\n}\n'
MOVE_BUTTON = Button(position=1, icon=228, condition=3, action=9, enabled_string=664)

def icons_grp(frames: int = 4) -> CacheGRP:
	# A small cmdicons.grp, so the icons can be drawn without the game's files
	grp = GRP()
	grp.load_frames([[[1 if (x + y + frame) % 3 else 0 for x in range(ButtonRow.ICON_WIDTH)] for y in range(ButtonRow.ICON_HEIGHT)] for frame in range(frames)])
	cache = CacheGRP()
	cache.load(IO.output_to_bytes(grp.save))
	return cache

class Test_PyGRAFT_button_set_builder(PyGRAFTTestCase):
	def open_builder(self, *, hover: bool = False) -> tuple[PyGRAFT, ButtonSetBuilderView]:
		def make() -> tuple[PyGRAFT, ButtonSetBuilderView]:
			gui = self.open_pygraft()
			gui.data_context.set_cmdicons_grp(icons_grp())
			tab = self.display_tab(gui, 'Button Sets')
			assert isinstance(tab, ButtonSetsTab)
			return gui, tab.editor.builder_view
		if not hover:
			return make()
		# The window is shown, so the real pointer can be over it, and its events would show/hide the actions too, so only the generated events are used
		original_entered = ButtonRow.pointer_entered
		original_left = ButtonRow.pointer_left
		def generated_entered(row: ButtonRow, event: UI.Event) -> None:
			if event.send_event:
				original_entered(row, event)
		def generated_left(row: ButtonRow, event: UI.Event) -> None:
			if event.send_event:
				original_left(row, event)
		with mock.patch.object(ButtonRow, 'pointer_entered', generated_entered), mock.patch.object(ButtonRow, 'pointer_left', generated_left):
			gui, view = make()
		gui.deiconify()
		self.pump(gui)
		return gui, view

	def set_buttons(self, gui: PyGRAFT, view: ButtonSetBuilderView, buttons: list[Button]) -> None:
		assert view.entry_id is not None
		gui.buttons_data.graft.button_sets[view.entry_id].buttons = buttons
		view.load(view.entry_id, view.entry_name)
		self.pump(view)

	def click_widget(self, widget: UI.Misc) -> None:
		widget.event_generate(UI.Mouse.Click_Left.event(), x=2, y=2)
		self.pump(widget)

	def selected_rows(self, view: ButtonSetBuilderView) -> list[int]:
		return [index for index, row in enumerate(view.rows) if row.selected]

	def assert_edited(self, gui: PyGRAFT) -> None:
		self.assertTrue(gui.buttons_data.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	# Loading

	def test_builder_shows_a_row_for_each_button(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=7, icon=0, enabled_string=1), Button(position=8, icon=1, enabled_string=0), Button(position=9, icon=2, enabled_string=2)])
		buttons = gui.buttons_data.graft.button_sets[0].buttons
		self.assertEqual(len(view.rows), len(buttons))
		self.assertEqual(view.rows[1].string_text.get(), 'No String')
		for row, button in zip(view.rows, buttons):
			self.assertEqual(row.position_text.get(), str(button.position))
			self.assertEqual(row.string_text.get(), view.string_text(button.enabled_string))
			self.assertTrue(row.icon_canvas.find_withtag('icon'))
		self.assertFalse(gui.buttons_data.edited)

	def test_first_button_is_selected(self) -> None:
		gui, view = self.open_builder()
		self.assertEqual(view.selected, 0)
		self.assertEqual(self.selected_rows(view), [0])
		self.assertIs(view.settings_view.button, gui.buttons_data.graft.button_sets[0].buttons[0])

	def test_selecting_a_set_shows_its_buttons(self) -> None:
		gui, view = self.open_builder()
		self.select_in_list(gui, 5)
		self.assertEqual(view.entry_id, 5)
		self.assertEqual(len(view.rows), len(gui.buttons_data.graft.button_sets[5].buttons))

	def test_reloading_the_set_keeps_the_selection(self) -> None:
		gui, view = self.open_builder()
		view.select_button(2)
		gui.refresh()
		self.pump(gui)
		self.assertEqual(view.selected, 2)

	def test_scroll_view_height_is_a_fixed_number_of_rows(self) -> None:
		_, view = self.open_builder()
		self.assertEqual(view.scroll_view.winfo_reqheight(), round(ButtonSetBuilderView.VISIBLE_ROWS * ButtonRow.ROW_HEIGHT))
		self.assertEqual(view.rows[0].winfo_reqheight(), ButtonRow.ROW_HEIGHT)

	def test_no_button_sets_is_read_only(self) -> None:
		gui, view = self.open_builder()
		gui.buttons_data.graft.button_sets = []
		gui.buttons_data.graft.button_cards = []
		gui.refresh()
		self.pump(gui)
		self.assertIsNone(view.entry_id)
		self.assertEqual(view.rows, [])
		self.assertEqual(str(view.add_button_button['state']), UI.DISABLED)
		self.assertEqual(str(view.settings_view.position_dropdown.entry['state']), UI.DISABLED)

	def test_empty_set_disables_the_settings(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [])
		self.assertIsNone(view.selected)
		self.assertIsNone(view.settings_view.button)
		self.assertEqual(str(view.settings_view.find_icon_button['state']), UI.DISABLED)
		self.assertEqual(str(view.add_button_button['state']), UI.NORMAL)

	# Selecting

	def test_clicking_a_row_selects_it(self) -> None:
		gui, view = self.open_builder()
		self.click_widget(view.rows[1].string_label)
		self.assertEqual(view.selected, 1)
		self.assertEqual(self.selected_rows(view), [1])
		self.assertIs(view.settings_view.button, gui.buttons_data.graft.button_sets[0].buttons[1])
		self.click_widget(view.rows[2].icon_canvas)
		self.assertEqual(self.selected_rows(view), [2])
		self.assertFalse(gui.buttons_data.edited)

	def test_selected_row_uses_the_selection_colors(self) -> None:
		_, view = self.open_builder()
		background = UI.Style().lookup('.', 'selectbackground')
		foreground = UI.Style().lookup('.', 'selectforeground')
		self.assertNotEqual(background, '')
		self.assertEqual(view.rows[0].string_label.cget('bg'), background)
		self.assertEqual(view.rows[0].string_label.cget('fg'), foreground)
		self.assertNotEqual(view.rows[1].string_label.cget('bg'), background)

	# Hovering

	def move_pointer(self, view: ButtonSetBuilderView, row: ButtonRow, pattern: str, widget: UI.Misc) -> None:
		# Sends `row` an Enter/Leave with the pointer inside `widget` (without moving the real pointer)
		row.event_generate(pattern, x=5, y=5, rootx=widget.winfo_rootx() + 5, rooty=widget.winfo_rooty() + 5, sendevent=True)
		self.pump(view)

	def shown_actions(self, view: ButtonSetBuilderView) -> list[int]:
		return [index for index, row in enumerate(view.rows) if row.actions_shown()]

	def test_actions_are_only_shown_while_hovered(self) -> None:
		_, view = self.open_builder(hover=True)
		self.assertEqual(self.shown_actions(view), [])
		self.move_pointer(view, view.rows[0], '<Enter>', view.rows[0].string_label)
		self.assertEqual(self.shown_actions(view), [0])
		# Moving onto the row's own widgets keeps them
		self.move_pointer(view, view.rows[0], '<Leave>', view.rows[0].move_up_button)
		self.assertEqual(self.shown_actions(view), [0])
		self.move_pointer(view, view.rows[0], '<Leave>', view.rows[1].string_label)
		self.assertEqual(self.shown_actions(view), [])

	# Editing the list

	def test_move_down_moves_the_button_and_its_selection(self) -> None:
		gui, view = self.open_builder()
		buttons = list(gui.buttons_data.graft.button_sets[0].buttons)
		self.invoke(view.rows[0].move_down_button)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons, [buttons[1], buttons[0], buttons[2]])
		self.assertEqual(view.selected, 1)
		self.assert_edited(gui)

	def test_move_up_is_disabled_on_the_first_row(self) -> None:
		_, view = self.open_builder()
		self.assertEqual(str(view.rows[0].move_up_button['state']), UI.DISABLED)
		self.assertEqual(str(view.rows[-1].move_down_button['state']), UI.DISABLED)
		self.assertEqual(str(view.rows[1].move_up_button['state']), UI.NORMAL)

	def test_delete_removes_the_button(self) -> None:
		gui, view = self.open_builder()
		buttons = list(gui.buttons_data.graft.button_sets[0].buttons)
		view.select_button(2)
		self.invoke(view.rows[2].delete_button)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons, buttons[:2])
		self.assertEqual(len(view.rows), 2)
		self.assertEqual(view.selected, 1)
		self.assert_edited(gui)

	def test_deleting_before_the_selection_keeps_the_selected_button(self) -> None:
		gui, view = self.open_builder()
		buttons = list(gui.buttons_data.graft.button_sets[0].buttons)
		view.select_button(2)
		view.delete_button(0)
		self.pump(view)
		self.assertIs(view.settings_view.button, buttons[2])

	def test_deleting_every_button_clears_the_selection(self) -> None:
		gui, view = self.open_builder()
		for _ in range(3):
			view.delete_button(0)
		self.pump(view)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons, [])
		self.assertIsNone(view.selected)
		self.assertIsNone(view.settings_view.button)

	def test_add_below_inserts_a_new_button_in_a_free_slot(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1), Button(position=2)])
		view.add_button_after(0)
		self.pump(view)
		buttons = gui.buttons_data.graft.button_sets[0].buttons
		self.assertEqual(len(buttons), 3)
		self.assertEqual(buttons[1], Button(position=3, condition=ButtonCodeCommands.Always.function_index, action=ButtonCodeCommands.Nothing.function_index))
		self.assertEqual(view.selected, 1)
		self.assert_edited(gui)

	def test_add_button_adds_to_an_empty_set(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [])
		self.invoke(view.add_button_button)
		self.assertEqual(len(gui.buttons_data.graft.button_sets[0].buttons), 1)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons[0].position, 1)
		self.assertEqual(view.selected, 0)

	def test_new_button_uses_the_first_slot_when_every_slot_is_used(self) -> None:
		self.assertEqual(ButtonSetBuilderView.new_button([Button(position=position) for position in range(1, 10)]).position, 1)

	# Preview

	def test_preview_shows_each_slot(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=7, icon=0), Button(position=8, icon=1), Button(position=9, icon=2)])
		positions = [button.position for button in view.buttons()]
		for position in range(1, 10):
			self.assertEqual(view.preview.slot_text(position, 'number'), str(position))
			self.assertEqual(bool(view.preview.slots[position].find_withtag('icon')), position in positions)
			self.assertIsNone(view.preview.slot_text(position, 'count'))
		self.assertTrue(view.preview.slot_selected(view.buttons()[0].position))
		self.assertEqual([position for position in range(1, 10) if view.preview.slot_selected(position)], [view.buttons()[0].position])

	def test_clicking_a_slot_selects_its_button(self) -> None:
		_, view = self.open_builder()
		position = view.buttons()[2].position
		self.click_widget(view.preview.slots[position])
		self.assertEqual(view.selected, 2)
		self.assertTrue(view.preview.slot_selected(position))

	def test_clicking_an_empty_slot_does_nothing(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1)])
		self.click_widget(view.preview.slots[5])
		self.assertEqual(view.selected, 0)

	def test_clicking_a_shared_slot_cycles_its_buttons(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1, icon=0), Button(position=2), Button(position=1, icon=1)])
		self.assertEqual(view.preview.slot_text(1, 'count'), '1/2')
		self.click_widget(view.preview.slots[1])
		self.assertEqual(view.selected, 2)
		self.assertEqual(view.preview.slot_text(1, 'count'), '2/2')
		self.click_widget(view.preview.slots[1])
		self.assertEqual(view.selected, 0)
		self.assertEqual(view.preview.slot_text(1, 'count'), '1/2')

	def test_shared_slot_keeps_showing_its_button_after_another_is_selected(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1), Button(position=2), Button(position=1)])
		view.select_button(2)
		view.select_button(1)
		self.assertEqual(view.preview.slot_text(1, 'count'), '2/2')
		self.assertFalse(view.preview.slot_selected(1))
		# Clicking the slot selects the button it shows
		self.click_widget(view.preview.slots[1])
		self.assertEqual(view.selected, 2)

	# Button Settings

	def test_settings_show_the_selected_button(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=4, icon=2, condition=ButtonCodeCommands.CanUpgrade.function_index, condition_param=3, action=ButtonCodeCommands.Train.function_index, action_param=7, enabled_string=5, disabled_string=6)])
		settings = view.settings_view
		self.assertEqual(settings.position_dropdown.text.get(), '4 (Middle Left)')
		self.assertEqual(settings.icon.get(), 2)
		self.assertEqual(settings.condition_editor.function.get(), ButtonCodeCommands.CanUpgrade.function_index)
		assert settings.condition_editor.param_value is not None
		self.assertEqual(settings.condition_editor.param_value.get(), 3)
		assert settings.action_editor.param_value is not None
		self.assertEqual(settings.action_editor.param_value.get(), 7)
		self.assertEqual(settings.enabled_string.get(), 5)
		self.assertEqual(settings.disabled_string.get(), 6)
		self.assertTrue(settings.icon_preview.find_withtag('icon'))
		self.assertFalse(gui.buttons_data.edited)

	def test_changing_the_position_moves_the_button(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1)])
		view.settings_view.position.set(4)
		self.pump(view)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons[0].position, 5)
		self.assertEqual(view.rows[0].position_text.get(), '5')
		self.assertTrue(view.preview.slot_selected(5))
		self.assertFalse(view.preview.slots[1].find_withtag('icon'))
		self.assert_edited(gui)

	def test_invalid_position_is_listed(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=12)])
		self.assertEqual(view.settings_view.position_dropdown.text.get(), '12 (Invalid)')
		self.assertEqual([position for position in range(1, 10) if view.preview.slot_selected(position)], [])
		view.settings_view.position.set(0)
		self.pump(view)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons[0].position, 1)
		self.assertEqual(len(view.settings_view.position_dropdown.entries), 9)

	def test_changing_the_icon_updates_the_row(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1, icon=0)])
		image_before = view.rows[0].icon_canvas.itemcget('icon', 'image')
		view.settings_view.icon.set(1)
		self.pump(view)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons[0].icon, 1)
		self.assertNotEqual(view.rows[0].icon_canvas.itemcget('icon', 'image'), image_before)
		self.assert_edited(gui)

	def test_find_icon_sets_the_chosen_icon(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1, icon=0)])
		with mock.patch(ICON_SELECT_DIALOG) as dialog:
			self.invoke(view.settings_view.find_icon_button)
		dialog.assert_called_once()
		self.assertIs(dialog.call_args.kwargs['icon_source'], gui.data_context)
		self.assertIs(dialog.call_args.kwargs['window_geometry'], gui.config_.windows.icon_select)
		self.assertEqual(dialog.call_args.kwargs['selected_index'], 0)
		dialog.call_args.kwargs['delegate'](3)
		self.pump(view)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons[0].icon, 3)

	def test_clicking_the_icon_preview_finds_an_icon(self) -> None:
		_, view = self.open_builder()
		with mock.patch(ICON_SELECT_DIALOG) as dialog:
			self.click_widget(view.settings_view.icon_preview)
		dialog.assert_called_once()

	def test_condition_without_a_param_has_no_param_editor(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1, condition=ButtonCodeCommands.CanUpgrade.function_index, condition_param=4)])
		editor = view.settings_view.condition_editor
		self.assertIsNotNone(editor.param_editor)
		editor.function.set(ButtonCodeCommands.Always.function_index)
		self.pump(view)
		button = gui.buttons_data.graft.button_sets[0].buttons[0]
		self.assertEqual((button.condition, button.condition_param), (ButtonCodeCommands.Always.function_index, 0))
		self.assertIsNone(editor.param_editor)
		self.assert_edited(gui)

	def test_condition_with_the_same_kind_of_param_keeps_it(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1, condition=ButtonCodeCommands.CanResearchTech.function_index, condition_param=5)])
		editor = view.settings_view.condition_editor
		editor.function.set(ButtonCodeCommands.CanPlayerUseTech.function_index)
		self.pump(view)
		button = gui.buttons_data.graft.button_sets[0].buttons[0]
		self.assertEqual((button.condition, button.condition_param), (ButtonCodeCommands.CanPlayerUseTech.function_index, 5))
		# A different kind of parameter starts at 0
		editor.function.set(ButtonCodeCommands.CanUpgrade.function_index)
		self.pump(view)
		self.assertEqual((button.condition, button.condition_param), (ButtonCodeCommands.CanUpgrade.function_index, 0))

	def test_changing_the_action_param(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1, action=ButtonCodeCommands.Train.function_index, action_param=0)])
		editor = view.settings_view.action_editor
		assert editor.param_value is not None
		editor.param_value.set(9)
		self.pump(view)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons[0].action_param, 9)
		self.assert_edited(gui)

	def test_queue_slot_param_lists_the_slots(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1, action=ButtonCodeCommands.CancelTrain.function_index, action_param=0xFE)])
		editor = view.settings_view.action_editor
		assert editor.param_editor is not None
		self.assertEqual(editor.param_editor.dropdown.entries, ['Slot 1', 'Slot 2', 'Slot 3', 'Slot 4', 'Slot 5', 'Last', 'Unknown'])
		self.assertEqual(editor.param_editor.dropdown.text.get(), 'Last')

	def test_rows_show_strings_without_hotkeys_or_control_characters(self) -> None:
		gui, view = self.open_builder()
		stat_txt = TBL()
		stat_txt.strings = ['m\x01Train \x03M\x01arine\x00', 'Terran Marine\x00']
		gui.data_context.set_stat_txt_tbl(stat_txt)
		self.set_buttons(gui, view, [Button(position=1, enabled_string=1), Button(position=2, enabled_string=2), Button(position=3, enabled_string=3)])
		self.assertEqual([row.string_text.get() for row in view.rows], ['Train Marine', 'Terran Marine', 'Unknown String 3'])

	def test_changing_the_strings(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1)])
		view.settings_view.enabled_string.set(3)
		view.settings_view.disabled_string.set(4)
		self.pump(view)
		button = gui.buttons_data.graft.button_sets[0].buttons[0]
		self.assertEqual((button.enabled_string, button.disabled_string), (3, 4))
		self.assertEqual(view.rows[0].string_text.get(), view.string_text(3))
		self.assert_edited(gui)

	def test_help_shows_the_command_help(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1, condition=ButtonCodeCommands.Always.function_index)])
		editor = view.settings_view.condition_editor
		self.assertTrue(editor.help_tooltip.text.startswith('always()'))
		editor.function.set(ButtonCodeCommands.CanUpgrade.function_index)
		self.pump(view)
		self.assertTrue(editor.help_tooltip.text.startswith('can_upgrade(upgrade)'))

	# Copy and paste

	def two_buttons(self, gui: PyGRAFT, view: ButtonSetBuilderView) -> list[Button]:
		buttons = [Button(position=2, icon=1, enabled_string=1), Button(position=3, icon=2, enabled_string=2)]
		self.set_buttons(gui, view, [button.copy() for button in buttons])
		return buttons

	def test_clipboard_buttons_have_tooltips(self) -> None:
		_, view = self.open_builder()
		self.assertTrue(getattr(view.copy_button, '_tooltip_Tooltip').text.startswith('Copy Button, hold Shift to copy button set ('))
		self.assertTrue(getattr(view.paste_button, '_tooltip_Tooltip').text.startswith('Paste Button, hold Shift to paste button set ('))

	def test_copy_puts_the_selected_buttons_code_on_the_clipboard(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=2), MOVE_BUTTON.copy()])
		view.select_button(1)
		self.invoke(view.copy_button)
		self.assertEqual(view.clipboard_get(), MOVE_CODE)

	def test_shift_click_copies_the_button_set(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [MOVE_BUTTON.copy(), MOVE_BUTTON.copy()])
		view.clipboard_set('')
		self.click(view.copy_button, 2, 2, UI.Shift.Click_Left)
		self.assertEqual(view.clipboard_get(), MOVE_CODE * 2)

	def test_paste_replaces_the_selected_button(self) -> None:
		gui, view = self.open_builder()
		buttons = self.two_buttons(gui, view)
		view.select_button(1)
		view.clipboard_set(MOVE_CODE)
		self.invoke(view.paste_button)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons, [buttons[0], MOVE_BUTTON])
		self.assertEqual(view.selected, 1)
		self.assertEqual(view.rows[1].position_text.get(), '1')
		self.assert_edited(gui)

	def test_paste_adds_the_button_to_an_empty_set(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [])
		view.clipboard_set(MOVE_CODE)
		self.invoke(view.paste_button)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons, [MOVE_BUTTON])
		self.assertEqual(view.selected, 0)
		self.assertIs(view.settings_view.button, gui.buttons_data.graft.button_sets[0].buttons[0])

	def test_paste_of_more_than_one_button_changes_nothing(self) -> None:
		gui, view = self.open_builder()
		buttons = self.two_buttons(gui, view)
		view.clipboard_set(MOVE_CODE * 2)
		with mock.patch(ERROR_DIALOG) as error_dialog:
			self.invoke(view.paste_button)
		error_dialog.assert_called_once()
		self.assertIn('The clipboard has 2 buttons', str(error_dialog.call_args.args[1]))
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons, buttons)
		self.assertFalse(gui.buttons_data.edited)

	def test_paste_error_changes_nothing(self) -> None:
		gui, view = self.open_builder()
		buttons = self.two_buttons(gui, view)
		view.clipboard_set('not_a_button\n')
		with mock.patch(ERROR_DIALOG) as error_dialog:
			self.invoke(view.paste_button)
		error_dialog.assert_called_once()
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons, buttons)
		self.assertFalse(gui.buttons_data.edited)

	def test_shift_click_pastes_the_button_set(self) -> None:
		gui, view = self.open_builder()
		self.two_buttons(gui, view)
		view.clipboard_set(MOVE_CODE * 3)
		self.click(view.paste_button, 2, 2, UI.Shift.Click_Left)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons, [MOVE_BUTTON] * 3)
		self.assertEqual(len(view.rows), 3)
		self.assertEqual(view.selected, 0)
		self.assert_edited(gui)

	def test_clipboard_shortcuts_copy_and_paste_the_selected_button(self) -> None:
		gui, view = self.open_builder()
		buttons = self.two_buttons(gui, view)
		self.show(gui)
		view.focus_force()
		self.pump(gui)
		view.select_button(1)
		self.shortcut(view, UI.Ctrl.c)
		self.assertEqual(view.clipboard_get().count('button {'), 1)
		view.select_button(0)
		self.shortcut(view, UI.Ctrl.v)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons, [buttons[1], buttons[1]])

	def test_shift_clipboard_shortcuts_copy_and_paste_the_button_set(self) -> None:
		gui, view = self.open_builder()
		self.two_buttons(gui, view)
		self.show(gui)
		view.focus_force()
		self.pump(gui)
		self.shortcut(view, UI.Shift.Ctrl.c)
		self.assertEqual(view.clipboard_get().count('button {'), 2)
		view.clipboard_set(MOVE_CODE * 3)
		self.shortcut(view, UI.Shift.Ctrl.v)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons, [MOVE_BUTTON] * 3)

	def test_clipboard_shortcuts_are_left_to_a_focused_text_field(self) -> None:
		gui, view = self.open_builder()
		buttons = self.two_buttons(gui, view)
		self.show(gui)
		entry = view.settings_view.position_dropdown.entry
		entry.focus_force()
		self.pump(gui)
		view.clipboard_set(MOVE_CODE * 3)
		for pattern in (UI.Ctrl.c, UI.Shift.Ctrl.c, UI.Ctrl.v, UI.Shift.Ctrl.v):
			self.shortcut(entry, pattern)
		self.assertEqual(view.clipboard_get(), MOVE_CODE * 3)
		self.assertEqual(gui.buttons_data.graft.button_sets[0].buttons, buttons)

	def test_copy_and_paste_are_disabled_without_a_button_set(self) -> None:
		gui, view = self.open_builder()
		gui.buttons_data.graft.button_sets = []
		gui.buttons_data.graft.button_cards = []
		gui.refresh()
		self.pump(gui)
		self.assertEqual(str(view.copy_button['state']), UI.DISABLED)
		self.assertEqual(str(view.paste_button['state']), UI.DISABLED)

	# Leaving

	def test_leaving_never_asks(self) -> None:
		gui, view = self.open_builder()
		view.delete_button(0)
		with mock.patch(ASK_YES_NO_CANCEL) as ask:
			self.select_in_list(gui, 5)
			self.assertTrue(gui.confirm_apply_before_save())
		ask.assert_not_called()
		self.assertEqual(view.entry_id, 5)

	def test_script_shows_the_builders_changes(self) -> None:
		gui, view = self.open_builder()
		view.delete_button(0)
		tab = gui.notebook.active
		assert isinstance(tab, ButtonSetsTab)
		with mock.patch(ASK_YES_NO_CANCEL) as ask:
			tab.editor.notebook.display('Script')
			self.pump(gui)
		ask.assert_not_called()
		script_view = tab.editor.script_view
		self.assertEqual(script_view.text.get('1.0', 'end-1c').count('button {'), 2)

	# Layout

	def help_x(self, view: ButtonSetBuilderView, field_editor: UI.Misc) -> int:
		# The x of the `?` that follows an editor in its field
		field = field_editor.nametowidget(field_editor.winfo_parent())
		label = [child for child in field.winfo_children() if isinstance(child, UI.Label) and child.cget('text') == '?'][0]
		self.pump(view)
		return label.winfo_x() + field.winfo_x()

	def test_param_editor_doesnt_move_the_other_help(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1, condition=ButtonCodeCommands.Always.function_index)])
		gui.deiconify()
		self.pump(gui)
		before = [self.help_x(view, editor) for editor in (view.settings_view.position_dropdown, view.settings_view.enabled_string_editor)]
		view.settings_view.condition_editor.function.set(ButtonCodeCommands.CanUpgrade.function_index)
		self.pump(gui)
		self.assertIsNotNone(view.settings_view.condition_editor.param_editor)
		after = [self.help_x(view, editor) for editor in (view.settings_view.position_dropdown, view.settings_view.enabled_string_editor)]
		self.assertEqual(after, before)

	def test_selected_row_actions_use_the_selection_background(self) -> None:
		_, view = self.open_builder()
		background = UI.Style().lookup('.', 'selectbackground')
		def frames(widget: UI.Misc) -> list[UI.Misc]:
			children = [frame for child in widget.winfo_children() for frame in frames(child)]
			return children if isinstance(widget, UI.Button) else [widget, *children]
		for widget in frames(view.rows[0].actions):
			if not isinstance(widget, UI.Button):
				self.assertEqual(widget.cget('bg'), background)
		self.assertEqual(view.rows[0].move_up_button.cget('highlightbackground'), background)
		self.assertNotEqual(view.rows[1].actions.cget('bg'), background)
		# Deselecting restores the row's background
		view.select_button(1)
		self.assertNotEqual(view.rows[0].actions.cget('bg'), background)

	def test_settings_are_sized_to_fit(self) -> None:
		_, view = self.open_builder()
		settings_frame = view.settings_view.master
		assert isinstance(settings_frame, UI.LabelFrame)
		info = settings_frame.pack_info()
		self.assertEqual(info['fill'], 'none')
		self.assertEqual(info['anchor'], UI.W)

	def test_preview_labels_have_a_shadow_under_them(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1), Button(position=1)])
		canvas = view.preview.slots[1]
		for tag in ('number', 'count'):
			shadow = canvas.find_withtag(f'{tag}_shadow')
			label = canvas.find_withtag(tag)
			self.assertEqual(canvas.itemcget(shadow[0], 'text'), canvas.itemcget(label[0], 'text'))
			self.assertEqual(canvas.itemcget(shadow[0], 'fill'), '#000000')
			# Drawn first, so it's under the label
			self.assertLess(canvas.find_all().index(shadow[0]), canvas.find_all().index(label[0]))

	def test_selected_slot_border_uses_the_selection_color(self) -> None:
		_, view = self.open_builder()
		canvas = view.preview.slots[view.buttons()[0].position]
		color = canvas.itemcget(canvas.find_withtag('selection')[0], 'outline')
		self.assertEqual(color, UI.Style().lookup('.', 'selectbackground'))
		self.assertNotEqual(color, '')

	def test_preview_icons_are_centered_with_the_labels_on_the_edges(self) -> None:
		gui, view = self.open_builder()
		self.set_buttons(gui, view, [Button(position=1, icon=0), Button(position=1, icon=1)])
		canvas = view.preview.slots[1]
		width, height = int(canvas.cget('width')), int(canvas.cget('height'))
		self.assertGreater(width, ButtonRow.ICON_WIDTH)
		self.assertGreater(height, ButtonRow.ICON_HEIGHT)
		# The test icons fill their whole frame
		left = (width - ButtonRow.ICON_WIDTH) // 2
		top = (height - ButtonRow.ICON_HEIGHT) // 2
		self.assertEqual(canvas.bbox('icon'), (left, top, left + ButtonRow.ICON_WIDTH, top + ButtonRow.ICON_HEIGHT))
		number = canvas.bbox('number')
		self.assertLessEqual(number[0], 2)
		self.assertLessEqual(number[1], 0)
		count = canvas.bbox('count')
		self.assertGreaterEqual(count[2], width - 2)
		self.assertGreaterEqual(count[3], height - 1)

	def test_hidden_actions_give_their_space_to_the_string(self) -> None:
		gui, view = self.open_builder(hover=True)
		self.set_buttons(gui, view, [Button(position=1, enabled_string=1), Button(position=2)])
		row = view.rows[0]
		self.pump(gui)
		self.assertEqual(row.actions.winfo_manager(), '')
		hidden_width = row.string_label.winfo_width()
		row_size = (row.winfo_width(), row.winfo_height())
		self.move_pointer(view, row, '<Enter>', row.string_label)
		self.assertEqual(row.actions.winfo_manager(), 'grid')
		self.assertTrue(row.actions.winfo_ismapped())
		self.assertLess(row.string_label.winfo_width(), hidden_width)
		self.assertEqual((row.winfo_width(), row.winfo_height()), row_size)
		self.move_pointer(view, row, '<Leave>', view.rows[1].string_label)
		self.assertEqual(row.actions.winfo_manager(), '')
		self.assertEqual(row.string_label.winfo_width(), hidden_width)
		self.assertEqual((row.winfo_width(), row.winfo_height()), row_size)
