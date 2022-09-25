#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyBIN')

def main():
	from PyMS.PyBIN.PyBIN import PyBIN, LONG_VERSION

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pybin.py','pybin.pyw','pybin.exe']):
		gui = PyBIN()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyBIN [options] <inp> [out]', version='PyBIN %s' % LONG_VERSION)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, _ = p.parse_args()
		if opt.gui:
			gui = PyBIN(opt.gui)
			gui.startup()

if __name__ == '__main__':
	main()
