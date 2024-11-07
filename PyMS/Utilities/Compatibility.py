
import sys

class Requirement:
	none = 0

	MPQ = 1 << 0
	PIL = 1 << 1

def _show_error_uikit(program_name, message, warning): # type: (str, str, bool) -> bool
	from .DependencyError import DependencyError
	window = DependencyError(program_name, message, warning=warning)
	window.startup()
	if warning:
		return window.should_continue
	return False

def _show_error_tkinter(program_name, message, warning): # type: (str, str, bool) -> bool
	try:
		import tkinter.messagebox as messagebox
	except:
		import tkMessageBox as messagebox # type: ignore
	if warning:
		return messagebox.askyesno('Dependency Error', message + '\n\nWould you like to continue?')
	messagebox.showerror('Dependency Error', message)
	return False

def _show_error_console(program_name, message, warning): # type: (str, str, bool) -> bool
	print(message)
	print('  Readme (Local): README.md')
	print('  Readme (Online): https://github.com/poiuyqwert/PyMS#installation')
	if warning:
		response = input('Type Y to continue or anything else to exit: ')
		return response.lower() == 'y'
	return False

def show_error(program_name, message, warning=False): # type: (str, str, bool) -> None
	show_error_methods = [
		_show_error_uikit,
		_show_error_tkinter,
		_show_error_console
	]
	should_continue = False
	error = None # type: Exception | None
	for show_error_method in show_error_methods:
		try:
			should_continue = show_error_method(program_name, message, warning)
			error = None
			break
		except Exception as e:
			error = e
			continue
	if error is not None:
		raise error
	if not warning or not should_continue:
		sys.exit()

def check_compat(program_name, additional_requirements = Requirement.none): # type: (str, int) -> None
	supported_python_versions = {
		3: (11,12,13)
	}
	is_supported_major = sys.version_info.major in supported_python_versions
	if not is_supported_major or not sys.version_info.minor in supported_python_versions[sys.version_info.major]:
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
				show_error(program_name, 'You are using a newer Python version (%d.%d). It is possible that PyMS might not function properly.\nYou can continue to use the programs, or consult the Installation section of the Readme.'% (sys.version_info.major, sys.version_info.minor), warning=True)
		else:
			show_error(program_name, 'Incorrect Python version (%d.%d). Please consult the Installation section of the Readme.' % (sys.version_info.major, sys.version_info.minor))

	tcl_version = None
	try:
		import tkinter
		tcl_version = tkinter.Tcl().call("info", "patchlevel")
	except:
		try:
			import Tkinter as tkinter # type: ignore
			tcl_version = tkinter.Tcl().call("info", "patchlevel")
		except:
			show_error(program_name, 'Tkinter is missing. Please consult the Installation section of the Readme.')

	unsupported_tkinter = [
		(True, '8.6.13')
	]
	import platform
	is_mac = platform.system().lower() == 'darwin'
	if (is_mac, tcl_version) in unsupported_tkinter:
		show_error(program_name, 'Tkinter\'s Tcl/Tk version (%s) is incompatable. Please update your Python and/or Tcl/Tk version.' % tcl_version)

	if additional_requirements & Requirement.MPQ:
		from ..FileFormats.MPQ.MPQ import MPQ
		if not MPQ.supported():
			show_error(program_name, 'PyMS currently only has Windows and Mac support for MPQ files.\nIf you can help compile and test StormLib and/or SFmpq for your operating system, then please Contact me! See the Readme for contact details.')

	if additional_requirements & Requirement.PIL:
		try:
			from PIL import Image
			from PIL import ImageTk
		except:
			show_error(program_name, 'PIL/PILLOW is missing. Please consult the Installation section of the Readme.')
