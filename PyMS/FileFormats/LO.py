
from ..Utilities.fileutils import load_file
from ..Utilities.PyMSError import PyMSError
from ..Utilities.AtomicWriter import AtomicWriter

import struct, re

from typing import BinaryIO, TextIO, cast

class LO:
	def __init__(self): # type: () -> None
		self.frames = [[[0,0]]]

	def load_file(self, file): # type: (str | BinaryIO) -> None
		data = load_file(file, 'LO*')
		try:
			frames,overlays = tuple(int(v) for v in struct.unpack('<LL', data[:8]))
			framedata = [] # type: list[list[list[int]]]
			for frame in range(frames):
				framedata.append([])
				offset = struct.unpack('<L', data[8+4*frame:12+4*frame])[0]
				for _ in range(overlays):
					framedata[-1].append(list(int(v) for v in struct.unpack('bb', data[offset:offset+2])))
					offset += 2
			self.frames = framedata
		except:
			raise PyMSError('Load',"Unsupported LO* file '%s', could possibly be corrupt" % file)

	def interpret(self, file): # type: (str | TextIO) -> None
		if isinstance(file, str):
			try:
				f = open(file,'r')
				data = f.readlines()
				f.close()
			except:
				raise PyMSError('Interpreting',"Could not load file '%s'" % file)
		else:
			data = file.readlines()
		frames = [] # type: list[list[list[int]]]
		framedata = False
		overlays = -1
		for n,l in enumerate(data):
			if len(l) > 1:
				line = l.strip().split('#',1)[0]
				if line:
					if framedata:
						if line == 'Frame:':
							if overlays != -1:
								if len(frames[-1]) != overlays:
									raise PyMSError('Interpreting',"Frameset %s has an invalid amount of overlays (expected %s, got %s)" % (len(frames), overlays, len(frames[-1])))
								overlays = len(frames[-1])
							frames.append([])
						else:
							valid = re.match(r'\((-?\d+),\s*(-?\d+)\)', line)
							if valid:
								try:
									x,y = int(valid.group(1)),int(valid.group(2))
									if -127 > x > 127 or -127 > y > 127:
										raise Exception()
									frames[-1].append([x,y])
									if len(frames[-1]) == overlays:
										framedata = False
								except:
									raise PyMSError('Interpreting',"Invalid offset coordinates (%s,%s)" % (x,y),n,line)
							else:
								raise PyMSError('Interpreting',"Unknown line format, expected coordinates",n,line)
					elif line == 'Frame:':
						frames.append([])
						framedata = True
					else:
						raise PyMSError('Interpreting',"Unknown line format",n,line)
		self.frames = frames

	def decompile(self, file): # type: (str | TextIO) -> None
		if isinstance(file, str):
			try:
				f = cast(TextIO, AtomicWriter(file, 'w'))
			except:
				raise PyMSError('Decompile',"Could not open file '%s'" % file)
		else:
			f = file
		for frame in self.frames:
			f.write('Frame:\n')
			for overlay in frame:
				f.write('    (%s, %s)\n' % tuple(overlay))
			f.write('\n')
		f.close()

	def compile(self, file): # type: (str) -> None
		try:
			f = AtomicWriter(file, 'wb')
		except:
			raise PyMSError('Compile',"Could not open file '%s'" % file)
		overlays = len(self.frames[0])
		f.write(struct.pack('<LL', len(self.frames), overlays))
		data = b''
		offsets = b''
		offset = 8 + 4 * len(self.frames)
		for frame in self.frames:
			offsets += struct.pack('<L', offset)
			for overlay in frame:
				data += struct.pack('<bb', *overlay)
			offset += 2 * overlays
		f.write(offsets + data)
		f.close()
