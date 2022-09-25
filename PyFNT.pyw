#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat, Requirement
check_compat('PyFNT', Requirement.PIL)

def main():
	from PyMS.PyFNT.PyFNT import PyFNT, LONG_VERSION

	from PyMS.FileFormats.FNT import FNT, fnttobmp, bmptofnt
	from PyMS.FileFormats.BMP import BMP

	from PyMS.Utilities.PyMSError import PyMSError

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pyfnt.py','pyfnt.pyw','pyfnt.exe']):
		gui = PyFNT()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyFNT [options] <inp> [out]', version='PyFNT %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile FNT to a BMP [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a BMP to a FNT")
		p.add_option('-s', '--specifics', action='store', type='string', help="Specifies the lowest ASCII index and amount of letters (seperated by commas) when compiling")
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyFNT(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			ext = ['bmp','fnt'][opt.convert]
			if len(args) == 1:
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			if opt.convert:
				fnt = FNT()
				print("Reading FNT '%s'..." % args[0])
				try:
					fnt.load_file(args[0])
					print(" - '%s' read successfully\nDecompiling FNT to file '%s'..." % (args[0], args[1]))
					fnttobmp(fnt,args[1])
					print(" - '%s' written succesfully" % args[1])
				except PyMSError as e:
					print(repr(e))
			else:
				if not opt.specifics:
					p.error('You must supply the -s option when using the -c option')
				t = opt.specifics.split(',')
				try:
					lowi,letters = int(t),int(t)
				except:
					print('Invalid compiling specifics (must be lowest ASCII index followed by amount of letters, seperated by a comma)')
				else:
					if lowi < 1 or lowi > 255:
						print('Invalid lowest ASCII index (must be in the range 1-255)')
					elif letters < 1 or letters > 255:
						print('Invalid amount of letters (must be in the range 1-255)')
					elif lowi+letters > 256:
						print('Either too many letters where specified or too high an initial ASCII index')
					else:
						bmp = BMP()
						print("Reading BMP '%s'..." % args[0])
						try:
							bmp.load_file(args[0])
							print(" - '%s' read successfully\nDecompiling BMP to file '%s'..." % (args[0], args[1]))
							bmptofnt(bmp, lowi, letters, args[1])
							print(" - '%s' written succesfully" % args[1])
						except PyMSError as e:
							print(repr(e))

if __name__ == '__main__':
	main()