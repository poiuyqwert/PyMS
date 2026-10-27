
from .utils import PyAITestCase

from ...PyAI.CodeEditDialog import CodeEditDialog
from ...Utilities import UIKit as UI

CODE = """:start
    goto(target)
    stop()
--target--
    stop()
"""

class Test_Goto_Block_Definition(PyAITestCase):
	def make_editor(self) -> CodeEditDialog:
		pyai = self.make_pyai()
		editor = CodeEditDialog(pyai, pyai, pyai.config_, [])
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
		self.ctrl_click(editor, '2.11')
		self.assertEqual(editor.text.index(UI.INSERT), '4.0')

	def test_both_block_definition_forms_are_found(self) -> None:
		editor = self.make_editor()
		self.assertEqual(editor.find_definition('start'), '1.0')
		self.assertEqual(editor.find_definition('target'), '4.0')

	def test_ctrl_click_non_block_word_does_not_jump(self) -> None:
		editor = self.make_editor()
		self.ctrl_click(editor, '3.6')
		self.assertEqual(editor.text.index(f'{UI.INSERT} linestart'), '3.0')

	def test_undefined_block_name_has_no_definition(self) -> None:
		editor = self.make_editor()
		self.assertIsNone(editor.find_definition('missing'))
