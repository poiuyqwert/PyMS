#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat, Requirement
check_compat('PyPCX', Requirement.PIL)

def main():
	from PyMS.PyPCX.PyPCX import PyPCX, LONG_VERSION

	from PyMS.FileFormats import PCX
	from PyMS.FileFormats import BMP

	from PyMS.Utilities.PyMSError import PyMSError

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pypcx.py','pypcx.pyw','pypcx.exe']):
		gui = PyPCX()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyPCX [options] <inp> [out]', version='PyPCX %s' % LONG_VERSION)
		p.add_option('-p', '--pcx', action='store_true', dest='convert', help='Convert from PCX to BMP [Default]', default=True)
		p.add_option('-b', '--bmp', action='store_false', dest='convert', help="Convert from BMP to PCX")
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyPCX(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			pcx = PCX.PCX()
			bmp = BMP.BMP()
			ext = ['pcx','bmp'][opt.convert]
			if len(args) == 1:
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			if opt.convert:
				print("Reading PCX '%s'..." % args[0])
				try:
					pcx.load_file(args[0])
					print(" - '%s' read successfully\nConverting '%s' to %s file '%s'..." % (args[0], args[0], ext.upper(), args[1]))
					bmp.set_pixels(pcx.image,pcx.palette)
					bmp.save_file(args[1])
				except PyMSError as e:
					print(repr(e))
				else:
					print(" - '%s' written succesfully" % args[1])
			else:
				print("Reading BMP '%s'..." % args[0])
				try:
					bmp.load_file(args[0])
					print(" - '%s' read successfully\nConverting '%s' to %s file '%s'..." % (args[0], args[0], ext.upper(), args[1]))
					pcx.load_data(bmp.image,bmp.palette)
					pcx.save_file(args[1])
				except PyMSError as e:
					print(repr(e))
				else:
					print(" - '%s' written succesfully" % args[1])

if __name__ == '__main__':
	main()
