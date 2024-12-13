
from ...Utilities.CodeHandlers import CodeType
from ...Utilities.CodeHandlers import CodeCommand
from ...Utilities.CodeHandlers import LanguageDefinition
from ...Utilities import Struct
from ...Utilities.PyMSError import PyMSError

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
		self.assertTrue('Command `b` is invalid as language plugin `B` is not avaialable' in str(error_context.exception))
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
		self.assertTrue('Command `b` is invalid as language plugin `B` is not avaialable' in str(error_context.exception))
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
		self.assertTrue('Type `word` is invalid as language plugin `B` is not avaialable' in str(error_context.exception))
		self.assertTrue('Manually disabled' in str(error_context.exception))
