
import os

from unittest import mock

from .harness import UITestCase

from ..PyTRG.PyTRG import PyTRG
from ..FileFormats import TBL
from ..FileFormats.AIBIN import AIBIN
from ..FileFormats.TRG import Conditions
from ..Utilities.PyMSError import PyMSError

# These tests drive PyTRG through its public command methods, asserting on
# both widget and model state. The harness neutralizes settings I/O,
# analytics, the update check, and the tracer; the stat_txt/aiscript handlers
# are supplied as empty in-memory instances so no MPQs are needed.


class PyTRGTestCase(UITestCase):
	def make_pytrg(self) -> PyTRG:
		gui = self.make_window(PyTRG)
		gui.tbl = TBL.TBL()
		gui.aibin = AIBIN.AIBIN()
		return gui

	def settle_syntax_coloring(self, gui: PyTRG) -> None:
		# Recoloring runs on a chained 1ms `after` timer, so a single pump can
		# race it; pump until the pending update range is fully colored.
		for _ in range(10):
			self.pump(gui)
			if not gui.text.tag_ranges('Update'):
				break


class Test_PyTRG_autocomplete_options(PyTRGTestCase):
	def test_defined_constants_are_offered(self) -> None:
		gui = self.make_pytrg()
		gui.new()
		gui.text.load('Constant foo:\n\t5\n')
		self.settle_syntax_coloring(gui)
		options = gui.get_autocomplete_options('{f')
		assert options is not None
		self.assertIn('{foo}', options)

	def test_keywords_and_definition_names_are_offered(self) -> None:
		gui = self.make_pytrg()
		gui.new()
		self.settle_syntax_coloring(gui)
		options = gui.get_autocomplete_options('T')
		assert options is not None
		self.assertIn('Trigger', options)
		self.assertIn(Conditions.definitions_registry[0].name, options)

	def test_non_identifier_prefix_offers_nothing(self) -> None:
		gui = self.make_pytrg()
		gui.new()
		self.assertIsNone(gui.get_autocomplete_options('5'))
		self.assertIsNone(gui.get_autocomplete_options(''))


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


class Test_PyTRG_export(PyTRGTestCase):
	def test_unwritable_path_shows_error_instead_of_raising(self) -> None:
		gui = self.make_pytrg()
		gui.new()
		unwritable = os.path.join(os.path.dirname(__file__), 'does-not-exist', 'export.txt')
		with mock.patch('PyMS.PyTRG.PyTRG.ErrorDialog') as error_dialog, \
				mock.patch('PyMS.Utilities.Config.SelectFile.select_save', return_value=unwritable):
			gui.export()
		error_dialog.assert_called_once()
		error = error_dialog.call_args.args[1]
		self.assertIsInstance(error, PyMSError)
		self.assertNotEqual(gui.status.get(), 'Export Successful!')
