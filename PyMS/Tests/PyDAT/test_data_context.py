
from ...PyDAT.DataContext import DataContext, TicksPerSecond
from ...PyDAT.DataID import DATID, DataID
from ...FileFormats.DAT import DATImage
from ...FileFormats.IScriptBIN.IScriptBIN import IScriptBIN

import unittest
from unittest.mock import patch, mock_open


class Test_TicksPerSecond(unittest.TestCase):
	def test_values(self) -> None:
		self.assertEqual(TicksPerSecond.fastest, 24)
		self.assertEqual(TicksPerSecond.faster, 21)
		self.assertEqual(TicksPerSecond.fast, 18)
		self.assertEqual(TicksPerSecond.normal, 15)
		self.assertEqual(TicksPerSecond.slow, 12)
		self.assertEqual(TicksPerSecond.slower, 9)
		self.assertEqual(TicksPerSecond.slowest, 6)

	def test_descending_order(self) -> None:
		speeds = [
			TicksPerSecond.fastest, TicksPerSecond.faster, TicksPerSecond.fast,
			TicksPerSecond.normal, TicksPerSecond.slow, TicksPerSecond.slower, TicksPerSecond.slowest,
		]
		self.assertEqual(speeds, sorted(speeds, reverse=True))


class Test_dat_data(unittest.TestCase):
	EXPECTED = {
		DATID.units: 'units',
		DATID.weapons: 'weapons',
		DATID.flingy: 'flingy',
		DATID.sprites: 'sprites',
		DATID.images: 'images',
		DATID.upgrades: 'upgrades',
		DATID.techdata: 'technology',
		DATID.sfxdata: 'sounds',
		DATID.portdata: 'portraits',
		DATID.mapdata: 'campaign',
		DATID.orders: 'orders',
	}

	def setUp(self) -> None:
		self.dc = DataContext()

	def test_every_datid_maps_to_its_attribute(self) -> None:
		for datid, attr in Test_dat_data.EXPECTED.items():
			with self.subTest(datid=datid):
				self.assertIs(self.dc.dat_data(datid), getattr(self.dc, attr))

	def test_all_datids_are_covered(self) -> None:
		# A new DATID without a mapping would fall through to an implicit None.
		for datid in DATID:
			with self.subTest(datid=datid):
				self.assertIsNotNone(self.dc.dat_data(datid))


class Test_data_data(unittest.TestCase):
	EXPECTED = {
		DataID.stat_txt: 'stat_txt',
		DataID.unitnamestbl: 'unitnamestbl',
		DataID.imagestbl: 'imagestbl',
		DataID.sfxdatatbl: 'sfxdatatbl',
		DataID.portdatatbl: 'portdatatbl',
		DataID.mapdatatbl: 'mapdatatbl',
		DataID.cmdicons: 'cmdicons',
	}

	def setUp(self) -> None:
		self.dc = DataContext()

	def test_each_dataid_maps_to_its_attribute(self) -> None:
		for dataid, attr in Test_data_data.EXPECTED.items():
			with self.subTest(dataid=dataid):
				self.assertIs(self.dc.data_data(dataid), getattr(self.dc, attr))

	def test_iscriptbin_unset_before_loading(self) -> None:
		# iscriptbin is populated lazily by load_additional_files.
		with self.assertRaises(AttributeError):
			self.dc.data_data(DataID.iscriptbin)

	def test_iscriptbin_returned_once_set(self) -> None:
		iscriptbin = IScriptBIN()
		self.dc.iscriptbin = iscriptbin
		self.assertIs(self.dc.data_data(DataID.iscriptbin), iscriptbin)


class Test_load_hints(unittest.TestCase):
	def setUp(self) -> None:
		self.dc = DataContext()

	def test_construction_populates_hints(self) -> None:
		self.assertTrue(self.dc.hints)
		for key, value in self.dc.hints.items():
			self.assertIsInstance(key, str)
			self.assertIsInstance(value, str)

	def test_parses_key_value_lines(self) -> None:
		self.dc.hints = {}
		content = 'alpha=first value\nbeta=2\ngamma=g\n'
		with patch('builtins.open', mock_open(read_data=content)):
			self.dc.load_hints()
		self.assertEqual(self.dc.hints, {'alpha': 'first value', 'beta': '2', 'gamma': 'g'})

	def test_skips_blank_spaced_and_empty_value_lines(self) -> None:
		self.dc.hints = {}
		content = '\nkept=yes\nbad key=skipped\nnovalue=\nalso_kept=ok\n'
		with patch('builtins.open', mock_open(read_data=content)):
			self.dc.load_hints()
		self.assertEqual(self.dc.hints, {'kept': 'yes', 'also_kept': 'ok'})

	def test_multiple_equals_splits_on_the_last(self) -> None:
		# The key pattern is greedy, so a line with several '=' splits at the final one.
		self.dc.hints = {}
		with patch('builtins.open', mock_open(read_data='expr=a=b+c\n')):
			self.dc.load_hints()
		self.assertEqual(self.dc.hints, {'expr=a': 'b+c'})


class Test_image_frame_helpers(unittest.TestCase):
	def setUp(self) -> None:
		self.dc = DataContext()

	def test_get_cmdicon_none_without_icon_palette(self) -> None:
		self.assertEqual(self.dc.palettes, {})
		self.assertIsNone(self.dc.get_cmdicon(0))
		self.assertIsNone(self.dc.get_cmdicon(0, highlighted=True))

	def test_get_grp_frame_none_without_palette(self) -> None:
		# No palettes loaded, so every palette-resolution branch returns None.
		self.assertIsNone(self.dc.get_grp_frame('unit.grp'))
		self.assertIsNone(self.dc.get_grp_frame('thingy\\tileset\\x.grp'))
		self.assertIsNone(self.dc.get_grp_frame(
			'x.grp',
			draw_function=DATImage.DrawFunction.use_remapping,
			remapping=DATImage.Remapping.ofire,
		))

	def test_get_image_frame_none_without_dat(self) -> None:
		self.assertIsNone(self.dc.images.dat)
		self.assertIsNone(self.dc.get_image_frame(0))
