
from unittest import mock

from .utils import PyICETestCase

from ...PyICE.CodeEditDialog import CodeEditDialog
from ...Utilities import UIKit as UI

CODE = """.headerstart
IsId          0
Type          0
Init          Local00
.headerend

Local00:
	goto          Local01
	wait          1
Local01:
	end
"""

class Test_Goto_Block_Definition(PyICETestCase):
	def make_editor(self) -> CodeEditDialog:
		pyice = self.make_pyice()
		# The dialog always schedules a decompile of the selected scripts, which needs a loaded iscript.bin
		patcher = mock.patch.object(CodeEditDialog, 'load')
		patcher.start()
		self.addCleanup(patcher.stop)
		editor = CodeEditDialog(pyice, pyice, pyice.config_, [])
		editor.text.load(CODE)
		editor.geometry('600x400')
		self.show(editor)
		return editor

	def ctrl_click(self, editor: CodeEditDialog, index: str) -> None:
		bbox = editor.text.text.bbox(index)
		assert bbox is not None
		self.click(editor.text.text, bbox[0] + 1, bbox[1] + 1, UI.Ctrl.Click_Left)

	def test_ctrl_click_block_reference_moves_cursor_to_definition(self) -> None:
		editor = self.make_editor()
		self.ctrl_click(editor, '8.16')
		self.assertEqual(editor.text.index(UI.INSERT), '10.0')

	def test_ctrl_click_header_block_reference_moves_cursor_to_definition(self) -> None:
		editor = self.make_editor()
		self.ctrl_click(editor, '4.16')
		self.assertEqual(editor.text.index(UI.INSERT), '7.0')

	def test_ctrl_click_non_block_word_does_not_jump(self) -> None:
		editor = self.make_editor()
		self.ctrl_click(editor, '9.2')
		self.assertEqual(editor.text.index(f'{UI.INSERT} linestart'), '9.0')

	def test_undefined_block_name_has_no_definition(self) -> None:
		editor = self.make_editor()
		self.assertIsNone(editor.find_definition('Local99'))

	def test_autocomplete_includes_block_names(self) -> None:
		editor = self.make_editor()
		options = editor.get_autocomplete_options('\tgoto Lo')
		assert options is not None
		self.assertIn('Local00', options)
		self.assertIn('Local01', options)
