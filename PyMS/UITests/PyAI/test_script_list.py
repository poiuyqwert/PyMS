
from .utils import PyAITestCase

from ...FileFormats.AIBIN.AIScript import AIScript


def _script(script_id: str) -> AIScript:
	return AIScript(script_id, 0, 0, AIScript.blank_entry_point(), False)


class Test_PyAI_script_list(PyAITestCase):
	def test_special_script_id_is_marked(self) -> None:
		gui = self.make_pyai()
		self.assertTrue(gui.entry_text(_script('EnBk')).startswith('EnBk *   '))
		self.assertTrue(gui.entry_text(_script('Rscu')).startswith('Rscu *   '))

	def test_ordinary_script_id_is_not_marked(self) -> None:
		gui = self.make_pyai()
		self.assertTrue(gui.entry_text(_script('MYAI')).startswith('MYAI     '))

	def test_marker_keeps_columns_aligned(self) -> None:
		gui = self.make_pyai()
		special = gui.entry_text(_script('EnBk'))
		ordinary = gui.entry_text(_script('MYAI'))
		self.assertEqual(special.index('000'), ordinary.index('000'))
