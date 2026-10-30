
import unittest

from ...FileFormats.Tileset.Tileset import Tileset, TileType

from ..utils import resource_path


class Test_ImportGraphics_GroupMegatileIds(unittest.TestCase):
	"""`Tileset.import_graphics(TileType.group, ...)` should give every
	imported group its own full slice of 16 megatile ids, regardless of how
	many groups the source BMP contains.
	"""

	def test_two_groups_each_get_16_megatile_ids(self) -> None:
		tileset = Tileset()
		tileset.new_file()

		groups_before = tileset.cv5.group_count()
		tileset.import_graphics(TileType.group, [resource_path('two_groups.bmp', __file__)])

		groups_after = tileset.cv5.group_count()
		self.assertEqual(
			groups_after - groups_before, 2,
			'Expected exactly two new groups to be appended.',
		)

		group0 = tileset.cv5.get_group(groups_before)
		group1 = tileset.cv5.get_group(groups_before + 1)

		self.assertEqual(
			len(group0.megatile_ids), 16,
			'First imported group should own 16 megatile ids.',
		)
		self.assertEqual(
			len(group1.megatile_ids), 16,
			'Second imported group should own its own 16 megatile ids, not '
			'an empty slice carried over from the first.',
		)

	def test_three_groups_each_get_16_megatile_ids(self) -> None:
		tileset = Tileset()
		tileset.new_file()

		groups_before = tileset.cv5.group_count()
		tileset.import_graphics(TileType.group, [resource_path('three_groups.bmp', __file__)])

		for offset in range(3):
			group = tileset.cv5.get_group(groups_before + offset)
			self.assertEqual(
				len(group.megatile_ids), 16,
				f'Imported group #{offset} should own 16 megatile ids.',
			)


class Test_FindImageIds_ReturnsIndependentLists(unittest.TestCase):
	"""`VR4.find_image_ids` should return lists that callers can mutate
	without affecting VR4's internal `_lookup` storage or any subsequent
	lookup results.
	"""

	def test_mutating_returned_normal_ids_does_not_affect_subsequent_lookup(self) -> None:
		tileset = Tileset()
		tileset.new_file()
		image = tuple(tuple((x + y) & 0xFF for x in range(8)) for y in range(8))
		tileset.vr4.add_image(image)

		first_normal, _first_flipped = tileset.vr4.find_image_ids(image)
		self.assertEqual(len(first_normal), 1)

		first_normal.append(9999)

		second_normal, _second_flipped = tileset.vr4.find_image_ids(image)
		self.assertNotIn(
			9999, second_normal,
			'find_image_ids must hand callers a list independent of VR4._lookup '
			'so that mutating it cannot bleed into later lookups.',
		)
		self.assertEqual(
			len(second_normal), 1,
			'A later find_image_ids lookup should still report a single entry.',
		)

	def test_mutating_returned_flipped_ids_does_not_affect_subsequent_lookup(self) -> None:
		tileset = Tileset()
		tileset.new_file()
		# Use an asymmetric image so the normal and flipped hashes differ.
		image = tuple(tuple((x * 13 + y) & 0xFF for x in range(8)) for y in range(8))
		flipped = tuple(tuple(reversed(row)) for row in image)
		tileset.vr4.add_image(flipped)

		_normal, flipped_ids = tileset.vr4.find_image_ids(image)
		self.assertEqual(len(flipped_ids), 1)

		flipped_ids.append(1234)

		_normal2, flipped_ids2 = tileset.vr4.find_image_ids(image)
		self.assertNotIn(
			1234, flipped_ids2,
			'find_image_ids must also return an independent list for the '
			'flipped-hash side.',
		)


if __name__ == '__main__':
	unittest.main()
