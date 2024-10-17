
from . import utils

from ...FileFormats.AIBIN import AIBIN

from ..utils import resource_path

import io
import unittest

class Test_Round_Trip(unittest.TestCase):
	def test_round_trip(self) -> None:
		original_aiscript = AIBIN.AIBIN()
		original_aiscript.load(resource_path('aiscript.bin', __file__), resource_path('bwscript.bin', __file__))

		original_output_data_ai = io.BytesIO()
		original_output_data_bw = io.BytesIO()
		original_aiscript.save(original_output_data_ai, original_output_data_bw)
		original_data_ai = original_output_data_ai.getvalue()
		original_data_bw = original_output_data_bw.getvalue()

		original_output_code, serialize_context = utils.serialize_context()
		original_aiscript.decompile(serialize_context)
		original_code = original_output_code.getvalue()

		parse_context = utils.parse_context(original_code)
		scripts = AIBIN.AIBIN.compile(parse_context)
		new_aiscript = AIBIN.AIBIN()
		new_aiscript.add_scripts(scripts)

		new_output_data_ai = io.BytesIO()
		new_output_data_bw = io.BytesIO()
		new_aiscript.save(new_output_data_ai, new_output_data_bw)
		new_data_ai = new_output_data_ai.getvalue()
		new_data_bw = new_output_data_bw.getvalue()

		self.assertEqual(original_data_ai, new_data_ai)
		self.assertEqual(original_data_bw, new_data_bw)

		new_output, serialize_context = utils.serialize_context()
		new_aiscript.decompile(serialize_context)
		new_code = new_output.getvalue()

		self.assertEqual(original_code, new_code)
