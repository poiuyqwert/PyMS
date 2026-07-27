
from .utils import PyLOTestCase

from ...FileFormats.GRP import CacheGRP
from ...Utilities import UIKit as UI


class Test_PyLO_preview(PyLOTestCase):
	def test_previewing_first_frame_displays_frame_number_one(self) -> None:
		gui = self.make_pylo()
		gui.new()
		self.settle_syntax_coloring(gui)
		gui.text.mark_set(UI.INSERT, '2.0 lineend')
		gui.previewupdate()
		self.assertEqual(gui.previewing_basegrp_frame, 0)
		gui.framesupdate()
		self.assertEqual(gui.baseframes.get(), 'Base Frame: 1 / -')

	def test_preview_frame_index_counts_headers_before_cursor(self) -> None:
		gui = self.make_pylo()
		gui.new()
		gui.text.load('Frame:\n\t(0, 0)\nFrame:\n\t(1, 1)\nFrame:\n\t(2, 2)')
		self.settle_syntax_coloring(gui)
		gui.text.mark_set(UI.INSERT, '6.0 lineend')
		gui.previewupdate()
		self.assertEqual(gui.previewing_basegrp_frame, 2)
		self.assertEqual(gui.previewing_offset, (2, 2))

	def test_scrolling_overlay_frame_redraws_preview(self) -> None:
		gui = self.make_pylo()
		gui.new()
		self.settle_syntax_coloring(gui)
		grp = CacheGRP()
		grp.frames = 3
		gui.overlaygrp = grp
		gui.previewupdate()
		self.assertEqual(gui.previewing_overlaygrp_frame, 0)
		gui.scrolling('scroll', '1', 'units')
		self.assertEqual(gui.overlayframe, 1)
		self.assertEqual(gui.previewing_overlaygrp_frame, 1)
		self.assertEqual(gui.overlayframes.get(), 'Overlay Frame: 2 / 3')

	def test_grp_frame_render_failure_falls_back_to_no_image(self) -> None:
		gui = self.make_pylo()
		grp = CacheGRP()
		grp.frames = 3
		gui.basegrp = grp
		self.assertIsNone(gui.base_grp_frame(2))
