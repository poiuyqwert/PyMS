
import operator as _operator

class FileType(tuple):
	WILDCARD = '*'
	EXTSEP = '.' # Does Tkinter expect `os.extsep` or '.'?
	SEPARATOR = ';'

	@staticmethod
	def include_all_files(file_types): # type: (list[FileType]) -> list[FileType]
		all_files = FileType.all_files()
		if all_files in file_types:
			return file_types
		return file_types + [all_files]

	@staticmethod
	def default_extension(file_types): # type: (list[FileType]) -> (str | None)
		if not file_types:
			return None
		extension = file_types[0].extensions
		if FileType.SEPARATOR in extension:
			extension = extension.split(FileType.SEPARATOR)[0]
		if FileType.EXTSEP in extension:
			extension = FileType.EXTSEP.join(extension.split(FileType.EXTSEP)[1:])
		return extension

	@staticmethod
	def all_files(name='All Files'):
		return FileType(name, FileType.WILDCARD)

	@staticmethod
	def txt(name='Text Files'):
		return FileType(name, 'txt')

	@staticmethod
	def tbl(name='StarCraft Strings'):
		return FileType(name, 'tbl')

	@staticmethod
	def bin(name):
		return FileType(name, 'bin')

	@staticmethod
	def bin_ai(name='StarCraft AI Scripts'):
		return FileType.bin(name)

	@staticmethod
	def bin_dialog(name='StarCraft Dialogs'):
		return FileType.bin(name)

	@staticmethod
	def bin_iscript(name='StarCraft IScripts'):
		return FileType.bin(name)
	
	@staticmethod
	def mpq(name='MPQ Files'):
		return FileType(name, 'mpq')

	@staticmethod
	def mpq_all(name='All MPQ Files'):
		return FileType(name, 'mpq', 'exe', 'scm', 'scx')

	@staticmethod
	def exe(name='Executables'):
		return FileType(name, 'exe')

	@staticmethod
	def exe_mpq(name="Self-executing MPQ's"):
		return FileType.exe(name)

	@staticmethod
	def pal(name='RIFF, JASC, and StarCraft Palettes'):
		return FileType(name, 'pal')

	@staticmethod
	def pal_riff(name='RIFF Palettes'):
		return FileType.pal(name)

	@staticmethod
	def pal_jasc(name='JASC Palettes'):
		return FileType.pal(name)

	@staticmethod
	def pal_sc(name='StarCraft Palettes'):
		return FileType.pal(name)

	@staticmethod
	def pal_pcx(name='StarCraft Special Palettes'):
		return FileType.pcx(name)

	@staticmethod
	def wpe(name='StarCraft Tileset Palettes'):
		return FileType(name, 'wpe')

	@staticmethod
	def act(name='Adobe Color Table Palettes'):
		return FileType(name, 'act')

	@staticmethod
	def pcx(name='ZSoft PCX File'):
		return FileType(name, 'pcx')

	@staticmethod
	def bmp(name='8-Bit Bitmaps'):
		return FileType(name, 'bmp')

	@staticmethod
	def smk(name='Smacker Videos'):
		return FileType(name, 'smk')

	@staticmethod
	def dat(name='StarCraft DAT Files'):
		return FileType(name, 'dat')

	@staticmethod
	def grp(name='StarCraft Graphics'):
		return FileType(name, 'grp')

	@staticmethod
	def fnt(name='StarCraft Fonts'):
		return FileType(name, 'fnt')

	@staticmethod
	def got(name='StarCraft Game Templates'):
		return FileType(name, 'got')

	@staticmethod
	def trg(name='StarCraft Triggers'):
		return FileType(name, 'trg')

	@staticmethod
	def lo(name='All StarCraft Overlays'):
		return FileType(name, 'loa', 'lob', 'lod', 'lof', 'loo', 'los', 'lou', 'log', 'lol', 'lox')

	@staticmethod
	def loa(name='StarCraft Attack Overlays'):
		return FileType(name, 'loa')

	@staticmethod
	def lob(name='StarCraft Birth Overlays'):
		return FileType(name, 'lob')

	@staticmethod
	def lod(name='StarCraft Landing Dust Overlays'):
		return FileType(name, 'lod')

	@staticmethod
	def lof(name='StarCraft Fire Overlays'):
		return FileType(name, 'lof')

	@staticmethod
	def loo(name='StarCraft Powerup Overlays'):
		return FileType(name, 'loo')

	@staticmethod
	def los(name='StarCraft Shield/Smoke Overlays'):
		return FileType(name, 'los')

	@staticmethod
	def lou(name='StarCraft Liftoff Dust Overlays'):
		return FileType(name, 'lou')

	@staticmethod
	def log(name='Misc. StarCraft Overlays'):
		return FileType(name, 'log')

	@staticmethod
	def lol(name='Misc. StarCraft Overlays'):
		return FileType(name, 'lol')

	@staticmethod
	def lox(name='Misc. StarCraft Overlays'):
		return FileType(name, 'lox')

	@staticmethod
	def maps(name='All StarCraft Maps'):
		return FileType(name, 'chk', 'scm', 'scx')

	@staticmethod
	def chk(name='Raw StarCraft Maps'):
		return FileType(name, 'chk')

	@staticmethod
	def scm(name='StarCraft Maps'):
		return FileType(name, 'scm')

	@staticmethod
	def scx(name='BroodWar Maps'):
		return FileType(name, 'scx')

	@staticmethod
	def wav(name='Waveform Audio Files'):
		return FileType(name, 'wav')

	@staticmethod
	def spk(name='StarCraft Parallax Files'):
		return FileType(name, 'spk')

	@staticmethod
	def cv5(name='StarCraft Tilesets'):
		return FileType(name, 'cv5')

	def __new__(self, name, *extensions): # tyoe: (str, *str) -> FileType
		extensions = list(extensions) # type: list[str]
		for i, extension in enumerate(extensions):
			if extension and extension != FileType.WILDCARD and not extension.startswith(FileType.WILDCARD + FileType.EXTSEP):
				extensions[i] = (FileType.WILDCARD if extension.startswith(FileType.EXTSEP) else FileType.WILDCARD + FileType.EXTSEP) + extension
		name += ' (%s)' % ', '.join(extension[1:] for extension in extensions)
		return tuple.__new__(FileType, (name, FileType.SEPARATOR.join(extensions)))

	name = property(_operator.itemgetter(0)) # type: str
	
	extensions = property(_operator.itemgetter(1)) #type: str

	# Both `name` and `extensions` must be equal, unless `extensions == FileType.WILDCARD` then the names don't need to match
	def __eq__(self, other):
		if not isinstance(other, FileType):
			return False
		if not self.extensions == other.extensions:
			return False
		if self.extensions == FileType.WILDCARD:
			return True
		if not self.name == other.name:
			return False
		return True

def main():
	f = FileType.maps()
	print(f[0])
	print(f.name)
	print(f[1])
	print(f.extensions)

if __name__ == '__main__':
	main()
