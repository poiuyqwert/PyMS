from .utils import PyGRAFTTestCase, ASK_YES_NO_CANCEL

from ...PyGRAFT.PyGRAFT import PyGRAFT
from ...PyGRAFT.Tabs import ReqGraftTab
from ...PyGRAFT.RequirementsEditor.BuilderView import ReqBuilderView
from ...PyGRAFT.RequirementsEditor.OpcodeEditorView import OpcodeEditorView
from ...FileFormats.Graft import ReqScript
from ...FileFormats.Graft.CodeHandlers import RequirementCodeCommands
from ...FileFormats.Graft.CodeHandlers.RequirementCodeCommands import ReqCommandDefinition
from ...Utilities.CodeHandlers.CodeCommand import CodeCommand
from ...Utilities import UIKit as UI
from ...Utilities.utils import fit

from unittest import mock

from typing import Any

ERROR_DIALOG = 'PyMS.PyGRAFT.RequirementsEditor.BuilderView.ErrorDialog'
SHOW_INFO = 'tkinter.messagebox.showinfo'

# Unit 4 (Terran Siege Tank (Siege Mode)) has no vanilla script
UNSCRIPTED_UNIT = 4

R = RequirementCodeCommands

class Test_PyGRAFT_requirements_builder(PyGRAFTTestCase):
	def open_builder(self, title: str = 'Unit Training Reqs.') -> tuple[PyGRAFT, ReqGraftTab, ReqBuilderView]:
		gui = self.open_pygraft()
		tab = self.display_tab(gui, title)
		assert isinstance(tab, ReqGraftTab)
		return gui, tab, tab.editor.builder_view

	def names(self, view: ReqBuilderView) -> list[str]:
		return [command.definition.name for command in view.commands]

	def row_names(self, view: ReqBuilderView) -> list[str]:
		return [row.cmd_def.name for row in view.rows]

	def choose_opcode(self, view: ReqBuilderView, index: int, cmd_def: ReqCommandDefinition) -> None:
		row = view.rows[index]
		row.opcode.set(row.commands.index(cmd_def))
		self.pump(view)

	def set_commands(self, view: ReqBuilderView, commands: list[tuple[ReqCommandDefinition, list[int]]]) -> None:
		# Builds the script through the Builder's own actions
		while view.commands:
			view.delete_opcode(0)
		for index, (cmd_def, params) in enumerate(commands):
			view.add_opcode()
			if cmd_def is not R.HasCompleted:
				self.choose_opcode(view, index, cmd_def)
			if params:
				param_value = view.rows[index].param_value
				assert param_value is not None
				param_value.set(params[0])
		self.pump(view)

	# Loading

	def test_selected_entry_loads_a_row_per_opcode(self) -> None:
		gui, _, view = self.open_builder()
		script = gui.units_data.graft.get_script(0)
		assert script is not None
		self.assertEqual(self.names(view), [command.definition.name for command in script.commands])
		self.assertEqual(self.row_names(view), self.names(view))
		self.assertEqual([row.line_number.get() for row in view.rows], [str(n + 1) for n in range(len(script.commands))])
		first = view.rows[0]
		self.assertIs(first.cmd_def, R.CurrentUnitIs)
		assert first.param_value is not None
		self.assertEqual(first.param_value.get(), 111)
		self.assertIsNone(view.rows[1].param_editor)
		self.assertFalse(view.is_edited())
		self.assertEqual(view.apply_button['state'], UI.DISABLED)

	def test_unavailable_loaded_opcode_is_shown_and_reported(self) -> None:
		# A file can use an opcode its requirements don't have, which is shown (marked as not available) and reported as an error
		gui, _, view = self.open_builder('Tech Usage Reqs.')
		gui.tech_data.graft.set_script(ReqScript(0, [CodeCommand(R.IsHero, []), CodeCommand(R.AllowOnHallucinations, [])]))
		view.load(0, 'Stim Packs')
		self.pump(view)
		row = view.rows[1]
		self.assertIs(row.cmd_def, R.AllowOnHallucinations)
		self.assertEqual(row.opcode_dropdown.entries[row.opcode.get()], 'Allow On Hallucinations (Not Available)')
		with mock.patch(ERROR_DIALOG) as error_dialog:
			view.test()
		self.assertIn('`allow_on_hallucinations` is not available for tech use requirements', str(error_dialog.call_args.args[1]))
		self.assertEqual([row.has_error for row in view.rows], [False, True])
		self.choose_opcode(view, 1, R.IsWorker)
		self.assertNotIn(R.AllowOnHallucinations, view.rows[1].commands)
		self.assertIs(view.rows[1].cmd_def, R.IsWorker)

	def test_rows_are_shown_once_loaded(self) -> None:
		# Rows are only shown after they're loaded, so they never appear showing the wrong opcode
		gui = self.open_pygraft()
		shown: list[tuple[int, str]] = []
		original_pack = OpcodeEditorView.pack
		def recording_pack(row: OpcodeEditorView, **kwargs: Any) -> None:
			shown.append((row.index, row.cmd_def.name))
			original_pack(row, **kwargs)
		with mock.patch.object(OpcodeEditorView, 'pack', recording_pack):
			tab = self.display_tab(gui, 'Upgrade Research Reqs.')
		assert isinstance(tab, ReqGraftTab)
		view = tab.editor.builder_view
		self.assertEqual(shown, list(enumerate(self.names(view))))

	def test_upgrade_levels_are_indented_like_the_code(self) -> None:
		_, _, view = self.open_builder('Upgrade Research Reqs.')
		self.assertEqual(self.names(view), ['current_unit_is', 'is_not_lifted_off', 'is_not_training_or_morphing', 'level_1_requires', 'end_level_requirements', 'level_2_requires', 'has_completed', 'end_level_requirements', 'level_3_requires', 'has_completed'])
		self.assertEqual([row.indent for row in view.rows], [0, 0, 0, 0, 1, 0, 1, 1, 0, 1])

	def test_level_3_requires_indents_the_rest_of_the_script(self) -> None:
		_, _, view = self.open_builder('Upgrade Research Reqs.')
		self.set_commands(view, [(R.HasCompleted, [1]), (R.Level3Requires, []), (R.HasCompleted, [1]), (R.HasCompleted, [2])])
		self.assertEqual([row.indent for row in view.rows], [0, 0, 1, 1])

	def test_indents_follow_edits(self) -> None:
		_, _, view = self.open_builder('Upgrade Research Reqs.')
		self.set_commands(view, [(R.HasCompleted, [1]), (R.HasCompleted, [2]), (R.HasCompleted, [3])])
		self.assertEqual([row.indent for row in view.rows], [0, 0, 0])
		self.choose_opcode(view, 0, R.Level1Requires)
		self.choose_opcode(view, 2, R.EndLevelRequirements)
		self.assertEqual([row.indent for row in view.rows], [0, 1, 1])
		view.move_opcode(0, 1)
		self.assertEqual([row.indent for row in view.rows], [0, 0, 1])

	def test_entry_without_script_has_no_rows(self) -> None:
		gui, _, view = self.open_builder()
		self.select_in_list(gui, UNSCRIPTED_UNIT)
		self.assertEqual(view.commands, [])
		self.assertEqual(view.rows, [])
		self.assertEqual(view.add_opcode_button['state'], UI.NORMAL)

	def test_opcodes_are_the_files_opcodes_by_display_name(self) -> None:
		_, _, view = self.open_builder()
		row = view.rows[0]
		self.assertEqual(row.opcode_dropdown.entries, sorted(cmd_def.display_name for cmd_def in row.commands))
		self.assertNotIn(R.Level1Requires, row.commands)
		self.assertIn(R.HasCompleted, row.commands)

	def test_help_shows_the_opcodes_help(self) -> None:
		_, _, view = self.open_builder()
		row = view.rows[0]
		# The same help as the command's tooltip in the Script mode (its usage, description with the parameter named, and the parameter's help)
		self.assertEqual(row.help_tooltip.text, fit('', R.CurrentUnitIs.full_help_text()))
		self.assertIn('current_unit_is(unit)', row.help_tooltip.text)
		self.assertIn('Current unit is `unit`', row.help_tooltip.text)
		self.assertIn('unit: A unit ID, or its quoted name', row.help_tooltip.text)
		self.choose_opcode(view, 0, R.IsNotLiftedOff)
		self.assertEqual(view.rows[0].help_tooltip.text, fit('', R.IsNotLiftedOff.full_help_text()))

	def test_every_requirement_command_has_a_display_name(self) -> None:
		for cmd_def in R.all_req_commands:
			assert isinstance(cmd_def, ReqCommandDefinition)
			self.assertTrue(cmd_def.display_name)

	# Editing

	def test_add_opcode_appends_has_completed(self) -> None:
		_, _, view = self.open_builder()
		count = len(view.commands)
		view.add_opcode_button.invoke()
		self.pump(view)
		self.assertEqual(len(view.rows), count + 1)
		self.assertIs(view.commands[-1].definition, R.HasCompleted)
		self.assertEqual(view.commands[-1].params, [0])
		self.assertTrue(view.is_edited())
		self.assertEqual(view.apply_button['state'], UI.NORMAL)

	def test_row_add_opcode_inserts_below_the_row(self) -> None:
		_, _, view = self.open_builder()
		names = self.names(view)
		view.add_opcode_after(0)
		self.pump(view)
		self.assertEqual(self.names(view), [names[0], 'has_completed', *names[1:]])
		self.assertEqual([row.line_number.get() for row in view.rows], [str(n + 1) for n in range(len(names) + 1)])

	def test_move_and_delete(self) -> None:
		_, _, view = self.open_builder()
		names = self.names(view)
		view.move_opcode(0, 1)
		self.assertEqual(self.names(view), [names[1], names[0], *names[2:]])
		view.move_opcode(1, -1)
		self.assertEqual(self.names(view), names)
		view.move_opcode(0, -1)
		self.assertEqual(self.names(view), names)
		view.delete_opcode(0)
		self.assertEqual(self.names(view), names[1:])
		self.assertEqual(self.row_names(view), names[1:])
		self.assertTrue(view.is_edited())

	def test_move_buttons_are_disabled_at_the_ends(self) -> None:
		_, _, view = self.open_builder()
		self.assertEqual(view.rows[0].move_up_button['state'], UI.DISABLED)
		self.assertEqual(view.rows[0].move_down_button['state'], UI.NORMAL)
		self.assertEqual(view.rows[-1].move_up_button['state'], UI.NORMAL)
		self.assertEqual(view.rows[-1].move_down_button['state'], UI.DISABLED)

	def test_changing_opcode_changes_the_parameter_editor(self) -> None:
		gui, _, view = self.open_builder()
		self.choose_opcode(view, 1, R.IsResearched)
		row = view.rows[1]
		assert row.param_editor is not None and row.param_value is not None
		self.assertEqual(view.commands[1].params, [0])
		self.assertEqual(row.param_editor.dropdown.entries[0], gui.data_context.tech_display_names()[0])
		self.choose_opcode(view, 1, R.IsNotLiftedOff)
		self.assertIsNone(view.rows[1].param_editor)
		self.assertEqual(view.commands[1].params, [])

	def test_changing_to_the_same_parameter_kind_keeps_the_value(self) -> None:
		_, _, view = self.open_builder()
		self.choose_opcode(view, 0, R.MustHave)
		self.assertEqual(view.commands[0].params, [111])
		param_value = view.rows[0].param_value
		assert param_value is not None
		self.assertEqual(param_value.get(), 111)

	def test_has_completed_limits_its_unit(self) -> None:
		_, _, view = self.open_builder()
		self.choose_opcode(view, 0, R.HasCompleted)
		param_value = view.rows[0].param_value
		assert param_value is not None
		self.assertEqual(param_value.range, [0, R.OPCODE_MIN - 1])

	def test_parameter_change_edits_the_command(self) -> None:
		_, _, view = self.open_builder()
		param_value = view.rows[0].param_value
		assert param_value is not None
		param_value.set(7)
		self.pump(view)
		self.assertEqual(view.commands[0].params, [7])
		self.assertTrue(view.is_edited())

	# Applying

	def test_apply_sets_the_script(self) -> None:
		gui, _, view = self.open_builder()
		view.add_opcode()
		param_value = view.rows[-1].param_value
		assert param_value is not None
		param_value.set(5)
		view.apply_button.invoke()
		self.pump(gui)
		script = gui.units_data.graft.get_script(0)
		assert script is not None
		self.assertEqual(script.commands[-1].definition, R.HasCompleted)
		self.assertEqual(script.commands[-1].params, [5])
		self.assertTrue(gui.units_data.edited)
		self.assertFalse(view.is_edited())

	def test_empty_script_can_be_removed(self) -> None:
		gui, _, view = self.open_builder()
		self.set_commands(view, [])
		with mock.patch(ASK_YES_NO_CANCEL, return_value=True) as ask:
			self.assertTrue(view.apply())
		ask.assert_called_once()
		self.assertFalse(gui.units_data.has_script(0))

	def test_empty_script_cancel_applies_nothing(self) -> None:
		gui, _, view = self.open_builder()
		self.set_commands(view, [])
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None):
			self.assertFalse(view.apply())
		self.assertTrue(gui.units_data.has_script(0))
		self.assertTrue(view.is_edited())

	def test_test_reports_success_without_applying(self) -> None:
		gui, _, view = self.open_builder()
		view.add_opcode()
		with mock.patch(SHOW_INFO) as show_info:
			view.test_button.invoke()
		show_info.assert_called_once()
		self.assertFalse(gui.units_data.edited)
		self.assertTrue(view.is_edited())

	def test_unmatched_end_level_requirements_highlights_its_row(self) -> None:
		gui, _, view = self.open_builder('Upgrade Research Reqs.')
		self.set_commands(view, [(R.HasCompleted, [1]), (R.EndLevelRequirements, [])])
		with mock.patch(ERROR_DIALOG) as error_dialog:
			self.assertFalse(view.apply())
		error_dialog.assert_called_once()
		self.assertIn('`end_level_requirements` used outside', str(error_dialog.call_args.args[1]))
		self.assertEqual([row.has_error for row in view.rows], [False, True])
		self.assertEqual(view.rows[1].cget('bg'), OpcodeEditorView.ERROR_COLOR)
		self.assertTrue(view.is_edited())
		self.assertFalse(gui.upgrades_data.edited)

	def test_unended_upgrade_level_highlights_its_row(self) -> None:
		_, _, view = self.open_builder('Upgrade Research Reqs.')
		self.set_commands(view, [(R.HasCompleted, [1]), (R.Level1Requires, []), (R.HasCompleted, [2])])
		with mock.patch(ERROR_DIALOG) as error_dialog:
			view.test()
		self.assertIn('is not ended with `end_level_requirements`', str(error_dialog.call_args.args[1]))
		self.assertEqual([row.has_error for row in view.rows], [False, True, False])

	def test_upgrade_level_1_without_the_other_levels_highlights_its_row(self) -> None:
		_, _, view = self.open_builder('Upgrade Research Reqs.')
		self.set_commands(view, [(R.HasCompleted, [1]), (R.Level1Requires, []), (R.HasCompleted, [2]), (R.EndLevelRequirements, [])])
		with mock.patch(ERROR_DIALOG) as error_dialog:
			view.test()
		self.assertIn('`level_1_requires` is used without `level_2_requires` and `level_3_requires` after it', str(error_dialog.call_args.args[1]))
		self.assertEqual([row.has_error for row in view.rows], [False, True, False, False])

	def test_any_change_clears_the_highlight(self) -> None:
		_, _, view = self.open_builder('Upgrade Research Reqs.')
		self.set_commands(view, [(R.HasCompleted, [1]), (R.EndLevelRequirements, [])])
		with mock.patch(ERROR_DIALOG):
			view.test()
		self.assertTrue(view.rows[1].has_error)
		param_value = view.rows[0].param_value
		assert param_value is not None
		param_value.set(3)
		self.pump(view)
		self.assertEqual([row.has_error for row in view.rows], [False, False])
		self.assertEqual(view.rows[1].cget('bg'), view.rows[1].background_color)

	# Leaving

	def test_selecting_another_entry_cancelled_stays(self) -> None:
		gui, tab, view = self.open_builder()
		view.add_opcode()
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None):
			self.select_in_list(gui, 1)
		self.assertEqual(tab.selected, 0)
		self.assertTrue(view.is_edited())

	def test_selecting_another_entry_discarding(self) -> None:
		gui, tab, view = self.open_builder()
		view.add_opcode()
		with mock.patch(ASK_YES_NO_CANCEL, return_value=False):
			self.select_in_list(gui, 1)
		self.assertEqual(tab.selected, 1)
		self.assertFalse(view.is_edited())
		self.assertFalse(gui.units_data.edited)

	def test_switching_to_script_mode_applying(self) -> None:
		gui, tab, view = self.open_builder()
		view.add_opcode()
		notebook = tab.editor.notebook
		with mock.patch(ASK_YES_NO_CANCEL, return_value=True):
			notebook.display('Script')
		self.assertIs(notebook.active, tab.editor.script_view)
		self.assertTrue(gui.units_data.edited)
		self.assertTrue(tab.editor.script_view.text.get('end-1c linestart', 'end-1c').startswith('has_completed '))

	def test_switching_to_script_mode_cancelled_stays(self) -> None:
		_, tab, view = self.open_builder()
		view.add_opcode()
		notebook = tab.editor.notebook
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None):
			notebook.display('Script')
		self.assertIs(notebook.active, view)
		self.assertTrue(view.is_edited())

	def test_save_can_apply_first(self) -> None:
		gui, _, view = self.open_builder()
		view.add_opcode()
		with mock.patch(ASK_YES_NO_CANCEL, return_value=True):
			self.assertTrue(view.confirm_apply_before_save())
		self.assertTrue(gui.units_data.edited)
		self.assertFalse(view.is_edited())

	def test_revert_restores_the_script(self) -> None:
		_, _, view = self.open_builder()
		names = self.names(view)
		view.delete_opcode(0)
		view.revert_button.invoke()
		self.pump(view)
		self.assertEqual(self.names(view), names)
		self.assertFalse(view.is_edited())

	# Shortcuts and hovering

	def test_apply_shortcut_applies(self) -> None:
		gui, _, view = self.open_builder()
		view.add_opcode()
		gui.deiconify()
		entry = view.rows[0].opcode_dropdown.entry
		entry.focus_force()
		self.pump(gui)
		entry.event_generate(UI.Ctrl.Return.event())
		self.pump(gui)
		self.assertTrue(gui.units_data.edited)
		self.assertFalse(view.is_edited())

	def move_pointer(self, view: ReqBuilderView, row: OpcodeEditorView, pattern: str, widget: UI.Misc | None = None, *, x: int = 5, y: int = 5) -> None:
		# Sends `row` an Enter/Leave with the pointer at a position inside `widget` (without moving the real pointer), marked as sent so the real pointer's events can be told apart
		if widget is None:
			widget = row
		row.event_generate(pattern, x=x, y=y, rootx=widget.winfo_rootx() + x, rooty=widget.winfo_rooty() + y, sendevent=True)
		self.pump(view)

	def enter_row(self, view: ReqBuilderView, row: OpcodeEditorView, widget: UI.Misc | None = None) -> None:
		self.move_pointer(view, row, '<Enter>', widget)

	def leave_row(self, view: ReqBuilderView, row: OpcodeEditorView, widget: UI.Misc | None = None, *, x: int = 5, y: int = 5) -> None:
		# Leaves `row` with the pointer moving into `widget`
		self.move_pointer(view, row, '<Leave>', widget, x=x, y=y)

	def shown_actions(self, view: ReqBuilderView) -> list[int]:
		return [index for index, row in enumerate(view.rows) if row.actions_shown()]

	def open_shown_builder(self) -> tuple[PyGRAFT, ReqBuilderView]:
		# The window is shown, so the real pointer can be over it, and its events would show/hide the actions too, so only the generated events are used
		original_entered = OpcodeEditorView.pointer_entered
		original_left = OpcodeEditorView.pointer_left
		def generated_entered(row: OpcodeEditorView, event: UI.Event) -> None:
			if event.send_event:
				original_entered(row, event)
		def generated_left(row: OpcodeEditorView, event: UI.Event) -> None:
			if event.send_event:
				original_left(row, event)
		with mock.patch.object(OpcodeEditorView, 'pointer_entered', generated_entered), mock.patch.object(OpcodeEditorView, 'pointer_left', generated_left):
			gui, _, view = self.open_builder()
		gui.deiconify()
		self.pump(gui)
		return gui, view

	def test_actions_are_hidden_until_hovered(self) -> None:
		_, view = self.open_shown_builder()
		self.assertEqual(self.shown_actions(view), [])

	def test_entering_a_row_shows_its_actions(self) -> None:
		_, view = self.open_shown_builder()
		self.enter_row(view, view.rows[0], view.rows[0].opcode_dropdown.entry)
		self.assertEqual(self.shown_actions(view), [0])

	def test_moving_to_another_row_moves_the_actions(self) -> None:
		_, view = self.open_shown_builder()
		self.enter_row(view, view.rows[0])
		self.leave_row(view, view.rows[0], view.rows[1].opcode_dropdown.entry)
		self.enter_row(view, view.rows[1], view.rows[1].opcode_dropdown.entry)
		self.assertEqual(self.shown_actions(view), [1])

	def test_moving_onto_the_rows_own_widgets_keeps_the_actions(self) -> None:
		_, view = self.open_shown_builder()
		row = view.rows[0]
		self.enter_row(view, row)
		for widget in (row.line_label, row.opcode_dropdown.entry, row.move_up_button):
			self.leave_row(view, row, widget)
			self.assertEqual(self.shown_actions(view), [0])

	def test_leaving_the_rows_hides_the_actions(self) -> None:
		_, view = self.open_shown_builder()
		self.enter_row(view, view.rows[0])
		self.leave_row(view, view.rows[0], view.toolbar)
		self.assertEqual(self.shown_actions(view), [])
		# Leaving the window entirely
		self.enter_row(view, view.rows[0])
		self.leave_row(view, view.rows[0], x=-1000, y=-1000)
		self.assertEqual(self.shown_actions(view), [])

	def stacked_above(self, row: OpcodeEditorView) -> str:
		# Which of the actions and their cover is drawn on top (`winfo children` lists the lowest first)
		children = [str(child) for child in row.tk.splitlist(row.tk.call('winfo', 'children', str(row)))]
		actions_index = children.index(str(row.actions))
		cover_index = children.index(str(row.actions_cover))
		return 'actions' if actions_index > cover_index else 'cover'

	def test_actions_are_shown_by_raising_them_above_the_cover(self) -> None:
		# The cover always stays placed over the actions (removing it isn't always redrawn on macOS), only which one is on top changes
		_, view = self.open_shown_builder()
		row = view.rows[0]
		self.assertEqual(self.stacked_above(row), 'cover')
		self.enter_row(view, row)
		self.assertEqual(self.stacked_above(row), 'actions')
		self.assertEqual(row.actions_cover.winfo_manager(), 'place')
		self.assertTrue(row.actions_cover.winfo_ismapped())
		self.leave_row(view, row, view.toolbar)
		self.assertEqual(self.stacked_above(row), 'cover')
		self.assertEqual(row.actions_cover.winfo_manager(), 'place')

	def test_actions_keep_the_rows_size(self) -> None:
		gui, view = self.open_shown_builder()
		row = view.rows[0]
		size = (row.winfo_width(), row.winfo_height())
		# The hidden actions still take their space in the row, under the cover
		self.assertTrue(row.actions.winfo_ismapped())
		self.assertEqual((row.actions_cover.winfo_width(), row.actions_cover.winfo_height()), (row.actions.winfo_width(), row.actions.winfo_height()))
		row.show_actions()
		self.pump(gui)
		self.assertEqual((row.winfo_width(), row.winfo_height()), size)
		row.hide_actions()
		self.pump(gui)
		self.assertEqual((row.winfo_width(), row.winfo_height()), size)

	def test_hidden_actions_cover_matches_the_error_highlight(self) -> None:
		_, _, view = self.open_builder()
		row = view.rows[0]
		row.set_error(True)
		self.assertEqual(row.actions_cover.cget('bg'), OpcodeEditorView.ERROR_COLOR)
		row.set_error(False)
		self.assertEqual(row.actions_cover.cget('bg'), row.background_color)

	def test_loaded_commands_are_copies(self) -> None:
		gui, _, view = self.open_builder()
		view.rows[0].param_changed(9)
		script = gui.units_data.graft.get_script(0)
		assert script is not None
		self.assertEqual(script.commands[0].params, [111])
		self.assertIsInstance(view.commands[0], CodeCommand)
