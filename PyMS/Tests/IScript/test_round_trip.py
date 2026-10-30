
from . import utils

from ...FileFormats.IScriptBIN import IScriptBIN

from ..utils import resource_path

import io
import unittest

class Test_Round_Trip(unittest.TestCase):
	def test_round_trip(self) -> None:
		original_iscript = IScriptBIN.IScriptBIN()
		original_iscript.load(resource_path('iscript.bin', __file__))

		original_output_data = io.BytesIO()
		original_iscript.save(original_output_data)
		original_data = original_output_data.getvalue()

		original_output_code, serialize_context = utils.serialize_context()
		original_iscript.decompile(serialize_context)
		original_code = original_output_code.getvalue()

		parse_context = utils.parse_context(original_code)
		scripts = IScriptBIN.IScriptBIN.compile(parse_context)
		new_iscript = IScriptBIN.IScriptBIN()
		new_iscript.add_scripts(scripts)

		new_output_data = io.BytesIO()
		new_iscript.save(new_output_data)
		new_data = new_output_data.getvalue()

		self.assertEqual(original_data, new_data)

		new_output, serialize_context = utils.serialize_context()
		new_iscript.decompile(serialize_context)
		new_code = new_output.getvalue()

		self.assertEqual(original_code, new_code)
