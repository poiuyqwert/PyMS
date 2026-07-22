
import tkinter

from unittest import mock

from .harness import UITestCase

from ..PyBIN.PyBIN import PyBIN
from ..PyBIN.WidgetNode import WidgetNode
from ..FileFormats import DialogBIN
from ..Utilities import IO
from ..Utilities import UIKit as UI
from ..Utilities.CheckSaved import CheckSaved

# These tests drive PyBIN's widget tree through its public command methods,
# asserting on both the canvas and the model. The harness neutralizes settings
# I/O, analytics, the update check, and the tracer; the MPQ handler is stubbed
# to find no files so asset loads fall back to their failure paths without
# touching disk.


class PyBINTestCase(UITestCase):
	def make_pybin(self) -> PyBIN:
		gui = self.make_window(PyBIN, extra_patches={
			'PyMS.Utilities.MPQHandler.MPQHandler.get_file': {'return_value': None},
		})
		gui.new()
		self.pump(gui)
		return gui

	def add_group_with_buttons(self, gui: PyBIN) -> tuple[WidgetNode, list[WidgetNode]]:
		# Build (via the same command the toolbar menu invokes) a group under the
		# dialog containing two buttons, leaving the group selected.
		assert gui.dialog is not None
		gui.select_node(gui.dialog)
		gui.add_new_node(-1)
		group = gui.selected_node
		assert group is not None
		gui.add_new_node(DialogBIN.BINWidget.TYPE_BUTTON)
		button1 = gui.selected_node
		assert button1 is not None
		gui.add_new_node(DialogBIN.BINWidget.TYPE_BUTTON)
		button2 = gui.selected_node
		assert button2 is not None
		self.pump(gui)
		self.assertEqual(group.children, [button2, button1])
		gui.select_node(group)
		self.pump(gui)
		return (group, [button1, button2])

	def canvas_item_ids(self, gui: PyBIN) -> set[int]:
		return set(tkinter.Canvas.find_all(gui.widgetCanvas))


class Test_PyBIN_import(PyBINTestCase):
	def test_import_marks_document_edited(self) -> None:
		# A freshly imported dialog is unsaved work: it must be flagged edited
		# so closing without saving prompts instead of silently discarding it.
		gui = self.make_pybin()
		assert gui.bin is not None
		dialog_text = IO.output_to_text(gui.bin.decompile)
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value=dialog_text):
			gui.iimport()
		self.pump(gui)
		self.assertTrue(gui.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	def test_import_without_open_file_leaves_no_save_target_so_save_prompts(self) -> None:
		gui = self.make_pybin()
		assert gui.bin is not None
		# IO.InputText treats a string that isn't an existing path as raw
		# content, so returning decompiled text from the file dialog keeps the
		# import entirely in-memory.
		dialog_text = IO.output_to_text(gui.bin.decompile)
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value=dialog_text):
			gui.iimport()
		self.pump(gui)
		self.assertIsNone(gui.file)
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_save', return_value='') as select_save:
			result = gui.save()
		select_save.assert_called_once()
		self.assertEqual(result, CheckSaved.cancelled)

	def test_import_into_open_file_keeps_it_as_the_save_target(self) -> None:
		gui = self.make_pybin()
		assert gui.bin is not None
		dialog_text = IO.output_to_text(gui.bin.decompile)
		with mock.patch('PyMS.FileFormats.DialogBIN.DialogBIN.DialogBIN.load', return_value=None):
			gui.open(file='opened.bin')
		self.pump(gui)
		self.assertEqual(gui.file, 'opened.bin')
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value=dialog_text):
			gui.iimport()
		self.pump(gui)
		self.assertEqual(gui.file, 'opened.bin')
		with mock.patch('PyMS.FileFormats.DialogBIN.DialogBIN.DialogBIN.save', return_value=None) as bin_save, \
				mock.patch('PyMS.PyBIN.PyBIN.check_allow_overwrite_internal_file', return_value=True):
			result = gui.save()
		self.assertEqual(result, CheckSaved.saved)
		bin_save.assert_called_once_with('opened.bin')


class Test_PyBIN_remove_node(PyBINTestCase):
	def test_removing_widget_removes_it_from_model(self) -> None:
		gui = self.make_pybin()
		assert gui.bin is not None and gui.dialog is not None
		gui.select_node(gui.dialog)
		gui.add_new_node(DialogBIN.BINWidget.TYPE_BUTTON)
		gui.remove_node()
		self.pump(gui)
		self.assertEqual(gui.bin.widgets, [gui.dialog.widget])
		self.assertEqual(gui.flattened_nodes(), [gui.dialog])
		self.assertIsNone(gui.selected_node)
		self.assertTrue(gui.edited)

	def test_removing_group_removes_descendant_widgets_from_model(self) -> None:
		gui = self.make_pybin()
		assert gui.bin is not None and gui.dialog is not None
		self.add_group_with_buttons(gui)
		self.assertEqual(len(gui.bin.widgets), 3)
		gui.remove_node()
		self.pump(gui)
		self.assertEqual(gui.bin.widgets, [gui.dialog.widget])
		self.assertEqual(gui.flattened_nodes(), [gui.dialog])
		self.assertIsNone(gui.selected_node)
		self.assertTrue(gui.edited)

	def test_removing_group_excludes_descendant_widgets_from_saved_file(self) -> None:
		gui = self.make_pybin()
		assert gui.bin is not None
		self.add_group_with_buttons(gui)
		gui.remove_node()
		reloaded = DialogBIN.DialogBIN()
		reloaded.load(IO.output_to_bytes(gui.bin.save))
		self.assertEqual(len(reloaded.widgets), 1)
		self.assertEqual(reloaded.widgets[0].type, DialogBIN.BINWidget.TYPE_DIALOG)

	def test_removing_group_removes_descendant_canvas_items(self) -> None:
		gui = self.make_pybin()
		baseline = self.canvas_item_ids(gui)
		group, buttons = self.add_group_with_buttons(gui)
		self.assertGreater(len(self.canvas_item_ids(gui)), len(baseline))
		gui.remove_node()
		self.pump(gui)
		for node in (group, *buttons):
			self.assertIsNone(node.item_bounds)
		self.assertEqual(self.canvas_item_ids(gui), baseline)

	def test_removing_group_containing_scr_widget_clears_scr_flag(self) -> None:
		gui = self.make_pybin()
		assert gui.bin is not None and gui.dialog is not None
		gui.select_node(gui.dialog)
		gui.add_new_node(-1)
		group = gui.selected_node
		assert group is not None
		gui.add_new_node(DialogBIN.BINWidget.TYPE_HTML)
		self.pump(gui)
		self.assertTrue(gui.scr_enabled.get())
		gui.select_node(group)
		gui.remove_node()
		self.pump(gui)
		self.assertEqual(gui.bin.widgets, [gui.dialog.widget])
		self.assertFalse(gui.scr_enabled.get())
