
from ...PyDAT import IconData as IconDataMod
from ...PyDAT.IconData import IconData
from ...PyDAT.DataID import DataID
from ...PyDAT.DataContext import DataContext
from ...FileFormats.GRP import CacheGRP
from ...FileFormats.PCX import PCX

import unittest
from unittest.mock import Mock, patch
from typing import cast


def _context() -> DataContext:
	return cast(DataContext, Mock())


def _failing_context() -> DataContext:
	# A context whose MPQ lookups raise, to exercise the load failure paths.
	mock = Mock()
	mock.mpq_handler.load_file.side_effect = Exception('boom')
	return cast(DataContext, mock)


def _grp(frames: int = 3, width: int = 36, height: int = 34) -> CacheGRP:
	grp = Mock()
	grp.frames = frames
	grp.width = width
	grp.height = height
	return cast(CacheGRP, grp)


class Test_construction(unittest.TestCase):
	def test_initial_state(self) -> None:
		icon = IconData(_context())
		self.assertIsNone(icon.grp)
		self.assertIsNone(icon.ticon_pcx)
		self.assertEqual(icon.names, ())
		self.assertEqual(icon.images, {})


class Test_frame_count(unittest.TestCase):
	def test_without_grp_uses_name_count(self) -> None:
		icon = IconData(_context())
		icon.names = ('a', 'b', 'c')
		self.assertEqual(icon.frame_count(), 3)

	def test_with_grp_uses_grp_frames(self) -> None:
		icon = IconData(_context())
		icon.names = ('a', 'b', 'c')
		icon.grp = _grp(frames=7)
		self.assertEqual(icon.frame_count(), 7)


class Test_frame_size(unittest.TestCase):
	def test_without_grp_is_default(self) -> None:
		self.assertEqual(IconData(_context()).frame_size(), (36, 34))

	def test_with_grp_uses_grp_size(self) -> None:
		icon = IconData(_context())
		icon.grp = _grp(width=40, height=48)
		self.assertEqual(icon.frame_size(), (40, 48))


class Test_save_data(unittest.TestCase):
	def test_asserts_without_grp(self) -> None:
		with self.assertRaises(AssertionError):
			IconData(_context()).save_data()

	def test_delegates_to_grp(self) -> None:
		icon = IconData(_context())
		grp = Mock()
		grp.save.side_effect = lambda f: f.write(b'icon-bytes')
		icon.grp = cast(CacheGRP, grp)
		self.assertEqual(icon.save_data(), b'icon-bytes')


class Test_update_names(unittest.TestCase):
	def _run(self, names: list[str], grp: CacheGRP | None) -> IconData:
		icon = IconData(_context())
		icon.grp = grp
		with patch.object(IconDataMod.Assets, 'data_cache', return_value=tuple(names)):
			icon.update_names()
		return icon

	def test_without_grp_uses_all_names_and_fires_callback(self) -> None:
		icon = IconData(_context())
		fired: list[DataID] = []
		icon.update_cb += fired.append
		with patch.object(IconDataMod.Assets, 'data_cache', return_value=('a', 'b', 'c')):
			icon.update_names()
		self.assertEqual(icon.names, ('a', 'b', 'c'))
		self.assertEqual(fired, [DataID.cmdicons])

	def test_truncates_to_fewer_frames(self) -> None:
		icon = self._run(['a', 'b', 'c', 'd'], _grp(frames=2))
		self.assertEqual(icon.names, ('a', 'b'))

	def test_keeps_names_when_counts_match(self) -> None:
		icon = self._run(['a', 'b', 'c'], _grp(frames=3))
		self.assertEqual(icon.names, ('a', 'b', 'c'))

	def test_pads_to_more_frames(self) -> None:
		icon = self._run(['a', 'b', 'c'], _grp(frames=5))
		self.assertEqual(icon.names, ('a', 'b', 'c', 'Unknown', 'Unknown'))

	def test_does_not_corrupt_real_data_cache(self) -> None:
		# The (immutable) cache must be unaffected by padding the name list.
		before = IconDataMod.Assets.data_cache(IconDataMod.Assets.DataReference.Icons)
		icon = IconData(_context())
		icon.grp = _grp(frames=len(before) + 3)
		icon.update_names()
		self.assertEqual(IconDataMod.Assets.data_cache(IconDataMod.Assets.DataReference.Icons), before)
		self.assertEqual(len(icon.names), len(before) + 3)


class Test_load_grp(unittest.TestCase):
	def test_success_sets_grp_clears_images_and_updates_names(self) -> None:
		icon = IconData(_context())
		icon.images = {True: {}}
		grp = _grp(frames=2)
		with patch.object(IconDataMod, 'CacheGRP', return_value=grp):
			with patch.object(IconDataMod.Assets, 'data_cache', return_value=('a', 'b', 'c')):
				icon.load_grp()
		self.assertIs(icon.grp, grp)
		self.assertEqual(icon.images, {})
		self.assertEqual(icon.names, ('a', 'b'))

	def test_failure_leaves_grp_none_and_images_intact(self) -> None:
		icon = IconData(_failing_context())
		icon.images = {False: {}}
		icon.load_grp()
		self.assertIsNone(icon.grp)
		self.assertEqual(icon.images, {False: {}})


class Test_load_ticon_pcx(unittest.TestCase):
	def test_success_sets_pcx_and_clears_images(self) -> None:
		icon = IconData(_context())
		icon.images = {True: {}}
		pcx = cast(PCX, Mock())
		with patch.object(IconDataMod, 'PCX', return_value=pcx):
			icon.load_ticon_pcx()
		self.assertIs(icon.ticon_pcx, pcx)
		self.assertEqual(icon.images, {})

	def test_failure_leaves_pcx_none(self) -> None:
		icon = IconData(_failing_context())
		icon.load_ticon_pcx()
		self.assertIsNone(icon.ticon_pcx)
