from .utils import words, decompile_req, compile_req, decompile_req_script, compile_req_script, parse_context
from ...FileFormats.Graft import AbstractReqGraft, ReqScript, UnitsGraft, UpgradesGraft, ResearchGraft, TechGraft, OrdersGraft, FGP
from ...FileFormats.Graft.CodeHandlers import RequirementCodeCommands, UnitRequirementsLanguage, UpgradeRequirementsLanguage, ResearchRequirementsLanguage, TechRequirementsLanguage, OrderRequirementsLanguage
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
	0xFF20, 0x0074, 0xFFFF, # Level 2: has_completed Terran Science Facility
	0xFF21, 0x0074, 0xFFFF, # Level 3: has_completed Terran Science Facility (ends the script)
	0xFFFF, # End of file
)

INFANTRY_ARMOR_TEXT = """Upgrade 0:	# Terran Infantry Armor
	current_unit_is 'Terran Engineering Bay'
	is_not_lifted_off
	is_not_training_or_morphing
	level_1_requires
		end_level_requirements
	level_2_requires
		has_completed 'Terran Science Facility'
		end_level_requirements
	level_3_requires
		has_completed 'Terran Science Facility'
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
		self.assertIn("Unit 1:\t# Terran Ghost\n\tcurrent_unit_is 'Terran Barracks'\n\tis_not_constructing_addon\n\tis_not_lifted_off\n\thas_completed 'Terran Covert Ops'\n\thas_completed 'Terran Academy'\n", text)

class Test_Load(unittest.TestCase):
	def test_upgrade_sub_lists(self) -> None:
		graft = _load(UpgradesGraft, INFANTRY_ARMOR)
		self.assertEqual(graft.list_ids(), [0])
		self.assertEqual(decompile_req(graft), INFANTRY_ARMOR_TEXT)
		self.assertEqual(IO.output_to_bytes(graft.save), INFANTRY_ARMOR)

	def test_sub_list_indentation_is_optional(self) -> None:
		flat_text = INFANTRY_ARMOR_TEXT.replace('\t\t', '\t')
		graft = UpgradesGraft()
		graft.replace_scripts(compile_req(flat_text, UpgradesGraft))
		self.assertEqual(IO.output_to_bytes(graft.save), INFANTRY_ARMOR)

	def test_unknown_opcodes_fail(self) -> None:
		# 0xFF27 isn't a requirement opcode for any file
		for graft_type in REQ_GRAFT_TYPES:
			with self.subTest(graft_type=graft_type.__name__):
				with self.assertRaises(PyMSError) as cm:
					graft_type().load(words(0, 7, 0xFF27, 0xFFFF, 0xFFFF))
				self.assertIn(f'has the word 0xFF27, which is not an opcode for {graft_type.LANGUAGE.DESCRIPTION.lower()}', str(cm.exception))

	def test_opcodes_of_the_other_kind_of_requirements_fail(self) -> None:
		# units.dat requirements and the other requirements are checked by different functions, which each only handle their own opcodes
		for graft_type, word in ((UnitsGraft, 0xFF1F), (UnitsGraft, 0xFF0F), (UpgradesGraft, 0xFF04), (ResearchGraft, 0xFF0B), (TechGraft, 0xFF25), (OrdersGraft, 0xFF10)):
			with self.subTest(graft_type=graft_type.__name__, word=f'0x{word:04X}'):
				with self.assertRaises(PyMSError) as cm:
					graft_type().load(words(0, 7, word, 0xFFFF, 0xFFFF, 0xFFFF))
				self.assertIn(f'has the word 0x{word:04X}, which is not an opcode for {graft_type.LANGUAGE.DESCRIPTION.lower()}', str(cm.exception))

	def test_unavailable_opcodes_load_but_fail_to_save(self) -> None:
		# The non-unit requirements are all checked the same way, so they load with each other's opcodes
		for graft_type, data, name in (
			(UpgradesGraft, words(0, 5, 0xFF0F, 0xFFFF, 0xFFFF), 'must_be_researched'),
			(ResearchGraft, words(0, 5, 0xFF0F, 0xFFFF, 0xFFFF), 'must_be_researched'),
			(TechGraft, words(0, 5, 0xFF1E, 0xFFFF, 0xFFFF), 'allow_on_hallucinations'),
			(OrdersGraft, words(0, 5, 0xFF0F, 0xFFFF, 0xFFFF), 'must_be_researched'),
		):
			with self.subTest(graft_type=graft_type.__name__):
				graft = _load(graft_type, data)
				self.assertIn(f'\t{name}\n', decompile_req(graft))
				with self.assertRaises(PyMSError) as cm:
					IO.output_to_bytes(graft.save)
				self.assertIn(f'`{name}` is not available for {graft_type.LANGUAGE.DESCRIPTION.lower()} in script 5', str(cm.exception))

	def test_unavailable_sub_list_opcode_keeps_its_sub_list(self) -> None:
		# The 0xFFFF after `level_1_requires` ends its sub-list, not the script
		graft = _load(OrdersGraft, words(0, 5, 0xFF1F, 0x0074, 0xFFFF, 0xFF05, 0xFFFF, 0xFFFF))
		script = graft.get_script(5)
		assert script is not None
		self.assertEqual([command.definition for command in script.commands], [RequirementCodeCommands.Level1Requires, RequirementCodeCommands.HasCompleted, RequirementCodeCommands.EndLevelRequirements, RequirementCodeCommands.IsNotLiftedOff])

	def test_does_not_have_exit_is_an_order_opcode(self) -> None:
		# The vanilla Nydus Canal exit order requirements
		data = words(0, 46, 0xFF02, 0x0086, 0xFF0D, 0xFFFF, 0xFFFF)
		graft = _load(OrdersGraft, data)
		script = graft.get_script(46)
		assert script is not None
		self.assertEqual([command.definition for command in script.commands], [RequirementCodeCommands.CurrentUnitIs, RequirementCodeCommands.DoesNotHaveExit])
		self.assertIn("\tcurrent_unit_is 'Zerg Nydus Canal'\n\tdoes_not_have_exit\n", decompile_req(graft))
		self.assertEqual(IO.output_to_bytes(graft.save), data)

	def test_must_have_addon_reads_its_unit(self) -> None:
		graft = _load(UnitsGraft, words(0, 5, 0xFF04, 120, 0x0074, 0xFFFF, 0xFFFF))
		script = graft.get_script(5)
		assert script is not None
		self.assertEqual([command.definition for command in script.commands], [RequirementCodeCommands.MustHaveAddon, RequirementCodeCommands.HasCompleted])
		self.assertEqual(script.commands[0].params, [120])
		self.assertIn("\tmust_have_addon 'Terran Machine Shop'\n\thas_completed 'Terran Science Facility'\n", decompile_req(graft))

	def test_bare_values_are_has_completed(self) -> None:
		graft = _load(UnitsGraft, words(0, 1, 0x0070, 0xFFFF, 0xFFFF))
		script = graft.get_script(1)
		assert script is not None
		self.assertEqual(script.commands[0].definition, RequirementCodeCommands.HasCompleted)
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
				self.assertIn('not enough data to read', str(cm.exception))

	def test_failed_load_keeps_existing_scripts(self) -> None:
		graft = _load(UpgradesGraft, INFANTRY_ARMOR)
		with self.assertRaises(PyMSError):
			graft.load(words(0, 1))
		self.assertEqual(graft.list_ids(), [0])

class Test_Save(unittest.TestCase):
	def test_unended_sub_list_fails(self) -> None:
		graft = UpgradesGraft()
		graft.set_script(ReqScript(0, [CodeCommand(RequirementCodeCommands.Level1Requires, [])]))
		with self.assertRaises(PyMSError) as cm:
			IO.output_to_bytes(graft.save)
		self.assertIn('sub-list is not ended', str(cm.exception))

	def test_unavailable_command_fails(self) -> None:
		graft = UnitsGraft()
		graft.set_script(ReqScript(0, [CodeCommand(RequirementCodeCommands.Level1Requires, []), CodeCommand(RequirementCodeCommands.EndLevelRequirements, [])]))
		with self.assertRaises(PyMSError) as cm:
			IO.output_to_bytes(graft.save)
		self.assertIn('`level_1_requires` is not available for unit requirements in script 0', str(cm.exception))

	def test_empty_script(self) -> None:
		graft = OrdersGraft()
		graft.set_script(ReqScript(3))
		self.assertEqual(IO.output_to_bytes(graft.save), words(0, 3, 0xFFFF, 0xFFFF))

class Test_Scripts(unittest.TestCase):
	def test_set_script_inserts_new_ids_in_order(self) -> None:
		graft = _load(UnitsGraft, words(0, 9, 0xFFFF, 2, 0xFFFF, 20, 0xFFFF, 0xFFFF))
		graft.set_script(ReqScript(15))
		graft.set_script(ReqScript(2, [CodeCommand(RequirementCodeCommands.HasCompleted, [7])]))
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
		scripts = compile_req('Unit 0:\n\tcurrent_unit_is 111\n\thas_completed "Terran Academy"\n\thas_completed 0x75\n', UnitsGraft)
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
		self.assertCompileError('Unit 0:\n\tlevel_1_requires\n', UnitsGraft, '`level_1_requires` is not available for unit requirements', 2)
		self.assertCompileError('Unit 0:\n\tend_level_requirements\n', UnitsGraft, '`end_level_requirements` is not available for unit requirements', 2)
		self.assertCompileError('Order 0:\n\tis_researched 1\n', OrdersGraft, '`is_researched` is not available for order requirements', 2)
		self.assertCompileError('Unit 0:\n\tdoes_not_have_exit\n', UnitsGraft, '`does_not_have_exit` is not available for unit requirements', 2)
		self.assertCompileError('Unit 0:\n\traw 0xFF05\n', UnitsGraft, 'Unknown command `raw`', 2)

	def test_compile_requires_the_files_language(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			UnitsGraft.compile(parse_context('Unit 0:\n', language=UpgradesGraft.LANGUAGE()))
		self.assertIn('Unit Requirements scripts must be compiled with a parse context using `UnitRequirementsLanguage`', str(cm.exception))

	def test_compile_requires_the_files_own_language(self) -> None:
		# Research and tech use requirements have the same opcodes, but each file has its own language
		with self.assertRaises(PyMSError) as cm:
			ResearchGraft.compile(parse_context('Research 1:\n\tmust_be_researched\n', language=TechGraft.LANGUAGE()))
		self.assertIn('Tech Research Requirements scripts must be compiled with a parse context using `ResearchRequirementsLanguage`', str(cm.exception))

	def test_end_level_requirements_outside_sublist(self) -> None:
		self.assertCompileError('Upgrade 0:\n\tend_level_requirements\n', UpgradesGraft, '`end_level_requirements` used outside of a `level_1_requires` or `level_2_requires` sub-list')

	def test_unended_sublist(self) -> None:
		self.assertCompileError('Upgrade 0:\n\tlevel_1_requires\n', UpgradesGraft, 'sub-list is not ended with `end_level_requirements`')

	def test_has_unit_too_large(self) -> None:
		self.assertCompileError('Unit 0:\n\thas_completed 0xFF00\n', UnitsGraft, 'Value is too large for `unit`')

	def test_unknown_name(self) -> None:
		self.assertCompileError("Unit 0:\n\thas_completed 'Not A Unit'\n", UnitsGraft, '`Not A Unit` is not a known unit name')

	def test_name_of_multiple_ids(self) -> None:
		self.assertCompileError("Unit 0:\n\thas_completed 'Same'\n", UnitsGraft, '`Same` is the name of multiple unit IDs (0, 1)', data_context=_duplicate_names_context())

	def test_unique_name_beside_duplicate_names(self) -> None:
		scripts = compile_req("Unit 0:\n\thas_completed 'Other'\n", UnitsGraft, _duplicate_names_context())
		self.assertEqual(scripts[0].commands[0].params, [2])

class Test_Decompile(unittest.TestCase):
	def test_duplicate_names_are_written_as_ids(self) -> None:
		graft = _load(UnitsGraft, words(0, 2, 0, 1, 2, 0xFFFF, 0xFFFF))
		text = decompile_req(graft, _duplicate_names_context())
		self.assertEqual(text, "Unit 2:\t# Terran Vulture (Other)\n\thas_completed 0\t# Terran Marine (Same)\n\thas_completed 1\t# Terran Ghost (Same)\n\thas_completed 'Other'\n")
		graft.replace_scripts(compile_req(text, UnitsGraft, _duplicate_names_context()))
		self.assertEqual(IO.output_to_bytes(graft.save), words(0, 2, 0, 1, 2, 0xFFFF, 0xFFFF))

class Test_ScriptBody(unittest.TestCase):
	def test_vanilla_scripts_round_trip(self) -> None:
		for graft_type in REQ_GRAFT_TYPES:
			graft = graft_type()
			graft.new()
			for entry_id in graft.list_ids():
				with self.subTest(graft_type=graft_type.__name__, entry_id=entry_id):
					script = graft.get_script(entry_id)
					assert script is not None
					recompiled = compile_req_script(decompile_req_script(graft, entry_id), graft_type, entry_id)
					self.assertEqual(recompiled.entry_id, entry_id)
					self.assertEqual([(command.definition, command.params) for command in recompiled.commands], [(command.definition, command.params) for command in script.commands])

	def test_body_has_no_header_and_starts_unindented(self) -> None:
		graft = _load(UpgradesGraft, INFANTRY_ARMOR)
		body = ''.join(line[1:] + '\n' for line in INFANTRY_ARMOR_TEXT.splitlines()[1:])
		self.assertEqual(decompile_req_script(graft, 0), body)

	def test_decompile_unknown_script(self) -> None:
		graft = _load(UpgradesGraft, INFANTRY_ARMOR)
		with self.assertRaises(PyMSError) as cm:
			decompile_req_script(graft, 5)
		self.assertIn('There is no script with ID 5', str(cm.exception))

	def test_compile_sets_the_entry_id(self) -> None:
		script = compile_req_script('# Comment\ncurrent_unit_is 111\n\nhas_completed 0x75\n', UnitsGraft, 9)
		self.assertEqual(script.entry_id, 9)
		self.assertEqual([command.definition for command in script.commands], [RequirementCodeCommands.CurrentUnitIs, RequirementCodeCommands.HasCompleted])

	def test_empty_body(self) -> None:
		self.assertEqual(compile_req_script('# Nothing\n\n', OrdersGraft, 3).commands, [])

	def assertBodyError(self, code: str, graft_type: type[AbstractReqGraft], message: str, line: int | None) -> None:
		with self.assertRaises(PyMSError) as cm:
			compile_req_script(code, graft_type, 0)
		self.assertIn(message, str(cm.exception))
		self.assertEqual(cm.exception.line, line)

	def test_header_is_an_error(self) -> None:
		self.assertBodyError('is_not_lifted_off\nUnit 0:\n', UnitsGraft, '`Unit` headers are not allowed', 2)

	def test_unknown_command(self) -> None:
		self.assertBodyError('is_not_lifted_off\n\tis_awesome\n', UnitsGraft, 'Unknown command `is_awesome`', 2)

	def test_unavailable_command(self) -> None:
		self.assertBodyError('does_not_have_exit\n', UnitsGraft, '`does_not_have_exit` is not available for unit requirements', 1)

	def test_unended_sublist_points_at_the_sublist(self) -> None:
		self.assertBodyError('is_not_lifted_off\nlevel_1_requires\nhas_completed 0\n', UpgradesGraft, 'sub-list is not ended with `end_level_requirements`', 2)

	def test_end_level_requirements_outside_sublist_points_at_it(self) -> None:
		self.assertBodyError('is_not_lifted_off\nend_level_requirements\n', UpgradesGraft, '`end_level_requirements` used outside of', 2)

	def test_compile_requires_the_files_language(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			ReqScript.compile(parse_context('', language=UpgradesGraft.LANGUAGE()), 0, UnitsGraft.LANGUAGE)
		self.assertIn('Unit Requirements scripts must be compiled with a parse context using `UnitRequirementsLanguage`', str(cm.exception))

class Test_UpgradeLevels(unittest.TestCase):
	# The game only checks `level_1_requires`, jumping from it to the `level_N_requires` word for the current level, then checking up to the next 0xFFFF

	def assertBodyError(self, code: str, message: str, line: int) -> None:
		with self.assertRaises(PyMSError) as cm:
			compile_req_script(code, UpgradesGraft, 0)
		self.assertIn(message, str(cm.exception))
		self.assertEqual(cm.exception.line, line)

	def test_all_levels_in_order_are_valid(self) -> None:
		code = 'is_not_lifted_off\nlevel_1_requires\nhas_completed 1\nend_level_requirements\nlevel_2_requires\nend_level_requirements\nlevel_3_requires\nhas_completed 2\nhas_completed 3\n'
		self.assertEqual(len(compile_req_script(code, UpgradesGraft, 0).commands), 9)

	def test_later_level_needs_level_1(self) -> None:
		self.assertBodyError('is_not_lifted_off\nlevel_3_requires\nhas_completed 1\n', '`level_3_requires` is used without a `level_1_requires` before it', 2)
		self.assertBodyError('level_2_requires\nend_level_requirements\nlevel_3_requires\n', '`level_2_requires` is used without a `level_1_requires` before it', 1)

	def test_levels_must_be_in_order(self) -> None:
		self.assertBodyError('level_1_requires\nend_level_requirements\nlevel_3_requires\n', '`end_level_requirements` must be directly followed by `level_2_requires`', 3)

	def test_next_level_before_the_sub_list_is_ended_points_at_the_sub_list(self) -> None:
		self.assertBodyError('is_not_lifted_off\nlevel_1_requires\nhas_completed 1\nlevel_2_requires\nend_level_requirements\nlevel_3_requires\n', 'A `level_1_requires` or `level_2_requires` sub-list is not ended with `end_level_requirements`', 2)
		self.assertBodyError('level_1_requires\nend_level_requirements\nlevel_2_requires\nhas_completed 1\nlevel_3_requires\n', 'A `level_1_requires` or `level_2_requires` sub-list is not ended with `end_level_requirements`', 3)

	def test_first_error_is_reported_whatever_its_kind(self) -> None:
		# The misplaced `end_level_requirements` comes before the `has_completed` that is too large
		script = ReqScript(0, [
			CodeCommand(RequirementCodeCommands.IsNotLiftedOff, []),
			CodeCommand(RequirementCodeCommands.EndLevelRequirements, []),
			CodeCommand(RequirementCodeCommands.HasCompleted, [0xFF00]),
		])
		self.assertEqual(script.find_invalid_command(UpgradesGraft.LANGUAGE), ('`end_level_requirements` used outside of a `level_1_requires` or `level_2_requires` sub-list in script 0', 1))
		script.commands.reverse()
		invalid = script.find_invalid_command(UpgradesGraft.LANGUAGE)
		assert invalid is not None
		self.assertIn('`has_completed` unit ID 65280 is too large', invalid[0])
		self.assertEqual(invalid[1], 0)

	def test_levels_are_used_once(self) -> None:
		self.assertBodyError('level_1_requires\nend_level_requirements\nlevel_2_requires\nend_level_requirements\nlevel_3_requires\nlevel_1_requires\nend_level_requirements\n', '`level_1_requires` is used more than once', 6)

	def test_level_1_needs_the_other_levels(self) -> None:
		self.assertBodyError('is_not_lifted_off\nlevel_1_requires\nhas_completed 1\nend_level_requirements\n', '`level_1_requires` is used without `level_2_requires` and `level_3_requires` after it', 2)
		self.assertBodyError('level_1_requires\nend_level_requirements\nlevel_2_requires\nend_level_requirements\n', '`level_1_requires` is used without `level_3_requires` after it', 1)

	def test_end_level_requirements_is_directly_followed_by_the_next_level(self) -> None:
		self.assertBodyError('level_1_requires\nend_level_requirements\nhas_completed 1\nlevel_2_requires\nend_level_requirements\nlevel_3_requires\n', '`end_level_requirements` must be directly followed by `level_2_requires`', 3)
		self.assertBodyError('level_1_requires\nend_level_requirements\nlevel_2_requires\nend_level_requirements\nis_not_lifted_off\nlevel_3_requires\n', '`end_level_requirements` must be directly followed by `level_3_requires`', 5)

	def test_or_does_not_follow_a_level(self) -> None:
		self.assertBodyError('level_1_requires\nor\nhas_completed 1\nend_level_requirements\nlevel_2_requires\nend_level_requirements\nlevel_3_requires\n', '`or` can\'t directly follow `level_1_requires`', 2)
		self.assertBodyError('level_1_requires\nend_level_requirements\nlevel_2_requires\nend_level_requirements\nlevel_3_requires\nor\nhas_completed 1\n', '`or` can\'t directly follow `level_3_requires`', 6)

	def test_or_does_not_come_before_end_level_requirements(self) -> None:
		self.assertBodyError('level_1_requires\nhas_completed 1\nor\nend_level_requirements\nlevel_2_requires\nend_level_requirements\nlevel_3_requires\n', '`or` can\'t directly come before `end_level_requirements`', 3)

	def test_params_are_not_upgrade_level_words(self) -> None:
		# The game's jump to a level searches every word, including parameters
		for value in (0xFF20, 0xFF21):
			with self.subTest(value=f'0x{value:04X}'):
				script = ReqScript(0, [
					CodeCommand(RequirementCodeCommands.Level1Requires, []),
					CodeCommand(RequirementCodeCommands.CurrentUnitIs, [value]),
					CodeCommand(RequirementCodeCommands.EndLevelRequirements, []),
					CodeCommand(RequirementCodeCommands.Level2Requires, []),
					CodeCommand(RequirementCodeCommands.EndLevelRequirements, []),
					CodeCommand(RequirementCodeCommands.Level3Requires, []),
				])
				invalid = script.find_invalid_command(UpgradesGraft.LANGUAGE)
				assert invalid is not None
				self.assertIn(f'`current_unit_is` can\'t use the value 0x{value:04X} after `level_1_requires`', invalid[0])
				self.assertEqual(invalid[1], 1)

	def test_params_before_level_1_are_not_checked(self) -> None:
		script = ReqScript(0, [
			CodeCommand(RequirementCodeCommands.CurrentUnitIs, [0xFF20]),
			CodeCommand(RequirementCodeCommands.Level1Requires, []),
			CodeCommand(RequirementCodeCommands.EndLevelRequirements, []),
			CodeCommand(RequirementCodeCommands.Level2Requires, []),
			CodeCommand(RequirementCodeCommands.EndLevelRequirements, []),
			CodeCommand(RequirementCodeCommands.Level3Requires, []),
		])
		self.assertIsNone(script.find_invalid_command(UpgradesGraft.LANGUAGE))

	def test_invalid_levels_load_but_fail_to_save(self) -> None:
		# Level 1 without levels 2 and 3
		graft = _load(UpgradesGraft, words(0, 5, 0xFF1F, 0x0074, 0xFFFF, 0xFF05, 0xFFFF, 0xFFFF))
		with self.assertRaises(PyMSError) as cm:
			IO.output_to_bytes(graft.save)
		self.assertIn('`end_level_requirements` must be directly followed by `level_2_requires` in script 5', str(cm.exception))

class Test_LanguageCommands(unittest.TestCase):
	def test_commands_are_the_languages_commands(self) -> None:
		for language, commands in (
			(UnitRequirementsLanguage, RequirementCodeCommands.unit_req_commands),
			(UpgradeRequirementsLanguage, RequirementCodeCommands.upgrade_req_commands),
			(ResearchRequirementsLanguage, RequirementCodeCommands.research_req_commands),
			(TechRequirementsLanguage, RequirementCodeCommands.tech_use_req_commands),
			(OrderRequirementsLanguage, RequirementCodeCommands.order_req_commands),
		):
			with self.subTest(language=language.__name__):
				self.assertEqual(language.commands(), commands)

	def test_upgrade_levels_are_only_for_upgrades(self) -> None:
		for graft_type in (UnitsGraft, ResearchGraft, TechGraft, OrdersGraft):
			for name in ('level_1_requires', 'level_2_requires', 'level_3_requires', 'end_level_requirements'):
				with self.subTest(graft_type=graft_type.__name__, name=name):
					with self.assertRaises(PyMSError) as cm:
						compile_req_script(f'{name}\n', graft_type, 0)
					self.assertIn(f'`{name}` is not available for {graft_type.LANGUAGE.DESCRIPTION.lower()}', str(cm.exception))

	def test_must_be_researched_is_only_for_tech_use(self) -> None:
		self.assertEqual(compile_req_script('must_be_researched\n', TechGraft, 0).commands[0].definition, RequirementCodeCommands.MustBeResearched)
		for graft_type in (UnitsGraft, UpgradesGraft, ResearchGraft, OrdersGraft):
			with self.subTest(graft_type=graft_type.__name__):
				with self.assertRaises(PyMSError) as cm:
					compile_req_script('must_be_researched\n', graft_type, 0)
				self.assertIn(f'`must_be_researched` is not available for {graft_type.LANGUAGE.DESCRIPTION.lower()}', str(cm.exception))

	def test_allow_on_hallucinations_is_not_for_tech_use_or_units(self) -> None:
		allowed: tuple[type[AbstractReqGraft], ...] = (UpgradesGraft, ResearchGraft, OrdersGraft)
		for graft_type in allowed:
			with self.subTest(graft_type=graft_type.__name__):
				self.assertEqual(compile_req_script('allow_on_hallucinations\n', graft_type, 0).commands[0].definition, RequirementCodeCommands.AllowOnHallucinations)
		not_allowed: tuple[type[AbstractReqGraft], ...] = (UnitsGraft, TechGraft)
		for graft_type in not_allowed:
			with self.subTest(graft_type=graft_type.__name__):
				with self.assertRaises(PyMSError) as cm:
					compile_req_script('allow_on_hallucinations\n', graft_type, 0)
				self.assertIn(f'`allow_on_hallucinations` is not available for {graft_type.LANGUAGE.DESCRIPTION.lower()}', str(cm.exception))

	def test_every_opcode_is_available_somewhere(self) -> None:
		self.assertEqual(sorted(RequirementCodeCommands.unit_loadable_opcodes.keys() | RequirementCodeCommands.check_allowed_loadable_opcodes.keys()), list(range(0xFF01, 0xFF27)))

	def test_loadable_opcodes_are_the_available_opcodes_of_the_files_kind(self) -> None:
		self.assertEqual(set(UnitRequirementsLanguage.LOADABLE_OPCODES.values()), {cmd_def for cmd_def in RequirementCodeCommands.unit_req_commands if cmd_def.byte_code_id is not None})
		check_allowed_commands = {cmd_def for language in (UpgradeRequirementsLanguage, ResearchRequirementsLanguage, TechRequirementsLanguage, OrderRequirementsLanguage) for cmd_def in language.commands() if cmd_def.byte_code_id is not None}
		for language in (UpgradeRequirementsLanguage, ResearchRequirementsLanguage, TechRequirementsLanguage, OrderRequirementsLanguage):
			with self.subTest(language=language.__name__):
				self.assertEqual(set(language.LOADABLE_OPCODES.values()), check_allowed_commands)

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
		for words_list, message in (([0xFF1F, 0xFFFF], 'not enough data to read'), ([0xFF04], 'has the word 0xFF04, which is not an opcode for upgrade requirements')):
			with self.subTest(message=message):
				graft = _load(UpgradesGraft, INFANTRY_ARMOR)
				fgp = FGP()
				fgp.requirements[UpgradesGraft] = {0: None, 2: words_list}
				with self.assertRaises(PyMSError) as cm:
					graft.import_fgp(fgp)
				self.assertIn(message, str(cm.exception))
				self.assertEqual(graft.list_ids(), [0])
