from .utils import PyGRAFTTestCase, ASK_YES_NO_CANCEL

from ...PyGRAFT.PyGRAFT import PyGRAFT
from ...PyGRAFT.Tabs import ButtonSetsTab
from ...PyGRAFT.ButtonSetEditor.ScriptView import ButtonSetScriptView
from ...FileFormats.Graft import Button, ButtonSet
from ...FileFormats.Graft.CodeHandlers import GraftSerializeContext
from ...Utilities import UIKit as UI

import io
import time

from unittest import mock

ERROR_DIALOG = 'PyMS.PyGRAFT.ScriptEditor.ScriptView.ErrorDialog'
SHOW_INFO = 'tkinter.messagebox.showinfo'

# Always, Move
MOVE_CODE = 'button {\n\tposition TL\n\ticon 228\n\talways\n\tmove\n\tenabled_str 664\n\tdisabled_str 0\n}\n'
MOVE_BUTTON = Button(position=1, icon=228, condition=3, action=9, enabled_string=664)

class Test_PyGRAFT_button_sets_editor(PyGRAFTTestCase):
	def open_button_sets_tab(self) -> tuple[PyGRAFT, ButtonSetsTab, ButtonSetScriptView]:
		gui = self.open_pygraft()
		tab = self.display_tab(gui, 'Button Sets')
		assert isinstance(tab, ButtonSetsTab)
		return gui, tab, tab.editor.script_view

	def set_body(self, gui: PyGRAFT, set_id: int) -> str:
		# The decompiled button set as the view shows it (without the final newline, which the text widget supplies)
		output = io.StringIO()
		gui.buttons_data.graft.decompile_button_set(GraftSerializeContext(output, gui.data_context), set_id)
		return output.getvalue().rstrip('\n')

	def code(self, view: ButtonSetScriptView) -> str:
		return view.text.get('1.0', 'end-1c')

	def set_code(self, view: ButtonSetScriptView, code: str) -> None:
		view.text.delete('1.0', UI.END)
		view.text.insert('1.0', code)
		self.pump(view)

	def wait_for_highlighting(self, view: ButtonSetScriptView) -> None:
		# Highlighting is done in an `after` callback
		for _ in range(20):
			self.pump(view)
			if not view.text.tag_ranges('Update'):
				return
			time.sleep(0.01)

	def tag_texts(self, view: ButtonSetScriptView, tag: str) -> list[str]:
		ranges = view.text.tag_ranges(tag)
		return [view.text.get(ranges[n], ranges[n + 1]) for n in range(0, len(ranges), 2)]

	# Loading

	def test_selected_set_loads_its_buttons(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		self.assertEqual(self.code(view), self.set_body(gui, 0))
		self.assertTrue(self.code(view).startswith('button {\n\tposition BL'))
		self.assertNotIn('button_set', self.code(view))
		self.assertFalse(view.is_edited())
		self.assertEqual(view.apply_button['state'], UI.DISABLED)
		self.assertFalse(gui.buttons_data.edited)

	def test_selecting_a_set_loads_it(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		self.select_in_list(gui, 5)
		self.assertEqual(view.entry_id, 5)
		self.assertEqual(self.code(view), self.set_body(gui, 5))

	def test_script_mode_is_shown_first(self) -> None:
		_, tab, view = self.open_button_sets_tab()
		self.assertIs(tab.editor.notebook.active, view)

	def test_no_button_sets_is_read_only(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		gui.buttons_data.graft.button_sets = []
		gui.buttons_data.graft.button_cards = []
		gui.refresh()
		self.pump(gui)
		self.assertIsNone(view.entry_id)
		self.assertEqual(self.code(view), '')
		self.assertTrue(view.text.read_only)

	# Editing and applying

	def test_typing_marks_only_the_editor_edited(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		self.assertTrue(view.is_edited())
		self.assertEqual(view.apply_button['state'], UI.NORMAL)
		self.assertEqual(view.revert_button['state'], UI.NORMAL)
		self.assertEqual(view.editstatus['state'], UI.NORMAL)
		self.assertFalse(gui.buttons_data.edited)

	def test_apply_sets_the_buttons(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		self.select_in_list(gui, 3)
		self.set_code(view, '# Not kept\n' + MOVE_CODE)
		self.assertTrue(view.apply())
		self.assertEqual(gui.buttons_data.graft.button_sets[3], ButtonSet([MOVE_BUTTON]))
		self.assertTrue(gui.buttons_data.edited)
		self.assertEqual(gui.editstatus['state'], UI.NORMAL)
		# The editor shows the applied buttons, and is no longer edited
		self.assertEqual(self.code(view), self.set_body(gui, 3))
		self.assertNotIn('Not kept', self.code(view))
		self.assertFalse(view.is_edited())
		self.assertEqual(view.editstatus['state'], UI.DISABLED)
		self.assertEqual(self.list_selection(gui), [3])

	def test_applying_empty_code_removes_every_button(self) -> None:
		gui, tab, view = self.open_button_sets_tab()
		self.set_code(view, '# Nothing\n')
		with mock.patch(ASK_YES_NO_CANCEL) as ask:
			self.assertTrue(view.apply())
		ask.assert_not_called()
		self.assertEqual(gui.buttons_data.graft.button_sets[0], ButtonSet())
		# The set is kept, so the list is unchanged
		self.assertEqual(len(tab.entry_names()), 98)
		self.assertEqual(self.code(view), '')

	def test_header_is_an_error(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		self.set_code(view, 'button_set 0 {\n}\n')
		with mock.patch(ERROR_DIALOG) as error_dialog:
			self.assertFalse(view.apply())
		error_dialog.assert_called_once()
		self.assertIn('headers are not allowed', str(error_dialog.call_args.args[1]))
		self.assertTrue(view.is_edited())
		self.assertFalse(gui.buttons_data.edited)

	def test_compile_error_keeps_the_code(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		code = MOVE_CODE + 'button {\n\tposition TM\n\ticon 0\n\tis_awesome\n}\n'
		self.set_code(view, code)
		with mock.patch(ERROR_DIALOG) as error_dialog:
			self.assertFalse(view.apply())
		self.assertIn("Unknown button command 'is_awesome'", str(error_dialog.call_args.args[1]))
		self.assertEqual(self.code(view), code)
		self.assertFalse(gui.buttons_data.edited)
		self.assertEqual(str(view.text.tag_ranges('Error')[0]), '12.0')

	def test_test_reports_success_without_applying(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		with mock.patch(SHOW_INFO) as show_info:
			view.test()
		show_info.assert_called_once()
		self.assertTrue(view.is_edited())
		self.assertFalse(gui.buttons_data.edited)

	def test_revert_restores_the_buttons(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		view.revert()
		self.assertEqual(self.code(view), self.set_body(gui, 0))
		self.assertFalse(view.is_edited())

	# Leaving with unapplied changes

	def test_selecting_another_set_cancelled_stays(self) -> None:
		gui, tab, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None) as ask:
			self.select_in_list(gui, 1)
		self.assertIn('Replay: Paused', ask.call_args.kwargs['message'])
		self.assertEqual(tab.selected, 0)
		self.assertEqual(self.list_selection(gui), [0])
		self.assertEqual(self.code(view), MOVE_CODE)

	def test_selecting_another_set_discarding(self) -> None:
		gui, tab, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		with mock.patch(ASK_YES_NO_CANCEL, return_value=False):
			self.select_in_list(gui, 1)
		self.assertEqual(tab.selected, 1)
		self.assertEqual(self.code(view), self.set_body(gui, 1))
		self.assertFalse(gui.buttons_data.edited)

	def test_selecting_another_set_applying(self) -> None:
		gui, tab, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		with mock.patch(ASK_YES_NO_CANCEL, return_value=True):
			self.select_in_list(gui, 1)
		self.assertEqual(tab.selected, 1)
		self.assertEqual(self.list_selection(gui), [1])
		self.assertEqual(gui.buttons_data.graft.button_sets[0], ButtonSet([MOVE_BUTTON]))
		self.assertTrue(gui.buttons_data.edited)

	def test_applying_failure_stays(self) -> None:
		gui, tab, view = self.open_button_sets_tab()
		self.set_code(view, 'is_awesome\n')
		with mock.patch(ASK_YES_NO_CANCEL, return_value=True), mock.patch(ERROR_DIALOG):
			self.select_in_list(gui, 1)
		self.assertEqual(tab.selected, 0)
		self.assertEqual(self.code(view), 'is_awesome\n')

	def test_unedited_editor_leaves_without_asking(self) -> None:
		gui, tab, _ = self.open_button_sets_tab()
		with mock.patch(ASK_YES_NO_CANCEL) as ask:
			self.select_in_list(gui, 1)
			self.display_tab(gui, 'Button Cards')
		ask.assert_not_called()
		self.assertEqual(tab.selected, 1)

	def test_switching_file_tab_cancelled_stays(self) -> None:
		gui, tab, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None):
			# Clicking a tab selects it before displaying it
			gui.notebook.tab.set(gui.notebook.pages['Button Cards'][1])
			self.display_tab(gui, 'Button Cards')
		self.assertIs(gui.active_tab(), tab)
		self.assertEqual(gui.notebook.tab.get(), gui.notebook.pages['Button Sets'][1])
		self.assertEqual(self.code(view), MOVE_CODE)

	def test_switching_file_tab_applying(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		with mock.patch(ASK_YES_NO_CANCEL, return_value=True):
			cards_tab = self.display_tab(gui, 'Button Cards')
		self.assertIs(gui.active_tab(), cards_tab)
		self.assertEqual(gui.buttons_data.graft.button_sets[0], ButtonSet([MOVE_BUTTON]))
		self.assertFalse(view.is_edited())

	def test_switching_mode_cancelled_stays(self) -> None:
		_, tab, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		notebook = tab.editor.notebook
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None):
			notebook.tab.set(notebook.pages['Builder'][1])
			notebook.display('Builder')
		self.assertIs(notebook.active, view)
		self.assertEqual(notebook.tab.get(), notebook.pages['Script'][1])
		self.assertTrue(view.is_edited())

	def test_switching_mode_discarding(self) -> None:
		gui, tab, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		notebook = tab.editor.notebook
		with mock.patch(ASK_YES_NO_CANCEL, return_value=False):
			notebook.display('Builder')
		self.assertIs(notebook.active, tab.editor.builder_view)
		self.assertFalse(view.is_edited())
		self.assertFalse(gui.buttons_data.edited)

	def test_new_asks_first(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None) as ask:
			gui.new()
		ask.assert_called_once()
		self.assertEqual(self.code(view), MOVE_CODE)

	# Saving with unapplied changes

	def test_save_can_apply_first(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		with mock.patch(ASK_YES_NO_CANCEL, return_value=True) as ask, mock.patch.object(gui, 'save_graft_data') as save_graft_data:
			gui.save()
		self.assertIn('before saving', ask.call_args.kwargs['message'])
		save_graft_data.assert_called_once()
		self.assertEqual(gui.buttons_data.graft.button_sets[0], ButtonSet([MOVE_BUTTON]))

	def test_save_without_applying_keeps_the_code(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		with mock.patch(ASK_YES_NO_CANCEL, return_value=False), mock.patch.object(gui, 'save_graft_data') as save_graft_data:
			gui.save()
		save_graft_data.assert_called_once()
		self.assertEqual(len(gui.buttons_data.graft.button_sets[0].buttons), 3)
		self.assertTrue(view.is_edited())
		self.assertEqual(self.code(view), MOVE_CODE)

	def test_save_cancelled(self) -> None:
		gui, _, view = self.open_button_sets_tab()
		self.set_code(view, MOVE_CODE)
		with mock.patch(ASK_YES_NO_CANCEL, return_value=None), mock.patch.object(gui, 'save_graft_data') as save_graft_data:
			gui.save()
		save_graft_data.assert_not_called()

	# Language

	def test_highlighted_commands_are_button_commands(self) -> None:
		_, _, view = self.open_button_sets_tab()
		self.set_code(view, 'button {\n\tposition TL\n\tuse_button_set 0\n\tmove\n}\n')
		self.wait_for_highlighting(view)
		self.assertEqual(self.tag_texts(view, 'Command'), ['button', 'position', 'move'])
		self.assertEqual(self.tag_texts(view, 'Operator'), ['{', '}'])

	def test_highlighted_keywords_are_parameter_keywords(self) -> None:
		_, _, view = self.open_button_sets_tab()
		self.set_code(view, 'button {\n\tposition BL\n\tcancel_train last\n\tTLX\n}\n')
		self.wait_for_highlighting(view)
		self.assertEqual(self.tag_texts(view, 'Keyword'), ['BL', 'last'])

	def test_autocomplete_offers_the_button_keyword(self) -> None:
		_, _, view = self.open_button_sets_tab()
		options = view.get_autocomplete_options('')
		assert options is not None
		self.assertIn('button', options)
		self.assertIn('move', options)
		self.assertNotIn('use_button_set', options)
		self.assertIn('BL', options)
		self.assertIn('last', options)
