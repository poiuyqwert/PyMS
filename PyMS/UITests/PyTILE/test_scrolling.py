
from .utils import PyTILETestCase

from ...PyTILE.PyTILE import PyTILE
from ...Utilities import UIKit as UI


class Test_PyTILE_scrolling(PyTILETestCase):
	def _canvas(self, view: UI.ScrollView | UI.FlowView) -> UI.Canvas:
		# The canvas scrolling the view's content
		return next(child for child in view.winfo_children() if isinstance(child, UI.Canvas))

	def _open(self) -> PyTILE:
		# Enough groups that the group palette scrolls, in a window short enough that the group settings scroll too
		gui = self.with_open_tileset(group_count=400)
		gui.geometry('700x300')
		self.pump(gui)
		return gui

	def test_wheel_over_group_settings_leaves_the_palette_alone(self) -> None:
		gui = self._open()
		self.assertLess(self._canvas(gui.flow_view).yview()[1], 1)
		gui.flow_view.subviews[0].event_generate(UI.Mouse.Scroll(), delta=-120)
		self.pump(gui)
		self.assertGreater(self._canvas(gui.flow_view).yview()[0], 0)
		self.assertEqual(gui.palette.canvas.yview()[0], 0)

	def test_wheel_over_palette_leaves_the_group_settings_alone(self) -> None:
		gui = self._open()
		gui.palette.canvas.event_generate(UI.Mouse.Scroll(), delta=-120)
		self.pump(gui)
		self.assertGreater(gui.palette.canvas.yview()[0], 0)
		self.assertEqual(self._canvas(gui.flow_view).yview()[0], 0)
