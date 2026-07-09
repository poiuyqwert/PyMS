
from ...PyGRP.utils import find_frame_bmps

import unittest
from unittest import mock

class Test_Find_Frame_BMPs(unittest.TestCase):
	def test_collects_consecutive_matching_files(self) -> None:
		listing = ['apple.bmp', 'unit 000.bmp', 'unit 001.bmp', 'unit 002.bmp', 'zebra.bmp']
		with mock.patch('os.listdir', return_value=listing):
			name, files = find_frame_bmps('dir', 'unit 000.bmp')
		self.assertEqual(name, 'unit')
		self.assertEqual(files, ['unit 000.bmp', 'unit 001.bmp', 'unit 002.bmp'])

	def test_starts_at_the_named_file(self) -> None:
		listing = ['unit 000.bmp', 'unit 001.bmp', 'unit 002.bmp']
		with mock.patch('os.listdir', return_value=listing):
			_, files = find_frame_bmps('dir', 'unit 001.bmp')
		self.assertEqual(files, ['unit 001.bmp', 'unit 002.bmp'])

	def test_listing_is_sorted_before_matching(self) -> None:
		listing = ['unit 001.bmp', 'unit 000.bmp']
		with mock.patch('os.listdir', return_value=listing):
			_, files = find_frame_bmps('dir', 'unit 000.bmp')
		self.assertEqual(files, ['unit 000.bmp', 'unit 001.bmp'])

	def test_stops_at_first_non_matching_file(self) -> None:
		listing = ['unit 000.bmp', 'unit 001.bmp', 'uzzz.bmp', 'unit 002.bmp']
		with mock.patch('os.listdir', return_value=listing):
			_, files = find_frame_bmps('dir', 'unit 000.bmp')
		self.assertEqual(files, ['unit 000.bmp', 'unit 001.bmp', 'unit 002.bmp'])

	def test_name_is_derived_from_last_space(self) -> None:
		listing = ['my unit 000.bmp', 'my unit 001.bmp']
		with mock.patch('os.listdir', return_value=listing):
			name, files = find_frame_bmps('dir', 'my unit 000.bmp')
		self.assertEqual(name, 'my unit')
		self.assertEqual(files, ['my unit 000.bmp', 'my unit 001.bmp'])

	def test_name_with_space_but_no_frame_number_is_single(self) -> None:
		listing = ['my unit.bmp', 'my zebra.bmp']
		with mock.patch('os.listdir', return_value=listing):
			name, files = find_frame_bmps('dir', 'my unit.bmp')
		self.assertEqual(name, 'my unit')
		self.assertEqual(files, ['my unit.bmp'])

	def test_trailing_word_with_digits_is_not_a_frame_number(self) -> None:
		listing = ['unit v2.bmp']
		with mock.patch('os.listdir', return_value=listing):
			name, files = find_frame_bmps('dir', 'unit v2.bmp')
		self.assertEqual(name, 'unit v2')
		self.assertEqual(files, ['unit v2.bmp'])

	def test_name_without_space_matches_only_the_named_file(self) -> None:
		listing = ['sprite.bmp', 'sprite2.bmp']
		with mock.patch('os.listdir', return_value=listing):
			name, files = find_frame_bmps('dir', 'sprite.bmp')
		self.assertEqual(name, 'sprite')
		self.assertEqual(files, ['sprite.bmp'])

	def test_missing_named_file_finds_nothing(self) -> None:
		listing = ['unit 000.bmp']
		with mock.patch('os.listdir', return_value=listing):
			_, files = find_frame_bmps('dir', 'other 000.bmp')
		self.assertEqual(files, [])
