
from ...Utilities.utils import FFile
from ...FileFormats import GRP

import unittest

class Test_Save_And_Load(unittest.TestCase):
	def test_single_frame(self):
		width = 16
		height = 16
		image = list(range(y*width,(y+1)*width) for y in range(height))

		saved_file = FFile()

		save_grp = GRP.GRP()
		save_grp.load_data([image])
		save_grp.save_file(saved_file)

		load_grp = GRP.GRP()
		load_grp.load_file(saved_file)

		self.assertEqual(load_grp.width, width)
		self.assertEqual(load_grp.height, height)
		self.assertEqual(load_grp.images[0], image)

	def test_two_frames(self):
		width = 16
		height = 16
		image = list(range(y*width,(y+1)*width) for y in range(height))

		saved_file = FFile()

		save_grp = GRP.GRP()
		save_grp.load_data([image, image])
		save_grp.save_file(saved_file)

		load_grp = GRP.GRP()
		load_grp.load_file(saved_file)

		self.assertEqual(load_grp.width, width)
		self.assertEqual(load_grp.height, height)
		self.assertEqual(load_grp.images[0], image)
		self.assertEqual(load_grp.images[1], image)

	def test_frame_offset(self):
		width = 5
		height = 5
		image = [
			[0,0,0,0,0],
			[0,0,0,0,0],
			[0,0,1,0,0],
			[0,0,0,0,0],
			[0,0,0,0,0],
		]

		saved_file = FFile()

		save_grp = GRP.GRP()
		save_grp.load_data([image])
		save_grp.save_file(saved_file)

		load_grp = GRP.GRP()
		load_grp.load_file(saved_file)

		self.assertEqual(load_grp.width, width)
		self.assertEqual(load_grp.height, height)
		self.assertEqual(load_grp.images[0], image)


	def test_frame_offsets(self):
		width = 5
		height = 5
		images = [
			[
				[0,0,0,0,0],
				[0,1,0,0,0],
				[0,0,0,0,0],
				[0,0,0,0,0],
				[0,0,0,0,0]
			],
			[
				[0,0,0,0,0],
				[0,0,0,0,0],
				[0,0,0,0,0],
				[0,0,0,1,0],
				[0,0,0,0,0]
			]
		]

		saved_file = FFile()

		save_grp = GRP.GRP()
		save_grp.load_data(images)
		save_grp.save_file(saved_file)

		load_grp = GRP.GRP()
		load_grp.load_file(saved_file)

		self.assertEqual(load_grp.width, width)
		self.assertEqual(load_grp.height, height)
		self.assertEqual(load_grp.images[0], images[0])
		self.assertEqual(load_grp.images[1], images[1])

	def test_empty_frame(self):
		width = 5
		height = 5
		image = [
			[0,0,0,0,0],
			[0,0,0,0,0],
			[0,0,0,0,0],
			[0,0,0,0,0],
			[0,0,0,0,0],
		]

		saved_file = FFile()

		save_grp = GRP.GRP()
		save_grp.load_data([image])
		save_grp.save_file(saved_file)

		load_grp = GRP.GRP()
		load_grp.load_file(saved_file)

		self.assertEqual(load_grp.width, width)
		self.assertEqual(load_grp.height, height)
		self.assertEqual(load_grp.images[0], image)
