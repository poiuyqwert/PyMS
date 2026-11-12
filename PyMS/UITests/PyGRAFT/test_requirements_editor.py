from .utils import PyGRAFTTestCase, ASK_YES_NO_CANCEL

from ...PyGRAFT.PyGRAFT import PyGRAFT
from ...PyGRAFT.Tabs import ReqGraftTab
from ...PyGRAFT.RequirementsEditor.ScriptView import ReqScriptView
from ...FileFormats.Graft.CodeHandlers import RequirementCodeCommands, GraftSerializeContext
from ...Utilities import UIKit as UI

import io
import time

from unittest import mock

ERROR_DIALOG = 'PyMS.PyGRAFT.ScriptEditor.ScriptView.ErrorDialog'
SHOW_INFO = 'tkinter.messagebox.showinfo'

# Unit 4 (Terran Siege Tank (Siege Mode)) has no vanilla script
UNSCRIPTED_UNIT = 4

class Test_PyGRAFT_requirements_editor(PyGRAFTTestCase):
	def open_req_tab(self, title: str = 'Unit Training Reqs.') -> tuple[PyGRAFT, ReqGraftTab, ReqScriptView]:
		gui = self.open_pygraft()
		tab = self.display_tab(gui, title)
		assert isinstance(tab, ReqGraftTab)
		# The editor opens in Builder mode
		tab.editor.notebook.display('Script')
		self.pump(gui)
		return gui, tab, tab.editor.script_view

	def script_body(self, gui: PyGRAFT, entry_id: int) -> str:
		# The decompiled script as the view shows it (without the final newline, which the text widget supplies)
		output = io.StringIO()
		gui.units_data.graft.decompile_script(GraftSerializeContext(output, gui.data_context), entry_id)
		return output.getvalue().rstrip('\n')

	def code(self, view: ReqScriptView) -> str:
		return view.text.get('1.0', 'end-1c')

	def set_code(self, view: ReqScriptView, code: str) -> None:
		view.text.delete('1.0', UI.END)
		view.text.insert('1.0', code)
		self.pump(view)

	def wait_for_highlighting(self, view: ReqScriptView) -> None:
		# Highlighting is done in an `after` callback
		for _ in range(20):
			self.pump(view)
			if not view.text.tag_ranges('Update'):
				return
			time.sleep(0.01)

	def tag_texts(self, view: ReqScriptView, tag: str) -> list[str]:
		ranges = view.text.tag_ranges(tag)
		return [view.text.get(ranges[n], ranges[n + 1]) for n in range(0, len(ranges), 2)]

	# Loading

	def test_selected_entry_loads_its_script_body(self) -> None:
		gui, _, view = self.open_req_tab()
		self.assertEqual(self.code(view), self.script_body(gui, 0))
		self.assertTrue(self.code(view).startswith('current_unit_is'))
		self.assertFalse(view.is_edited())
		self.assertEqual(view.apply_button['state'], UI.DISABLED)
		self.assertFalse(gui.units_data.edited)

	def test_loaded_script_has_no_trailing_blank_line(self) -> None:
		_, _, view = self.open_req_tab()
		self.assertFalse(self.code(view).endswith('\n'))
		self.assertNotEqual(view.text.get('end-1c linestart', 'end-1c'), '')

	def test_entry_without_script_is_empty(self) -> None:
		gui, _, view = self.open_req_tab()
		self.assertFalse(gui.units_data.has_script(UNSCRIPTED_UNIT))
		self.select_in_list(gui, UNSCRIPTED_UNIT)
		self.assertEqual(self.code(view), '')

	def test_builder_mode_is_shown_first(self) -> None:
		gui = self.open_pygraft()
		tab = self.display_tab(gui, 'Unit Training Reqs.')
		assert isinstance(tab, ReqGraftTab)
		self.assertIs(tab.editor.notebook.active, tab.editor.builder_view)

	# Editing and applying

	def test_typing_marks_only_the_editor_edited(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		self.assertTrue(view.is_edited())
		self.assertEqual(view.apply_button['state'], UI.NORMAL)
		self.assertEqual(view.revert_button['state'], UI.NORMAL)
		self.assertFalse(gui.units_data.edited)

	def test_apply_sets_the_script(self) -> None:
		gui, _, view = self.open_req_tab()
		self.select_in_list(gui, UNSCRIPTED_UNIT)
		self.assertEqual(gui.listbox.itemcget(UNSCRIPTED_UNIT, 'foreground'), gui.listbox.listbox.cget('disabledforeground'))
		self.set_code(view, '# Not kept\nis_not_lifted_off\n')
		self.assertTrue(view.apply())
		script = gui.units_data.graft.get_script(UNSCRIPTED_UNIT)
		assert script is not None
		self.assertEqual([command.definition for command in script.commands], [RequirementCodeCommands.IsNotLiftedOff])
		self.assertTrue(gui.units_data.edited)
		self.assertEqual(gui.listbox.itemcget(UNSCRIPTED_UNIT, 'foreground'), '')
		# The editor shows the applied script, and is no longer edited
		self.assertEqual(self.code(view), 'is_not_lifted_off')
		self.assertFalse(view.is_edited())
		self.assertEqual(self.list_selection(gui), [UNSCRIPTED_UNIT])

	def test_compile_error_keeps_the_code(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\nis_awesome\n')
		with mock.patch(ERROR_DIALOG) as error_dialog:
			self.assertFalse(view.apply())
		error_dialog.assert_called_once()
		self.assertIn('Unknown command `is_awesome`', str(error_dialog.call_args.args[1]))
		self.assertEqual(self.code(view), 'is_not_lifted_off\nis_awesome\n')
		self.assertTrue(view.is_edited())
		self.assertFalse(gui.units_data.edited)
		self.assertTrue(view.text.tag_ranges('Error'))
		self.assertEqual(str(view.text.tag_ranges('Error')[0]), '2.0')

	def test_test_reports_success_without_applying(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		with mock.patch(SHOW_INFO) as show_info:
			view.test()
		show_info.assert_called_once()
		self.assertTrue(view.is_edited())
		self.assertFalse(gui.units_data.edited)

	def test_empty_script_can_be_removed(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, '# Nothing\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=True) as ask:
			self.assertTrue(view.apply())
		self.assertIn('is empty', ask.call_args.kwargs['message'])
		self.assertFalse(gui.units_data.has_script(0))
		self.assertEqual(gui.listbox.itemcget(0, 'foreground'), gui.listbox.listbox.cget('disabledforeground'))
		self.assertTrue(gui.units_data.edited)

	def test_empty_script_can_be_kept(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, '')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=False):
			self.assertTrue(view.apply())
		script = gui.units_data.graft.get_script(0)
		assert script is not None
		self.assertEqual(script.commands, [])
		self.assertEqual(gui.listbox.itemcget(0, 'foreground'), '')

	def test_empty_script_cancel_applies_nothing(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, '')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None):
			self.assertFalse(view.apply())
		self.assertTrue(gui.units_data.has_script(0))
		self.assertFalse(gui.units_data.edited)
		self.assertTrue(view.is_edited())

	def test_save_indicator_shows_the_edited_state(self) -> None:
		gui, _, view = self.open_req_tab()
		self.assertEqual(view.editstatus['state'], UI.DISABLED)
		self.set_code(view, 'is_not_lifted_off\n')
		self.assertEqual(view.editstatus['state'], UI.NORMAL)
		view.revert()
		self.assertEqual(view.editstatus['state'], UI.DISABLED)
		self.set_code(view, 'is_not_lifted_off\n')
		self.assertTrue(view.apply())
		self.assertEqual(view.editstatus['state'], UI.DISABLED)
		# The main window's indicator is for the file, which applying edited
		self.assertEqual(gui.editstatus['state'], UI.NORMAL)

	def test_revert_restores_the_script(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		view.revert()
		self.assertEqual(self.code(view), self.script_body(gui, 0))
		self.assertFalse(view.is_edited())

	# Leaving with unapplied changes

	def test_selecting_another_entry_cancelled_stays(self) -> None:
		gui, tab, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None) as ask:
			self.select_in_list(gui, 1)
		self.assertIn('Terran Marine', ask.call_args.kwargs['message'])
		self.assertEqual(tab.selected, 0)
		self.assertEqual(self.list_selection(gui), [0])
		self.assertEqual(self.code(view), 'is_not_lifted_off\n')

	def test_selecting_another_entry_discarding(self) -> None:
		gui, tab, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=False):
			self.select_in_list(gui, 1)
		self.assertEqual(tab.selected, 1)
		self.assertIn('Terran Covert Ops', self.code(view))
		self.assertFalse(view.is_edited())
		self.assertFalse(gui.units_data.edited)

	def test_selecting_another_entry_applying(self) -> None:
		gui, tab, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=True):
			self.select_in_list(gui, 1)
		self.assertEqual(tab.selected, 1)
		self.assertEqual(self.list_selection(gui), [1])
		self.assertTrue(gui.units_data.edited)
		script = gui.units_data.graft.get_script(0)
		assert script is not None
		self.assertEqual(len(script.commands), 1)

	def test_applying_failure_stays(self) -> None:
		gui, tab, view = self.open_req_tab()
		self.set_code(view, 'is_awesome\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=True), mock.patch(ERROR_DIALOG):
			self.select_in_list(gui, 1)
		self.assertEqual(tab.selected, 0)
		self.assertEqual(self.list_selection(gui), [0])
		self.assertEqual(self.code(view), 'is_awesome\n')

	def test_unedited_editor_leaves_without_asking(self) -> None:
		gui, tab, _ = self.open_req_tab()
		with mock.patch(ASK_YES_NO_CANCEL) as ask:
			self.select_in_list(gui, 1)
			self.display_tab(gui, 'Order Reqs.')
		ask.assert_not_called()
		self.assertEqual(tab.selected, 1)

	def test_switching_file_tab_cancelled_stays(self) -> None:
		gui, tab, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None):
			# Clicking a tab selects it before displaying it
			gui.notebook.tab.set(gui.notebook.pages['Order Reqs.'][1])
			self.display_tab(gui, 'Order Reqs.')
		self.assertIs(gui.active_tab(), tab)
		self.assertEqual(gui.notebook.tab.get(), gui.notebook.pages['Unit Training Reqs.'][1])
		self.assertEqual(self.code(view), 'is_not_lifted_off\n')

	def test_switching_file_tab_discarding(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=False):
			orders_tab = self.display_tab(gui, 'Order Reqs.')
		self.assertIs(gui.active_tab(), orders_tab)
		self.assertFalse(view.is_edited())
		self.assertFalse(gui.units_data.edited)

	def test_switching_mode_cancelled_stays(self) -> None:
		_, tab, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		notebook = tab.editor.notebook
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None):
			notebook.tab.set(notebook.pages['Builder'][1])
			notebook.display('Builder')
		self.assertIs(notebook.active, view)
		self.assertEqual(notebook.tab.get(), notebook.pages['Script'][1])
		self.assertTrue(view.is_edited())

	def test_switching_mode_applying(self) -> None:
		gui, tab, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		notebook = tab.editor.notebook
		with mock.patch(ASK_YES_NO_CANCEL, return_value=True):
			notebook.display('Builder')
		self.assertIs(notebook.active, tab.editor.builder_view)
		self.assertTrue(gui.units_data.edited)

	def test_exit_cancelled_stays(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None), mock.patch.object(gui, 'check_saved') as check_saved:
			gui.exit()
		check_saved.assert_not_called()
		self.assertTrue(view.is_edited())

	def test_new_asks_first(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None) as ask:
			gui.new()
		ask.assert_called_once()
		self.assertEqual(self.code(view), 'is_not_lifted_off\n')

	# Saving with unapplied changes

	def test_save_can_apply_first(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=True) as ask, mock.patch.object(gui, 'save_graft_data') as save_graft_data:
			gui.save()
		self.assertIn('before saving', ask.call_args.kwargs['message'])
		save_graft_data.assert_called_once()
		script = gui.units_data.graft.get_script(0)
		assert script is not None
		self.assertEqual(len(script.commands), 1)

	def test_save_without_applying_keeps_the_code(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=False), mock.patch.object(gui, 'save_graft_data') as save_graft_data:
			gui.save()
		save_graft_data.assert_called_once()
		script = gui.units_data.graft.get_script(0)
		assert script is not None
		self.assertEqual(len(script.commands), 3)
		self.assertTrue(view.is_edited())
		self.assertEqual(self.code(view), 'is_not_lifted_off\n')

	def test_save_cancelled(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None), mock.patch.object(gui, 'save_graft_data') as save_graft_data:
			gui.save()
		save_graft_data.assert_not_called()

	# Shortcuts

	def focus_text(self, gui: PyGRAFT, view: ReqScriptView) -> None:
		gui.deiconify()
		gui.focus_force()
		view.text.text.focus_force()
		self.pump(gui)

	def test_apply_shortcut_applies(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off')
		self.focus_text(gui, view)
		view.text.text.event_generate(UI.Ctrl.Return.event())
		self.pump(gui)
		self.assertTrue(gui.units_data.edited)

	def test_apply_shortcut_does_not_type_a_newline(self) -> None:
		gui, _, view = self.open_req_tab()
		# Code with an error isn't reloaded, so the code after applying is what's in the editor
		self.set_code(view, 'is_awesome')
		view.text.mark_set(UI.INSERT, UI.END)
		self.focus_text(gui, view)
		with mock.patch(ERROR_DIALOG) as error_dialog:
			view.text.text.event_generate(UI.Ctrl.Return.event())
			self.pump(gui)
		error_dialog.assert_called_once()
		self.assertEqual(self.code(view), 'is_awesome')

	def test_tab_completes_a_tab_indented_command(self) -> None:
		gui, _, view = self.open_req_tab('Upgrade Research Reqs.')
		# Sub-list bodies are indented with a tab, which isn't part of the word being completed
		self.set_code(view, 'level_1_requires\n\tend')
		view.text.mark_set(UI.INSERT, UI.END)
		self.focus_text(gui, view)
		view.text.text.event_generate(UI.Key.Tab.event())
		self.pump(gui)
		self.assertEqual(self.code(view), 'level_1_requires\n\tend_level_requirements')

	def test_test_shortcut_does_not_edit_the_code(self) -> None:
		gui, _, view = self.open_req_tab()
		self.set_code(view, 'is_not_lifted_off\n')
		view.text.mark_set(UI.INSERT, '1.5')
		self.focus_text(gui, view)
		with mock.patch(SHOW_INFO) as show_info:
			view.text.text.event_generate(UI.Ctrl.t.event())
			self.pump(gui)
		show_info.assert_called_once()
		# The text's own Ctrl+T (transposing characters) doesn't run
		self.assertEqual(self.code(view), 'is_not_lifted_off\n')

	def test_toolbar_shortcuts_are_bound_on_the_text(self) -> None:
		_, _, view = self.open_req_tab()
		for shortcut in (UI.Ctrl.Return, UI.Ctrl.t, UI.Ctrl.f, UI.Ctrl.Alt.c):
			self.assertTrue(view.text.text.bind(shortcut()))
			self.assertFalse(view.bind(shortcut()))

	# Languages

	def test_highlighted_commands_are_the_files_commands(self) -> None:
		gui, _, unit_view = self.open_req_tab()
		self.set_code(unit_view, 'does_not_have_exit\nis_not_lifted_off\n')
		self.wait_for_highlighting(unit_view)
		self.assertEqual(self.tag_texts(unit_view, 'Command'), ['is_not_lifted_off'])
		unit_view.revert()
		order_tab = self.display_tab(gui, 'Order Reqs.')
		assert isinstance(order_tab, ReqGraftTab)
		order_view = order_tab.editor.script_view
		self.set_code(order_view, 'does_not_have_exit\nis_not_lifted_off\n')
		self.wait_for_highlighting(order_view)
		self.assertEqual(self.tag_texts(order_view, 'Command'), ['does_not_have_exit', 'is_not_lifted_off'])

	def test_command_tooltips_stay_bound_after_switching_tabs(self) -> None:
		gui, _, view = self.open_req_tab()
		self.display_tab(gui, 'Order Reqs.')
		self.display_tab(gui, 'Unit Training Reqs.')
		self.assertTrue(view.text.text.tk.call(str(view.text.text), 'tag', 'bind', 'Command'))
		tooltip = getattr(view.text.text, '_tooltip_CommandTooltip')
		self.assertIn('Is not lifted off', tooltip.gettext('is_not_lifted_off'))

	def test_every_req_tab_has_an_editor_for_its_file(self) -> None:
		gui = self.open_pygraft()
		for tab in gui.tabs:
			if isinstance(tab, ReqGraftTab):
				self.assertIs(tab.editor.script_view.graft_data, tab.graft_data)
