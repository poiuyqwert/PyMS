
class Requirement:
	none = 0

	MPQ = (1 << 0)
	PIL = (1 << 1)

def check_compat(program_name, additional_requirements=Requirement.none): # type: (str, int) -> None
	import sys

	try:
		from . import UIKit as _
	except:
		print('Tkinter is missing. Please consult the Installation section of the README.md in your PyMS folder, or online at https://github.com/poiuyqwert/PyMS#installation')
		sys.exit()

	from . import Assets
	from .DependencyError import DependencyError

	readmes = (
		('Readme (Local)', 'file:///%s' % Assets.readme_file_path),
		('Readme (Online)', 'https://github.com/poiuyqwert/PyMS#installation')
	)

	if sys.version_info.major != 2 or sys.version_info.minor != 7:
		DependencyError(program_name, 'Incorrect Python version (%d.%d instead of 2.7). Please consult the Installation section of the Readme.' % (sys.version_info.major, sys.version_info.minor), readmes).startup()
		sys.exit()

	if additional_requirements & Requirement.MPQ:
		from ..FileFormats.MPQ.MPQ import MPQ
		if not MPQ.supported():
			DependencyError(program_name, 'PyMS currently only has Windows and Mac support for MPQ files.\nIf you can help compile and test StormLib and/or SFmpq for your operating system, then please Contact me! See the Readme for contact details.', readmes).startup()
			sys.exit()

	if additional_requirements & Requirement.PIL:
		try:
			from PIL import Image as PILImage
			try:
				from PIL import ImageTk
			except:
				import ImageTk
		except:
			DependencyError(program_name, 'PIL/PILLOW is missing. Please consult the Installation section of the Readme.', readmes).startup()
			sys.exit()
