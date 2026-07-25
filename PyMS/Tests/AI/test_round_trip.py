
from . import utils

from ...FileFormats.AIBIN import AIBIN
from ...FileFormats.AIBIN.CodeHandlers import CodeCommands
from ...FileFormats.AIBIN.CodeHandlers.AISourceCodeHandlers import AIDefsSourceCodeHandler
from ...Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from ...Utilities import IO

from ..utils import resource_path

import io
import unittest

def _load_bins(ai_name: str, bw_name: str) -> AIBIN.AIBIN:
	ai_bin = AIBIN.AIBIN()
	ai_bin.load(resource_path(ai_name, __file__), resource_path(bw_name, __file__))
	return ai_bin

def _save_bins(ai_bin: AIBIN.AIBIN) -> tuple[bytes, bytes]:
	ai_output = io.BytesIO()
	bw_output = io.BytesIO()
	ai_bin.save(ai_output, bw_output)
	return (ai_output.getvalue(), bw_output.getvalue())

def _reload_bins(ai_data: bytes, bw_data: bytes) -> AIBIN.AIBIN:
	ai_bin = AIBIN.AIBIN()
	ai_bin.load(io.BytesIO(ai_data), io.BytesIO(bw_data))
	return ai_bin

def _decompile_all(ai_bin: AIBIN.AIBIN) -> str:
	output, serialize_context = utils.serialize_context()
	ai_bin.decompile(serialize_context)
	return output.getvalue()

def _read_fixture(name: str) -> bytes:
	with open(resource_path(name, __file__), 'rb') as f:
		return f.read()

class Test_Round_Trip(unittest.TestCase):
	def test_round_trip_no_unitdef(self) -> None:
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

	def test_round_trip_with_unitdef(self) -> None:
		original_aiscript = AIBIN.AIBIN()
		original_aiscript.load(resource_path('aiscript.bin', __file__), resource_path('bwscript.bin', __file__))

		original_output_data_ai = io.BytesIO()
		original_output_data_bw = io.BytesIO()
		original_aiscript.save(original_output_data_ai, original_output_data_bw)
		original_data_ai = original_output_data_ai.getvalue()
		original_data_bw = original_output_data_bw.getvalue()

		definitions_handler = DefinitionsHandler()
		handler = AIDefsSourceCodeHandler()
		with IO.InputText(resource_path('unitdef.txt', __file__)) as f:
			unitdef_code = f.read()
		parse_context = utils.parse_context(unitdef_code, definitions_handler=definitions_handler)
		handler.parse(parse_context)
		parse_context.finalize()

		original_output_code, serialize_context = utils.serialize_context(definitions_handler)
		original_aiscript.decompile(serialize_context)
		original_code = original_output_code.getvalue()

		parse_context = utils.parse_context(original_code, definitions_handler=definitions_handler)
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

		new_output, serialize_context = utils.serialize_context(definitions_handler)
		new_aiscript.decompile(serialize_context)
		new_code = new_output.getvalue()

		self.assertEqual(original_code, new_code)

class Test_Resave(unittest.TestCase):
	def test_resave_reaches_binary_fixpoint(self) -> None:
		ai_bin = _load_bins('aiscript.bin', 'bwscript.bin')
		first_ai, first_bw = _save_bins(ai_bin)

		reloaded = _reload_bins(first_ai, first_bw)
		second_ai, second_bw = _save_bins(reloaded)

		self.assertEqual(first_ai, second_ai)
		self.assertEqual(first_bw, second_bw)

	def test_resave_does_not_grow_files(self) -> None:
		ai_bin = _load_bins('aiscript.bin', 'bwscript.bin')
		ai_data, bw_data = _save_bins(ai_bin)

		self.assertLessEqual(len(ai_data), len(_read_fixture('aiscript.bin')))
		self.assertLessEqual(len(bw_data), len(_read_fixture('bwscript.bin')))

	def test_resave_preserves_decompiled_source(self) -> None:
		ai_bin = _load_bins('aiscript.bin', 'bwscript.bin')
		original_code = _decompile_all(ai_bin)

		reloaded = _reload_bins(*_save_bins(ai_bin))

		self.assertEqual(original_code, _decompile_all(reloaded))

class Test_Expanded_Round_Trip(unittest.TestCase):
	def test_expanded_fixture_reloads_as_expanded(self) -> None:
		ai_bin = _load_bins('expanded_aiscript.bin', 'expanded_bwscript.bin')
		self.assertTrue(ai_bin.expanded)

	def test_expanded_resave_is_byte_identical(self) -> None:
		# The expanded fixtures are the fixpoint of load -> save, so resaving
		# must reproduce them exactly (no duplicated code, no extra long jumps)
		ai_bin = _load_bins('expanded_aiscript.bin', 'expanded_bwscript.bin')
		ai_data, bw_data = _save_bins(ai_bin)

		self.assertEqual(ai_data, _read_fixture('expanded_aiscript.bin'))
		self.assertEqual(bw_data, _read_fixture('expanded_bwscript.bin'))

	def test_expanded_resave_preserves_decompiled_source(self) -> None:
		ai_bin = _load_bins('expanded_aiscript.bin', 'expanded_bwscript.bin')
		original_code = _decompile_all(ai_bin)

		reloaded = _reload_bins(*_save_bins(ai_bin))

		self.assertEqual(original_code, _decompile_all(reloaded))

	SMALL_EXPANDED_SOURCE = """
script AAAA {
    name_string 0
    bin_file aiscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point AAAA_entry
}
:AAAA_entry
wait 4660
random_jump 128 AAAA_entry
goto AAAA_entry

script BBBB {
    name_string 0
    bin_file bwscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point BBBB_entry
}
:BBBB_entry
wait 30583
random_jump 128 BBBB_entry
goto BBBB_entry
"""

	@staticmethod
	def _count_long_jumps(data: bytes) -> int:
		# Expanded files start with a table of `goto` long jump trampolines
		# directly after the u32 headers array offset
		count = 0
		offset = 4
		while data[offset] == CodeCommands.Goto.byte_code_id:
			count += 1
			offset += 5
		return count

	def test_expanded_save_only_emits_own_scripts_per_file(self) -> None:
		parse_context = utils.parse_context(Test_Expanded_Round_Trip.SMALL_EXPANDED_SOURCE)
		scripts = AIBIN.AIBIN.compile(parse_context)
		ai_bin = AIBIN.AIBIN()
		ai_bin.expand()
		ai_bin.add_scripts(scripts)
		ai_data, bw_data = _save_bins(ai_bin)

		# Each file gets a long jump for its own script's short block reference only
		self.assertEqual(self._count_long_jumps(ai_data), 1)
		self.assertEqual(self._count_long_jumps(bw_data), 1)
		# `wait 4660` belongs to the aiscript-only script, `wait 30583` to the
		# bwscript-only script; neither's code may leak into the other file
		aaaa_wait = bytes([CodeCommands.Wait.byte_code_id or 0]) + (4660).to_bytes(2, 'little')
		bbbb_wait = bytes([CodeCommands.Wait.byte_code_id or 0]) + (30583).to_bytes(2, 'little')
		self.assertIn(aaaa_wait, ai_data)
		self.assertNotIn(aaaa_wait, bw_data)
		self.assertIn(bbbb_wait, bw_data)
		self.assertNotIn(bbbb_wait, ai_data)
