
from __future__ import annotations

from ..utils import is_mac

__all__ = [
	'FileType',
]

class FileType(tuple[str, str]):
	WILDCARD = '*'
	EXTSEP = '.' # Does Tkinter expect `os.extsep` or '.'?
	SEPARATOR = ' '

	@staticmethod
	def include_all_files(file_types: list[FileType]) -> list[FileType]:
		all_files = FileType.all_files()
		if all_files in file_types:
			return file_types
		return file_types + [all_files]

	@staticmethod
	def default_extension(file_types: list[FileType]) -> (str | None):
		if not file_types:
			return None
		extension = file_types[0].extensions
		if FileType.SEPARATOR in extension:
			extension = extension.split(FileType.SEPARATOR)[0]
		if FileType.EXTSEP in extension:
			extension = FileType.EXTSEP.join(extension.split(FileType.EXTSEP)[1:])
		return extension

	@staticmethod
	def all_files(name: str = 'All Files') -> FileType:
		return FileType(name, FileType.WILDCARD)

	@staticmethod
	def txt(name: str = 'Text Files') -> FileType:
		return FileType(name, 'txt')

	@staticmethod
	def tbl(name: str = 'StarCraft Strings') -> FileType:
		return FileType(name, 'tbl')

	@staticmethod
	def bin(name: str) -> FileType:
		return FileType(name, 'bin')

	@staticmethod
	def bin_ai(name: str = 'StarCraft AI Scripts') -> FileType:
		return FileType.bin(name)

	@staticmethod
	def bin_dialog(name: str = 'StarCraft Dialogs') -> FileType:
		return FileType.bin(name)

	@staticmethod
	def bin_iscript(name: str = 'StarCraft IScripts') -> FileType:
		return FileType.bin(name)

	@staticmethod
	def mpq(name: str = 'MPQ Files') -> FileType:
		return FileType(name, 'mpq')

	@staticmethod
	def mpq_all(name: str = 'All MPQ Files') -> FileType:
		return FileType(name, 'mpq', 'exe', 'scm', 'scx')

	@staticmethod
	def exe(name: str = 'Executables') -> FileType:
		return FileType(name, 'exe')

	@staticmethod
	def exe_mpq(name: str = "FileType-executing MPQ's") -> FileType:
		return FileType.exe(name)

	@staticmethod
	def pal(name: str = 'RIFF, JASC, and StarCraft Palettes') -> FileType:
		return FileType(name, 'pal')

	@staticmethod
	def pal_riff(name: str = 'RIFF Palettes') -> FileType:
		return FileType.pal(name)

	@staticmethod
	def pal_jasc(name: str = 'JASC Palettes') -> FileType:
		return FileType.pal(name)

	@staticmethod
	def pal_sc(name: str = 'StarCraft Palettes') -> FileType:
		return FileType.pal(name)

	@staticmethod
	def pal_pcx(name: str = 'StarCraft Special Palettes') -> FileType:
		return FileType.pcx(name)

	@staticmethod
	def wpe(name: str = 'StarCraft Tileset Palettes') -> FileType:
		return FileType(name, 'wpe')

	@staticmethod
	def act(name: str = 'Adobe Color Table Palettes') -> FileType:
		return FileType(name, 'act')

	@staticmethod
	def pcx(name: str = 'ZSoft PCX File') -> FileType:
		return FileType(name, 'pcx')

	@staticmethod
	def bmp(name: str = '8-Bit Bitmaps') -> FileType:
		return FileType(name, 'bmp')

	@staticmethod
	def smk(name: str = 'Smacker Videos') -> FileType:
		return FileType(name, 'smk')

	@staticmethod
	def dat(name: str = 'StarCraft DAT Files') -> FileType:
		return FileType(name, 'dat')

	@staticmethod
	def grp(name: str = 'StarCraft Graphics') -> FileType:
		return FileType(name, 'grp')

	@staticmethod
	def fnt(name: str = 'StarCraft Fonts') -> FileType:
		return FileType(name, 'fnt')

	@staticmethod
	def got(name: str = 'StarCraft Game Templates') -> FileType:
		return FileType(name, 'got')

	@staticmethod
	def trg(name: str = 'StarCraft Triggers') -> FileType:
		return FileType(name, 'trg')

	@staticmethod
	def lo(name: str = 'All StarCraft Overlays') -> FileType:
		return FileType(name, 'loa', 'lob', 'lod', 'lof', 'loo', 'los', 'lou', 'log', 'lol', 'lox')

	@staticmethod
	def loa(name: str = 'StarCraft Attack Overlays') -> FileType:
		return FileType(name, 'loa')

	@staticmethod
	def lob(name: str = 'StarCraft Birth Overlays') -> FileType:
		return FileType(name, 'lob')

	@staticmethod
	def lod(name: str = 'StarCraft Landing Dust Overlays') -> FileType:
		return FileType(name, 'lod')

	@staticmethod
	def lof(name: str = 'StarCraft Fire Overlays') -> FileType:
		return FileType(name, 'lof')

	@staticmethod
	def loo(name: str = 'StarCraft Powerup Overlays') -> FileType:
		return FileType(name, 'loo')

	@staticmethod
	def los(name: str = 'StarCraft Shield/Smoke Overlays') -> FileType:
		return FileType(name, 'los')

	@staticmethod
	def lou(name: str = 'StarCraft Liftoff Dust Overlays') -> FileType:
		return FileType(name, 'lou')

	@staticmethod
	def log(name: str = 'Misc. StarCraft Overlays') -> FileType:
		return FileType(name, 'log')

	@staticmethod
	def lol(name: str = 'Misc. StarCraft Overlays') -> FileType:
		return FileType(name, 'lol')

	@staticmethod
	def lox(name: str = 'Misc. StarCraft Overlays') -> FileType:
		return FileType(name, 'lox')

	@staticmethod
	def maps(name: str = 'All StarCraft Maps') -> FileType:
		return FileType(name, 'chk', 'scm', 'scx')

	@staticmethod
	def chk(name: str = 'Raw StarCraft Maps') -> FileType:
		return FileType(name, 'chk')

	@staticmethod
	def scm(name: str = 'StarCraft Maps') -> FileType:
		return FileType(name, 'scm')

	@staticmethod
	def scx(name: str = 'BroodWar Maps') -> FileType:
		return FileType(name, 'scx')

	@staticmethod
	def wav(name: str = 'Waveform Audio Files') -> FileType:
		return FileType(name, 'wav')

	@staticmethod
	def spk(name: str = 'StarCraft Parallax Files') -> FileType:
		return FileType(name, 'spk')

	@staticmethod
	def cv5(name: str = 'StarCraft Tilesets') -> FileType:
		return FileType(name, 'cv5')

	@staticmethod
	def json(name: str = 'JSON') -> FileType:
		return FileType(name, 'json')

	def __new__(cls, name: str, *exts: str) -> FileType:
		extensions: list[str] = list(exts)
		for i, extension in enumerate(extensions):
			if extension and extension != FileType.WILDCARD and not extension.startswith(FileType.WILDCARD + FileType.EXTSEP):
				extensions[i] = (FileType.WILDCARD if extension.startswith(FileType.EXTSEP) else FileType.WILDCARD + FileType.EXTSEP) + extension
		if not is_mac():
			name += f' ({", ".join(extension[1:] for extension in extensions)})'
		return tuple.__new__(FileType, (name, FileType.SEPARATOR.join(extensions))) # type: ignore[type-var]

	@property
	def name(self) -> str:
		return self[0]

	@property
	def extensions(self) -> str:
		return self[1]

	@property
	def extensions_tuple(self) -> tuple[str, ...]:
		return tuple(self.extensions.split(FileType.SEPARATOR))

	# Both `name` and `extensions` must be equal, unless `extensions == FileType.WILDCARD` then the names don't need to match
	def __eq__(self, other: object) -> bool:
		if not isinstance(other, FileType):
			return False
		if not self.extensions == other.extensions:
			return False
		if self.extensions == FileType.WILDCARD:
			return True
		if not self.name == other.name:
			return False
		return True

# def _main() -> None:
# 	f = FileType.maps()
# 	print((f[0]))
# 	print((f.name))
# 	print((f[1]))
# 	print((f.extensions))

# if __name__ == '__main__':
# 	_main()
