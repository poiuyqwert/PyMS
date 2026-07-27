
from .utils import PyPCXTestCase, ASK_SAVE

from unittest import mock


class Test_PyPCX_preview(PyPCXTestCase):
	def test_preview_reuses_single_canvas_image(self) -> None:
		gui = self.open_pypcx()
		self.import_bmp(gui)
		items = gui.canvas.find_all()
		self.assertEqual(len(items), 1)
		self.import_bmp(gui)
		gui.preview()
		self.pump(gui)
		self.assertEqual(gui.canvas.find_all(), items)
		assert gui.canvas_image is not None
		self.assertEqual(gui.canvas_image.cget('image'), str(gui.image))

	def test_close_hides_canvas_and_preview_restores_it(self) -> None:
		gui = self.open_pypcx()
		self.import_bmp(gui)
		self.assertEqual(gui.canvas.winfo_manager(), 'pack')
		with mock.patch(ASK_SAVE, return_value=False):
			gui.close()
		self.pump(gui)
		self.assertEqual(gui.canvas.winfo_manager(), '')
		self.assertEqual(gui.canvas.find_all(), [])
		self.import_bmp(gui)
		self.assertEqual(gui.canvas.winfo_manager(), 'pack')
