#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat, Requirement
check_compat('PyJSON', Requirement.PIL)

def main() -> None:
	from PyMS.PyJSON.PyJSON import PyJSON, LONG_VERSION

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pyjson.py','pyjson.pyw','pyjson.exe']):
		gui = PyJSON()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyJSON [options]', version='PyJSON %s' % LONG_VERSION)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, _ = p.parse_args()
		if opt.gui:
			gui = PyJSON(opt.gui)
			gui.startup()

if __name__ == '__main__':
	main()
