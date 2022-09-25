#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyLO')

def main():
	from PyMS.PyLO.PyLO import PyLO, LONG_VERSION

	from PyMS.FileFormats.LO import LO

	from PyMS.Utilities.PyMSError import PyMSError

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pylo.py','pylo.pyw','pylo.exe']):
		gui = PyLO()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyLO [options] <inp> [out]', version='PyLO %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a LO? file [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a LO? file")
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyLO(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			lo = LO()
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'lox'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			try:
				if opt.convert:
					print("Reading LO? '%s'..." % args[0])
					lo.load_file(args[0])
					print(" - '%s' read successfully\nDecompiling LO? file '%s'..." % (args[0],args[0]))
					lo.decompile(args[1])
					print(" - '%s' written succesfully" % args[1])
				else:
					print("Interpreting file '%s'..." % args[0])
					lo.interpret(args[0])
					print(" - '%s' read successfully\nCompiling file '%s' to LO? format..." % (args[0],args[0]))
					lo.compile(args[1])
					print(" - '%s' written succesfully" % args[1])
			except PyMSError as e:
				print(repr(e))

if __name__ == '__main__':
	main()
