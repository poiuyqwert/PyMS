
from ...FileFormats.SMK import SMK, SMKAudioInfo, SMKFrameInfo, SMKFrame, BitStream, HuffTree
from ...Utilities.PyMSError import PyMSError
from ..utils import resource_path

import io
import struct
import unittest

SAMPLE_SMK = 'UUjFid00.smk'


class _BitWriter:
	# Writes bits LSB-first to match how `BitStream.read` consumes them.
	def __init__(self) -> None:
		self.bits: list[int] = []

	def write(self, value: int, count: int) -> '_BitWriter':
		for i in range(count):
			self.bits.append((value >> i) & 1)
		return self

	def to_bytes(self) -> bytes:
		out = bytearray()
		for i in range(0, len(self.bits), 8):
			byte = 0
			for j, bit in enumerate(self.bits[i:i + 8]):
				byte |= bit << j
			out.append(byte)
		return bytes(out)


def _two_leaf_tree() -> HuffTree:
	writer = _BitWriter()
	writer.write(1, 1)              # has a tree
	writer.write(1, 1)              # root is internal
	writer.write(0, 1).write(0x41, 8)  # branch0 leaf
	writer.write(0, 1).write(0x42, 8)  # branch1 leaf
	writer.write(0, 1)             # end marker (0 = ok)
	return HuffTree(BitStream(writer.to_bytes()))


def _build_smk(*, sig: bytes = b'SMK2', width: int = 4, height: int = 4, frames: int = 1, framerate: int = 100, flags: int = 0) -> bytes:
	effective = frames + (1 if flags & SMK.SMK_FLAG_RING_FRAME else 0)
	header = struct.pack('<4s3LlL', sig, width, height, frames, framerate, flags)
	header += struct.pack('<7L', *([0] * 7))       # audio sizes (unused)
	header += struct.pack('<5L', 1, 0, 0, 0, 0)    # trees_size=1, others 0
	header += struct.pack('<7L', *([0] * 7))       # audio rates
	header += struct.pack('<L', 0)                 # dummy
	body = struct.pack(f'<{effective}L', *([0] * effective))  # frame sizes (chunk_size 0)
	body += struct.pack(f'<{effective}B', *([0] * effective))  # frame types
	body += b'\x00'  # 4 empty BigHuffTrees (each reads two 0 bits)
	return header + body


class Test_SMKAudioInfo_load_info(unittest.TestCase):
	def test_defaults(self) -> None:
		info = SMKAudioInfo()
		info.load_info(0)
		self.assertFalse(info.has_audio)
		self.assertEqual(info.compressed, SMKAudioInfo.COMPRESSION_NONE)
		self.assertEqual(info.bit_depth, 8)
		self.assertEqual(info.channels, 1)
		self.assertEqual(info.rate, 0)

	def test_has_audio_and_rate(self) -> None:
		info = SMKAudioInfo()
		info.load_info(SMKAudioInfo.FLAG_HAS_AUDIO | 22050)
		self.assertTrue(info.has_audio)
		self.assertEqual(info.rate, 22050)

	def test_smk_compression(self) -> None:
		info = SMKAudioInfo()
		info.load_info(SMKAudioInfo.FLAG_COMPRESSED)
		self.assertEqual(info.compressed, SMKAudioInfo.COMPRESSION_SMK)

	def test_bink_compression_overrides_smk(self) -> None:
		info = SMKAudioInfo()
		info.load_info(SMKAudioInfo.FLAG_COMPRESSED | SMKAudioInfo.FLAG_COMPRESS_BINK1)
		self.assertEqual(info.compressed, SMKAudioInfo.COMPRESSION_BINK)

	def test_bit_depth_and_channels(self) -> None:
		info = SMKAudioInfo()
		info.load_info(SMKAudioInfo.FLAG_BIT_DEPTH | SMKAudioInfo.FLAG_CHANNELS)
		self.assertEqual(info.bit_depth, 16)
		self.assertEqual(info.channels, 2)

	def test_rate_is_low_24_bits(self) -> None:
		info = SMKAudioInfo()
		info.load_info(0xFFFFFFFF)
		self.assertEqual(info.rate, 0x00FFFFFF)


class Test_SMKFrameInfo_load_info(unittest.TestCase):
	def test_defaults(self) -> None:
		info = SMKFrameInfo()
		info.load_info(0, 0)
		self.assertFalse(info.keyframe)
		self.assertFalse(info.unknown)
		self.assertEqual(info.chunk_size, 0)
		self.assertEqual(info.type, 0)

	def test_keyframe_and_unknown_flags(self) -> None:
		info = SMKFrameInfo()
		info.load_info(SMKFrameInfo.FLAG_KEYFRAME | SMKFrameInfo.FLAG_UNKNOWN, 0)
		self.assertTrue(info.keyframe)
		self.assertTrue(info.unknown)

	def test_chunk_size_masks_low_two_bits(self) -> None:
		info = SMKFrameInfo()
		info.load_info(0x107, 0)  # flags in low 2 bits, size rounds down to 0x104
		self.assertEqual(info.chunk_size, 0x104)

	def test_type_passed_through(self) -> None:
		info = SMKFrameInfo()
		info.load_info(0, SMKFrameInfo.TYPE_PALETTE)
		self.assertEqual(info.type, SMKFrameInfo.TYPE_PALETTE)


class Test_BitStream(unittest.TestCase):
	def test_full_byte_lsb_first(self) -> None:
		self.assertEqual(BitStream(b'\xAB').read(8), 0xAB)

	def test_sequential_reads(self) -> None:
		writer = _BitWriter().write(5, 3).write(200, 8).write(1, 1)
		stream = BitStream(writer.to_bytes())
		self.assertEqual(stream.read(3), 5)
		self.assertEqual(stream.read(8), 200)
		self.assertEqual(stream.read(1), 1)

	def test_multi_byte_value(self) -> None:
		# Little-endian across bytes.
		self.assertEqual(BitStream(b'\x01\x02').read(16), 0x0201)

	def test_single_bits(self) -> None:
		stream = BitStream(b'\x01')  # only bit 0 set
		self.assertEqual(stream.read(1), 1)
		self.assertEqual(stream.read(1), 0)


class Test_HuffTree(unittest.TestCase):
	def test_builds_structure(self) -> None:
		tree = _two_leaf_tree()
		assert tree.root.branch0 is not None and tree.root.branch1 is not None
		self.assertEqual(tree.root.branch0.value, 0x41)
		self.assertEqual(tree.root.branch1.value, 0x42)

	def test_lookup_branch0(self) -> None:
		# Navigate to branch0 with a 0 bit, then a 0 bit terminates at the leaf.
		self.assertEqual(_two_leaf_tree().lookup(BitStream(bytes([0b00]))), 0x41)

	def test_lookup_branch1(self) -> None:
		# A 1 bit navigates to branch1, then a 0 bit terminates.
		self.assertEqual(_two_leaf_tree().lookup(BitStream(bytes([0b01]))), 0x42)

	def test_end_marker_error(self) -> None:
		writer = _BitWriter().write(1, 1).write(0, 1).write(0x55, 8).write(1, 1)
		with self.assertRaises(PyMSError):
			HuffTree(BitStream(writer.to_bytes()))

	def test_lookup_stops_at_leaf_without_extra_bit(self) -> None:
		# A leaf is reached by its path bits alone; no trailing 0 is consumed.
		tree = _two_leaf_tree()
		stream = BitStream(bytes([0b1]))  # one bit: navigate to branch1
		self.assertEqual(tree.lookup(stream), 0x42)
		self.assertEqual(stream.bit, 1)  # only the single navigation bit was read

	def test_absent_tree_is_single_zero_leaf(self) -> None:
		# A 0 tag means no tree: it decodes as a degenerate single leaf of value 0,
		# and a lookup consuming no navigation bits returns that 0.
		writer = _BitWriter().write(0, 1).write(0, 1)  # no tree, then end marker
		tree = HuffTree(BitStream(writer.to_bytes()))
		self.assertIsNone(tree.root.branch0)
		self.assertEqual(tree.root.value, 0)
		self.assertEqual(tree.lookup(BitStream(b'\x00')), 0)


class Test_load_palette(unittest.TestCase):
	def _palette_for(self, data: bytes, current_frame: int = 0, last_palette: list | None = None) -> list:
		smk = SMK()
		smk.current_frame = current_frame
		smk.frame_info = [SMKFrameInfo() for _ in range(current_frame + 1)]
		smk.frame_cache = {current_frame: SMKFrame()}
		if current_frame and last_palette is not None:
			previous = SMKFrame()
			previous.palette = last_palette
			smk.frame_cache[current_frame - 1] = previous
		smk._load_palette(data)  # pylint: disable=protected-access
		return smk.frame_cache[current_frame].palette

	def test_literal_colors_use_rgb_lookup(self) -> None:
		data = b''.join(bytes([i % 64, (i * 2) % 64, (i * 3) % 64]) for i in range(256))
		palette = self._palette_for(data)
		self.assertEqual(len(palette), 256)
		self.assertEqual(palette[1], (SMK.RGB_LOOKUP[1], SMK.RGB_LOOKUP[2], SMK.RGB_LOOKUP[3]))

	def test_copy_run_without_previous_frame_is_black(self) -> None:
		# One literal then runs filling the remaining 255 entries.
		data = bytes([1, 2, 3]) + bytes([0xBF]) * 3 + bytes([0xBE])
		palette = self._palette_for(data)
		self.assertEqual(len(palette), 256)
		self.assertEqual(palette[0], (SMK.RGB_LOOKUP[1], SMK.RGB_LOOKUP[2], SMK.RGB_LOOKUP[3]))
		self.assertEqual(palette[1], (0, 0, 0))

	def test_copy_run_copies_from_previous_frame(self) -> None:
		previous = [(10, 20, 30)] * 256
		# A copy of 256 entries from the start of the previous frame's palette.
		data = bytes([0xBF]) * 4  # 4 runs of 64 = 256
		palette = self._palette_for(data, current_frame=1, last_palette=previous)
		self.assertEqual(len(palette), 256)
		self.assertEqual(palette[0], (10, 20, 30))


class Test_load_data(unittest.TestCase):
	def test_smk2(self) -> None:
		smk = SMK()
		smk.load_data(_build_smk(sig=b'SMK2', width=320, height=200))
		self.assertEqual(smk.version, SMK.SMK2)
		self.assertEqual((smk.width, smk.height), (320, 200))
		self.assertEqual(smk.frames, 1)

	def test_smk4(self) -> None:
		smk = SMK()
		smk.load_data(_build_smk(sig=b'SMK4'))
		self.assertEqual(smk.version, SMK.SMK4)

	def test_fps_positive_framerate(self) -> None:
		smk = SMK()
		smk.load_data(_build_smk(framerate=100))
		self.assertEqual(smk.fps, 10)

	def test_fps_negative_framerate(self) -> None:
		smk = SMK()
		smk.load_data(_build_smk(framerate=-50))
		self.assertEqual(smk.fps, 2000)

	def test_fps_zero_framerate(self) -> None:
		smk = SMK()
		smk.load_data(_build_smk(framerate=0))
		self.assertEqual(smk.fps, 10)

	def test_ring_frame_increments_count(self) -> None:
		smk = SMK()
		smk.load_data(_build_smk(frames=1, flags=SMK.SMK_FLAG_RING_FRAME))
		self.assertEqual(smk.frames, 2)

	def test_invalid_signature_raises(self) -> None:
		with self.assertRaises(PyMSError):
			SMK().load_data(_build_smk(sig=b'XXXX'))

	def test_builds_trees_and_info(self) -> None:
		smk = SMK()
		smk.load_data(_build_smk())
		assert smk.audio_info is not None and smk.frame_info is not None
		self.assertEqual(len(smk.audio_info), 7)
		self.assertEqual(len(smk.frame_info), 1)
		self.assertIsNotNone(smk.tree_mmap)
		self.assertIsNotNone(smk.tree_type)

	def test_load_file_accepts_binary_io(self) -> None:
		smk = SMK()
		smk.load_file(io.BytesIO(_build_smk()))
		self.assertEqual(smk.version, SMK.SMK2)


class Test_real_file(unittest.TestCase):
	def _load(self) -> SMK:
		smk = SMK()
		smk.load_file(resource_path(SAMPLE_SMK, __file__))
		return smk

	def test_header(self) -> None:
		smk = self._load()
		self.assertEqual(smk.version, SMK.SMK2)
		self.assertEqual((smk.width, smk.height), (60, 56))
		self.assertEqual(smk.frames, 10)
		self.assertEqual(smk.fps, 10)

	def test_get_frame_decodes_image_and_palette(self) -> None:
		smk = self._load()
		frame = smk.get_frame()
		self.assertEqual(len(frame.image), smk.height)
		self.assertEqual(len(frame.image[0]), smk.width)
		self.assertEqual(len(frame.palette), 256)
		# A real decoded frame has more than one distinct color.
		self.assertGreater(len({pixel for row in frame.image for pixel in row}), 1)

	def test_decodes_all_frames(self) -> None:
		# Exercises the full Huffman/BigHuffTree decode (including the move-to-front
		# cache) and the frame video-block decoder across every frame.
		smk = self._load()
		for _ in range(smk.frames):
			frame = smk.get_frame()
			self.assertEqual(len(frame.image), smk.height)
			self.assertEqual(len(frame.image[0]), smk.width)
			smk.next_frame()
		self.assertEqual(smk.current_frame, 0)  # wraps back to the start

	def test_get_frame_is_cached(self) -> None:
		smk = self._load()
		self.assertIs(smk.get_frame(), smk.get_frame())

	def test_seek_keyframe(self) -> None:
		smk = self._load()
		assert smk.frame_info is not None
		smk.seek_keyframe(smk.frames - 1)
		# Lands on a keyframe at or before the requested frame (or frame 0).
		self.assertTrue(smk.current_frame == 0 or smk.frame_info[smk.current_frame].keyframe)
		self.assertLessEqual(smk.current_frame, smk.frames - 1)
