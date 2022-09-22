#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyAI')

def main():
	from PyMS.PyTRG.PyTRG import PyTRG, LONG_VERSION

	from PyMS.FileFormats.TRG import TRG

	from PyMS.Utilities import Assets
	from PyMS.Utilities.PyMSError import PyMSError

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pytrg.py','pytrg.pyw','pytrg.exe']):
		gui = PyTRG()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyTRG [options] <inp> [out]', version='PyTRG %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a TRG file [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a TRG file")
		p.add_option('-t', '--trig', action='store_true', help="Used to decompile/compile a GOT compatable TRG", default=False)
		p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for parameter types, conditions and actions with parameter lists, and AIScripts [default: Off]", default=False)
		p.add_option('-s', '--stattxt',  help="Used to signify the stat_txt.tbl file to use [default: Libs\\MPQ\\rez\\stat_txt.tbl]", default=Assets.mpq_file_path('rez', 'stat_txt.tbl'))
		p.add_option('-a', '--aiscript', help="Used to signify the aiscript.bin file to use [default: Libs\\MPQ\\scripts\\aiscript.bin]", default=Assets.mpq_file_path('scripts', 'aiscript.bin'))
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyTRG(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			trg = TRG()
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'trg'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			try:
				if opt.convert:
					if opt.trig:
						print("Reading GOT compatable TRG '%s'..." % args[0])
					else:
						print("Reading TRG '%s'..." % args[0])
					trg.load_file(args[0], opt.trig)
					print(" - '%s' read successfully\nDecompiling TRG file '%s'..." % (args[0],args[0]))
					trg.decompile(args[1], opt.reference)
					print(" - '%s' written succesfully" % args[1])
				else:
					print("Interpreting file '%s'..." % args[0])
					trg.interpret(args[0])
					print(" - '%s' read successfully" % args[0])
					if opt.trig:
						print("Compiling file '%s' to GOT compatable TRG format..." % args[0])
					else:
						print("Compiling file '%s' to TRG format..." % args[0])
					trg.compile(args[1], opt.trig)
					print(" - '%s' written succesfully" % args[1])
			except PyMSError as e:
				print(repr(e))

if __name__ == '__main__':
	main()
