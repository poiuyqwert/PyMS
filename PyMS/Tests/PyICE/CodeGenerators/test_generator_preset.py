
from ....PyICE.CodeGenerators.GeneratorPreset import GeneratorPreset, DEFAULT_PRESETS
from ....PyICE.CodeGenerators.CodeGeneratorVariable import CodeGeneratorVariable
from ....PyICE.CodeGenerators.CodeGeneratorRange import CodeGeneratorTypeRange
from ....Utilities.PyMSError import PyMSError

import unittest


def _preset() -> GeneratorPreset:
	return GeneratorPreset(
		name='Demo',
		code='playfram $frame',
		variables=[CodeGeneratorVariable('frame', CodeGeneratorTypeRange(0, 10, 1))],
	)


class Test_GeneratorPreset(unittest.TestCase):
	def test_to_json(self) -> None:
		self.assertEqual(_preset().to_json(), {
			'name': 'Demo',
			'code': 'playfram $frame',
			'variables': [{
				'name': 'frame',
				'generator': {'type': 'range', 'start': 0, 'stop': 10, 'step': 1},
			}],
		})

	def test_round_trip(self) -> None:
		preset = _preset()
		restored = GeneratorPreset.from_json(preset.to_json())
		self.assertEqual(restored, preset)

	def test_from_json_with_empty_variables(self) -> None:
		preset = GeneratorPreset.from_json({'name': 'Empty', 'code': 'wait 1', 'variables': []})
		self.assertEqual(preset.variables, [])

	def test_from_json_missing_field_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			GeneratorPreset.from_json({'name': 'NoCode', 'variables': []})
		self.assertIn('missing `code`', str(cm.exception))

	def test_default_presets_json_is_stable(self) -> None:
		# Every bundled preset must serialize, deserialize, and re-serialize unchanged.
		# (Compared via JSON because list repeaters are stateless singletons without value equality.)
		self.assertTrue(DEFAULT_PRESETS)
		for preset in DEFAULT_PRESETS:
			json = preset.to_json()
			self.assertEqual(GeneratorPreset.from_json(json).to_json(), json)
