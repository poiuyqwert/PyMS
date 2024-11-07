
from . import utils

from ...FileFormats.AIBIN import AIBIN

from ..utils import resource_path
from ...Utilities.PyMSError import PyMSError

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
    entry_point SGTB_EntryPoint
}"""

	@staticmethod
	def BWSS(entry_point: str = 'BWSS_0000') -> str:
		return f"""script BWSS {{
    name_string 0
    bin_file bwscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point {entry_point}
}}"""

class Block:
	@staticmethod
	def shared_0000(owners: list[str] = ['BASE', 'SEPB', 'SGTB']) -> str:
		comment = ''
		if owners:
			comment = '\t# Shared by: ' + ', '.join(owners)
		return f""":shared_0000{comment}
wait 1

goto shared_0000"""

	SGTB_EntryPoint = """:SGTB_EntryPoint
goto shared_0000"""

	BWSS_0000 = """:BWSS_0000
stop"""

class Scripts:
	full_ai_script = f"""
{Header.BASE}

{Block.shared_0000()}


{Header.SEPB}

{Header.SGTB}

{Block.SGTB_EntryPoint}

"""

	fill_bw_script = f"""
{Header.BWSS()}

{Block.BWSS_0000}

"""

class Test_Shared_Blocks(unittest.TestCase):
	def test_compile_all(self) -> None:
		parse_context = utils.parse_context(Scripts.full_ai_script)
		ai = AIBIN.AIBIN()
		scripts = AIBIN.AIBIN.compile(parse_context)
		ai.add_scripts(scripts)
		
		self.assertSequenceEqual([script.id for script in ai.list_scripts()], ['BASE', 'SEPB', 'SGTB'])
		base = ai.get_script('BASE')
		assert base is not None
		sepb = ai.get_script('SEPB')
		assert sepb is not None
		self.assertEqual(base.entry_point, sepb.entry_point)

	def test_load(self) -> None:
		ai = AIBIN.AIBIN()
		ai.load(resource_path('shared_blocks_aiscript.bin', __file__), None)

		self.assertSequenceEqual([script.id for script in ai.list_scripts()], ['BASE', 'SEPB', 'SGTB'])
		base = ai.get_script('BASE')
		assert base is not None
		sepb = ai.get_script('SEPB')
		assert sepb is not None
		self.assertEqual(base.entry_point, sepb.entry_point)

	def test_compile_decompile(self) -> None:
		parse_context = utils.parse_context(Scripts.full_ai_script)
		ai = AIBIN.AIBIN()
		scripts = AIBIN.AIBIN.compile(parse_context)
		ai.add_scripts(scripts)

		output, serialize_context = utils.serialize_context()
		ai.decompile(serialize_context)
		code = output.getvalue()

		self.assertEqual(code, Scripts.full_ai_script)

	def test_decompile_all(self) -> None:
		ai = AIBIN.AIBIN()
		ai.load(resource_path('shared_blocks_aiscript.bin', __file__), None)
		output, serialize_context = utils.serialize_context()
		ai.decompile(serialize_context)
		code = output.getvalue()

		self.assertEqual(code, Scripts.full_ai_script)

	def test_remove_BASE_then_decompile_all(self) -> None:
		ai = AIBIN.AIBIN()
		ai.load(resource_path('shared_blocks_aiscript.bin', __file__), None)
		ai.remove_script('BASE')
		output, serialize_context = utils.serialize_context()
		ai.decompile(serialize_context)
		code = output.getvalue()

		expected_code = f"""
{Header.SEPB}

{Block.shared_0000(['SEPB', 'SGTB'])}


{Header.SGTB}

{Block.SGTB_EntryPoint}

"""
		self.assertEqual(code, expected_code)

	def test_decompile_external(self) -> None:
		ai = AIBIN.AIBIN()
		ai.load(resource_path('shared_blocks_aiscript.bin', __file__), None)
		output, serialize_context = utils.serialize_context()
		ai.decompile(serialize_context, ['SGTB'])
		code = output.getvalue()

		expected_code = f"""
{Header.SGTB}

{Block.SGTB_EntryPoint}


{Block.shared_0000()}


{Header.BASE}

{Header.SEPB}
"""
		print(f'`{code}`')
		print(f'*{expected_code}*')
		self.assertEqual(code, expected_code)

	def test_cross_references_invalid(self) -> None:
		code = f"""
{Header.BASE}
{Block.shared_0000(['BASE', 'BWSS'])}

{Header.BWSS('shared_0000')}
"""
		print(code)
		parse_context = utils.parse_context(code)
		with self.assertRaises(PyMSError) as error_context:
			AIBIN.AIBIN.compile(parse_context)
		print(str(error_context.exception))
		self.assertTrue('is cross referenced by scripts' in str(error_context.exception))

	def test_indirect_cross_references_invalid(self) -> None:
		code = """
:shared_0000
stop

:BASE_0000
goto BASE_0001

:BASE_0002
goto shared_0000

:BASE_0001
goto BASE_0002

script BASE {
    name_string 0
    bin_file aiscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point BASE_0000
}

script BWSS {
    name_string 0
    bin_file bwscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point BWSS_0000
}
:BWSS_0000
goto BWSS_0001

:BWSS_0002
goto shared_0000

:BWSS_0001
goto BWSS_0002
"""
		print(code)
		parse_context = utils.parse_context(code)
		ai = AIBIN.AIBIN()
		with self.assertRaises(PyMSError) as error_context:
			AIBIN.AIBIN.compile(parse_context)
		print(str(error_context.exception))
		self.assertTrue('is cross referenced by scripts' in str(error_context.exception))
