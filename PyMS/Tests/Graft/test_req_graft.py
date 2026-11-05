from .utils import words, decompile_req, compile_req, parse_context
from ...FileFormats.Graft import AbstractReqGraft, ReqScript, UnitsGraft, UpgradesGraft, ResearchGraft, TechGraft, OrdersGraft, FGP
from ...FileFormats.Graft.CodeHandlers import RequirementCodeCommands
from ...Utilities.DataContext import DataContext
from ...FileFormats.TBL import TBL
from ...Utilities.CodeHandlers.CodeCommand import CodeCommand
from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO

import unittest

# Terran Infantry Armor, with its upgrade level sub-lists
INFANTRY_ARMOR = words(
	0x0000, # Header word
	0x0000, # Upgrade 0
	0xFF02, 0x007A, # Current unit is Terran Engineering Bay
	0xFF05, 0xFF07,
	0xFF1F, 0xFFFF, # Level 1 (empty sub-list)
	0xFF20, 0x0074, 0xFFFF, # Level 2: has Terran Science Facility
	0xFF21, 0x0074, 0xFFFF, # Level 3: has Terran Science Facility (ends the script)
	0xFFFF, # End of file
)

INFANTRY_ARMOR_TEXT = """Upgrade 0:	# Terran Infantry Armor
	current_unit_is 'Terran Engineering Bay'
	is_not_lifted_off
	is_not_training_or_morphing
	upgrade_level_1
	end_sublist
	upgrade_level_2
	has 'Terran Science Facility'
	end_sublist
	upgrade_level_3
	has 'Terran Science Facility'
"""

REQ_GRAFT_TYPES: tuple[type[AbstractReqGraft], ...] = (UnitsGraft, UpgradesGraft, ResearchGraft, TechGraft, OrdersGraft)

def _duplicate_names_context() -> DataContext:
	# Units 0 and 1 are both named `Same`, unit 2 is named `Other`
	stat_txt = TBL()
	stat_txt.strings = ['Same\x00*\x00', 'Same\x00*\x00', 'Other\x00*\x00']
	return DataContext(stat_txt_tbl=stat_txt)

def _load(graft_type: type[AbstractReqGraft], data: bytes) -> AbstractReqGraft:
	graft = graft_type()
	graft.load(data)
	return graft

class Test_Defaults(unittest.TestCase):
	def test_load_save_is_byte_identical(self) -> None:
		for graft_type in REQ_GRAFT_TYPES:
			with self.subTest(graft_type=graft_type.__name__):
				with IO.InputBytes(graft_type.default_path()) as f:
					data = f.read()
				graft = graft_type()
				graft.new()
				self.assertEqual(IO.output_to_bytes(graft.save), data)

	def test_decompile_compile_is_byte_identical(self) -> None:
		for graft_type in REQ_GRAFT_TYPES:
			with self.subTest(graft_type=graft_type.__name__):
				graft = graft_type()
				graft.new()
				text = decompile_req(graft)
				recompiled = graft_type()
				recompiled.replace_scripts(compile_req(text, graft_type))
				self.assertEqual(IO.output_to_bytes(recompiled.save), IO.output_to_bytes(graft.save))
				self.assertEqual(decompile_req(recompiled), text)

	def test_vanilla_marine_and_ghost(self) -> None:
		graft = UnitsGraft()
		graft.new()
		text = decompile_req(graft)
		self.assertIn("Unit 0:\t# Terran Marine\n\tcurrent_unit_is 'Terran Barracks'\n\tis_not_constructing_addon\n\tis_not_lifted_off\n", text)
		self.assertIn("Unit 1:\t# Terran Ghost\n\tcurrent_unit_is 'Terran Barracks'\n\tis_not_constructing_addon\n\tis_not_lifted_off\n\thas 'Terran Covert Ops'\n\thas 'Terran Academy'\n", text)

class Test_Load(unittest.TestCase):
	def test_upgrade_sub_lists(self) -> None:
		graft = _load(UpgradesGraft, INFANTRY_ARMOR)
		self.assertEqual(graft.list_ids(), [0])
		self.assertEqual(decompile_req(graft), INFANTRY_ARMOR_TEXT)
		self.assertEqual(IO.output_to_bytes(graft.save), INFANTRY_ARMOR)

	def test_unavailable_opcodes_fail(self) -> None:
		# 0xFF1F isn't a units.dat opcode, and 0xFF27 isn't an opcode at all
		for graft_type, data, word in ((UnitsGraft, words(0, 5, 0xFF1F, 0xFFFF, 0xFFFF), 'FF1F'), (OrdersGraft, words(0, 7, 0xFF27, 0xFFFF, 0xFFFF), 'FF27')):
			with self.subTest(graft_type=graft_type.__name__):
				with self.assertRaises(PyMSError) as cm:
					graft_type().load(data)
				self.assertIn(f'has the word 0x{word}, which is not an opcode for', str(cm.exception))

	def test_does_not_have_exit_is_an_order_opcode(self) -> None:
		# The vanilla Nydus Canal exit order requirements
		data = words(0, 46, 0xFF02, 0x0086, 0xFF0D, 0xFFFF, 0xFFFF)
		graft = _load(OrdersGraft, data)
		script = graft.get_script(46)
		assert script is not None
		self.assertEqual([command.definition for command in script.commands], [RequirementCodeCommands.CurrentUnitIs, RequirementCodeCommands.DoesNotHaveExit])
		self.assertIn("\tcurrent_unit_is 'Zerg Nydus Canal'\n\tdoes_not_have_exit\n", decompile_req(graft))
		self.assertEqual(IO.output_to_bytes(graft.save), data)

	def test_bare_values_are_has_unit(self) -> None:
		graft = _load(UnitsGraft, words(0, 1, 0x0070, 0xFFFF, 0xFFFF))
		script = graft.get_script(1)
		assert script is not None
		self.assertEqual(script.commands[0].definition, RequirementCodeCommands.Has)
		self.assertEqual(script.commands[0].params, [0x70])

	def test_header_word_is_preserved(self) -> None:
		data = words(0x1234, 0, 0xFF05, 0xFFFF, 0xFFFF)
		graft = _load(UnitsGraft, data)
		self.assertEqual(graft.header_word, 0x1234)
		self.assertEqual(IO.output_to_bytes(graft.save), data)

	def test_file_order_is_preserved(self) -> None:
		data = words(0, 9, 0xFF05, 0xFFFF, 2, 0xFF05, 0xFFFF, 0xFFFF)
		graft = _load(UnitsGraft, data)
		self.assertEqual(graft.list_ids(), [9, 2])
		self.assertEqual(IO.output_to_bytes(graft.save), data)

	def test_duplicate_ids_keep_the_last(self) -> None:
		graft = UnitsGraft()
		warnings = graft.load(words(0, 1, 0xFF05, 0xFFFF, 1, 0xFF11, 0xFFFF, 0xFFFF))
		self.assertEqual(len(warnings), 1)
		self.assertIn('defined multiple times', warnings[0].warning)
		script = graft.get_script(1)
		assert script is not None
		self.assertEqual(script.commands[0].definition.byte_code_id, 0xFF11)

	def test_trailing_data_warns(self) -> None:
		graft = UnitsGraft()
		warnings = graft.load(words(0, 0xFFFF, 0x1234))
		self.assertEqual(len(warnings), 1)
		self.assertIn('2 bytes of unused data', warnings[0].warning)

	def test_missing_end_of_list(self) -> None:
		for data in (b'', words(0), words(0, 1, 0xFF05), words(0, 1, 0xFF02), words(0, 1, 0xFF1F, 0xFFFF, 0xFFFF)):
			with self.subTest(data=data):
				graft = UpgradesGraft()
				with self.assertRaises(PyMSError) as cm:
					graft.load(data)
				self.assertIn('ends before its end of list marker', str(cm.exception))

	def test_failed_load_keeps_existing_scripts(self) -> None:
		graft = _load(UpgradesGraft, INFANTRY_ARMOR)
		with self.assertRaises(PyMSError):
			graft.load(words(0, 1))
		self.assertEqual(graft.list_ids(), [0])

class Test_Save(unittest.TestCase):
	def test_unended_sub_list_fails(self) -> None:
		graft = UpgradesGraft()
		graft.set_script(ReqScript(0, [CodeCommand(RequirementCodeCommands.UpgradeLevel1, [])]))
		with self.assertRaises(PyMSError) as cm:
			IO.output_to_bytes(graft.save)
		self.assertIn('sub-list is not ended', str(cm.exception))

	def test_unavailable_command_fails(self) -> None:
		graft = UnitsGraft()
		graft.set_script(ReqScript(0, [CodeCommand(RequirementCodeCommands.UpgradeLevel1, []), CodeCommand(RequirementCodeCommands.EndSublist, [])]))
		with self.assertRaises(PyMSError) as cm:
			IO.output_to_bytes(graft.save)
		self.assertIn('`upgrade_level_1` is not available for unit requirements in script 0', str(cm.exception))

	def test_empty_script(self) -> None:
		graft = OrdersGraft()
		graft.set_script(ReqScript(3))
		self.assertEqual(IO.output_to_bytes(graft.save), words(0, 3, 0xFFFF, 0xFFFF))

class Test_Scripts(unittest.TestCase):
	def test_set_script_inserts_new_ids_in_order(self) -> None:
		graft = _load(UnitsGraft, words(0, 9, 0xFFFF, 2, 0xFFFF, 20, 0xFFFF, 0xFFFF))
		graft.set_script(ReqScript(15))
		graft.set_script(ReqScript(2, [CodeCommand(RequirementCodeCommands.Has, [7])]))
		self.assertEqual(graft.list_ids(), [9, 2, 15, 20])

	def test_set_script_without_replace(self) -> None:
		graft = _load(UnitsGraft, words(0, 9, 0xFFFF, 0xFFFF))
		with self.assertRaises(PyMSError) as cm:
			graft.set_script(ReqScript(9), allow_replace=False)
		self.assertIn('Script 9 already exists', str(cm.exception))

	def test_remove_script(self) -> None:
		graft = _load(UnitsGraft, words(0, 9, 0xFFFF, 2, 0xFFFF, 0xFFFF))
		removed = graft.remove_script(9)
		self.assertIsNotNone(removed)
		self.assertEqual(graft.list_ids(), [2])

class Test_Compile(unittest.TestCase):
	def test_numbers_and_names(self) -> None:
		scripts = compile_req('Unit 0:\n\tcurrent_unit_is 111\n\thas "Terran Academy"\n\thas 0x75\n', UnitsGraft)
		graft = UnitsGraft()
		graft.replace_scripts(scripts)
		self.assertEqual(IO.output_to_bytes(graft.save), words(0, 0, 0xFF02, 111, 112, 0x75, 0xFFFF, 0xFFFF))

	def test_parenthesized_commands_and_comments(self) -> None:
		scripts = compile_req('# A comment\nTech 5: # Header comment\n\tcurrent_unit_is("Terran Academy") # Trailing comment\n\n\tis_not_burrowed\n', TechGraft)
		graft = TechGraft()
		graft.replace_scripts(scripts)
		self.assertEqual(IO.output_to_bytes(graft.save), words(0, 5, 0xFF02, 112, 0xFF11, 0xFFFF, 0xFFFF))

	def test_empty_scripts(self) -> None:
		scripts = compile_req('Order 4:\nOrder 7:\n', OrdersGraft)
		self.assertEqual([(script.entry_id, script.commands) for script in scripts], [(4, []), (7, [])])

	def assertCompileError(self, code: str, graft_type: type[AbstractReqGraft], message: str, line: int | None = None, data_context: DataContext | None = None) -> None:
		with self.assertRaises(PyMSError) as cm:
			compile_req(code, graft_type, data_context)
		self.assertIn(message, str(cm.exception))
		if line is not None:
			self.assertEqual(cm.exception.line, line)

	def test_unknown_command(self) -> None:
		self.assertCompileError('Unit 0:\n\tis_awesome\n', UnitsGraft, 'Unknown command `is_awesome`', 2)

	def test_command_outside_script(self) -> None:
		self.assertCompileError('is_not_lifted_off\n', UnitsGraft, 'is not inside a `Unit` script', 1)

	def test_wrong_header_keyword(self) -> None:
		self.assertCompileError('Unit 0:\n', UpgradesGraft, 'Unknown command `Unit`', 1)

	def test_duplicate_header(self) -> None:
		self.assertCompileError('Unit 1:\nUnit 1:\n', UnitsGraft, 'Unit 1 is already defined on line 1', 2)

	def test_header_id_out_of_range(self) -> None:
		self.assertCompileError('Unit 65535:\n', UnitsGraft, 'Unit ID `65535` is out of range')

	def test_unavailable_opcode(self) -> None:
		self.assertCompileError('Unit 0:\n\tupgrade_level_1\n', UnitsGraft, '`upgrade_level_1` is not available for unit requirements', 2)
		self.assertCompileError('Unit 0:\n\tend_sublist\n', UnitsGraft, '`end_sublist` is not available for unit requirements', 2)
		self.assertCompileError('Order 0:\n\tis_researched 1\n', OrdersGraft, '`is_researched` is not available for order requirements', 2)
		self.assertCompileError('Unit 0:\n\tdoes_not_have_exit\n', UnitsGraft, '`does_not_have_exit` is not available for unit requirements', 2)
		self.assertCompileError('Unit 0:\n\traw 0xFF05\n', UnitsGraft, 'Unknown command `raw`', 2)

	def test_compile_requires_the_files_language(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			UnitsGraft.compile(parse_context('Unit 0:\n', language=UpgradesGraft.LANGUAGE()))
		self.assertIn('UnitsGraft scripts must be compiled with a parse context using `UnitRequirementsLanguage`', str(cm.exception))

	def test_files_share_the_other_requirements_language(self) -> None:
		# Research and tech use requirements have the same opcodes, so one language compiles both
		scripts = ResearchGraft.compile(parse_context('Research 1:\n\tmust_be_researched\n', language=TechGraft.LANGUAGE()))
		self.assertEqual(scripts[0].commands[0].definition.name, 'must_be_researched')

	def test_end_sublist_outside_sublist(self) -> None:
		self.assertCompileError('Upgrade 0:\n\tend_sublist\n', UpgradesGraft, '`end_sublist` used outside of an `upgrade_level_1` or `upgrade_level_2` sub-list')

	def test_unended_sublist(self) -> None:
		self.assertCompileError('Upgrade 0:\n\tupgrade_level_2\n', UpgradesGraft, 'sub-list is not ended with `end_sublist`')

	def test_has_unit_too_large(self) -> None:
		self.assertCompileError('Unit 0:\n\thas 0xFF00\n', UnitsGraft, 'Value is too large for `unit`')

	def test_unknown_name(self) -> None:
		self.assertCompileError("Unit 0:\n\thas 'Not A Unit'\n", UnitsGraft, '`Not A Unit` is not a known unit name')

	def test_name_of_multiple_ids(self) -> None:
		self.assertCompileError("Unit 0:\n\thas 'Same'\n", UnitsGraft, '`Same` is the name of multiple unit IDs (0, 1)', data_context=_duplicate_names_context())

	def test_unique_name_beside_duplicate_names(self) -> None:
		scripts = compile_req("Unit 0:\n\thas 'Other'\n", UnitsGraft, _duplicate_names_context())
		self.assertEqual(scripts[0].commands[0].params, [2])

class Test_Decompile(unittest.TestCase):
	def test_duplicate_names_are_written_as_ids(self) -> None:
		graft = _load(UnitsGraft, words(0, 2, 0, 1, 2, 0xFFFF, 0xFFFF))
		text = decompile_req(graft, _duplicate_names_context())
		self.assertEqual(text, "Unit 2:\t# Terran Vulture (Other)\n\thas 0\t# Terran Marine (Same)\n\thas 1\t# Terran Ghost (Same)\n\thas 'Other'\n")
		graft.replace_scripts(compile_req(text, UnitsGraft, _duplicate_names_context()))
		self.assertEqual(IO.output_to_bytes(graft.save), words(0, 2, 0, 1, 2, 0xFFFF, 0xFFFF))

class Test_ImportFGP(unittest.TestCase):
	def test_replaces_adds_and_removes_scripts(self) -> None:
		graft = _load(UnitsGraft, words(0, 0, 0xFF05, 0xFFFF, 1, 0xFF05, 0xFFFF, 0xFFFF))
		fgp = FGP()
		fgp.requirements[UnitsGraft] = {
			0: [0xFF11, 0xFFFF],
			1: None,
			5: [0x0070], # No terminator
		}
		self.assertEqual(graft.import_fgp(fgp), [])
		self.assertEqual(IO.output_to_bytes(graft.save), words(0, 0, 0xFF11, 0xFFFF, 5, 0x0070, 0xFFFF, 0xFFFF))

	def test_invalid_scripts_fail_without_changes(self) -> None:
		for words_list, message in (([0xFF1F, 0xFFFF], 'ends before its end of list marker'), ([0xFF04], 'has the word 0xFF04, which is not an opcode for upgrade requirements')):
			with self.subTest(message=message):
				graft = _load(UpgradesGraft, INFANTRY_ARMOR)
				fgp = FGP()
				fgp.requirements[UpgradesGraft] = {0: None, 2: words_list}
				with self.assertRaises(PyMSError) as cm:
					graft.import_fgp(fgp)
				self.assertIn(message, str(cm.exception))
				self.assertEqual(graft.list_ids(), [0])
