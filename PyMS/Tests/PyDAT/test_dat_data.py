
from ...PyDAT.DataContext import DataContext
from ...PyDAT.DATData import DATData
from ...PyDAT.DataID import DATID
from ...FileFormats import DAT
from ...FileFormats.DAT.AbstractDAT import AbstractDAT
from ...Utilities import Assets
from ...Utilities import IO
from ...Utilities.PyMSError import PyMSError

import unittest
from unittest.mock import patch, mock_open


def _data(dc: DataContext) -> DATData[DAT.UnitsDAT]:
	return DATData(dc, dat_id=DATID.units, dat_type=DAT.UnitsDAT, data_file=Assets.DataReference.Units, entry_type_name='Unit')


class Test_construction(unittest.TestCase):
	def setUp(self) -> None:
		self.dc = DataContext()

	def test_initial_state(self) -> None:
		data = _data(self.dc)
		self.assertIsNone(data.dat)
		self.assertIsNone(data.default_dat)
		self.assertIsNone(data.file_path)
		self.assertEqual(data.names, ())
		self.assertEqual(data.name_overrides, {})
		self.assertEqual(data.dat_id, DATID.units)
		self.assertEqual(data.entry_type_name, 'Unit')


class Test_new_file(unittest.TestCase):
	def setUp(self) -> None:
		self.dc = DataContext()

	def test_without_default_creates_fresh_dat(self) -> None:
		data = _data(self.dc)
		data.file_path = 'stale'
		data.new_file()
		self.assertIsNotNone(data.dat)
		self.assertIsNone(data.file_path)
		self.assertEqual(data.entry_count(), DAT.UnitsDAT.FORMAT.entries)
		self.assertEqual(len(data.names), data.entry_count())

	def test_with_default_deep_copies(self) -> None:
		data = _data(self.dc)
		default = DAT.UnitsDAT()
		default.new_file()
		data.default_dat = default
		data.new_file()
		self.assertIsNotNone(data.dat)
		self.assertIsNot(data.dat, default)
		self.assertIsNone(data.file_path)


class Test_load_save(unittest.TestCase):
	def setUp(self) -> None:
		self.dc = DataContext()

	def test_load_bytes_clears_path_and_round_trips(self) -> None:
		source = DAT.UnitsDAT()
		source.new_file()
		raw = IO.output_to_bytes(source.save)
		data = _data(self.dc)
		data.file_path = 'stale'
		data.load(raw)
		self.assertIsNotNone(data.dat)
		self.assertIsNone(data.file_path)
		self.assertEqual(data.save_data(), raw)

	def test_save_data_asserts_without_dat(self) -> None:
		with self.assertRaises(AssertionError):
			_data(self.dc).save_data()

	def test_save_file_is_noop_without_dat(self) -> None:
		data = _data(self.dc)
		with patch.object(DAT.UnitsDAT, 'save') as save:
			data.save_file('ignored')
		save.assert_not_called()

	def test_save_file_delegates_to_dat(self) -> None:
		data = _data(self.dc)
		data.new_file()
		with patch.object(DAT.UnitsDAT, 'save') as save:
			data.save_file('out.dat')
		save.assert_called_once_with('out.dat')

	def test_load_path_sets_path_and_loads(self) -> None:
		data = _data(self.dc)
		with patch.object(DAT.UnitsDAT, 'load') as load:
			data.load('in.dat')
		load.assert_called_once_with('in.dat')
		self.assertIsNotNone(data.dat)
		self.assertEqual(data.file_path, 'in.dat')


class Test_entry_count_and_expand(unittest.TestCase):
	def setUp(self) -> None:
		self.dc = DataContext()

	def test_entry_count_falls_back_to_format(self) -> None:
		self.assertEqual(_data(self.dc).entry_count(), DAT.UnitsDAT.FORMAT.entries)

	def test_entry_count_uses_default_dat(self) -> None:
		data = _data(self.dc)
		default = DAT.UnitsDAT()
		default.new_file()
		default.expand_entries(5)
		data.default_dat = default
		self.assertEqual(data.entry_count(), default.entry_count())

	def test_is_expanded_default_false(self) -> None:
		self.assertFalse(_data(self.dc).is_expanded())

	def test_expand_entries_without_dat_returns_false(self) -> None:
		self.assertFalse(_data(self.dc).expand_entries(1))

	def test_expand_entries_grows_and_marks_expanded(self) -> None:
		data = _data(self.dc)
		data.new_file()
		before = data.entry_count()
		self.assertTrue(data.expand_entries(4))
		self.assertGreater(data.entry_count(), before)
		self.assertTrue(data.is_expanded())


class Test_names(unittest.TestCase):
	def setUp(self) -> None:
		self.dc = DataContext()

	def test_update_names_populates_and_fires_callback(self) -> None:
		data = _data(self.dc)
		fired: list[DATID] = []
		data.update_cb += fired.append
		data.update_names()
		self.assertEqual(len(data.names), data.entry_count())
		self.assertEqual(fired, [DATID.units])

	def test_entry_name_in_range_uses_cached_name(self) -> None:
		data = _data(self.dc)
		data.new_file()
		self.assertEqual(data.entry_name(0), data.names[0])

	def test_entry_name_out_of_range_is_computed(self) -> None:
		data = _data(self.dc)
		data.new_file()
		name = data.entry_name(10_000)
		self.assertIn('10000', name)


class Test_name_overrides(unittest.TestCase):
	def setUp(self) -> None:
		self.dc = DataContext()

	def test_load_parses_overrides(self) -> None:
		data = _data(self.dc)
		with patch('builtins.open', mock_open(read_data='3:Custom\n5+:Appended\n')):
			data.load_name_overrides('ignored', update_names=False)
		self.assertEqual(data.name_overrides, {3: (False, 'Custom'), 5: (True, 'Appended')})

	def test_load_invalid_raises(self) -> None:
		data = _data(self.dc)
		with patch('builtins.open', mock_open(read_data='not a valid override line\n')):
			with self.assertRaises(PyMSError) as cm:
				data.load_name_overrides('ignored', update_names=False)
		self.assertIn('Invalid name override', str(cm.exception))

	def test_load_triggers_update_names_by_default(self) -> None:
		data = _data(self.dc)
		fired: list[DATID] = []
		data.update_cb += fired.append
		with patch('builtins.open', mock_open(read_data='0:First\n')):
			data.load_name_overrides('ignored')
		self.assertEqual(fired, [DATID.units])

	def test_save_writes_sorted_overrides(self) -> None:
		data = _data(self.dc)
		data.name_overrides = {5: (True, 'Appended'), 3: (False, 'Custom')}
		handle = mock_open()
		with patch('builtins.open', handle):
			data.save_name_overrides('ignored')
		written = [call.args[0] for call in handle().write.call_args_list]
		self.assertEqual(written, ['3:Custom\n', '5+:Appended\n'])

	def test_overrides_round_trip(self) -> None:
		data = _data(self.dc)
		data.name_overrides = {1: (False, 'One'), 7: (True, 'Seven')}
		handle = mock_open()
		with patch('builtins.open', handle):
			data.save_name_overrides('ignored')
		written = ''.join(call.args[0] for call in handle().write.call_args_list)
		reloaded = _data(self.dc)
		with patch('builtins.open', mock_open(read_data=written)):
			reloaded.load_name_overrides('ignored', update_names=False)
		self.assertEqual(reloaded.name_overrides, data.name_overrides)


class Test_subclasses(unittest.TestCase):
	def setUp(self) -> None:
		self.dc = DataContext()

	def _subclasses(self):
		return [
			(self.dc.units, DATID.units, 'Unit'),
			(self.dc.weapons, DATID.weapons, 'Weapon'),
			(self.dc.flingy, DATID.flingy, 'Flingy'),
			(self.dc.sprites, DATID.sprites, 'Sprite'),
			(self.dc.images, DATID.images, 'Image'),
			(self.dc.upgrades, DATID.upgrades, 'Upgrade'),
			(self.dc.technology, DATID.techdata, 'Technology'),
			(self.dc.sounds, DATID.sfxdata, 'Sound'),
			(self.dc.portraits, DATID.portdata, 'Portrait'),
			(self.dc.campaign, DATID.mapdata, 'Map'),
			(self.dc.orders, DATID.orders, 'Order'),
		]

	def test_construction_parameters(self) -> None:
		for data, dat_id, entry_type_name in self._subclasses():
			with self.subTest(dat_id=dat_id):
				self.assertEqual(data.dat_id, dat_id)
				self.assertEqual(data.entry_type_name, entry_type_name)
				self.assertTrue(issubclass(data.dat_type, AbstractDAT))

	def test_update_names_lengths_and_callbacks(self) -> None:
		for data, dat_id, _ in self._subclasses():
			with self.subTest(dat_id=dat_id):
				fired: list[DATID] = []
				data.update_cb += fired.append
				data.update_names()
				self.assertEqual(len(data.names), data.entry_count())
				self.assertEqual(fired, [dat_id])
				self.assertTrue(all(isinstance(name, str) for name in data.names))
