#!/usr/bin/env python
# pylint: disable=consider-using-f-string

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyGRAFT')

def main(): # type: () -> None
	from PyMS.PyGRAFT.PyGRAFT import PyGRAFT, LONG_VERSION
	from PyMS.PyGRAFT import CLI

	from PyMS.Utilities.PyMSError import PyMSError

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pygraft.py','pygraft.pyw','pygraft.exe']):
		gui = PyGRAFT()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyGRAFT [options] <inp> [out]', version='PyGRAFT %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a Graft file [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a Graft file")
		p.add_option('-u', '--units', action='store_const', const='units', dest='type', help="Decompiling/Compiling Units.graft [default]", default='units')
		p.add_option('-g', '--upgrades', action='store_const', const='upgrades', dest='type', help="Decompiling/Compiling Upgrades.graft")
		p.add_option('-r', '--research', action='store_const', const='research', dest='type', help="Decompiling/Compiling Research.graft")
		p.add_option('-t', '--tech', action='store_const', const='tech', dest='type', help="Decompiling/Compiling Tech.graft")
		p.add_option('-o', '--orders', action='store_const', const='orders', dest='type', help="Decompiling/Compiling Orders.graft")
		p.add_option('-b', '--buttons', action='store_const', const='buttons', dest='type', help="Decompiling/Compiling Buttons.graft")
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyGRAFT(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			if len(args) == 1:
				ext = 'txt' if opt.convert else 'graft'
				args.append('%s%s%s' % (os.path.splitext(args[0])[0], os.extsep, ext))
			try:
				if opt.convert:
					print("Decompiling Graft file '%s'..." % args[0])
					CLI.decompile_graft(opt.type, args[0], args[1])
				else:
					print("Compiling file '%s' to Graft format..." % args[0])
					CLI.compile_graft(opt.type, args[0], args[1])
				print(" - '%s' written succesfully" % args[1])
			except PyMSError as e:
				print(repr(e))

if __name__ == '__main__':
	main()
