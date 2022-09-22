#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyPAL')

def main():
	from PyMS.PyPAL.PyPAL import PyPAL, LONG_VERSION

	from PyMS.FileFormats.Palette import Palette

	from PyMS.Utilities.PyMSError import PyMSError

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pypal.py','pypal.pyw','pypal.exe']):
		gui = PyPAL()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyPAL [options] <inp> [out]', version='PyPAL %s' % LONG_VERSION)
		p.add_option('-s', '--starcraft', action='store_const', const=Palette.FileType.sc_pal, dest='file_type', help="Convert to StarCraft PAL format [default]", default=0)
		p.add_option('-w', '--wpe', action='store_const', const=Palette.FileType.wpe, dest='file_type', help="Convert to StarCraft WPE format")
		p.add_option('-r', '--riff', action='store_const', const=Palette.FileType.riff, dest='file_type', help="Convert to RIFF PAL format")
		p.add_option('-j', '--jasc', action='store_const', const=Palette.FileType.jasc, dest='file_type', help="Convert to JASC PAL format")
		p.add_option('-a', '--act', action='store_consts', const=Palette.FileType.act, dest='file_type', help="Convert to Adobe Color Table format")
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyPAL(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			pal = Palette()
			if len(args) == 1:
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, opt.file_type.ext))
			print("Reading Palette '%s'..." % args[0])
			try:
				pal.load_file(args[0])
				print(" - '%s' read successfully\nConverting '%s' to %s file '%s'..." % (args[0], args[0], opt.file_type.ext.upper(), args[1]))
				pal.save(args[1], opt.file_type.format)
				print(" - '%s' written succesfully" % args[1])
			except PyMSError as e:
				print(repr(e))

if __name__ == '__main__':
	main()
