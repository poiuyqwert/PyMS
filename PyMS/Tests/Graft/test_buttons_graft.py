from .utils import button_bytes, buttons_file, decompile_buttons, compile_buttons, parse_context
from ...FileFormats.Graft import ButtonsGraft, Button, StatInfo, ButtonCard, UnitsGraft, FGP, FGPUnit
from ...FileFormats.Graft.CodeHandlers import ButtonsLanguage, ButtonCodeCommands
from ...Utilities.DataContext import DataContext
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
		self.assertEqual(len(graft.button_cards), 250)
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
		self.assertIn('button_card 0 {\t# Terran Marine\n\tuse_button_set 68\t# Marine/Firebat + Heroes\n\tconnected_unit None\n}\n', text)
		self.assertIn("unit_stat_info 0 {\t# Terran Marine\n\tunit_unused 'Terran Marine'\n\tchanged_unit\n\tdraw_unit\n}\n", text)

	def test_vanilla_stat_info_units(self) -> None:
		graft = ButtonsGraft()
		graft.new()
		text = decompile_buttons(graft)
		# The vanilla game leaves the unused unit as 0 for unused units
		self.assertIn("unit_stat_info 91 {\t# Cargo Ship (Unused) (Unused)\n\tunit_unused 'Terran Marine'\n\tchanged_never\n\tdraw_none\n}\n", text)
		self.assertIn("unit_stat_info 120 {\t# Terran Machine Shop\n\tunit_unused 'Terran Machine Shop'\n\tchanged_building\n\tdraw_building\n}\n", text)

	def test_vanilla_function_params(self) -> None:
		graft = ButtonsGraft()
		graft.new()
		text = decompile_buttons(graft)
		self.assertIn('\t\tcancel_train last\n', text)
		self.assertIn('\t\tshow_button_set 238\t# Zerg Basic Buildings\n', text)
		self.assertIn('\t\thas_no_exit\n', text)
		self.assertIn('\t\tcan_morph_lurker\n', text)

	def test_vanilla_special_button_card_headers(self) -> None:
		graft = ButtonsGraft()
		graft.new()
		self.assertIn('button_card 238 {\t# Zerg Basic Buildings\n\tuse_button_set 19\t# Basic Zerg Buildings\n', decompile_buttons(graft))

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
		graft.button_cards = []
		graft.stat_info = []
		text = decompile_buttons(graft)
		self.assertEqual(compile_buttons(text).button_sets, [[button]])
		return text

	def test_function_parameters_are_named(self) -> None:
		text = self._round_trip(Button.unpack(TRAIN_MARINE))
		self.assertIn("\t\tcan_create 'Terran Marine'\n\t\ttrain 'Terran Marine'\n", text)

	def test_values_of_functions_without_params_are_not_written(self) -> None:
		graft = ButtonsGraft()
		graft.button_sets = [[Button(condition=3, condition_param=254, action=9, action_param=0x10)]]
		graft.button_cards = []
		graft.stat_info = []
		text = decompile_buttons(graft)
		self.assertIn('\t\talways\n\t\tmove\n', text)
		self.assertEqual(compile_buttons(text).button_sets, [[Button(condition=3, action=9)]])

	def test_every_function_round_trips(self) -> None:
		for commands, field in ((ButtonCodeCommands.condition_commands, 'condition'), (ButtonCodeCommands.action_commands, 'action')):
			for index, cmd_def in enumerate(commands):
				with self.subTest(name=cmd_def.name):
					self.assertEqual(cmd_def.function_index, index)
					# The value 0 is valid for every parameter (and is the only value for functions without one)
					param = 1 if cmd_def.param_types else 0
					self.assertIn(f'\t\t{cmd_def.name}', self._round_trip(Button(**{field: index, f'{field}_param': param})))

	def test_queue_slots(self) -> None:
		for value, text in ((0, '1'), (4, '5'), (0xFE, 'last')):
			with self.subTest(text=text):
				self.assertIn(f'\t\tcancel_train {text}\n', self._round_trip(Button(condition=10, action=4, action_param=value)))

	def test_special_button_cards(self) -> None:
		self.assertIn('\t\tshow_button_set 228\t# Blank\n', self._round_trip(Button(action=59, action_param=228)))

	def test_button_cards_and_units_are_separate_blocks(self) -> None:
		graft = ButtonsGraft()
		graft.button_cards = [ButtonCard(None, None)]
		graft.stat_info = [StatInfo(0, 1, 0), StatInfo(5, 1, 0)]
		text = decompile_buttons(graft)
		self.assertEqual(text, "button_card 0 {\t# Terran Marine\n\tuse_button_set None\n\tconnected_unit None\n}\n\nunit_stat_info 0 {\t# Terran Marine\n\tunit_unused 'Terran Marine'\n\tchanged_unit\n\tdraw_unit\n}\n\nunit_stat_info 1 {\t# Terran Ghost\n\tunit_unused 'Terran Siege Tank<0>Tank Mode'\n\tchanged_unit\n\tdraw_unit\n}\n\n")
		recompiled = compile_buttons(text)
		self.assertEqual((recompiled.button_cards, recompiled.stat_info), (graft.button_cards, graft.stat_info))

class Test_Load(unittest.TestCase):
	def test_shared_button_sets(self) -> None:
		data = buttons_file([MOVE, STOP, TRAIN_MARINE], [(2, 0, 0xFFFF, 0), (1, 2, 5, 0), (2, 0, 0xFFFF, 0), (0, 0, 0xFFFF, 0)], [(0, 1, 0), (7, 2, 1)])
		graft = _load(data)
		self.assertEqual(graft.button_sets, [[Button.unpack(MOVE), Button.unpack(STOP)], [Button.unpack(TRAIN_MARINE)]])
		self.assertEqual(graft.button_cards, [ButtonCard(0), ButtonCard(1, 5), ButtonCard(0), ButtonCard()])
		self.assertEqual(graft.stat_info, [StatInfo(0, 1, 0), StatInfo(7, 2, 1)])
		self.assertEqual(IO.output_to_bytes(graft.save), data)

	def test_unreferenced_buttons_are_kept(self) -> None:
		data = buttons_file([MOVE, STOP, TRAIN_MARINE], [(1, 1, 0xFFFF, 0)], [])
		graft = _load(data)
		self.assertEqual(len(graft.button_sets), 3)
		self.assertEqual(graft.button_cards, [ButtonCard(1)])
		self.assertEqual(IO.output_to_bytes(graft.save), data)

	def test_padding_is_discarded(self) -> None:
		graft = ButtonsGraft()
		warnings = graft.load(buttons_file([MOVE], [(1, 0, 0xFFFF, 0x1234), (1, 0, 0xFFFF, 0), (1, 0, 5, 1)], []))
		self.assertEqual([warning.warning for warning in warnings], ['Button card(s) 0, 2 have unused data after their connected unit, it will be discarded'])
		self.assertEqual(graft.button_cards, [ButtonCard(0), ButtonCard(0), ButtonCard(0, 5)])
		self.assertEqual(IO.output_to_bytes(graft.save), buttons_file([MOVE], [(1, 0, 0xFFFF, 0), (1, 0, 0xFFFF, 0), (1, 0, 5, 0)], []))

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

	def test_unknown_status_function_fails(self) -> None:
		graft = _load(buttons_file([MOVE], [(1, 0, 0xFFFF, 0)], [(0, 1, 0)]))
		with self.assertRaises(PyMSError) as cm:
			graft.load(buttons_file([MOVE], [(1, 0, 0xFFFF, 0)], [(0, 1, 0), (1, 50, 0)]))
		self.assertIn('Unit 1 uses unknown status function 50', str(cm.exception))
		self.assertEqual(graft.stat_info, [StatInfo(0, 1, 0)])

	def test_unknown_display_function_fails(self) -> None:
		graft = ButtonsGraft()
		with self.assertRaises(PyMSError) as cm:
			graft.load(buttons_file([MOVE], [(1, 0, 0xFFFF, 0)], [(0, 1, 60)]))
		self.assertIn('Unit 0 uses unknown display function 60', str(cm.exception))

	def test_unknown_condition_fails(self) -> None:
		graft = _load(buttons_file([MOVE], [(1, 0, 0xFFFF, 0)], []))
		with self.assertRaises(PyMSError) as cm:
			graft.load(buttons_file([STOP, button_bytes(1, 0, 500, 9)], [(2, 0, 0xFFFF, 0)], []))
		self.assertIn('Button set 0 uses unknown button condition 500', str(cm.exception))
		self.assertEqual(graft.button_sets, [[Button.unpack(MOVE)]])

	def test_unknown_action_fails(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_load(buttons_file([button_bytes(1, 0, 3, 600)], [(1, 0, 0xFFFF, 0)], []))
		self.assertIn('Button set 0 uses unknown button action 600', str(cm.exception))

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
		self.assertIn('too small for its 1 buttons, 1 button cards, and 0 stat infos', str(cm.exception))

	def test_button_card_buttons_past_the_end(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			ButtonsGraft().load(buttons_file([MOVE], [(2, 0, 0xFFFF, 0)], []))
		self.assertIn('button card 0 uses buttons 0 to 1 but there are only 1 buttons', str(cm.exception))

	def test_failed_load_keeps_existing_data(self) -> None:
		graft = _load(buttons_file([MOVE], [(1, 0, 0xFFFF, 0)], []))
		with self.assertRaises(PyMSError):
			graft.load(b'')
		self.assertEqual(graft.button_cards, [ButtonCard(0)])

class Test_Save(unittest.TestCase):
	def test_empty_button_set_saves_as_no_buttons(self) -> None:
		graft = ButtonsGraft()
		graft.button_sets = [[]]
		graft.button_cards = [ButtonCard(0, 3)]
		graft.stat_info = []
		self.assertEqual(IO.output_to_bytes(graft.save), buttons_file([], [(0, 0, 3, 0)], []))

	def test_missing_button_set_fails(self) -> None:
		graft = ButtonsGraft()
		graft.button_cards = [ButtonCard(4)]
		with self.assertRaises(PyMSError) as cm:
			IO.output_to_bytes(graft.save)
		self.assertIn('Button card 0 uses button set 4, which does not exist', str(cm.exception))

class Test_Editing(unittest.TestCase):
	def test_remove_button_set_renumbers_references(self) -> None:
		graft = ButtonsGraft()
		graft.button_sets = [[Button.unpack(MOVE)], [Button.unpack(STOP)], [Button.unpack(TRAIN_MARINE)]]
		graft.button_cards = [ButtonCard(2), ButtonCard(0)]
		self.assertEqual(graft.remove_button_set(1), [Button.unpack(STOP)])
		self.assertEqual(graft.button_cards, [ButtonCard(1), ButtonCard(0)])

	def test_remove_used_button_set_fails(self) -> None:
		graft = ButtonsGraft()
		graft.button_sets = [[Button.unpack(MOVE)]]
		graft.button_cards = [ButtonCard(0), ButtonCard(0)]
		with self.assertRaises(PyMSError) as cm:
			graft.remove_button_set(0)
		self.assertIn("can't be removed because it is used by button card(s) 0, 1", str(cm.exception))

	def test_set_counts(self) -> None:
		graft = ButtonsGraft()
		graft.set_button_card_count(300)
		graft.set_stat_count(230)
		self.assertEqual(len(graft.button_cards), 300)
		self.assertEqual(graft.stat_info[229], StatInfo(229))
		graft.set_button_card_count(10)
		graft.set_stat_count(5)
		self.assertEqual((len(graft.button_cards), len(graft.stat_info)), (10, 5))

def _button(body: str, position: int = 1) -> str:
	return f'\tbutton {position} {{\n' + ''.join(f'\t\t{line}\n' for line in body.split('\n')) + '\t}\n'

MOVE_BODY = 'icon 0\nalways\nmove\nenabled_str 0\ndisabled_str 0'

class Test_Compile(unittest.TestCase):
	def test_names_and_defaults(self) -> None:
		graft = compile_buttons(f"""button_set 0 {{
{_button("icon 0\ncan_create 'Terran Marine'\ntrain 'Terran Marine'\nenabled_str 1\ndisabled_str 0")}{_button('icon 0x10\nalways\nupgrade "Terran Infantry Armor"\nenabled_str 2\ndisabled_str 3', 2)}}}
button_set 2 {{
}}
button_card 1 {{
	use_button_set 0
	connected_unit 'Terran Ghost'
}}

button_card 3 {{
}}
unit_stat_info 0 {{
	changed_unit
	draw_unit
}}
unit_stat_info 1 {{
	draw_building
	unit_unused 'Terran Goliath'
	changed_never
}}
""")
		self.assertEqual(graft.button_sets, [[Button(position=1, condition=4, action=3, enabled_string=1), Button(position=2, icon=16, condition=3, action=26, enabled_string=2, disabled_string=3)], [], []])
		self.assertEqual(graft.button_cards, [ButtonCard(), ButtonCard(0, 1), ButtonCard(), ButtonCard()])
		self.assertEqual(graft.stat_info, [StatInfo(0, 1, 0), StatInfo(3, 0, 1)])

	def test_buttons_can_share_a_position(self) -> None:
		graft = compile_buttons('button_set 0 {\n' + _button(MOVE_BODY) + _button(MOVE_BODY) + '}\n')
		self.assertEqual(graft.button_sets, [[Button(position=1, condition=3, action=9)] * 2])

	def test_queue_slot_params(self) -> None:
		for text, value in (('1', 0), ('5', 4), ('last', 0xFE)):
			with self.subTest(text=text):
				graft = compile_buttons('button_set 0 {\n' + _button(f'icon 0\nis_training\ncancel_train {text}\nenabled_str 0\ndisabled_str 0') + '}\n')
				self.assertEqual(graft.button_sets, [[Button(position=1, condition=10, action=4, action_param=value)]])

	def test_button_card_accepts_unit_names(self) -> None:
		graft = compile_buttons('button_set 0 {\n' + _button("icon 0\nalways\nshow_button_set 'Terran SCV'\nenabled_str 0\ndisabled_str 0") + '}\n')
		self.assertEqual(graft.button_sets, [[Button(position=1, condition=3, action=59, action_param=7)]])

	def assertCompileError(self, code: str, message: str, line: int | None = None) -> None:
		with self.assertRaises(PyMSError) as cm:
			compile_buttons(code)
		self.assertIn(message, str(cm.exception))
		if line is not None:
			self.assertEqual(cm.exception.line, line)

	def test_stat_info_unit_allows_32_bit_values(self) -> None:
		graft = ButtonsGraft()
		graft.button_cards = []
		graft.stat_info = [StatInfo(0x10000, 1, 0)]
		text = decompile_buttons(graft)
		self.assertIn('\tunit_unused 65536\n', text)
		self.assertEqual(compile_buttons(text).stat_info, graft.stat_info)

	def test_missing_status_function(self) -> None:
		self.assertCompileError('unit_stat_info 0 {\n\tunit_unused 0\n\tdraw_unit\n}\n', "Unit stat info 0 is missing 'status_function'", 4)

	def test_missing_display_function(self) -> None:
		self.assertCompileError('unit_stat_info 0 {\n\tchanged_unit\n}\n', "Unit stat info 0 is missing 'display_function'", 3)

	def test_duplicate_stat_function(self) -> None:
		self.assertCompileError('unit_stat_info 0 {\n\tchanged_unit\n\tchanged_building\n}\n', "Duplicate unit stat info command 'changed_building'", 3)

	def test_stat_functions_are_written_by_name(self) -> None:
		self.assertCompileError('unit_stat_info 0 {\n\t1\n}\n', "Expected a unit stat info command, got '1' instead", 2)

	def test_stat_function_rejects_a_param(self) -> None:
		self.assertCompileError('unit_stat_info 0 {\n\tchanged_unit 1\n}\n', "Unexpected token '1' (expected end of line or file)", 2)

	def test_missing_unit(self) -> None:
		self.assertCompileError('unit_stat_info 1 {\n\tchanged_never\n\tdraw_unit\n}\n', 'Unit stat info 0 is not defined (every unit up to the last `unit_stat_info` needs one)')

	def test_undefined_button_set(self) -> None:
		self.assertCompileError('button_set 0 {\n}\nbutton_card 0 {\n\tuse_button_set 1\n}\n', 'Button card 0 uses button set 1, which is not defined', 3)

	def test_duplicate_property(self) -> None:
		self.assertCompileError('button_card 0 {\n\tuse_button_set None\n\tuse_button_set None\n}\n', "Duplicate button card command 'use_button_set'", 3)

	def test_duplicate_choice(self) -> None:
		self.assertCompileError('button_set 0 {\n' + _button('icon 0\nalways\nis_player_nuke_ready') + '}\n', "Duplicate button command 'is_player_nuke_ready'", 5)

	def test_missing_field(self) -> None:
		self.assertCompileError('button_set 0 {\n' + _button('always\nmove\nenabled_str 0\ndisabled_str 0') + '}\n', "Button 1 is missing 'icon'", 7)

	def test_duplicate_header(self) -> None:
		self.assertCompileError('button_set 0 {\n}\nbutton_set 0 {\n}\n', 'Button set 0 is already defined on line 1', 3)

	def test_unknown_function(self) -> None:
		self.assertCompileError('button_set 0 {\n' + _button('icon 0\nis_sometimes') + '}\n', "Unknown button command 'is_sometimes'", 4)

	def test_function_without_param_rejects_a_param(self) -> None:
		self.assertCompileError('button_set 0 {\n' + _button("icon 0\nalways 'Terran Marine'") + '}\n', "Unexpected token ''Terran Marine'' (expected end of line or file)", 4)

	def test_function_param_is_required(self) -> None:
		self.assertCompileError('button_set 0 {\n' + _button('icon 0\nalways\ntrain') + '}\n', 'for `unit`', 5)

	def test_invalid_queue_slots(self) -> None:
		for text in ('0', '6', 'first'):
			with self.subTest(text=text):
				self.assertCompileError('button_set 0 {\n' + _button(f'icon 0\nis_training\ncancel_train {text}') + '}\n', f'Invalid value `{text}` for `queue_slot` (expected 1 to 5, or `last`)', 5)

	def test_button_card_has_no_button_set_or_padding_commands(self) -> None:
		self.assertCompileError('button_card 0 {\n\tbutton_set 0\n}\n', "Unknown button card command 'button_set'", 2)
		self.assertCompileError('button_card 0 {\n\tpadding 7\n}\n', "Unknown button card command 'padding'", 2)

	def test_unknown_unit_command(self) -> None:
		self.assertCompileError('button_card 0 {\n\ticon 0\n}\n', "Unknown button card command 'icon'", 2)
		self.assertCompileError('unit_stat_info 0 {\n\tbutton_set 0\n}\n', "Unknown unit stat info command 'button_set'", 2)

	def test_parens_and_flat_forms(self) -> None:
		graft = compile_buttons("button_set 0 {\n" + _button("icon(0)\nalways()\ntrain('Terran Marine')\nenabled_str 0\ndisabled_str 0") + "}\nbutton_card 0 {\n\tuse_button_set(0)\n\tconnected_unit(None)\n}\nunit_stat_info 0 {\n\tunit_unused(7)\n\tchanged_unit()\n\tdraw_unit()\n}\n")
		self.assertEqual(graft.button_sets, [[Button(position=1, condition=3, action=3)]])
		self.assertEqual(graft.button_cards, [ButtonCard(0)])
		self.assertEqual(graft.stat_info, [StatInfo(7, 1, 0)])

	def test_too_many_parameters(self) -> None:
		self.assertCompileError('button_card 0 {\n\tuse_button_set 0 1\n}\n', 'expected end of line or file', 2)

	def test_unclosed_block(self) -> None:
		self.assertCompileError('button_set 0 {\n' + _button(MOVE_BODY), "Expected a '}' to end the button set, got end of file instead")

	def test_text_after_block(self) -> None:
		self.assertCompileError('button_card 0 {\n} button_card 1 {\n}\n', "Unexpected token 'button_card' (expected end of line or file)", 2)

	def test_requires_buttons_language(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			ButtonsGraft.compile(parse_context('unit_stat_info 0 {\n}\n', language=UnitsGraft.LANGUAGE()))
		self.assertIn('ButtonsGraft must be compiled with a parse context using `ButtonsLanguage`', str(cm.exception))

	def test_language_has_the_commands(self) -> None:
		language = ButtonsLanguage()
		for name in ('icon', 'always', 'move', 'enabled_str', 'disabled_str', 'use_button_set', 'connected_unit', 'unit_unused', 'changed_never', 'draw_none'):
			with self.subTest(name=name):
				self.assertIsNotNone(language.lookup_command(name, LanguageContext()))

	def test_command_outside_block(self) -> None:
		self.assertCompileError('icon 0\n', "Unexpected token 'icon' (expected 'button_set' or 'button_card' or 'unit_stat_info')", 1)

	def test_block_needs_braces(self) -> None:
		self.assertCompileError('button_set 0\n', "Expected a '{' to start the button set, got", 1)

class Test_ImportFGP(unittest.TestCase):
	def test_unknown_function_fails(self) -> None:
		graft = ButtonsGraft()
		graft.button_sets = [[Button.unpack(MOVE)]]
		graft.button_cards = [ButtonCard(0)]
		graft.stat_info = []
		fgp = FGP()
		fgp.button_sets = {0: [Button.unpack(STOP)], 1: [Button(condition=3, action=600)]}
		fgp.units = [FGPUnit(0, None, 0xFFFF, None)]
		with self.assertRaises(PyMSError) as cm:
			graft.import_fgp(fgp)
		self.assertIn('Button set 1 uses unknown button action 600', str(cm.exception))
		self.assertEqual(graft.button_sets, [[Button.unpack(MOVE)]])
		self.assertEqual(graft.button_cards, [ButtonCard(0)])

	def test_unknown_stat_function_fails(self) -> None:
		graft = ButtonsGraft()
		graft.button_sets = [[Button.unpack(MOVE)]]
		graft.button_cards = [ButtonCard(0)]
		graft.stat_info = [StatInfo(0, 1, 0)]
		fgp = FGP()
		fgp.button_sets = {0: [Button.unpack(STOP)]}
		fgp.units = [FGPUnit(0, 0, 0xFFFF, StatInfo(0, 1, 9))]
		with self.assertRaises(PyMSError) as cm:
			graft.import_fgp(fgp)
		self.assertIn('Unit 0 uses unknown display function 9', str(cm.exception))
		self.assertEqual(graft.button_sets, [[Button.unpack(MOVE)]])
		self.assertEqual(graft.stat_info, [StatInfo(0, 1, 0)])

	def test_overlays_buttons(self) -> None:
		graft = ButtonsGraft()
		graft.button_sets = [[Button.unpack(MOVE)]]
		graft.button_cards = [ButtonCard(0), ButtonCard(0)]
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
			'FireGraft unit 9 is past the last button card (1) and was skipped',
		])
		self.assertEqual(graft.button_sets, [[Button.unpack(MOVE)], [], [Button.unpack(STOP)]])
		self.assertEqual(graft.button_cards, [ButtonCard(None, 5), ButtonCard(2)])
		self.assertEqual(graft.stat_info, [StatInfo(0, 1, 0)])
