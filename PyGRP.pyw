#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat, Requirement
check_compat('PyGRP', Requirement.PIL)

def main():
	from PyMS.PyGRP.PyGRP import PyGRP, LONG_VERSION
	from PyMS.PyGRP.utils import grptobmp, bmptogrp

	from PyMS.FileFormats.Palette import Palette

	from PyMS.Utilities.PyMSError import PyMSError

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pygrp.py','pygrp.pyw','pygrp.exe']):
		gui = PyGRP()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyGRP [options] <inp> [out]', version='PyGRP %s' % LONG_VERSION)
		p.add_option('-p', '--palette', metavar='FILE', help='Choose a palette for GRP to BMP conversion [default: %default]', default='Units.pal')
		p.add_option('-g', '--grptobmps', action='store_true', dest='convert', help="Converting from GRP to BMP's [default]", default=True)
		p.add_option('-b', '--bmpstogrp', action='store_false', dest='convert', help="Converting from BMP's to GRP")
		p.add_option('-u', '--uncompressed', action='store_true', help="Used to signify if the GRP is uncompressed (both to and from BMP) [default: Compressed]", default=False)
		p.add_option('-o', '--onebmp', action='store_true', help='Used to signify that you want to convert a GRP to one BMP file. [default: Multiple]', default=False)
		p.add_option('-f', '--frames', type='int', help='Used to signify you are using a single BMP with alll frames, and how many frames there are.', default=0)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyGRP(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			pal = Palette()
			fullfile = os.path.abspath(os.path.join('Palettes',opt.palette))
			ext = os.extsep + 'pal'
			if not fullfile.endswith(ext):
				fullfile += ext
			print("Reading palette '%s'..." % fullfile)
			try:
				pal.load_file(fullfile)
				print(" - '%s' read successfully" % fullfile)
				path = os.path.dirname(args[0])
				if not path:
					path = os.path.abspath('')
				args[0] = os.path.join(path,os.path.basename(args[0]))
				if opt.convert:
					grptobmp(path, pal, opt.uncompressed, opt.onebmp, *args)
				else:
					bmptogrp(path, pal, opt.uncompressed, opt.frames, *args)
			except PyMSError as e:
				print(repr(e))

if __name__ == '__main__':
	main()
