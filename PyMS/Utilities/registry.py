
from .PyMSError import PyMSError

import sys, os

IS_AVAILABLE = True
try:
	from winreg import OpenKey, EnumKey, DeleteKey, HKEY_CLASSES_ROOT, REG_SZ, SetValue # type: ignore[attr-defined] # pylint: disable=import-error
except Exception:
	IS_AVAILABLE = False
	def OpenKey(_a,_b) -> str:
		return ''
	def EnumKey(_a,_b) -> str:
		return ''
	def DeleteKey(_a,_b) -> None:
		pass
	HKEY_CLASSES_ROOT = ''
	REG_SZ = ''
	def SetValue(_a,_b,_c,_d) -> None:
		pass

def register(program_name: str, extension: str, file_type_name: str | None = None) -> None:
	if not IS_AVAILABLE:
		raise PyMSError('Registry', 'You can currently only set as the default program on Windows machines.')
	def delkey(key,sub_key):
		try:
			h = OpenKey(key,sub_key)
		except OSError as e:
			if e.errno == 2:
				return
			raise
		try:
			while True:
				n = EnumKey(h,0)
				delkey(h,n)
		except EnvironmentError:
			pass
		h.Close()
		DeleteKey(key,sub_key)

	from . import Assets
	key = f'{program_name}:{extension}'
	if file_type_name:
		file_type_name = ' ' + file_type_name
	else:
		file_type_name = ''
	if hasattr(sys, 'frozen'):
		executable = f'"{sys.executable}"'
	else:
		executable = f'"{sys.executable.replace("python.exe","pythonw.exe")}" "{os.path.join(Assets.base_dir, program_name + ".pyw")}"'
	try:
		delkey(HKEY_CLASSES_ROOT, os.extsep + extension)
		delkey(HKEY_CLASSES_ROOT, key)
		SetValue(HKEY_CLASSES_ROOT, '.' + extension, REG_SZ, key)
		SetValue(HKEY_CLASSES_ROOT, key, REG_SZ, f'StarCraft{file_type_name} *.{extension} file ({program_name})')
		SetValue(HKEY_CLASSES_ROOT, key + '\\DefaultIcon', REG_SZ, Assets.image_path(f'{program_name}.ico'))
		SetValue(HKEY_CLASSES_ROOT, key + '\\Shell', REG_SZ, 'open')
		SetValue(HKEY_CLASSES_ROOT, key + '\\Shell\\open\\command', REG_SZ, f'{executable} --gui "%%1"')
	except Exception as exc:
		raise PyMSError('Registry', 'Could not complete file association.') from exc
	from .UIKit import MessageBox
	MessageBox.showinfo('Success!', 'The file association was set.')
