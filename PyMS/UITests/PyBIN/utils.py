
from ..harness import UITestCase

from ...PyBIN.PyBIN import PyBIN
from ...PyBIN.WidgetNode import WidgetNode
from ...FileFormats import DialogBIN

import tkinter

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
