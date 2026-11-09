
from ...Utilities import Config
from ...Utilities import UIKit as UI
from ...PyAI.CodeEditDialog import CodeEditDialog as PyAICodeEditDialog
from ...PyAI.Config import PyAIConfig
from ...PyICE.CodeEditDialog import CodeEditDialog as PyICECodeEditDialog
from ...PyICE.Config import PyICEConfig
from ...PyTRG.PyTRG import PyTRG
from ...PyTRG.Config import PyTRGConfig
from ...PyLO.PyLO import PyLO
from ...PyLO.Config import PyLOConfig
from ...PyGRAFT.RequirementsEditor.ReqSyntaxHighlighting import build_syntax_highlighting as build_graft_syntax_highlighting
from ...PyGRAFT.Config import PyGRAFTConfig
from ...FileFormats.Graft.UnitsGraft import UnitsGraft

import unittest
from unittest import mock

def _program_highlights() -> dict[str, tuple[Config.Group, list[UI.HighlightComponent]]]:
	with mock.patch.object(Config.Config, '_read', return_value={}):
		pyai = PyAIConfig().code.highlights
		pyice = PyICEConfig().code.highlights
		pytrg = PyTRGConfig().highlights
		pylo = PyLOConfig().highlights
		pygraft = PyGRAFTConfig().code.highlights
	return {
		'PyAI': (pyai, list(PyAICodeEditDialog.build_syntax_highlighting(pyai).all_highlight_components())),
		'PyICE': (pyice, list(PyICECodeEditDialog.build_syntax_highlighting(pyice).all_highlight_components())),
		'PyTRG': (pytrg, list(PyTRG.build_syntax_highlighting(pytrg).all_highlight_components())),
		'PyLO': (pylo, list(PyLO.build_syntax_highlighting(pylo).all_highlight_components())),
		'PyGRAFT': (pygraft, list(build_graft_syntax_highlighting(pygraft, UnitsGraft.LANGUAGE).all_highlight_components())),
	}

class Test_Shared_Highlight_Keys(unittest.TestCase):
	def setUp(self) -> None:
		self.programs = _program_highlights()

	def test_component_key_is_its_config_field(self) -> None:
		for program, (highlights, components) in self.programs.items():
			fields = dict(Config.Group._fields(highlights))
			for component in components:
				with self.subTest(program=program, component=component.name):
					self.assertIn(component.key, fields)
					self.assertIs(fields[component.key], component.highlight_style)

	def test_every_config_field_is_editable(self) -> None:
		for program, (highlights, components) in self.programs.items():
			with self.subTest(program=program):
				keys = set(component.key for component in components)
				fields = set(key for key, _ in Config.Group._fields(highlights))
				self.assertEqual(fields, keys)

	def test_shared_key_has_same_name_and_default_in_every_program(self) -> None:
		seen: dict[str, tuple[str, str, dict]] = {}
		for program, (_, components) in self.programs.items():
			for component in components:
				component.highlight_style.reset()
				style = component.highlight_style.encode()
				assert isinstance(style, dict)
				if component.key not in seen:
					seen[component.key] = (program, component.name, style)
					continue
				first_program, name, first_style = seen[component.key]
				with self.subTest(key=component.key, programs=(first_program, program)):
					self.assertEqual(component.name, name)
					self.assertEqual(style, first_style)
