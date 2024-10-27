
class Requirement:
	none = 0

	MPQ = 1 << 0
	PIL = 1 << 1

def check_compat(program_name, additional_requirements = Requirement.none): # type: (str, int) -> None
	import sys

	supported_python_versions = {
		3: (11,12,13)
	}
	if sys.version_info.major < min(supported_python_versions.keys()):
		print('Your Python version is too old (%d.%d). Please consult the Installation section of the README.md in your PyMS folder, or online at https://github.com/poiuyqwert/PyMS#installation' % (sys.version_info.major, sys.version_info.minor))
		sys.exit()

	tcl_version = None
	try:
		import tkinter
		tcl_version = tkinter.Tcl().call("info", "patchlevel")
	except:
		try:
			import Tkinter as tkinter # type: ignore # pylint: disable=reportMissingImports
			tcl_version = tkinter.Tcl().call("info", "patchlevel")
		except:
			print('Tkinter is missing. Please consult the Installation section of the README.md in your PyMS folder, or online at https://github.com/poiuyqwert/PyMS#installation')
			sys.exit()

	unsupported_tkinter = [
		(True, '8.6.13')
	]
	import platform
	is_mac = platform.system().lower() == 'darwin'
	if (is_mac, tcl_version) in unsupported_tkinter:
		print('Tkinter\'s Tcl/Tk version (%s) is incompatable. Please update your Python and/or Tcl/Tk version.' % tcl_version)
		sys.exit()

	from .DependencyError import DependencyError

	is_supported_major = sys.version_info.major in supported_python_versions
	if not is_supported_major or not sys.version_info.minor in supported_python_versions[sys.version_info.major]:
		# TODO: Warn about newer minor versions but give option to continue using?
		if is_supported_major and sys.version_info.minor > max(supported_python_versions[sys.version_info.major]):
			from .PyMSConfig import PYMS_CONFIG
			from .SemVer import SemVer
			from . import Assets
			skip = False
			dont_remind_me_raw = PYMS_CONFIG.reminder.python_version.value
			if dont_remind_me_raw:
				dont_remind_me = SemVer(dont_remind_me_raw)
				if dont_remind_me >= SemVer(Assets.version('PyMS')):
					skip = True
			if not skip:
				window = DependencyError(program_name, 'You are using a newer Python version (%d.%d). It is possible that PyMS might not function properly.\nYou can continue to use the programs, or consult the Installation section of the Readme.'% (sys.version_info.major, sys.version_info.minor), warning=True)
				window.startup()
				if not window.should_continue:
					sys.exit()
		else:
			DependencyError(program_name, 'Incorrect Python version (%d.%d). Please consult the Installation section of the Readme.' % (sys.version_info.major, sys.version_info.minor)).startup()
			sys.exit()

	if additional_requirements & Requirement.MPQ:
		from ..FileFormats.MPQ.MPQ import MPQ
		if not MPQ.supported():
			DependencyError(program_name, 'PyMS currently only has Windows and Mac support for MPQ files.\nIf you can help compile and test StormLib and/or SFmpq for your operating system, then please Contact me! See the Readme for contact details.').startup()
			sys.exit()

	if additional_requirements & Requirement.PIL:
		try:
			from PIL import Image
			from PIL import ImageTk
		except:
			DependencyError(program_name, 'PIL/PILLOW is missing. Please consult the Installation section of the Readme.').startup()
			sys.exit()
