
from . import utils

from ...FileFormats.AIBIN import AIBIN

import unittest

class Test_Parse_Owners(unittest.TestCase):
	def test_predef_uses(self) -> None:
		code = """
:TEST_1
stop

:TEST_2
goto TEST_1

script TEST {
    name_string 0
    bin_file aiscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point TEST_2
}
"""

		parse_context = utils.parse_context(code)
		ai = AIBIN.AIBIN()
		scripts = AIBIN.AIBIN.compile(parse_context)
		ai.add_scripts(scripts)

		test_script = ai.list_scripts()[0]

		test_1_meta = parse_context.lookup_block_metadata_by_name('TEST_1')
		assert test_1_meta is not None
		self.assertEqual(test_1_meta.uses, [test_script])

		test_2_meta = parse_context.lookup_block_metadata_by_name('TEST_2')
		assert test_2_meta is not None
		self.assertEqual(test_2_meta.uses, [test_script])

	def test_indirect_uses(self) -> None:
		code = """
:SHARED_0
stop

:BASE_0
goto BASE_1

:BASE_2
goto SHARED_0

:BASE_1
goto BASE_2

script BASE {
    name_string 0
    bin_file aiscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point BASE_0
}

script TEST {
    name_string 0
    bin_file aiscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point TEST_0
}
:TEST_0
goto TEST_1

:TEST_2
goto SHARED_0

:TEST_1
goto TEST_2
"""
		parse_context = utils.parse_context(code)
		ai = AIBIN.AIBIN()
		scripts = AIBIN.AIBIN.compile(parse_context)
		ai.add_scripts(scripts)

		base_script = ai.list_scripts()[0]
		assert base_script.id == 'BASE'

		base_0_meta = parse_context.lookup_block_metadata_by_name('BASE_0')
		assert base_0_meta is not None
		self.assertEqual(base_0_meta.uses, [base_script])

		base_1_meta = parse_context.lookup_block_metadata_by_name('BASE_1')
		assert base_1_meta is not None
		self.assertEqual(base_1_meta.uses, [base_script])

		base_2_meta = parse_context.lookup_block_metadata_by_name('BASE_2')
		assert base_2_meta is not None
		self.assertEqual(base_2_meta.uses, [base_script])

		test_script = ai.list_scripts()[1]
		assert test_script.id == 'TEST'

		test_0_meta = parse_context.lookup_block_metadata_by_name('TEST_0')
		assert test_0_meta is not None
		self.assertEqual(test_0_meta.uses, [test_script])

		test_1_meta = parse_context.lookup_block_metadata_by_name('TEST_1')
		assert test_1_meta is not None
		self.assertEqual(test_1_meta.uses, [test_script])

		test_2_meta = parse_context.lookup_block_metadata_by_name('TEST_2')
		assert test_2_meta is not None
		self.assertEqual(test_2_meta.uses, [test_script])

		shared_0_meta = parse_context.lookup_block_metadata_by_name('SHARED_0')
		assert shared_0_meta is not None
		self.assertEqual(shared_0_meta.uses, [base_script, test_script])
