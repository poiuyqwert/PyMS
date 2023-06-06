
from enum import Flag, auto

class Requirement(Flag):
	none = 0

	MPQ = auto()
	PIL = auto()

def check_compat(program_name, additional_requirements=Requirement.none): # type: (str, Requirement) -> None
	import sys

	tcl_version = None
	try:
		import tkinter
		tcl_version = tkinter.Tcl().call("info", "patchlevel")
	except:
		print('Tkinter is missing. Please consult the Installation section of the README.md in your PyMS folder, or online at https://github.com/poiuyqwert/PyMS#installation')
		raise

	from .utils import is_mac
	unsupported_tkinter = [
		(True, '8.6.13')
	]
	if (is_mac(), tcl_version) in unsupported_tkinter:
		print('Tkinter\'s Tcl/Tk version (%s) is incompatable. Please update your Python and/or Tcl/Tk version.' % tcl_version)
		sys.exit()

	from . import Assets
	from .DependencyError import DependencyError

	readmes = (
		('Readme (Local)', 'file:///%s' % Assets.readme_file_path),
		('Readme (Online)', 'https://github.com/poiuyqwert/PyMS#installation')
	)

	required_major = 3
	required_minor = 11
	if sys.version_info.major != required_major or sys.version_info.minor != required_minor:
		DependencyError(program_name, 'Incorrect Python version (%d.%d instead of %d.%d). Please consult the Installation section of the Readme.' % (sys.version_info.major, sys.version_info.minor, required_major, required_minor), readmes).startup()
		sys.exit()

	if additional_requirements & Requirement.MPQ:
		from ..FileFormats.MPQ.MPQ import MPQ
		if not MPQ.supported():
			DependencyError(program_name, 'PyMS currently only has Windows and Mac support for MPQ files.\nIf you can help compile and test StormLib and/or SFmpq for your operating system, then please Contact me! See the Readme for contact details.', readmes).startup()
			sys.exit()

	if additional_requirements & Requirement.PIL:
		try:
			from PIL import Image
			from PIL import ImageTk
		except:
			DependencyError(program_name, 'PIL/PILLOW is missing. Please consult the Installation section of the Readme.', readmes).startup()
			sys.exit()
