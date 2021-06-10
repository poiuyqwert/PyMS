
from PyMS.PyPAL.PyPAL import PyPAL, LONG_VERSION

from PyMS.FileFormats import Palette

from PyMS.Utilities.PyMSError import PyMSError

import os, optparse

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pypal.py','pypal.pyw','pypal.exe']):
		gui = PyPAL()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyPAL [options] <inp> [out]', version='PyPAL %s' % LONG_VERSION)
		p.add_option('-s', '--starcraft', action='store_const', const=0, dest='format', help="Convert to StarCraft PAL format [default]", default=0)
		p.add_option('-w', '--wpe', action='store_const', const=1, dest='format', help="Convert to StarCraft WPE format")
		p.add_option('-r', '--riff', action='store_const', const=2, dest='format', help="Convert to RIFF PAL format")
		p.add_option('-j', '--jasc', action='store_const', const=3, dest='format', help="Convert to JASC PAL format")
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
			pal = Palette.Palette()
			ext = ['pal','wpe','pal','pal'][opt.format]
			if len(args) == 1:
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			print "Reading Palette '%s'..." % args[0]
			try:
				pal.load_file(args[0])
				print " - '%s' read successfully\nConverting '%s' to %s file '%s'..." % (args[0], args[0], ext.upper(), args[1])
				[pal.save_sc_pal,pal.save_sc_wpe,pal.save_riff_pal,pal.save_jasc_pal][opt.format](args[1])
				print " - '%s' written succesfully" % args[1]
			except PyMSError, e:
				print repr(e)

if __name__ == '__main__':
	main()
