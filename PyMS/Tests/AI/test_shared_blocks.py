
from . import utils

from ...FileFormats.AIBIN import AIBIN

from ..utils import resource_path
from ...Utilities import IO

import unittest

class Header:
	BASE = """script BASE {
    name_string 0
    bin_file aiscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point shared_0000
}"""
	SEPB = """script SEPB {
    name_string 0
    bin_file aiscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point shared_0000
}"""
	SGTB = """script SGTB {
    name_string 0
    bin_file aiscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point SGTB_0000
}"""
class Block:
	shared_0000 = """:shared_0000
wait 1

goto shared_0000"""

	SGTB_0000 = """:SGTB_0000
goto shared_0000"""

class Scripts:
	full_script = f"""{Header.BASE}
{Block.shared_0000}


{Header.SEPB}


{Header.SGTB}
{Block.SGTB_0000}
"""

class Test_Shared_Blocks(unittest.TestCase):
	def test_compile_all(self) -> None:
		parse_context = utils.parse_context(Scripts.full_script)
		ai = AIBIN.AIBIN()
		ai.compile(parse_context)
		
		self.assertSequenceEqual([script.id for script in ai.list_scripts()], ['BASE', 'SEPB', 'SGTB'])
		base = ai.get_script('BASE')
		assert base is not None
		sepb = ai.get_script('SEPB')
		assert sepb is not None
		self.assertEqual(base.entry_point, sepb.entry_point)

	def test_load(self):
		ai = AIBIN.AIBIN()
		ai.load(resource_path('shared_blocks.bin', __file__), None)

		self.assertSequenceEqual([script.id for script in ai.list_scripts()], ['BASE', 'SEPB', 'SGTB'])
		base = ai.get_script('BASE')
		assert base is not None
		sepb = ai.get_script('SEPB')
		assert sepb is not None
		self.assertEqual(base.entry_point, sepb.entry_point)

	def test_decompile_all(self):
		ai = AIBIN.AIBIN()
		ai.load(resource_path('shared_blocks.bin', __file__), None)
		serialize_context = utils.serialize_context()
		code = IO.output_to_text(lambda f: ai.decompile(f, serialize_context))

		self.assertEqual(code, Scripts.full_script)

	def test_remove_BASE_then_decompile_all(self):
		ai = AIBIN.AIBIN()
		ai.load(resource_path('shared_blocks.bin', __file__), None)
		ai.remove_script('BASE')
		serialize_context = utils.serialize_context()
		code = IO.output_to_text(lambda f: ai.decompile(f, serialize_context))
		print(f'`{code}`')

		self.assertEqual(code, f"""{Header.SEPB}
{Block.shared_0000}

{Header.SGTB}
{Block.SGTB_0000}
""")
