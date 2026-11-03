from .utils import button_bytes, buttons_file, decompile_buttons, compile_buttons, parse_context
from ...FileFormats.Graft import ButtonsGraft, Button, StatInfo, UnitButtons, UnitsGraft, FGP, FGPUnit
from ...FileFormats.Graft.CodeHandlers import ButtonsLanguage, DataContext, CodeCommands
from ...FileFormats.TBL import TBL
from ...Utilities.CodeHandlers.LanguageDefinition import LanguageContext
from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO

import unittest

MOVE = button_bytes(1, 228, 3, 9, enabled_string=664) # Always, Move
STOP = button_bytes(2, 229, 3, 10, enabled_string=665) # Always, Stop
TRAIN_MARINE = button_bytes(1, 0, 4, 3, enabled_string=1) # Can Create Unit (Marine), Create Unit (Marine)

def _load(data: bytes) -> ButtonsGraft:
	graft = ButtonsGraft()
	graft.load(data)
	return graft

class Test_Defaults(unittest.TestCase):
	def test_load_save_is_byte_identical(self) -> None:
		with IO.InputBytes(ButtonsGraft.default_path()) as f:
			data = f.read()
		graft = ButtonsGraft()
		self.assertEqual(graft.load(data), [])
		self.assertEqual(len(graft.button_sets), 98)
		self.assertEqual(len(graft.units), 250)
		self.assertEqual(len(graft.stat_info), 228)
		self.assertEqual(IO.output_to_bytes(graft.save), data)

	def test_decompile_compile_is_byte_identical(self) -> None:
		graft = ButtonsGraft()
		graft.new()
		text = decompile_buttons(graft)
		recompiled = compile_buttons(text)
		self.assertEqual(IO.output_to_bytes(recompiled.save), IO.output_to_bytes(graft.save))
		self.assertEqual(decompile_buttons(recompiled), text)

	def test_vanilla_marine(self) -> None:
		graft = ButtonsGraft()
		graft.new()
		text = decompile_buttons(graft)
		self.assertIn('unit 0 {\t# Terran Marine\n\tbutton_set 68\t# Marine/Firebat + Heroes\n\tconnected_unit None\n\tstat_info(StatusFunction2, DisplayFunction1)\t# Stat preset: Normal Unit\n}\n', text)

	def test_vanilla_replay_buttons(self) -> None:
		graft = ButtonsGraft()
		graft.new()
		stat_txt = TBL()
		stat_txt.strings = ['\x00'] * 1544
		stat_txt.strings[1540] = 'u\x00Speed \x03U\x01p\x00'
		stat_txt.strings[1541] = 'p\x00\x03P\x01lay\x00'
		stat_txt.strings[1543] = 'd\x00Slow \x03D\x01own\x00'
		text = decompile_buttons(graft, DataContext(stat_txt_tbl=stat_txt))
		self.assertTrue(text.startswith('''button_set 0 {\t# Replay: Paused
	button 7 {\t# Bottom Left
		icon 386\t# Play (Replay)
		is_watching_replay
		play_pause_replay
		enabled_str 1542\t# p<0><3>P<1>lay
		disabled_str 0
	}
	button 8 {\t# Bottom Middle
		icon 389\t# Slow Down (Replay)
		can_slow_down_replay
		slow_down_replay
		enabled_str 1544\t# d<0>Slow <3>D<1>own
		disabled_str 0
	}
	button 9 {\t# Bottom Right
		icon 388\t# Speed Up (Replay)
		can_speed_up_replay
		speed_up_replay
		enabled_str 1541\t# u<0>Speed <3>U<1>p
		disabled_str 0
	}
}

'''), text[:1000])

class Test_Decompile(unittest.TestCase):
	def _round_trip(self, button: Button) -> str:
		graft = ButtonsGraft()
		graft.button_sets = [[button]]
		graft.units = []
		graft.stat_info = []
		text = decompile_buttons(graft)
		self.assertEqual(compile_buttons(text).button_sets, [[button]])
		return text

	def test_function_parameters_are_named(self) -> None:
		text = self._round_trip(Button.unpack(TRAIN_MARINE))
		self.assertIn("\t\tcan_create 'Terran Marine'\n\t\ttrain 'Terran Marine'\n", text)

	def test_unused_function_values_are_kept(self) -> None:
		text = self._round_trip(Button(condition=3, condition_param=254, action=4, action_param=0x10))
		self.assertIn('\t\talways 254\n\t\tcancel_train 16\n', text)

	def test_every_function_round_trips(self) -> None:
		for commands, field in ((CodeCommands.condition_commands, 'condition'), (CodeCommands.action_commands, 'action')):
			for index, cmd_def in enumerate(commands):
				with self.subTest(name=cmd_def.name):
					self.assertEqual(cmd_def.function_index, index)
					self.assertIn(f'\t\t{cmd_def.name}', self._round_trip(Button(**{field: index, f'{field}_param': 1})))

	def test_unknown_functions_use_their_index(self) -> None:
		text = self._round_trip(Button(condition=500, condition_param=5, action=600, action_param=6))
		self.assertIn('\t\tcondition 500 5\n\t\taction 600 6\n', text)

	def test_unit_padding(self) -> None:
		graft = ButtonsGraft()
		graft.units = [UnitButtons(None, None, 7)]
		graft.stat_info = []
		self.assertIn('unit 0 {\t# Terran Marine\n\tbutton_set None\n\tconnected_unit None\n\tpadding 7\n}\n', decompile_buttons(graft))

class Test_Load(unittest.TestCase):
	def test_shared_button_sets(self) -> None:
		data = buttons_file([MOVE, STOP, TRAIN_MARINE], [(2, 0, 0xFFFF, 0), (1, 2, 5, 0), (2, 0, 0xFFFF, 0), (0, 0, 0xFFFF, 0)], [(0, 1, 0), (7, 2, 1)])
		graft = _load(data)
		self.assertEqual(graft.button_sets, [[Button.unpack(MOVE), Button.unpack(STOP)], [Button.unpack(TRAIN_MARINE)]])
		self.assertEqual(graft.units, [UnitButtons(0), UnitButtons(1, 5), UnitButtons(0), UnitButtons()])
		self.assertEqual(graft.stat_info, [StatInfo(0, 1, 0), StatInfo(7, 2, 1)])
		self.assertEqual(IO.output_to_bytes(graft.save), data)

	def test_unreferenced_buttons_are_kept(self) -> None:
		data = buttons_file([MOVE, STOP, TRAIN_MARINE], [(1, 1, 0xFFFF, 0)], [])
		graft = _load(data)
		self.assertEqual(len(graft.button_sets), 3)
		self.assertEqual(graft.units, [UnitButtons(1)])
		self.assertEqual(IO.output_to_bytes(graft.save), data)

	def test_padding_is_preserved(self) -> None:
		data = buttons_file([MOVE], [(1, 0, 0xFFFF, 0x1234)], [])
		graft = _load(data)
		self.assertEqual(graft.units[0].padding, 0x1234)
		self.assertIn('\tpadding 4660\n', decompile_buttons(graft))
		self.assertEqual(IO.output_to_bytes(graft.save), data)

	def test_overlapping_sets_are_separated(self) -> None:
		data = buttons_file([MOVE, STOP, TRAIN_MARINE], [(3, 0, 0xFFFF, 0), (2, 1, 0xFFFF, 0)], [])
		graft = ButtonsGraft()
		warnings = graft.load(data)
		self.assertEqual(len(warnings), 1)
		self.assertIn('overlap another button set', warnings[0].warning)
		self.assertEqual(graft.button_sets, [[Button.unpack(MOVE), Button.unpack(STOP), Button.unpack(TRAIN_MARINE)], [Button.unpack(STOP), Button.unpack(TRAIN_MARINE)]])
		saved = IO.output_to_bytes(graft.save)
		self.assertEqual(saved, buttons_file([MOVE, STOP, TRAIN_MARINE, STOP, TRAIN_MARINE], [(3, 0, 0xFFFF, 0), (2, 3, 0xFFFF, 0)], []))
		# The separated sets are stable
		self.assertEqual(IO.output_to_bytes(_load(saved).save), saved)
		# The separated sets don't share buttons
		graft.button_sets[1][0].icon = 1
		self.assertEqual(graft.button_sets[0][1].icon, 229)

	def test_unknown_functions_warn(self) -> None:
		graft = ButtonsGraft()
		warnings = graft.load(buttons_file([button_bytes(1, 0, 500, 600)], [(1, 0, 0xFFFF, 0)], [(0, 50, 60)]))
		messages = [warning.warning for warning in warnings]
		self.assertEqual(messages, [
			'Button set 0 uses unknown button condition 500',
			'Button set 0 uses unknown button action 600',
			'Unit 0 uses unknown status function 50',
			'Unit 0 uses unknown display function 60',
		])

	def test_trailing_data_warns(self) -> None:
		graft = ButtonsGraft()
		warnings = graft.load(buttons_file([], [], []) + b'\x00\x00')
		self.assertEqual(len(warnings), 1)
		self.assertIn('2 bytes of unused data', warnings[0].warning)

	def test_too_small_for_header(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			ButtonsGraft().load(b'\x00' * 11)
		self.assertIn('too small for its header', str(cm.exception))

	def test_too_small_for_counts(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			ButtonsGraft().load(buttons_file([MOVE], [(1, 0, 0xFFFF, 0)], [])[:-1])
		self.assertIn('too small for its 1 buttons, 1 units, and 0 stat infos', str(cm.exception))

	def test_unit_buttons_past_the_end(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			ButtonsGraft().load(buttons_file([MOVE], [(2, 0, 0xFFFF, 0)], []))
		self.assertIn('unit 0 uses buttons 0 to 1 but there are only 1 buttons', str(cm.exception))

	def test_failed_load_keeps_existing_data(self) -> None:
		graft = _load(buttons_file([MOVE], [(1, 0, 0xFFFF, 0)], []))
		with self.assertRaises(PyMSError):
			graft.load(b'')
		self.assertEqual(graft.units, [UnitButtons(0)])

class Test_Save(unittest.TestCase):
	def test_empty_button_set_saves_as_no_buttons(self) -> None:
		graft = ButtonsGraft()
		graft.button_sets = [[]]
		graft.units = [UnitButtons(0, 3)]
		graft.stat_info = []
		self.assertEqual(IO.output_to_bytes(graft.save), buttons_file([], [(0, 0, 3, 0)], []))

	def test_missing_button_set_fails(self) -> None:
		graft = ButtonsGraft()
		graft.units = [UnitButtons(4)]
		with self.assertRaises(PyMSError) as cm:
			IO.output_to_bytes(graft.save)
		self.assertIn('Unit 0 uses button set 4, which does not exist', str(cm.exception))

class Test_Editing(unittest.TestCase):
	def test_remove_button_set_renumbers_references(self) -> None:
		graft = ButtonsGraft()
		graft.button_sets = [[Button.unpack(MOVE)], [Button.unpack(STOP)], [Button.unpack(TRAIN_MARINE)]]
		graft.units = [UnitButtons(2), UnitButtons(0)]
		self.assertEqual(graft.remove_button_set(1), [Button.unpack(STOP)])
		self.assertEqual(graft.units, [UnitButtons(1), UnitButtons(0)])

	def test_remove_used_button_set_fails(self) -> None:
		graft = ButtonsGraft()
		graft.button_sets = [[Button.unpack(MOVE)]]
		graft.units = [UnitButtons(0), UnitButtons(0)]
		with self.assertRaises(PyMSError) as cm:
			graft.remove_button_set(0)
		self.assertIn("can't be removed because it is used by unit(s) 0, 1", str(cm.exception))

	def test_set_counts(self) -> None:
		graft = ButtonsGraft()
		graft.set_unit_count(300)
		graft.set_stat_count(230)
		self.assertEqual(len(graft.units), 300)
		self.assertEqual(graft.stat_info[229], StatInfo(229))
		graft.set_unit_count(10)
		graft.set_stat_count(5)
		self.assertEqual((len(graft.units), len(graft.stat_info)), (10, 5))

def _button(body: str, position: int = 1) -> str:
	return f'\tbutton {position} {{\n' + ''.join(f'\t\t{line}\n' for line in body.split('\n')) + '\t}\n'

MOVE_BODY = 'icon 0\nalways\nmove\nenabled_str 0\ndisabled_str 0'

class Test_Compile(unittest.TestCase):
	def test_names_and_defaults(self) -> None:
		graft = compile_buttons(f"""button_set 0 {{
{_button("icon 0\ncan_create 'Terran Marine'\ntrain 'Terran Marine'\nenabled_str 1\ndisabled_str 0")}{_button('icon 0x10\nalways\nupgrade "Terran Infantry Armor"\nenabled_str 2\ndisabled_str 3', 2)}}}
button_set 2 {{
}}
unit 0 {{
	stat_info(1, 0)
}}
unit 1 {{
	button_set 0
	connected_unit 'Terran Ghost'
	stat_info(StatusFunction2, DisplayFunction1, 9)
}}

unit 3 {{
}}
""")
		self.assertEqual(graft.button_sets, [[Button(position=1, condition=4, action=3, enabled_string=1), Button(position=2, icon=16, condition=3, action=26, enabled_string=2, disabled_string=3)], [], []])
		self.assertEqual(graft.units, [UnitButtons(), UnitButtons(0, 1), UnitButtons(), UnitButtons()])
		self.assertEqual(graft.stat_info, [StatInfo(0, 1, 0), StatInfo(9, 1, 0)])

	def test_buttons_can_share_a_position(self) -> None:
		graft = compile_buttons('button_set 0 {\n' + _button(MOVE_BODY) + _button(MOVE_BODY) + '}\n')
		self.assertEqual(graft.button_sets, [[Button(position=1, condition=3, action=9)] * 2])

	def test_raw_function_indices(self) -> None:
		graft = compile_buttons('button_set 0 {\n' + _button('icon 0\ncondition 3 0\naction 600 0x10\nenabled_str 0\ndisabled_str 0') + '}\n')
		self.assertEqual(graft.button_sets, [[Button(position=1, condition=3, action=600, action_param=16)]])

	def assertCompileError(self, code: str, message: str, line: int | None = None) -> None:
		with self.assertRaises(PyMSError) as cm:
			compile_buttons(code)
		self.assertIn(message, str(cm.exception))
		if line is not None:
			self.assertEqual(cm.exception.line, line)

	def test_missing_stat_info(self) -> None:
		self.assertCompileError('unit 0 {\n}\nunit 1 {\n\tstat_info(StatusFunction1, DisplayFunction1)\n}\n', 'Unit 0 is missing `stat_info`')

	def test_undefined_button_set(self) -> None:
		self.assertCompileError('button_set 0 {\n}\nunit 0 {\n\tbutton_set 1\n}\n', 'Unit 0 uses button set 1, which is not defined', 3)

	def test_duplicate_property(self) -> None:
		self.assertCompileError('unit 0 {\n\tbutton_set None\n\tbutton_set None\n}\n', "Duplicate unit command 'button_set'", 3)

	def test_duplicate_choice(self) -> None:
		self.assertCompileError('button_set 0 {\n' + _button('icon 0\nalways\nis_player_nuke_ready') + '}\n', "Duplicate button command 'is_player_nuke_ready'", 5)

	def test_missing_field(self) -> None:
		self.assertCompileError('button_set 0 {\n' + _button('always\nmove\nenabled_str 0\ndisabled_str 0') + '}\n', "Button 1 is missing 'icon'", 7)

	def test_duplicate_header(self) -> None:
		self.assertCompileError('button_set 0 {\n}\nbutton_set 0 {\n}\n', 'Button set 0 is already defined on line 1', 3)

	def test_unknown_function(self) -> None:
		self.assertCompileError('button_set 0 {\n' + _button('icon 0\nis_sometimes') + '}\n', "Unknown button command 'is_sometimes'", 4)

	def test_param_uses_condition_kind(self) -> None:
		# `always` takes no parameter, so a unit name isn't valid for it
		self.assertCompileError('button_set 0 {\n' + _button("icon 0\nalways 'Terran Marine'") + '}\n', "Invalid value `'Terran Marine'` for `condition_param`", 4)

	def test_function_param_is_required(self) -> None:
		self.assertCompileError('button_set 0 {\n' + _button('icon 0\nalways\ntrain') + '}\n', 'for `action_param`', 5)

	def test_unknown_unit_command(self) -> None:
		self.assertCompileError('unit 0 {\n\ticon 0\n}\n', "Unknown unit command 'icon'", 2)

	def test_parens_and_flat_forms(self) -> None:
		graft = compile_buttons("button_set 0 {\n" + _button("icon(0)\nalways()\ntrain('Terran Marine')\nenabled_str 0\ndisabled_str 0") + "}\nunit 0 {\n\tbutton_set(0)\n\tconnected_unit(None)\n\tstat_info 1 0 7\n}\n")
		self.assertEqual(graft.button_sets, [[Button(position=1, condition=3, action=3)]])
		self.assertEqual(graft.units, [UnitButtons(0)])
		self.assertEqual(graft.stat_info, [StatInfo(7, 1, 0)])

	def test_stat_info_requires_functions(self) -> None:
		self.assertCompileError('unit 0 {\n\tstat_info(StatusFunction1)\n}\n', 'expected `,` separating parameters', 2)

	def test_too_many_parameters(self) -> None:
		self.assertCompileError('unit 0 {\n\tbutton_set 0 1\n}\n', 'expected end of line or file', 2)

	def test_unclosed_block(self) -> None:
		self.assertCompileError('button_set 0 {\n' + _button(MOVE_BODY), "Expected a '}' to end the button set, got end of file instead")

	def test_text_after_block(self) -> None:
		self.assertCompileError('unit 0 {\n} unit 1 {\n}\n', "Unexpected token 'unit' (expected end of line or file)", 2)

	def test_requires_buttons_language(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			ButtonsGraft.compile(parse_context('unit 0 {\n}\n', language=UnitsGraft.LANGUAGE()))
		self.assertIn('ButtonsGraft must be compiled with a parse context using `ButtonsLanguage`', str(cm.exception))

	def test_language_has_the_commands(self) -> None:
		language = ButtonsLanguage()
		for name in ('icon', 'always', 'condition', 'move', 'action', 'enabled_str', 'disabled_str', 'button_set', 'connected_unit', 'stat_info', 'padding'):
			with self.subTest(name=name):
				self.assertIsNotNone(language.lookup_command(name, LanguageContext()))

	def test_command_outside_block(self) -> None:
		self.assertCompileError('icon 0\n', "Unexpected token 'icon' (expected 'button_set' or 'unit')", 1)

	def test_block_needs_braces(self) -> None:
		self.assertCompileError('button_set 0\n', "Expected a '{' to start the button set, got", 1)

class Test_ImportFGP(unittest.TestCase):
	def test_overlays_buttons(self) -> None:
		graft = ButtonsGraft()
		graft.button_sets = [[Button.unpack(MOVE)]]
		graft.units = [UnitButtons(0), UnitButtons(0)]
		graft.stat_info = [StatInfo(0, 1, 0)]
		fgp = FGP()
		fgp.button_sets = {2: [Button.unpack(STOP)]}
		fgp.units = [
			FGPUnit(1, 2, 0xFFFF, StatInfo(1, 2, 1)),
			FGPUnit(0, 7, 5, None),
			FGPUnit(9, 0, 0xFFFF, None),
		]
		warnings = graft.import_fgp(fgp)
		self.assertEqual([warning.warning for warning in warnings], [
			'FireGraft unit 1 is past the last unit with stat info (0), so its stat info was skipped',
			'FireGraft unit 0 uses button set 7, which does not exist, so it was set to no button set',
			'FireGraft unit 9 is past the last unit with buttons (1) and was skipped',
		])
		self.assertEqual(graft.button_sets, [[Button.unpack(MOVE)], [], [Button.unpack(STOP)]])
		self.assertEqual(graft.units, [UnitButtons(None, 5), UnitButtons(2)])
		self.assertEqual(graft.stat_info, [StatInfo(0, 1, 0)])
