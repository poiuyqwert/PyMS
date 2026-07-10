#!/usr/bin/env python
# pylint: disable=consider-using-f-string

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyMOD')

def main(): # type: () -> None
	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pymod.py','pymod.pyw','pymod.exe']):
		from PyMS.PyMOD.PyMOD import PyMOD

		gui = PyMOD()
		gui.startup()
	else:
		from PyMS.PyMOD.PyMOD import PyMOD, LONG_VERSION

		p = optparse.OptionParser(usage='usage: PyMOD [options] <project_path>', version='PyMOD %s' % LONG_VERSION)
		p.add_option('--gui', help="Opens a mod project with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyMOD(opt.gui)
			gui.startup()
		else:
			if len(args) != 1:
				p.error('Invalid amount of arguments')
			from PyMS.PyMOD.compile_project import compile_project

			sys.exit(0 if compile_project(args[0]) else 1)

if __name__ == '__main__':
	main()
