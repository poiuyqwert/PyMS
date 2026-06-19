
from ...Utilities.UIKit.FileType import FileType

import unittest
from unittest import mock

IS_MAC = 'PyMS.Utilities.UIKit.FileType.is_mac'


class Test_FileType_new(unittest.TestCase):
	def test_bare_extension_gets_wildcard_dot_prefix(self) -> None:
		self.assertEqual(FileType('Foo', 'txt').extensions, '*.txt')

	def test_leading_dot_extension_gets_wildcard_prefix(self) -> None:
		self.assertEqual(FileType('Foo', '.txt').extensions, '*.txt')

	def test_already_wildcarded_extension_unchanged(self) -> None:
		self.assertEqual(FileType('Foo', '*.txt').extensions, '*.txt')

	def test_bare_wildcard_unchanged(self) -> None:
		self.assertEqual(FileType('Foo', '*').extensions, '*')

	def test_multiple_extensions_space_joined(self) -> None:
		self.assertEqual(FileType('M', 'mpq', 'exe').extensions, '*.mpq *.exe')

	def test_name_on_mac_is_unchanged(self) -> None:
		with mock.patch(IS_MAC, return_value=True):
			self.assertEqual(FileType('Foo', 'txt').name, 'Foo')

	def test_name_off_mac_appends_extension(self) -> None:
		with mock.patch(IS_MAC, return_value=False):
			self.assertEqual(FileType('Foo', 'txt').name, 'Foo (.txt)')

	def test_name_off_mac_appends_all_extensions(self) -> None:
		with mock.patch(IS_MAC, return_value=False):
			self.assertEqual(FileType('M', 'mpq', 'exe').name, 'M (.mpq, .exe)')


class Test_default_extension(unittest.TestCase):
	def test_single_extension(self) -> None:
		self.assertEqual(FileType.default_extension([FileType.txt()]), 'txt')

	def test_uses_first_filetype(self) -> None:
		self.assertEqual(FileType.default_extension([FileType.bmp(), FileType.txt()]), 'bmp')

	def test_multiple_extensions_uses_first(self) -> None:
		self.assertEqual(FileType.default_extension([FileType('M', 'mpq', 'exe')]), 'mpq')

	def test_empty_list_returns_none(self) -> None:
		self.assertIsNone(FileType.default_extension([]))


class Test_include_all_files(unittest.TestCase):
	def test_appends_all_files_when_absent(self) -> None:
		result = FileType.include_all_files([FileType.txt()])
		self.assertEqual(result, [FileType.txt(), FileType.all_files()])

	def test_no_duplicate_when_present(self) -> None:
		result = FileType.include_all_files([FileType.all_files()])
		self.assertEqual(result, [FileType.all_files()])

	def test_empty_list_gets_all_files(self) -> None:
		self.assertEqual(FileType.include_all_files([]), [FileType.all_files()])

	def test_existing_wildcard_of_other_name_counts_as_present(self) -> None:
		# Any wildcard entry already matches every file, so a differently-named
		# wildcard satisfies "all files" and nothing extra is appended.
		existing = [FileType('Everything', '*')]
		self.assertEqual(FileType.include_all_files(existing), existing)


class Test_extensions_tuple(unittest.TestCase):
	def test_single(self) -> None:
		self.assertEqual(FileType('Foo', 'txt').extensions_tuple, ('*.txt',))

	def test_multiple(self) -> None:
		self.assertEqual(FileType('M', 'mpq', 'exe').extensions_tuple, ('*.mpq', '*.exe'))


class Test_eq(unittest.TestCase):
	def test_same_name_and_extension(self) -> None:
		self.assertEqual(FileType('A', 'txt'), FileType('A', 'txt'))

	def test_different_extension_not_equal(self) -> None:
		self.assertNotEqual(FileType('A', 'txt'), FileType('A', 'bmp'))

	def test_same_extension_different_name_not_equal(self) -> None:
		self.assertNotEqual(FileType('A', 'txt'), FileType('B', 'txt'))

	def test_wildcard_with_different_name_not_equal(self) -> None:
		self.assertNotEqual(FileType('A', '*'), FileType('B', '*'))

	def test_not_equal_to_non_filetype(self) -> None:
		self.assertNotEqual(FileType('A', 'txt'), 'not a filetype')


class Test_hash(unittest.TestCase):
	def test_equal_filetypes_hash_equal(self) -> None:
		self.assertEqual(hash(FileType('A', 'txt')), hash(FileType('A', 'txt')))

	def test_wildcards_with_different_names_are_distinct_in_a_set(self) -> None:
		# Equality requires both name and extensions to match, so wildcards with
		# different names are distinct members.
		self.assertEqual(len({FileType('A', '*'), FileType('B', '*')}), 2)

	def test_usable_in_a_set(self) -> None:
		types = {FileType('A', 'txt'), FileType('A', 'txt'), FileType('B', 'bmp')}
		self.assertEqual(len(types), 2)
