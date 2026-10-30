
from .utils import PyTRGTestCase

from ...FileFormats.TRG import Conditions


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
