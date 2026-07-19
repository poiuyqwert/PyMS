
from ...PyMOD.Meta import MetaHandler

import os
import unittest
from unittest import mock

ROOT_PATH = os.path.join(os.sep, 'project')
META_PATH = os.path.join(ROOT_PATH, '.build', 'meta.json')

def project_path(*path: str) -> str:
	return os.path.join(ROOT_PATH, *path)

class MetaTestCase(unittest.TestCase):
	def setUp(self) -> None:
		self.hashes: dict[str, str] = {}
		self.missing_files: set[str] = set()
		compute_patcher = mock.patch('PyMS.PyMOD.Meta.compute_file_hash', side_effect=lambda file_path: self.hashes[file_path])
		compute_patcher.start()
		self.addCleanup(compute_patcher.stop)
		isfile_patcher = mock.patch('PyMS.PyMOD.Meta._os.path.isfile', side_effect=self._isfile)
		isfile_patcher.start()
		self.addCleanup(isfile_patcher.stop)
		self.meta = MetaHandler(META_PATH, ROOT_PATH)

	def _isfile(self, file_path: str) -> bool:
		return file_path in self.hashes and file_path not in self.missing_files

	def record_build(self, input_paths: list[str], output_paths: list[str]) -> None:
		self.meta.update_metas(input_paths, output_paths)


class Test_check_requires_update(MetaTestCase):
	def test_unrecorded_files_require_update(self) -> None:
		self.hashes[project_path('source.txt')] = 'hash1'
		self.hashes[project_path('.build', 'intermediates', 'source.txt')] = 'hash2'
		self.assertTrue(self.meta.check_requires_update([project_path('source.txt')], [project_path('.build', 'intermediates', 'source.txt')]))

	def test_unchanged_files_require_no_update(self) -> None:
		source = project_path('source.txt')
		destination = project_path('.build', 'intermediates', 'source.txt')
		self.hashes[source] = 'hash1'
		self.hashes[destination] = 'hash2'
		self.record_build([source], [destination])
		self.assertFalse(self.meta.check_requires_update([source], [destination]))

	def test_changed_input_requires_update(self) -> None:
		source = project_path('source.txt')
		destination = project_path('.build', 'intermediates', 'source.txt')
		self.hashes[source] = 'hash1'
		self.hashes[destination] = 'hash2'
		self.record_build([source], [destination])
		self.hashes[source] = 'changed'
		self.assertTrue(self.meta.check_requires_update([source], [destination]))

	def test_changed_output_requires_update(self) -> None:
		source = project_path('source.txt')
		destination = project_path('.build', 'intermediates', 'source.txt')
		self.hashes[source] = 'hash1'
		self.hashes[destination] = 'hash2'
		self.record_build([source], [destination])
		self.hashes[destination] = 'changed'
		self.assertTrue(self.meta.check_requires_update([source], [destination]))

	def test_missing_output_file_requires_update(self) -> None:
		source = project_path('source.txt')
		destination = project_path('.build', 'intermediates', 'source.txt')
		self.hashes[source] = 'hash1'
		self.hashes[destination] = 'hash2'
		self.record_build([source], [destination])
		self.missing_files.add(destination)
		self.assertTrue(self.meta.check_requires_update([source], [destination]))

	def test_extra_input_requires_update(self) -> None:
		source = project_path('source.txt')
		config = project_path('config.json')
		destination = project_path('.build', 'intermediates', 'source.txt')
		self.hashes[source] = 'hash1'
		self.hashes[config] = 'hash2'
		self.hashes[destination] = 'hash3'
		self.record_build([source], [destination])
		self.assertTrue(self.meta.check_requires_update([source, config], [destination]))

	def test_removed_input_requires_update(self) -> None:
		source = project_path('source.txt')
		config = project_path('config.json')
		destination = project_path('.build', 'intermediates', 'source.txt')
		self.hashes[source] = 'hash1'
		self.hashes[config] = 'hash2'
		self.hashes[destination] = 'hash3'
		self.record_build([source, config], [destination])
		self.assertTrue(self.meta.check_requires_update([source], [destination]))

	def test_input_order_requires_no_update(self) -> None:
		source_a = project_path('a.txt')
		source_b = project_path('b.txt')
		destination = project_path('.build', 'intermediates', 'out.bin')
		self.hashes[source_a] = 'hash1'
		self.hashes[source_b] = 'hash2'
		self.hashes[destination] = 'hash3'
		self.record_build([source_b, source_a], [destination])
		self.assertFalse(self.meta.check_requires_update([source_a, source_b], [destination]))

	def test_renamed_input_with_identical_contents_requires_update(self) -> None:
		# The output can depend on input file names (e.g. GRP frame order), not just their contents
		old_source = project_path('frame 001.bmp')
		new_source = project_path('frame 010.bmp')
		destination = project_path('.build', 'intermediates', 'unit.grp')
		self.hashes[old_source] = 'same-hash'
		self.hashes[new_source] = 'same-hash'
		self.hashes[destination] = 'hash2'
		self.record_build([old_source], [destination])
		self.assertTrue(self.meta.check_requires_update([new_source], [destination]))

	def test_meta_without_a_recorded_fingerprint_requires_update(self) -> None:
		source = project_path('source.txt')
		destination = project_path('.build', 'intermediates', 'source.txt')
		self.hashes[source] = 'hash1'
		self.hashes[destination] = 'hash2'
		# A meta from before input fingerprints were recorded has matching output hashes but no
		# fingerprint entry for the target
		self.meta.update_output_metas([destination])
		self.assertTrue(self.meta.check_requires_update([source], [destination]))


class Test_meta_keys(MetaTestCase):
	def test_entries_are_keyed_relative_to_the_project_root(self) -> None:
		destination = project_path('.build', 'intermediates', 'sub', 'out.bin')
		self.hashes[destination] = 'hash1'
		self.meta.update_output_metas([destination])
		self.assertEqual(self.meta.meta['outputs'], {'.build/intermediates/sub/out.bin': 'hash1'})

	def test_has_output_only_reports_recorded_outputs(self) -> None:
		destination = project_path('.build', 'intermediates', 'out.bin')
		self.hashes[destination] = 'hash1'
		self.assertFalse(self.meta.has_output(destination))
		self.meta.update_output_metas([destination])
		self.assertTrue(self.meta.has_output(destination))


class Test_save(MetaTestCase):
	def test_prune_drops_entries_unused_this_compile(self) -> None:
		stale_source = project_path('deleted.txt')
		stale_destination = project_path('.build', 'intermediates', 'deleted.txt')
		self.hashes[stale_source] = 'hash1'
		self.hashes[stale_destination] = 'hash2'
		self.record_build([stale_source], [stale_destination])

		fresh_meta = MetaHandler(META_PATH, ROOT_PATH)
		fresh_meta.meta = self.meta.meta
		source = project_path('source.txt')
		destination = project_path('.build', 'intermediates', 'source.txt')
		self.hashes[source] = 'hash3'
		self.hashes[destination] = 'hash4'
		fresh_meta.update_metas([source], [destination])

		with mock.patch('builtins.open', mock.mock_open()):
			self.assertTrue(fresh_meta.save(prune=True))
		self.assertEqual(fresh_meta.meta['outputs'], {'.build/intermediates/source.txt': 'hash4'})
		self.assertEqual(list(fresh_meta.meta['inputs']), ['.build/intermediates/source.txt'])

	def test_save_without_prune_keeps_unused_entries(self) -> None:
		stale_destination = project_path('.build', 'intermediates', 'deleted.txt')
		self.hashes[stale_destination] = 'hash1'
		self.meta.update_output_metas([stale_destination])

		fresh_meta = MetaHandler(META_PATH, ROOT_PATH)
		fresh_meta.meta = self.meta.meta
		with mock.patch('builtins.open', mock.mock_open()):
			self.assertTrue(fresh_meta.save())
		self.assertEqual(fresh_meta.meta['outputs'], {'.build/intermediates/deleted.txt': 'hash1'})

	def test_files_skipped_by_the_incremental_check_survive_pruning(self) -> None:
		source = project_path('source.txt')
		destination = project_path('.build', 'intermediates', 'source.txt')
		self.hashes[source] = 'hash1'
		self.hashes[destination] = 'hash2'
		self.record_build([source], [destination])

		fresh_meta = MetaHandler(META_PATH, ROOT_PATH)
		fresh_meta.meta = self.meta.meta
		self.assertFalse(fresh_meta.check_requires_update([source], [destination]))
		with mock.patch('builtins.open', mock.mock_open()):
			self.assertTrue(fresh_meta.save(prune=True))
		self.assertEqual(fresh_meta.meta['outputs'], {'.build/intermediates/source.txt': 'hash2'})
		self.assertEqual(list(fresh_meta.meta['inputs']), ['.build/intermediates/source.txt'])


class Test_load(MetaTestCase):
	def test_load_accepts_valid_meta(self) -> None:
		data = '{"inputs": {"out.bin": "fingerprint1"}, "outputs": {"out.bin": "hash1"}}'
		with mock.patch('builtins.open', mock.mock_open(read_data=data)):
			self.assertTrue(self.meta.load())
		self.assertEqual(self.meta.meta['inputs'], {'out.bin': 'fingerprint1'})
		self.assertEqual(self.meta.meta['outputs'], {'out.bin': 'hash1'})

	def test_load_rejects_invalid_meta(self) -> None:
		for data in ('[]', '{"inputs": []}', '{"outputs": 1}', 'not json'):
			with mock.patch('builtins.open', mock.mock_open(read_data=data)):
				self.assertFalse(self.meta.load(), f'load() accepted {data!r}')

	def test_load_defaults_missing_fields(self) -> None:
		with mock.patch('builtins.open', mock.mock_open(read_data='{}')):
			self.assertTrue(self.meta.load())
		self.assertEqual(self.meta.meta['inputs'], {})
		self.assertEqual(self.meta.meta['outputs'], {})

	def test_load_drops_fields_from_older_meta_formats(self) -> None:
		data = '{"inputs": {}, "outputs": {}, "targets": {"out.bin": "fingerprint1"}}'
		with mock.patch('builtins.open', mock.mock_open(read_data=data)):
			self.assertTrue(self.meta.load())
		self.assertEqual(set(self.meta.meta), {'inputs', 'outputs'})
