#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat, Requirement
check_compat('PySPK', Requirement.PIL)

def main():
	from PyMS.PySPK.PySPK import PySPK, LONG_VERSION

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pyspk.py','pyspk.pyw','pyspk.exe']):
		gui = PySPK()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PySPK [options] <inp> [out]', version='PySPK %s' % LONG_VERSION)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, _ = p.parse_args()
		if opt.gui:
			gui = PySPK(opt.gui)
			gui.startup()

if __name__ == '__main__':
	main()
