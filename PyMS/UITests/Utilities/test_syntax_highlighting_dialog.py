
from unittest import mock

from ..harness import UITestCase

from ...Utilities import UIKit as UI
from ...Utilities import Config
from ...Utilities.PyMSError import PyMSError
from ...Utilities.SyntaxHighlightingDialog import SyntaxHighlightingDialog
from ...Utilities.SyntaxHighlightingFile import SyntaxHighlightingFile

ERROR_DIALOG = 'PyMS.Utilities.SyntaxHighlightingDialog.ErrorDialog'
PATH_EXISTS = 'PyMS.Utilities.SyntaxHighlightingDialog.os.path.exists'

def _loads(highlights: dict):
	def load(self: SyntaxHighlightingFile, _path: str) -> None:
		self.highlights = dict(highlights)
	return load

class Test_SyntaxHighlightingDialog(UITestCase):
	def setUp(self) -> None:
		super().setUp()
		self.number = UI.HighlightComponent(name='Number', description='Numbers', highlight_style=Config.HighlightStyle(default=Config.Style(foreground='#FF0000')))
		self.comment = UI.HighlightComponent(name='Comment', description='Comments', highlight_style=Config.HighlightStyle(default=Config.Style(foreground='#008000')))
		self.select_file = mock.Mock(spec=Config.SelectFile)

	def make_dialog(self) -> SyntaxHighlightingDialog:
		window = self.make_window(UI.MainWindow)
		with mock.patch.object(UI.WindowExtensions, 'grab_wait', lambda self: None):
			dialog = SyntaxHighlightingDialog(window, [self.number, self.comment], self.select_file)
		self.addCleanup(self._destroy, dialog)
		self.pump(dialog)
		return dialog

	def test_import_applies_matching_styles_and_refreshes_selection(self) -> None:
		dialog = self.make_dialog()
		self.select_file.select_open.return_value = 'colors.json'
		highlights = {'number': {'foreground': '#00FF00', 'background': '#000000', 'bold': True}, 'ai_id': {'foreground': '#123456'}}
		with mock.patch.object(SyntaxHighlightingFile, 'load', _loads(highlights)), \
				mock.patch(ERROR_DIALOG) as error_dialog:
			dialog.iimport()
		error_dialog.assert_not_called()
		self.assertEqual(self.number.highlight_style.style, Config.Style(foreground='#00FF00', background='#000000', bold=True))
		self.assertEqual(self.comment.highlight_style.style, Config.Style(foreground='#008000'))
		self.assertEqual(dialog.fgcanvas['background'], '#00FF00')
		self.assertTrue(dialog.bg.get())
		self.assertTrue(dialog.bold.get())

	def test_import_without_matching_styles_shows_error(self) -> None:
		dialog = self.make_dialog()
		self.select_file.select_open.return_value = 'colors.json'
		with mock.patch.object(SyntaxHighlightingFile, 'load', _loads({'ai_id': {'foreground': '#123456'}})), \
				mock.patch(ERROR_DIALOG) as error_dialog:
			dialog.iimport()
		error_dialog.assert_called_once()
		self.assertIn('no syntax highlighting styles used by this program', error_dialog.call_args.args[1].error)
		self.assertEqual(self.number.highlight_style.style, Config.Style(foreground='#FF0000'))

	def test_import_invalid_file_shows_load_error(self) -> None:
		dialog = self.make_dialog()
		self.select_file.select_open.return_value = 'colors.json'
		error = PyMSError('Load', 'Syntax highlighting file is not valid JSON')
		with mock.patch.object(SyntaxHighlightingFile, 'load', side_effect=error), \
				mock.patch(ERROR_DIALOG) as error_dialog:
			dialog.iimport()
		error_dialog.assert_called_once_with(dialog, error)

	def test_cancel_reverts_import(self) -> None:
		dialog = self.make_dialog()
		self.select_file.select_open.return_value = 'colors.json'
		with mock.patch.object(SyntaxHighlightingFile, 'load', _loads({'number': {'foreground': '#00FF00'}})):
			dialog.iimport()
		dialog.cancel()
		self.assertFalse(dialog.updated)
		self.assertEqual(self.number.highlight_style.style, Config.Style(foreground='#FF0000'))

	def test_export_merges_into_existing_file(self) -> None:
		dialog = self.make_dialog()
		self.select_file.select_save.return_value = 'colors.json'
		saved: list[dict] = []
		with mock.patch(PATH_EXISTS, return_value=True), \
				mock.patch.object(SyntaxHighlightingFile, 'load', _loads({'ai_id': {'foreground': '#123456'}, 'number': {'foreground': '#000000'}})), \
				mock.patch.object(SyntaxHighlightingFile, 'save', lambda self, _path: saved.append(dict(self.highlights))):
			dialog.export()
		self.assertEqual(saved, [{
			'ai_id': {'foreground': '#123456'},
			'number': {'foreground': '#FF0000', 'background': None, 'bold': False},
			'comment': {'foreground': '#008000', 'background': None, 'bold': False},
		}])

	def test_export_over_invalid_file_asks_before_overwriting(self) -> None:
		dialog = self.make_dialog()
		self.select_file.select_save.return_value = 'colors.json'
		saved: list[dict] = []
		with mock.patch(PATH_EXISTS, return_value=True), \
				mock.patch.object(SyntaxHighlightingFile, 'load', side_effect=PyMSError('Load', 'Syntax highlighting file is not valid JSON')), \
				mock.patch.object(SyntaxHighlightingFile, 'save', lambda self, _path: saved.append(dict(self.highlights))), \
				mock.patch.object(UI.MessageBox, 'askyesno', return_value=False) as askyesno:
			dialog.export()
			self.assertEqual(saved, [])
			askyesno.return_value = True
			dialog.export()
		self.assertEqual(askyesno.call_count, 2)
		self.assertEqual(list(saved[0].keys()), ['number', 'comment'])

	def test_export_write_failure_shows_error(self) -> None:
		dialog = self.make_dialog()
		self.select_file.select_save.return_value = 'colors.json'
		with mock.patch(PATH_EXISTS, return_value=False), \
				mock.patch.object(SyntaxHighlightingFile, 'save', side_effect=OSError('denied')), \
				mock.patch(ERROR_DIALOG) as error_dialog:
			dialog.export()
		error_dialog.assert_called_once()
		self.assertIn("Couldn't write", error_dialog.call_args.args[1].error)

	def test_reset_menu_lists_all_and_selected(self) -> None:
		dialog = self.make_dialog()
		last = dialog.reset_menu.index('end')
		assert last is not None
		labels = [dialog.reset_menu.entrycget(index, 'label') for index in range(last + 1)]
		self.assertEqual(labels, ['All Styles', 'Selected Style'])

	def test_reset_button_posts_reset_menu(self) -> None:
		dialog = self.make_dialog()
		with mock.patch.object(dialog.reset_menu, 'post') as post:
			dialog.reset_button.invoke()
		post.assert_called_once()

	def test_toolbar_is_below_listbox(self) -> None:
		dialog = self.make_dialog()
		self.assertEqual(dialog.toolbar.winfo_rootx(), dialog.listbox.winfo_rootx())
		self.assertGreaterEqual(dialog.toolbar.winfo_rooty(), dialog.listbox.winfo_rooty() + dialog.listbox.winfo_height())

	def test_reset_all_styles_restores_every_default(self) -> None:
		dialog = self.make_dialog()
		self.number.highlight_style.style = Config.Style(background='#FFFFFF', bold=True)
		self.comment.highlight_style.style = Config.Style()
		dialog.reset_menu.invoke('All Styles')
		self.assertEqual(self.number.highlight_style.style, Config.Style(foreground='#FF0000'))
		self.assertEqual(self.comment.highlight_style.style, Config.Style(foreground='#008000'))
		self.assertEqual(dialog.fgcanvas['background'], '#FF0000')
		self.assertFalse(dialog.bold.get())

	def test_reset_selected_style_only_restores_selection(self) -> None:
		dialog = self.make_dialog()
		self.number.highlight_style.style = Config.Style(background='#FFFFFF')
		self.comment.highlight_style.style = Config.Style(bold=True)
		dialog.listbox.select_clear(0, UI.END)
		dialog.listbox.select_set(1)
		dialog.highlight_component_selected()
		dialog.reset_menu.invoke('Selected Style')
		self.assertEqual(self.comment.highlight_style.style, Config.Style(foreground='#008000'))
		self.assertEqual(self.number.highlight_style.style, Config.Style(background='#FFFFFF'))
		self.assertEqual(dialog.fgcanvas['background'], '#008000')
		self.assertFalse(dialog.bold.get())
