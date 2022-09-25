#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyGOT')

def main():
	from PyMS.PyGOT.PyGOT import PyGOT, LONG_VERSION

	from PyMS.FileFormats.GOT import GOT
	from PyMS.FileFormats.TRG import TRG

	from PyMS.Utilities.PyMSError import PyMSError

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pygot.py','pygot.pyw','pygot.exe']):
		gui = PyGOT()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyGOT [options] <inp> [out]', version='PyGOT %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a GOT file [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a GOT file")
		p.add_option('-t', '--trig', help="Used to compile a TRG file to a GOT compatable TRG file")
		p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for settings at the top of the file [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyGOT(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			got = GOT()
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'got'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			try:
				if opt.convert:
					print("Reading GOT '%s'..." % args[0])
					got.load_file(args[0])
					print(" - '%s' read successfully\nDecompiling GOT file '%s'..." % (args[0],args[0]))
					got.decompile(args[1], opt.reference)
					print(" - '%s' written succesfully" % args[1])
				else:
					print("Interpreting file '%s'..." % args[0])
					got.interpret(args[0])
					print(" - '%s' read successfully\nCompiling file '%s' to GOT format..." % (args[0],args[0]))
					got.compile(args[1])
					print(" - '%s' written succesfully" % args[1])
					if opt.trig:
						print("Reading TRG '%s'..." % args[0])
						trg = TRG()
						trg.load_file(opt.trig)
						print(" - '%s' read successfully" % args[0])
						path = os.path.dirname(opt.trig)
						if not path:
							path = os.path.abspath('')
						file = '%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[1]).split(os.extsep)[:-1])), os.extsep, 'trg')
						print("Compiling file '%s' to GOT compatable TRG..." % file)
						trg.compile(file, True)
						print(" - '%s' written succesfully" % file)
			except PyMSError as e:
				print(repr(e))

if __name__ == '__main__':
	main()
