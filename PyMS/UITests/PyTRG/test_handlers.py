
from .utils import PyTRGTestCase

from unittest import mock


class Test_PyTRG_trg_handlers(PyTRGTestCase):
	def test_new_trg_carries_loaded_handlers(self) -> None:
		gui = self.make_pytrg()
		gui.new()
		assert gui.trg is not None
		self.assertIs(gui.trg.stat_txt, gui.tbl)
		self.assertIs(gui.trg.aiscript, gui.aibin)

	def test_opened_trg_carries_loaded_handlers(self) -> None:
		gui = self.make_pytrg()
		with mock.patch('PyMS.FileFormats.TRG.TRG.TRG.load', return_value=None):
			gui.open(file='fake.trg')
		assert gui.trg is not None
		self.assertIs(gui.trg.stat_txt, gui.tbl)
		self.assertIs(gui.trg.aiscript, gui.aibin)
