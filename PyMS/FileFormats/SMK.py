
from ..Utilities.fileutils import load_file
from ..Utilities.PyMSError import PyMSError

import struct

# http://wiki.multimedia.cx/index.php?title=Smacker


# import BMP,sys

class SMKAudioInfo:
	FLAG_COMPRESS_BINK1 = (1 << 26)
	FLAG_COMPRESS_BINK2 = (1 << 27)
	FLAG_CHANNELS = (1 << 28)
	FLAG_BIT_DEPTH = (1 << 29)
	FLAG_HAS_AUDIO = (1 << 30)
	FLAG_COMPRESSED = (1 << 31)

	COMPRESSION_NONE = 0
	COMPRESSION_SMK = 1
	COMPRESSION_BINK = 2 # Unsupported

	def __init__(self):
		self.has_audio = False
		self.compressed = SMKAudioInfo.COMPRESSION_NONE
		self.bit_depth = 8
		self.channels = 1
		self.rate = 0

	def load_info(self, info):
		self.has_audio = ((info & SMKAudioInfo.FLAG_HAS_AUDIO) == SMKAudioInfo.FLAG_HAS_AUDIO)
		self.compressed = SMKAudioInfo.COMPRESSION_NONE
		if info & SMKAudioInfo.FLAG_COMPRESSED:
			self.compressed = SMKAudioInfo.COMPRESSION_SMK
		if info & (SMKAudioInfo.FLAG_COMPRESS_BINK1 | SMKAudioInfo.FLAG_COMPRESS_BINK2):
			self.compressed = SMKAudioInfo.COMPRESSION_BINK
		if info & SMKAudioInfo.FLAG_BIT_DEPTH:
			self.bit_depth = 16
		else:
			self.bit_depth = 8
		if info & SMKAudioInfo.FLAG_CHANNELS:
			self.channels = 2
		else:
			self.channels = 1
		self.rate = (info & 0x00FFFFFF)

class SMKFrameInfo:
	FLAG_KEYFRAME = (1 << 0)
	FLAG_UNKNOWN = (1 << 1)

	TYPE_PALETTE = (1 << 0)
	TYPE_AUDIO_TRACK_0 = (1 << 1)
	TYPE_AUDIO_TRACK_1 = (1 << 2)
	TYPE_AUDIO_TRACK_2 = (1 << 3)
	TYPE_AUDIO_TRACK_3 = (1 << 4)
	TYPE_AUDIO_TRACK_4 = (1 << 5)
	TYPE_AUDIO_TRACK_5 = (1 << 6)
	TYPE_AUDIO_TRACK_6 = (1 << 7)

	def __init__(self):
		self.keyframe = False
		self.unknown = False
		self.chunk_size = 0
		self.type = 0

	def load_info(self, info, frame_type):
		self.keyframe = ((info & SMKFrameInfo.FLAG_KEYFRAME) == SMKFrameInfo.FLAG_KEYFRAME)
		self.unknown = ((info & SMKFrameInfo.FLAG_UNKNOWN) == SMKFrameInfo.FLAG_UNKNOWN)
		self.chunk_size = (info & 0xFFFFFFFC)
		self.type = frame_type

class SMKFrame:
	def __init__(self):
		self.audio = None
		self.palette = None
		self.image = None

class BitStream:
	def __init__(self, data):
		self.data = data
		self.byte = 0
		self.bit = 0

	def read(self, read_bits):
		value = 0
		bit = 0
		while read_bits:
			v = struct.unpack('<B', self.data[self.byte])[0]
			read = min(read_bits,8-self.bit)
			for read_bit in range(self.bit,self.bit+read):
				if read_bit > bit:
					value |= (v & (1 << read_bit)) >> (read_bit - bit)
				else:
					value |= (v & (1 << read_bit)) << (bit - read_bit)
				bit += 1
			self.bit += read
			if self.bit == 8:
				self.byte += 1
				self.bit = 0
			read_bits -= read
		return value

class HuffNode:
	def __init__(self):
		self.branch0 = None
		self.branch1 = None
		self.value = None
		self.escape_code = None

class HuffTree:
	def __init__(self, bit_stream):
		self.root = None
		if bit_stream.read(1):
			def build_node(node, d=0):
				if bit_stream.read(1):
					node.branch0 = HuffNode()
					build_node(node.branch0,d+1)
					node.branch1 = HuffNode()
					build_node(node.branch1,d+1)
				else:
					node.value = bit_stream.read(8)
					node.escape_code = 0xFF
			self.root = HuffNode()
			build_node(self.root)
		if bit_stream.read(1):
			raise PyMSError('HuffTree', "Couldn't read from bit stream")

	def lookup(self, bit_stream, node=None):
		value = None
		if node == None:
			node = self.root
		if node.branch0 == None:
			value = node.value
		elif bit_stream.read(1):
			value = self.lookup(bit_stream, node.branch1)
		else:
			value = self.lookup(bit_stream, node.branch0)
		return value

class BigHuffTree:
	def __init__(self, bit_stream):
		self.root = None
		self.cache = None
		if bit_stream.read(1):
			tree_low = HuffTree(bit_stream)
			tree_high = HuffTree(bit_stream)
			self.cache = [0,0,0]
			for i in range(3):
				low = bit_stream.read(8)
				high = bit_stream.read(8)
				self.cache[i] = low | (high << 8)
			def build_node(node, d=0):
				if bit_stream.read(1):
					node.branch0 = HuffNode()
					build_node(node.branch0,d+1)
					node.branch1 = HuffNode()
					build_node(node.branch1,d+1)
				else:
					low = tree_low.lookup(bit_stream)
					high = tree_high.lookup(bit_stream)
					node.value = low | (high << 8)
					if node.value == self.cache[0]:
						node.escape_code = 0
					elif node.value == self.cache[1]:
						node.escape_code = 1
					elif node.value == self.cache[2]:
						node.escape_code = 2
					else:
						node.escape_code = 0xFF
			self.root = HuffNode()
			build_node(self.root)
		if bit_stream.read(1):
			raise PyMSError('BigHuffTree', "Couldn't read from bit stream")

	def lookup(self, bit_stream, node=None):
		value = None
		if node == None:
			node = self.root
		if node.branch0 == None:
			if node.escape_code != 0xFF:
				value = self.cache[node.escape_code]
			else:
				value = node.value
			if self.cache[0] != value:
				self.cache[2] = self.cache[1]
				self.cache[1] = self.cache[0]
				self.cache[0] = value
		elif bit_stream.read(1):
			value = self.lookup(bit_stream, node.branch1)
		else:
			value = self.lookup(bit_stream, node.branch0)
		return value

	def reset_cache(self):
		self.cache = [0,0,0]

class SMK:
	SMK2 = 2
	SMK4 = 4

	SMK_FLAG_RING_FRAME = (1 << 0)
	SMK_FLAG_Y_INTERLACE = (1 << 1)
	SMK_FLAG_Y_DOUBLE = (1 << 2)

	RGB_LOOKUP = [
		0x00, 0x04, 0x08, 0x0C, 0x10, 0x14, 0x18, 0x1C,
		0x20, 0x24, 0x28, 0x2C, 0x30, 0x34, 0x38, 0x3C,
		0x41, 0x45, 0x49, 0x4D, 0x51, 0x55, 0x59, 0x5D,
		0x61, 0x65, 0x69, 0x6D, 0x71, 0x75, 0x79, 0x7D,
		0x82, 0x86, 0x8A, 0x8E, 0x92, 0x96, 0x9A, 0x9E,
		0xA2, 0xA6, 0xAA, 0xAE, 0xB2, 0xB6, 0xBA, 0xBE,
		0xC3, 0xC7, 0xCB, 0xCF, 0xD3, 0xD7, 0xDB, 0xDF,
		0xE3, 0xE7, 0xEB, 0xEF, 0xF3, 0xF7, 0xFB, 0xFF
	]

	VIDEO_BLOCK_TYPE_MONO = 0
	VIDEO_BLOCK_TYPE_FULL = 1
	VIDEO_BLOCK_TYPE_FULL_DOUBLE = 101
	VIDEO_BLOCK_TYPE_FULL_HALF = 102
	VIDEO_BLOCK_TYPE_UNCHANGED = 2
	VIDEO_BLOCK_TYPE_SOLID = 3

	VIDEO_BLOCK_SIZE_LOOKUP = [
		1,     2,    3,    4,    5,    6,    7,    8,
		9,    10,   11,   12,   13,   14,   15,   16,
		17,   18,   19,   20,   21,   22,   23,   24,
		25,   26,   27,   28,   29,   30,   31,   32,
		33,   34,   35,   36,   37,   38,   39,   40,
		41,   42,   43,   44,   45,   46,   47,   48,
		49,   50,   51,   52,   53,   54,   55,   56,
		57,   58,   59,  128,  256,  512, 1024, 2048
	]

	def __init__(self):
		self.version = 2
		self.width = 0
		self.height = 0
		self.frames = 0
		self.fps = 0
		self.flags = 0
		self.current_frame = 0
		self.last_frame = 0
		self.audio_info = None
		self.frame_info = None
		self.tree_mmap = None
		self.tree_mclr = None
		self.tree_full = None
		self.tree_type = None
		self.frame_data = None

		self.last_palette = None
		self.frame_cache = None

	def load_file(self, file):
		data = load_file(file, 'SMK')
		try:
			self.load_data(data)
		except PyMSError as e:
			raise e
		except:
			raise PyMSError('Load',"Unsupported SMK file '%s', could possibly be corrupt" % file)

	def load_data(self, data):
		signature,width,height,frames,framerate,smk_flags = struct.unpack('<4s3LlL', data[:24])
		if not signature in ('SMK2', 'SMK4'):
			raise PyMSError('Load',"Not an SMK file (no SMK header)")
		version = SMK.SMK2
		if signature == 'SMK4':
			version = SMK.SMK4
		if smk_flags & SMK.SMK_FLAG_RING_FRAME:
			frames += 1
		if framerate > 0:
			fps = 1000 / framerate
		elif framerate < 0:
			fps = 100000 / -framerate
		else:
			fps = 10
		_audio_sizes = struct.unpack('<7L', data[24:52]) # Unused?
		trees_size,_mmap_size,_mclr_size,_full_size,_type_size = struct.unpack('<5L', data[52:72])
		audio_rates = struct.unpack('<7L', data[72:100])
		audio_info = []
		for v in audio_rates:
			info = SMKAudioInfo()
			info.load_info(v)
			audio_info.append(info)
		o = 104
		frame_sizes = struct.unpack('<%dL' % frames, data[o:o+4*frames])
		o += 4*frames
		frame_types = struct.unpack('<%dB' % frames, data[o:o+frames])
		o += frames
		frame_info = []
		for i,t in zip(frame_sizes,frame_types):
			info = SMKFrameInfo()
			info.load_info(i,t)
			frame_info.append(info)
		# Load Trees
		stream = BitStream(data[o:o+trees_size])
		o += trees_size
		tree_mmap = BigHuffTree(stream)
		tree_mclr = BigHuffTree(stream)
		tree_full = BigHuffTree(stream)
		tree_type = BigHuffTree(stream)
		frame_data = []
		for f in frame_info:
			frame_data.append(data[o:o+f.chunk_size])
			o += f.chunk_size

		self.version = version
		self.width = width
		self.height = height
		self.frames = frames
		self.fps = fps
		self.flags = smk_flags
		self.current_frame = 0
		self.last_frame = 0
		self.audio_info = audio_info
		self.frame_info = frame_info
		self.tree_mmap = tree_mmap
		self.tree_mclr = tree_mclr
		self.tree_full = tree_full
		self.tree_type = tree_type
		self.frame_data = frame_data
		self.last_palette = None
		self.frame_cache = {}

	def load_palette(self, data):
		# print('Load Palette')
		_frame_info = self.frame_info[self.current_frame]
		last_frame = None
		if self.current_frame:
			last_frame = self.frame_cache[self.current_frame-1]
		palette = []
		i = 0
		o = 0
		while len(palette) < 256:
			r = struct.unpack('<B', data[o])[0]
			o += 1
			if r & 0xC0:
				copy = (r & 0x7F) + 1
				if r & 0x40:
					i = struct.unpack('<B', data[o])[0]
					o += 1
				if last_frame:
					palette.extend(last_frame.palette[i:i+copy])
				else:
					palette.extend(((0,0,0),) * copy)
				i += copy
			else:
				g,b = struct.unpack('<BB', data[o:o+2])
				o += 2
				palette.append((SMK.RGB_LOOKUP[r],SMK.RGB_LOOKUP[g],SMK.RGB_LOOKUP[b]))
		frame = self.frame_cache[self.current_frame]
		frame.palette = palette

	def load_audio(self, data):
		# print('Load Audio')
		pass

	def load_image(self, data):
		# print('Load Video')
		frame = self.frame_cache[self.current_frame]
		frame.image = [[0] * self.width for _ in range(self.height)]
		bit_stream = BitStream(data)
		x,y = 0,0
		# TEST = 0
		for tree in (self.tree_mmap,self.tree_mclr,self.tree_full,self.tree_type):
			tree.reset_cache()
		while y < self.height:
			unpack = self.tree_type.lookup(bit_stream)
			block_type = ((unpack & 0x0003))
			block_len = ((unpack & 0x00FC) >> 2)
			type_data = ((unpack & 0xFF00) >> 8)
			if block_type == SMK.VIDEO_BLOCK_TYPE_FULL and self.version == SMK.SMK4:
				if bit_stream.read(1):
					block_type = SMK.VIDEO_BLOCK_TYPE_FULL_DOUBLE
				elif bit_stream.read(1):
					block_type = SMK.VIDEO_BLOCK_TYPE_FULL_HALF
			size = SMK.VIDEO_BLOCK_SIZE_LOOKUP[block_len]
			for _ in range(size):
				# print(((TEST,i),(x,y),block_type,block_len,size,type_data))
				if block_type == SMK.VIDEO_BLOCK_TYPE_MONO:
					unpack = self.tree_mclr.lookup(bit_stream)
					high = (unpack & 0xFF00) >> 8
					low = (unpack & 0x00FF)
					mmap = self.tree_mmap.lookup(bit_stream)
					check = (1 << 0)
					for dy in range(4):
						for dx in range(4):
							if y+dy < self.height and x+dx < self.width:
								if mmap & check:
									frame.image[y+dy][x+dx] = high
								else:
									frame.image[y+dy][x+dx] = low
							check <<= 1
				elif block_type == SMK.VIDEO_BLOCK_TYPE_FULL:
					for dy in range(4):
						first = self.tree_full.lookup(bit_stream)
						second = self.tree_full.lookup(bit_stream)
						if y+dy < self.height:
							if x+3 < self.width:
								frame.image[y+dy][x+3] = ((first & 0xFF00) >> 8)
								if x+2 < self.width:
									frame.image[y+dy][x+2] = (first & 0x00FF)
									if x+1 < self.width:
										frame.image[y+dy][x+1] = ((second & 0xFF00) >> 8)
										frame.image[y+dy][x] = (second & 0x00FF)
				elif block_type == SMK.VIDEO_BLOCK_TYPE_UNCHANGED:
					last_frame = None
					if self.current_frame:
						last_frame = self.frame_cache[self.current_frame-1]
					for dy in range(4):
						for dx in range(4):
							if y+dy < self.height and x+dx < self.width:
								color = 0
								if last_frame:
									color = last_frame.image[y+dy][x+dx]
								frame.image[y+dy][x+dx] = color
				elif block_type == SMK.VIDEO_BLOCK_TYPE_SOLID:
					for dy in range(4):
						for dx in range(4):
							if y+dy < self.height and x+dx < self.width:
								frame.image[y+dy][x+dx] = type_data
				elif block_type == SMK.VIDEO_BLOCK_TYPE_FULL_DOUBLE:
					# print('VIDEO_BLOCK_TYPE_FULL_DOUBLE')
					pass
				elif block_type == SMK.VIDEO_BLOCK_TYPE_FULL_HALF:
					# print('VIDEO_BLOCK_TYPE_FULL_HALF')
					pass
				x += 4
				if x >= self.width:
					x = 0
					y += 4
				# bmp = BMP.BMP()
				# bmp.load_data(frame.image, frame.palette)
				# bmp.save_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/glue/mainmenu/editoron%d-%d.bmp' % (self.current_frame, TEST))
				# TEST += 1

	def get_frame(self):
		if self.current_frame in self.frame_cache:
			return self.frame_cache[self.current_frame]
		frame = SMKFrame()
		self.frame_cache[self.current_frame] = frame
		o = 0
		chunk = self.frame_data[self.current_frame]
		frame_info = self.frame_info[self.current_frame]
		if frame_info.type & SMKFrameInfo.TYPE_PALETTE:
			size = struct.unpack('<B', chunk[o])[0] * 4 - 1
			o += 1
			self.load_palette(chunk[o:o+size])
			o += size
		else:
			last_frame = None
			if self.current_frame:
				last_frame = self.frame_cache[self.current_frame-1]
			if last_frame:
				frame.palette = last_frame.palette
			else:
				frame.palette = ((0,0,0),) * 256
		for t,audio_info in enumerate(self.audio_info):
			if frame_info.type & (1 << (t + 1)) and audio_info.has_audio:
				size = struct.unpack('<L', chunk[o:o+4])[0] - 4
				o += 4
				self.load_audio(chunk[o:o+size])
				o += size
		self.load_image(chunk[o:])
		return self.frame_cache[self.current_frame]

	def seek_keyframe(self, frame):
		self.current_frame = frame
		while self.current_frame > 0 and not self.frame_info[self.current_frame].keyframe:
			self.current_frame -= 1

	def next_frame(self):
		if not self.current_frame in self.frame_cache:
			self.get_frame()
		self.current_frame += 1
		if self.current_frame == self.frames:
			self.current_frame = 0

	# def save_file(self, file):
	# 	data = self.save_data()
	# 	try:
	# 		f = AtomicWriter(file, 'wb')
	# 	except:
	# 		raise
	# 	f.write(data)
	# 	f.close()

	# def save_data(self):
	# 	pass

# if __name__ == '__main__':
# 	sys.stdout = open('/Users/zachzahos/Documents/Projects/PyMS/Libs/stdeo.txt','w')
# 	smk = SMK()

# 	smk.load_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/glue/mainmenu/editoron.smk')
# 	frame = smk.get_frame()
# 	bmp = BMP.BMP()
# 	bmp.load_data(frame.image, frame.palette)
# 	bmp.save_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/glue/mainmenu/editoron0.bmp')

# 	smk.load_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/glue/mainmenu/single.smk')
	# for f in range(smk.frames):
	# 	frame = smk.get_frame()
	# 	bmp = BMP.BMP()
	# 	bmp.load_data(frame.image, frame.palette)
	# 	bmp.save_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/glue/mainmenu/frame%d.bmp' % f)
	# 	smk.next_frame()
