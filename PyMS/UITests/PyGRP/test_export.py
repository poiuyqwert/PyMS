
from .utils import PyGRPTestCase

from ...PyGRP.utils import BMPStyle

import os
from unittest import mock

SELECT_SAVE = 'PyMS.Utilities.Config.SelectFile.select_save'
GRP_TO_BMPS = 'PyMS.PyGRP.PyGRP.grp_to_bmps'


class Test_PyGRP_exports(PyGRPTestCase):
	# `select_save` checks its chosen path against the internal-file overwrite
	# guard, so single-sheet mode must write exactly that path. Only per-frame
	# mode derives its own (numbered) file names.

	def test_single_sheet_export_writes_exactly_the_dialog_chosen_path(self) -> None:
		gui = self.with_frames(1)
		bmp = mock.Mock()
		file_path = os.path.join('fake_dir', 'my file.bmp')
		with mock.patch(SELECT_SAVE, return_value=file_path), \
				mock.patch(GRP_TO_BMPS, return_value=[bmp]), \
				mock.patch.object(gui, 'get_bmp_style', return_value=BMPStyle.single_bmp_framesets):
			gui.exports()
		bmp.save.assert_called_once_with(file_path)

	def test_per_frame_export_derives_numbered_frame_names(self) -> None:
		gui = self.with_frames(2)
		bmps = [mock.Mock(), mock.Mock()]
		with mock.patch(SELECT_SAVE, return_value=os.path.join('fake_dir', 'my file.bmp')), \
				mock.patch(GRP_TO_BMPS, return_value=bmps), \
				mock.patch.object(gui, 'get_bmp_style', return_value=BMPStyle.bmp_per_frame):
			gui.exports()
		bmps[0].save.assert_called_once_with(os.path.join('fake_dir', 'myfile 000.bmp'))
		bmps[1].save.assert_called_once_with(os.path.join('fake_dir', 'myfile 001.bmp'))
