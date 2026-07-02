
from .harness import UITestCase

from ..PyGRP.PyGRP import PyGRP
from ..FileFormats import GRP

# These tests drive PyGRP's frame list through its public command methods,
# asserting on both the listbox and the model. The harness neutralizes
# settings I/O, analytics, the update check, and the tracer; palettes are
# loaded from the real (read-only) bundled palette files.


def _frame(fill: int, width: int = 4, height: int = 4) -> GRP.Pixels:
	return [[fill] * width for _ in range(height)]


class PyGRPTestCase(UITestCase):
	def with_frames(self, count: int) -> PyGRP:
		# A new GRP populated with `count` distinct in-memory frames.
		gui = self.make_window(PyGRP)
		gui.new()
		assert gui.grp is not None
		gui.grp.load_frames([_frame(n + 1) for n in range(count)])
		gui.frames = [{} for _ in range(count)]
		gui.update_list()
		self.pump(gui)
		return gui

	def selection(self, gui: PyGRP) -> list[int]:
		return [int(i) for i in gui.listbox.curselection()]


class Test_PyGRP_update_list(PyGRPTestCase):
	def test_rebuild_preserves_selection(self) -> None:
		gui = self.with_frames(5)
		gui.listbox.select_set(2)
		gui.update_list()
		self.assertEqual(self.selection(gui), [2])

	def test_rebuild_drops_selection_beyond_new_frame_count(self) -> None:
		gui = self.with_frames(5)
		gui.listbox.select_set(1)
		gui.listbox.select_set(4)
		assert gui.grp is not None
		del gui.grp.images[3:]
		del gui.grp.images_bounds[3:]
		del gui.frames[3:]
		gui.grp.frames = 3
		gui.update_list()
		self.assertEqual(self.selection(gui), [1])


class Test_PyGRP_remove(PyGRPTestCase):
	def test_remove_middle_frame_selects_and_previews_same_index(self) -> None:
		gui = self.with_frames(5)
		gui.listbox.select_set(2)
		gui.remove()
		self.pump(gui)
		assert gui.grp is not None
		self.assertEqual(gui.grp.frames, 4)
		self.assertEqual(self.selection(gui), [2])
		self.assertEqual(gui.frame_index, 2)
		self.assertIsNotNone(gui.item)
		self.assertTrue(gui.edited)

	def test_remove_last_frame_selects_new_last(self) -> None:
		gui = self.with_frames(3)
		gui.listbox.select_set(2)
		gui.remove()
		self.assertEqual(self.selection(gui), [1])
		self.assertEqual(gui.frame_index, 1)

	def test_remove_tail_range_selects_new_last_frame(self) -> None:
		gui = self.with_frames(5)
		gui.listbox.select_set(3, 4)
		gui.remove()
		assert gui.grp is not None
		self.assertEqual(gui.grp.frames, 3)
		self.assertEqual(self.selection(gui), [2])
		self.assertEqual(gui.frame_index, 2)

	def test_remove_all_frames_clears_selection_and_preview(self) -> None:
		gui = self.with_frames(2)
		gui.listbox.select_set(0, 1)
		gui.remove()
		assert gui.grp is not None
		self.assertEqual(gui.grp.frames, 0)
		self.assertEqual(gui.listbox.size(), 0)
		self.assertEqual(self.selection(gui), [])
		self.assertIsNone(gui.frame_index)
		self.assertIsNone(gui.item)
		self.assertEqual(gui.grp.width, 0)
		self.assertEqual(gui.grp.height, 0)
