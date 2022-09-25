#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyTBL')

def main():
	from PyMS.PyTBL.PyTBL import PyTBL, LONG_VERSION

	from PyMS.FileFormats import TBL

	from PyMS.Utilities.PyMSError import PyMSError

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pytbl.py','pytbl.pyw','pytbl.exe']):
		gui = PyTBL()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyTBL [options] <inp> [out]', version='PyTBL %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a TBL file [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a TBL file")
		p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for colors and other special characters at the top [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyTBL(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			tbl = TBL.TBL()
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'tbl'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			try:
				if opt.convert:
					print("Reading TBL '%s'..." % args[0])
					tbl.load_file(args[0])
					print(" - '%s' read successfully\nDecompiling TBL file '%s'..." % (args[0],args[0]))
					tbl.decompile(args[1], opt.reference)
					print(" - '%s' written succesfully" % args[1])
				else:
					print("Interpreting file '%s'..." % args[0])
					tbl.interpret(args[0])
					print(" - '%s' read successfully\nCompiling file '%s' to TBL format..." % (args[0],args[0]))
					tbl.compile(args[1])
					print(" - '%s' written succesfully" % args[1])
			except PyMSError as e:
				print(repr(e))

if __name__ == '__main__':
	main()
	