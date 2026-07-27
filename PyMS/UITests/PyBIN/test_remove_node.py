
from .utils import PyBINTestCase

from ...FileFormats import DialogBIN
from ...Utilities import IO


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
