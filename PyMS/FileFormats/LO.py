
from ..Utilities.PyMSError import PyMSError
from ..Utilities import IO

import struct, re

class LO:
	def __init__(self) -> None:
		self.frames = [[[0,0]]]

	def load(self, any_input: IO.AnyInputBytes) -> None:
		with IO.InputBytes(any_input) as input_bytes:
			data = input_bytes.read()
		try:
			frames,overlays = tuple(int(v) for v in struct.unpack('<LL', data[:8]))
			framedata: list[list[list[int]]] = []
			for frame in range(frames):
				framedata.append([])
				offset = struct.unpack('<L', data[8+4*frame:12+4*frame])[0]
				for _ in range(overlays):
					framedata[-1].append(list(int(v) for v in struct.unpack('bb', data[offset:offset+2])))
					offset += 2
			self.frames = framedata
		except Exception as exc:
			raise PyMSError('Load', "Unsupported LO* file, could possibly be corrupt") from exc

	def interpret(self, any_input: IO.AnyInputText) -> None:
		with IO.InputText(any_input) as input_text:
			data = input_text.readlines()
		frames: list[list[list[int]]] = []
		framedata = False
		overlays = -1
		for n,l in enumerate(data):
			if len(l) > 1:
				line = l.strip().split('#',1)[0]
				if line:
					if framedata:
						if line == 'Frame:':
							if overlays == -1:
								overlays = len(frames[-1])
							elif len(frames[-1]) != overlays:
								raise PyMSError('Interpreting', f"Frameset {len(frames)} has an invalid amount of overlays (expected {overlays}, got {len(frames[-1])})")
							frames.append([])
						else:
							valid = re.match(r'\((-?\d+),\s*(-?\d+)\)', line)
							if valid:
								try:
									x,y = int(valid.group(1)),int(valid.group(2))
									if x < -128 or x > 127 or y < -128 or y > 127:
										raise PyMSError('Interpreting', f"Invalid offset coordinates ({x},{y})", line=n, code=line)
									frames[-1].append([x,y])
									if len(frames[-1]) == overlays:
										framedata = False
								except PyMSError:
									raise
								except Exception as exc:
									raise PyMSError('Interpreting', f"Invalid offset coordinates ({x},{y})", line=n, code=line) from exc
							else:
								raise PyMSError('Interpreting', "Unknown line format, expected coordinates", line=n, code=line)
					elif line == 'Frame:':
						frames.append([])
						framedata = True
					else:
						raise PyMSError('Interpreting', "Unknown line format", line=n, code=line)
		self.frames = frames

	def decompile(self, output: IO.AnyOutputText) -> None:
		with IO.OutputText(output) as f:
			for frame in self.frames:
				f.write('Frame:\n')
				for overlay in frame:
					f.write(f'    ({overlay[0]}, {overlay[1]})\n')
				f.write('\n')

	def save(self, output: IO.AnyOutputBytes) -> None:
		with IO.OutputBytes(output) as f:
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
