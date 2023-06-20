#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat, Requirement
check_compat('PyMPQ', Requirement.MPQ)

def main() -> None:
	from PyMS.PyMPQ.PyMPQ import PyMPQ, LONG_VERSION

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pympq.py','pympq.pyw','pympq.exe']):
		gui = PyMPQ()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyMPQ [options] <inp> [out]', version='PyMPQ %s' % LONG_VERSION)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, _ = p.parse_args()
		if opt.gui:
			gui = PyMPQ(opt.gui)
			gui.startup()

if __name__ == '__main__':
	main()