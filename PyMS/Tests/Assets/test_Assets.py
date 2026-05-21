
from ...Utilities import Assets

import os
import json
import unittest


class Test_paths(unittest.TestCase):
	def test_image_path_joins_images_dir(self) -> None:
		self.assertEqual(Assets.image_path('foo.gif'), os.path.join(Assets.images_dir, 'foo.gif'))

	def test_data_file_path_joins_data_dir(self) -> None:
		self.assertEqual(Assets.data_file_path('foo.txt'), os.path.join(Assets.data_dir, 'foo.txt'))

	def test_palette_file_path_joins_palettes_dir(self) -> None:
		self.assertEqual(Assets.palette_file_path('default.pal'), os.path.join(Assets.palettes_dir, 'default.pal'))

	def test_settings_file_path_appends_txt(self) -> None:
		self.assertEqual(Assets.settings_file_path('PyAI'), os.path.join(Assets.settings_dir, f'PyAI{os.extsep}txt'))

	def test_log_file_path_joins_logs_dir(self) -> None:
		self.assertEqual(Assets.log_file_path('error.log'), os.path.join(Assets.logs_dir, 'error.log'))

	def test_internal_temp_file_joins_temp_dir(self) -> None:
		self.assertEqual(Assets.internal_temp_file('scratch.bin'), os.path.join(Assets.internal_temp_dir, 'scratch.bin'))

	def test_theme_file_path_appends_txt(self) -> None:
		self.assertEqual(Assets.theme_file_path('Dark'), os.path.join(Assets.themes_dir, f'Dark{os.extsep}txt'))


class Test_version(unittest.TestCase):
	def test_returns_string(self) -> None:
		with open(Assets.versions_file_path, 'r', encoding='utf-8') as f:
			versions = json.load(f)
		any_name = next(iter(versions))
		self.assertEqual(Assets.version(any_name), versions[any_name])

	def test_unknown_program_raises(self) -> None:
		with self.assertRaises(KeyError):
			Assets.version('__definitely_not_a_program__')


class Test_mpq_helpers(unittest.TestCase):
	def test_mpq_file_path_joins_components(self) -> None:
		self.assertEqual(Assets.mpq_file_path('a', 'b', 'c'), os.path.join(Assets.mpq_dir, 'a', 'b', 'c'))

	def test_mpq_file_name_uses_backslash(self) -> None:
		self.assertEqual(Assets.mpq_file_name('a', 'b', 'c'), 'a\\b\\c')

	def test_mpq_file_ref_prefixes_MPQ(self) -> None:
		self.assertEqual(Assets.mpq_file_ref('a', 'b'), 'MPQ:a\\b')


class Test_mpq_file_path_to_file_name(unittest.TestCase):
	def test_returns_input_unchanged_when_outside_mpq_dir(self) -> None:
		path = os.path.join('not', 'under', 'mpq', 'file.dat')
		self.assertEqual(Assets.mpq_file_path_to_file_name(path), path)

	def test_single_component(self) -> None:
		path = Assets.mpq_file_path('file.dat')
		self.assertEqual(Assets.mpq_file_path_to_file_name(path), 'file.dat')

	def test_two_components(self) -> None:
		path = Assets.mpq_file_path('subdir', 'file.dat')
		self.assertEqual(Assets.mpq_file_path_to_file_name(path), 'subdir\\file.dat')

	def test_three_components(self) -> None:
		# ISS-353: paths deeper than 2 components were collapsed by os.path.split
		path = Assets.mpq_file_path('a', 'b', 'file.dat')
		self.assertEqual(Assets.mpq_file_path_to_file_name(path), 'a\\b\\file.dat')

	def test_deeply_nested_components(self) -> None:
		# ISS-353: verify deep nesting is preserved
		path = Assets.mpq_file_path('a', 'b', 'c', 'd', 'file.dat')
		self.assertEqual(Assets.mpq_file_path_to_file_name(path), 'a\\b\\c\\d\\file.dat')

	def test_round_trip_with_mpq_file_path(self) -> None:
		components = ('arr', 'units', 'protoss', 'zealot.grp')
		path = Assets.mpq_file_path(*components)
		self.assertEqual(Assets.mpq_file_path_to_file_name(path), Assets.mpq_file_name(*components))


class Test_mpq_file_path_to_ref(unittest.TestCase):
	def test_returns_input_unchanged_when_outside_mpq_dir(self) -> None:
		path = os.path.join('elsewhere', 'file.dat')
		self.assertEqual(Assets.mpq_file_path_to_ref(path), path)

	def test_single_component(self) -> None:
		path = Assets.mpq_file_path('file.dat')
		self.assertEqual(Assets.mpq_file_path_to_ref(path), 'MPQ:file.dat')

	def test_two_components(self) -> None:
		path = Assets.mpq_file_path('subdir', 'file.dat')
		self.assertEqual(Assets.mpq_file_path_to_ref(path), 'MPQ:subdir\\file.dat')

	def test_three_components(self) -> None:
		# ISS-353
		path = Assets.mpq_file_path('a', 'b', 'file.dat')
		self.assertEqual(Assets.mpq_file_path_to_ref(path), 'MPQ:a\\b\\file.dat')

	def test_deeply_nested_components(self) -> None:
		# ISS-353
		path = Assets.mpq_file_path('a', 'b', 'c', 'd', 'file.dat')
		self.assertEqual(Assets.mpq_file_path_to_ref(path), 'MPQ:a\\b\\c\\d\\file.dat')


class Test_mpq_ref_to_file_path(unittest.TestCase):
	def test_returns_input_unchanged_when_no_MPQ_prefix(self) -> None:
		self.assertEqual(Assets.mpq_ref_to_file_path('something else'), 'something else')

	def test_single_component(self) -> None:
		self.assertEqual(Assets.mpq_ref_to_file_path('MPQ:file.dat'), Assets.mpq_file_path('file.dat'))

	def test_multiple_components(self) -> None:
		self.assertEqual(
			Assets.mpq_ref_to_file_path('MPQ:a\\b\\c\\file.dat'),
			Assets.mpq_file_path('a', 'b', 'c', 'file.dat'),
		)


class Test_mpq_ref_to_file_name(unittest.TestCase):
	def test_returns_input_unchanged_when_no_MPQ_prefix(self) -> None:
		self.assertEqual(Assets.mpq_ref_to_file_name('not a ref'), 'not a ref')

	def test_strips_MPQ_prefix(self) -> None:
		self.assertEqual(Assets.mpq_ref_to_file_name('MPQ:a\\b\\c.dat'), 'a\\b\\c.dat')


class Test_mpq_round_trip(unittest.TestCase):
	def test_path_to_ref_to_path(self) -> None:
		components = ('a', 'b', 'c', 'file.dat')
		original = Assets.mpq_file_path(*components)
		ref = Assets.mpq_file_path_to_ref(original)
		self.assertEqual(Assets.mpq_ref_to_file_path(ref), original)

	def test_path_to_name_round_trip_components(self) -> None:
		# ISS-353: nested paths must round-trip preserving all components
		components = ('a', 'b', 'c', 'file.dat')
		path = Assets.mpq_file_path(*components)
		name = Assets.mpq_file_path_to_file_name(path)
		self.assertEqual(name.split('\\'), list(components))


class Test_data_cache(unittest.TestCase):
	def test_returns_lines_from_data_file(self) -> None:
		# Use a data ref that is known to exist in the project's Data folder.
		lines = Assets.data_cache(Assets.DataReference.Races)
		self.assertIsInstance(lines, list)
		self.assertTrue(all(isinstance(l, str) for l in lines))
		self.assertGreater(len(lines), 0)

	def test_result_is_cached(self) -> None:
		first = Assets.data_cache(Assets.DataReference.Races)
		second = Assets.data_cache(Assets.DataReference.Races)
		self.assertIs(first, second)


class Test_image_cache_reset(unittest.TestCase):
	def test_clear_image_cache_empties_cache(self) -> None:
		Assets._IMAGE_CACHE['__sentinel__'] = object()  # type: ignore[assignment]
		Assets.clear_image_cache()
		self.assertNotIn('__sentinel__', Assets._IMAGE_CACHE)

	def test_clear_help_image_cache_empties_cache(self) -> None:
		Assets._HELP_IMAGE_CACHE['__sentinel__'] = object()  # type: ignore[assignment]
		Assets.clear_help_image_cache()
		self.assertNotIn('__sentinel__', Assets._HELP_IMAGE_CACHE)


class Test_HelpFolder(unittest.TestCase):
	def _make_tree(self) -> tuple[Assets.HelpFolder, Assets.HelpFile, Assets.HelpFile]:
		root = Assets.HelpFolder('Help')
		sub = Assets.HelpFolder('Sub')
		root.add_folder(sub)
		file_root = Assets.HelpFile('intro.md', root)
		root.add_file(file_root)
		file_sub = Assets.HelpFile('deep.md', sub)
		sub.add_file(file_sub)
		return root, file_root, file_sub

	def test_add_folder_sets_parent(self) -> None:
		root, _, _ = self._make_tree()
		self.assertIs(root.folders[0].parent, root)

	def test_index_for_top_level_file(self) -> None:
		root, _, _ = self._make_tree()
		self.assertEqual(root.index('/Help/intro.md'), '0')

	def test_index_for_nested_file(self) -> None:
		root, _, _ = self._make_tree()
		# folder index after files: len(files)=1, folder index 0 → 1; then file in folder → 0
		self.assertEqual(root.index('/Help/Sub/deep.md'), '1.0')

	def test_index_without_help_prefix_returns_none(self) -> None:
		root, _, _ = self._make_tree()
		self.assertIsNone(root.index('/NotHelp/intro.md'))

	def test_index_missing_file_returns_none(self) -> None:
		root, _, _ = self._make_tree()
		self.assertIsNone(root.index('/Help/nonexistent.md'))

	def test_get_file_resolves_top_level(self) -> None:
		root, file_root, _ = self._make_tree()
		self.assertIs(root.get_file('0'), file_root)

	def test_get_file_resolves_nested(self) -> None:
		root, _, file_sub = self._make_tree()
		self.assertIs(root.get_file('1.0'), file_sub)

	def test_get_file_out_of_range_returns_none(self) -> None:
		root, _, _ = self._make_tree()
		self.assertIsNone(root.get_file('99'))


class Test_HelpFile(unittest.TestCase):
	def test_name_strips_extension(self) -> None:
		folder = Assets.HelpFolder('root')
		f = Assets.HelpFile('Programs/PyAI.md', folder)
		self.assertEqual(f.name, 'PyAI')

	def test_path_uses_forward_slashes(self) -> None:
		folder = Assets.HelpFolder('root')
		f = Assets.HelpFile(os.path.join('Programs', 'PyAI.md'), folder)
		self.assertEqual(f.path, 'Programs/PyAI.md')


class Test_help_tree(unittest.TestCase):
	def test_returns_root_folder(self) -> None:
		root = Assets.help_tree(force_update=True)
		self.assertIsInstance(root, Assets.HelpFolder)
		# Root corresponds to the Help directory's basename
		self.assertEqual(root.name, os.path.basename(Assets.help_dir))

	def test_cached_on_subsequent_calls(self) -> None:
		first = Assets.help_tree()
		second = Assets.help_tree()
		self.assertIs(first, second)


class Test_help_file_path(unittest.TestCase):
	def test_returns_none_for_missing_path(self) -> None:
		self.assertIsNone(Assets.help_file_path('/Help/__definitely_missing__.md'))

	def test_resolves_existing_file(self) -> None:
		# Pick any .md inside Help/ to verify resolution
		found_relative: str | None = None
		for path, _, filenames in os.walk(Assets.help_dir):
			for filename in filenames:
				if filename.endswith('.md') and not filename.startswith('.'):
					full = os.path.join(path, filename)
					found_relative = os.path.relpath(full, Assets.help_dir)
					break
			if found_relative:
				break
		if found_relative is None:
			self.skipTest('no help .md file to test against')
		query = '/Help/' + found_relative.replace(os.sep, '/')
		resolved = Assets.help_file_path(query)
		self.assertIsNotNone(resolved)
		assert resolved is not None
		self.assertTrue(os.path.exists(resolved))


class Test_theme_list(unittest.TestCase):
	def test_returns_sorted_list_of_strings(self) -> None:
		themes = Assets.theme_list()
		self.assertIsInstance(themes, list)
		self.assertEqual(themes, sorted(themes))
		for name in themes:
			self.assertIsInstance(name, str)
			self.assertFalse(name.endswith('.txt'))
