
from ...Utilities.CodeHandlers import CodeType
from ...Utilities.CodeHandlers import CodeCommand
from ...Utilities.CodeHandlers import LanguageDefinition
from ...Utilities.PyMSError import PyMSError
from ...Utilities import Struct

import unittest


ByteType = CodeType.IntCodeType('byte', 'byte', Struct.l_u8)
WordType = CodeType.IntCodeType('word', 'word', Struct.l_u16)

ACommand = CodeCommand.CodeCommandDefinition('a', 'a', 0, [ByteType])
BCommand = CodeCommand.CodeCommandDefinition('b', 'b', 1, [WordType])

CorePlugin = LanguageDefinition.LanguagePlugin(LanguageDefinition.LanguagePlugin.CORE_ID, [
		ACommand
	], [
		ByteType
	])
BPluginID = 'B'
BPlugin = LanguageDefinition.LanguagePlugin(BPluginID, [
		BCommand
	], [
		WordType
	])
Language = LanguageDefinition.LanguageDefinition([
	CorePlugin,
	BPlugin,
])


class Test_LanguagePlugin(unittest.TestCase):
	def test_duplicate_command_id_raises(self) -> None:
		a = CodeCommand.CodeCommandDefinition('a', 'a', 0, [])
		b = CodeCommand.CodeCommandDefinition('b', 'b', 0, [])
		with self.assertRaises(PyMSError):
			LanguageDefinition.LanguagePlugin('core', [a, b], [])

	def test_duplicate_command_name_raises(self) -> None:
		a = CodeCommand.CodeCommandDefinition('dup', 'a', 0, [])
		b = CodeCommand.CodeCommandDefinition('dup', 'b', 1, [])
		with self.assertRaises(PyMSError):
			LanguageDefinition.LanguagePlugin('core', [a, b], [])

	def test_duplicate_type_name_raises(self) -> None:
		t1 = CodeType.IntCodeType('byte', 'a', Struct.l_u8)
		t2 = CodeType.IntCodeType('byte', 'b', Struct.l_u16)
		with self.assertRaises(PyMSError):
			LanguageDefinition.LanguagePlugin('core', [], [t1, t2])

	def test_command_with_no_id_is_name_only(self) -> None:
		virtual = CodeCommand.CodeCommandDefinition('virtual', 'v', None, [])
		plugin = LanguageDefinition.LanguagePlugin('core', [virtual], [])
		self.assertIs(plugin.lookup_command('virtual'), virtual)
		self.assertIsNone(plugin.lookup_command(0))


class Test_LanguageDefinition(unittest.TestCase):
	def test_requires_core_plugin(self) -> None:
		non_core = LanguageDefinition.LanguagePlugin('extra', [], [])
		with self.assertRaises(PyMSError):
			LanguageDefinition.LanguageDefinition([non_core])

	def test_ambiguous_command_across_available_plugins_is_reported(self) -> None:
		# Two available plugins defining the same command name is a genuine
		# collision and should be surfaced, not silently resolved to whichever
		# plugin happens to be registered last.
		core_cmd = CodeCommand.CodeCommandDefinition('shared', 'core', 0, [])
		extra_cmd = CodeCommand.CodeCommandDefinition('shared', 'extra', 1, [])
		language = LanguageDefinition.LanguageDefinition([
			LanguageDefinition.LanguagePlugin(LanguageDefinition.LanguagePlugin.CORE_ID, [core_cmd], []),
			LanguageDefinition.LanguagePlugin('extra', [extra_cmd], []),
		])
		context = LanguageDefinition.LanguageContext()
		with self.assertRaises(PyMSError):
			language.lookup_command('shared', context)


class Test_Language_Comamnd_Bytecode(unittest.TestCase):
	def test_core_command_success(self) -> None:
		language_context = LanguageDefinition.LanguageContext()
		cmd_def = Language.lookup_command(0, language_context)
		self.assertEqual(cmd_def, ACommand)
		self.assertEqual(language_context.active_plugins(False), set([LanguageDefinition.LanguagePlugin.CORE_ID]))
		self.assertTrue('Command `a` referenced' in language_context.get_reasons(LanguageDefinition.LanguagePlugin.CORE_ID))

	def test_plugin_command_success(self) -> None:
		language_context = LanguageDefinition.LanguageContext()
		cmd_def = Language.lookup_command(1, language_context)
		self.assertEqual(cmd_def, BCommand)
		self.assertEqual(language_context.active_plugins(False), set([LanguageDefinition.LanguagePlugin.CORE_ID, BPluginID]))
		self.assertTrue('Command `b` referenced' in language_context.get_reasons(BPluginID))

	def test_unknown_command(self) -> None:
		language_context = LanguageDefinition.LanguageContext()
		cmd_def = Language.lookup_command(2, language_context)
		self.assertIsNone(cmd_def)
		self.assertEqual(language_context.active_plugins(False), set([LanguageDefinition.LanguagePlugin.CORE_ID]))

	def test_plugin_command_unavailable(self) -> None:
		language_context = LanguageDefinition.LanguageContext()
		language_context.set_status(BPluginID, LanguageDefinition.PluginStatus.unavailable, 'Manually disabled')
		with self.assertRaises(PyMSError) as error_context:
			Language.lookup_command(1, language_context)
		self.assertTrue('Command `b` is invalid as language plugin `B` is not available' in str(error_context.exception))
		self.assertTrue('Manually disabled' in str(error_context.exception))


class Test_Language_Command_Source(unittest.TestCase):
	def test_core_command_success(self) -> None:
		language_context = LanguageDefinition.LanguageContext()
		cmd_def = Language.lookup_command('a', language_context)
		self.assertEqual(cmd_def, ACommand)
		self.assertEqual(language_context.active_plugins(False), set([LanguageDefinition.LanguagePlugin.CORE_ID]))
		self.assertTrue('Command `a` referenced' in language_context.get_reasons(LanguageDefinition.LanguagePlugin.CORE_ID))

	def test_plugin_command_success(self) -> None:
		language_context = LanguageDefinition.LanguageContext()
		cmd_def = Language.lookup_command('b', language_context)
		self.assertEqual(cmd_def, BCommand)
		self.assertEqual(language_context.active_plugins(False), set([LanguageDefinition.LanguagePlugin.CORE_ID, BPluginID]))
		self.assertTrue('Command `b` referenced' in language_context.get_reasons(BPluginID))

	def test_unknown_command(self) -> None:
		language_context = LanguageDefinition.LanguageContext()
		cmd_def = Language.lookup_command('c', language_context)
		self.assertIsNone(cmd_def)
		self.assertEqual(language_context.active_plugins(False), set([LanguageDefinition.LanguagePlugin.CORE_ID]))

	def test_plugin_command_unavailable(self) -> None:
		language_context = LanguageDefinition.LanguageContext()
		language_context.set_status(BPluginID, LanguageDefinition.PluginStatus.unavailable, 'Manually disabled')
		with self.assertRaises(PyMSError) as error_context:
			Language.lookup_command('b', language_context)
		self.assertTrue('Command `b` is invalid as language plugin `B` is not available' in str(error_context.exception))
		self.assertTrue('Manually disabled' in str(error_context.exception))


class Test_Language_Type_Source(unittest.TestCase):
	def test_core_type_success(self) -> None:
		language_context = LanguageDefinition.LanguageContext()
		code_type = Language.lookup_type('byte', language_context)
		self.assertEqual(code_type, ByteType)
		self.assertEqual(language_context.active_plugins(False), set([LanguageDefinition.LanguagePlugin.CORE_ID]))
		self.assertTrue('Type `byte` referenced' in language_context.get_reasons(LanguageDefinition.LanguagePlugin.CORE_ID))

	def test_plugin_type_success(self) -> None:
		language_context = LanguageDefinition.LanguageContext()
		code_type = Language.lookup_type('word', language_context)
		self.assertEqual(code_type, WordType)
		self.assertEqual(language_context.active_plugins(False), set([LanguageDefinition.LanguagePlugin.CORE_ID, BPluginID]))
		self.assertTrue('Type `word` referenced' in language_context.get_reasons(BPluginID))

	def test_unknown_type(self) -> None:
		language_context = LanguageDefinition.LanguageContext()
		code_type = Language.lookup_type('long', language_context)
		self.assertIsNone(code_type)
		self.assertEqual(language_context.active_plugins(False), set([LanguageDefinition.LanguagePlugin.CORE_ID]))

	def test_plugin_type_unavailable(self) -> None:
		language_context = LanguageDefinition.LanguageContext()
		language_context.set_status(BPluginID, LanguageDefinition.PluginStatus.unavailable, 'Manually disabled')
		with self.assertRaises(PyMSError) as error_context:
			Language.lookup_type('word', language_context)
		self.assertTrue('Type `word` is invalid as language plugin `B` is not available' in str(error_context.exception))
		self.assertTrue('Manually disabled' in str(error_context.exception))


class Test_LanguageContext(unittest.TestCase):
	def test_core_is_active_by_default(self) -> None:
		context = LanguageDefinition.LanguageContext()
		self.assertEqual(context.get_status(LanguageDefinition.LanguagePlugin.CORE_ID), LanguageDefinition.PluginStatus.in_use)

	def test_unknown_plugin_status(self) -> None:
		context = LanguageDefinition.LanguageContext()
		self.assertEqual(context.get_status('mystery'), LanguageDefinition.PluginStatus.unknown)

	def test_setting_conflicting_status_raises(self) -> None:
		context = LanguageDefinition.LanguageContext()
		context.set_status('plugin', LanguageDefinition.PluginStatus.in_use, 'used')
		with self.assertRaises(PyMSError):
			context.set_status('plugin', LanguageDefinition.PluginStatus.unavailable, 'now off')

	def test_active_plugins_excludes_core_by_default(self) -> None:
		context = LanguageDefinition.LanguageContext()
		context.set_status('plugin', LanguageDefinition.PluginStatus.in_use, 'used')
		self.assertEqual(context.active_plugins(), {'plugin'})

	def test_active_plugins_can_include_core(self) -> None:
		context = LanguageDefinition.LanguageContext()
		self.assertIn(LanguageDefinition.LanguagePlugin.CORE_ID, context.active_plugins(False))


if __name__ == '__main__':
	unittest.main()
