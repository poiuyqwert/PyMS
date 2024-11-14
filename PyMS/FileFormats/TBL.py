
from ..Utilities.PyMSError import PyMSError
from ..Utilities.fileutils import load_file
from ..Utilities.AtomicWriter import AtomicWriter

import struct, re

from typing import BinaryIO

TBL_REF = """#----------------------------------------------------
# Misc.
#    <0> = End Substring
#    <9> = Tab
#   <10> = Newline
#   <18> = Right Align
#   <19> = Center Align
#   <27> = Escape Key
#   <35> = #
#   <60> = <
#   <62> = >
#
# Menu Screen Colors
#    <1> = Cyan
#    <2> = Cyan
#    <3> = Green
#    <4> = Light Green
#    <5> = Grey*
#    <6> = White
#    <7> = Red
#    <8> = Black*
#   <11> = Invisible*
#   <12> = Truncate
#   <14> = Black
#   <15> = Black
#   <16> = Black
#   <17> = Black
#   <20> = Invisible*
#   <21> = Black
#   <22> = Black
#   <23> = Black
#   <24> = Black
#   <25> = Black
#   <26> = Black/Cyan?
#   <27> = Black
#   <28> = Black
#
# In-game Colors
#    <1> = Cyan
#    <2> = Cyan
#    <3> = Yellow
#    <4> = White
#    <5> = Grey*
#    <6> = Red
#    <7> = Green
#    <8> = Red (Player 1)
#   <11> = Invisible*
#   <12> = Truncate
#   <14> = Blue (Player 2)
#   <15> = Teal (Player 3)
#   <16> = Purple (Player 4)
#   <17> = Orange (Player 5)
#   <20> = Invisible*
#   <21> = Brown (Player 6)
#   <22> = White (Player 7)
#   <23> = Yellow (Player 8)
#   <24> = Green (Player 9)
#   <25> = Brighter Yellow (Player 10)
#   <26> = Cyan (Player 12)
#   <27> = Pinkish (Player 11)
#   <28> = Dark Cyan
#   <29> = Greygreen
#   <30> = Bluegrey
#   <31> = Turquiose
#
# Hotkey Types
#    <0> = Label Only, no Requirements
#    <1> = Minerals, Gas, Supply (Unit/Building)
#    <2> = Upgrade Research
#    <3> = Spell
#    <4> = Technology Research
#    <5> = Minerals, Gas (Guardian/Devourer Aspect)
#
# * Starcraft will ignore all color tags after this.
#----------------------------------------------------
"""

DEF_DECOMPILE = ''.join([chr(x) for x in range(32)]) + '#<>'

def compile_string(string: str) -> str:
	def special_chr(o):
		c = int(o.group(1)) 
		if -1 > c or 255 < c:
			return o.group(0)
		return chr(c)
	return re.sub(r'<(\d+)>', special_chr, string)

def decompile_string(string: str, exclude: str = '', include: str = '') -> str:
	def special_chr(o):
		return '<%s>' % ord(o.group(0))
	decompile = DEF_DECOMPILE + include
	if exclude:
		decompile = re.sub('[%s]' % re.escape(exclude),'',decompile)
	return re.sub('([%s])' % decompile, special_chr, string)

class TBL:
	def __init__(self) -> None:
		self.strings: list[str] = []

	def load_file(self, file: str | BinaryIO) -> None:
		data = load_file(file, 'TBL')
		try:
			n = int(struct.unpack('<H', data[:2])[0])
			offsets = list(int(v) for v in struct.unpack('<%sH' % n, data[2:2+2*n]))
			findlen = list(offsets) + [len(data)]
			findlen.sort(reverse=True)
			lengths: dict[int, int] = {}
			for i in range(1,len(findlen)):
				start = findlen[i]
				if not start in lengths:
					end = findlen[i-1]
					lengths[start] = end-start
			strings: list[str] = []
			for i in range(len(offsets)):
				o = offsets[i]
				l = lengths[o]
				strings.append(data[o:o+l].decode('utf-8'))
			self.strings = strings
		except:
			raise PyMSError('Load',"Unsupported TBL file '%s', could possibly be corrupt" % file)

	def interpret(self, file: str) -> None:
		try:
			f = open(file,'r')
			lines = f.readlines()
			f.close()
		except:
			raise PyMSError('Interpreting',"Could not load file '%s'" % file)
		strings: list[str] = []
		for l in lines:
			line = l.split('#',1)[0]
			if line:
				if len(strings) == 65536:
					raise PyMSError('Interpreting',"There are too many string entries (max entries is 65536)")
				s = compile_string(line.rstrip('\r\n'))
				strings.append(s)
		self.strings = strings

	def save_data(self) -> bytes:
		o = 2 + 2 * len(self.strings)
		header = struct.pack('<H', len(self.strings))
		data = b''
		for s in self.strings:
			if not s.endswith('\x00'):
				s += '\x00'
			header += struct.pack('<H', o)
			data += s.encode('utf-8')
			o += len(s)
		return header + data

	def compile(self, file: str) -> None:
		try:
			f = AtomicWriter(file)
		except:
			raise PyMSError('Compile',"Could not load file '%s'" % file)
		data = self.save_data()
		f.write(data)
		f.close()

	def decompile(self, file: str, ref: bool = False) -> None:
		try:
			f = AtomicWriter(file)
		except:
			raise PyMSError('Decompile',"Could not load file '%s'" % file)
		if ref:
			f.write(TBL_REF.encode())
		for s in self.strings:
			f.write((decompile_string(s) + '\n').encode())
		f.close()

#t = TBL()
#t.load_file('Data\stat_txt.tbl')
#t.decompile('test.txt')
# t.interpret('test.txt')
# t.compile('test.tbl')
# t.compile('test.tbl')
# o = open('out.txt','w')
# def getord(o):
   # return '<%s>' % ord(o.group(0))
# for s in t.strings:
   # o.write(re.sub('([\x00\x01\x02\x03\x04\x05\x06\x07\x08<>])', getord, s) + '\n')
