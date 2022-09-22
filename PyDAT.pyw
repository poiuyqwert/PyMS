#!/usr/bin/env python

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyDAT')

def main():
	from PyMS.PyDAT.PyDAT import PyDAT, LONG_VERSION

	from PyMS.FileFormats import DAT

	from PyMS.Utilities.PyMSError import PyMSError
	from PyMS.Utilities import Assets

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pydat.py','pydat.pyw','pydat.exe']):
		gui = PyDAT()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyDAT [options] <inp> [out]', version='PyDAT %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a DAT file [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a DAT file")
		p.add_option('-u', '--units', action='store_const', const=0, dest='type', help="Decompiling/Compiling units.dat [default]", default=0)
		p.add_option('-w', '--weapons', action='store_const', const=1, dest='type', help="Decompiling/Compiling weapons.dat")
		p.add_option('-f', '--flingy', action='store_const', const=2, dest='type', help="Decompiling/Compiling flingy.dat")
		p.add_option('-s', '--sprites', action='store_const', const=3, dest='type', help="Decompiling/Compiling sprites.dat")
		p.add_option('-i', '--images', action='store_const', const=4, dest='type', help="Decompiling/Compiling images.dat")
		p.add_option('-g', '--upgrades', action='store_const', const=5, dest='type', help="Decompiling/Compiling upgrades.dat")
		p.add_option('-t', '--techdata', action='store_const', const=6, dest='type', help="Decompiling/Compiling techdata.dat")
		p.add_option('-l', '--sfxdata', action='store_const', const=7, dest='type', help="Decompiling/Compiling sfxdata.dat")
		p.add_option('-p', '--portdata', action='store_const', const=8, dest='type', help="Decompiling/Compiling portdata.dat")
		p.add_option('-m', '--mapdata', action='store_const', const=9, dest='type', help="Decompiling/Compiling mapdata.dat")
		p.add_option('-o', '--orders', action='store_const', const=10, dest='type', help="Decompiling/Compiling orders.dat")
		p.add_option('-n', '--ids', help="A list of ID's to decompile (seperated by commas) [default: All]", default='')
		p.add_option('-b', '--basedat', help="Used to signify the base DAT file to compile on top of", default='')
		p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for various values [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyDAT(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			dat = [DAT.UnitsDAT,DAT.WeaponsDAT,DAT.FlingyDAT,DAT.SpritesDAT,DAT.ImagesDAT,DAT.UpgradesDAT,DAT.TechDAT,DAT.SoundsDAT,DAT.PortraitsDAT,DAT.CampaignDAT,DAT.OrdersDAT][opt.type]()
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'dat'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			try:
				if opt.convert:
					if opt.ids:
						ids = []
						try:
							for i in opt.ids.split(','):
								ids.append(int(i))
								if ids[-1] < 0 or ids[-1] >= dat.count:
									raise PyMSError('Options',"Invalid ID '%s'" % ids[-1])
						except:
							raise PyMSError('Options','Invalid ID list')
					else:
						ids = None
					print("Reading DAT '%s'..." % args[0])
					dat.load_file(args[0])
					print(" - '%s' read successfully\nDecompiling DAT file '%s'..." % (args[0],args[0]))
					dat.decompile(args[1], opt.reference, ids)
					print(" - '%s' written succesfully" % args[1])
				else:
					if opt.basedat:
						basedat = os.path.abspath(opt.basedat)
					else:
						basedat = Assets.mpq_file_path('arr','%s%sdat' % (['units','weapons','flingy','sprites','images','upgrades','techdata','sfxdata','portdata','mapdata','orders'][opt.type],os.extsep))
					print("Loading base DAT file '%s'..." % basedat)
					dat.load_file(basedat)
					print(" - '%s' read successfully\nInterpreting file '%s'..." % (basedat,args[0]))
					dat.interpret(args[0])
					print(" - '%s' read successfully\nCompiling file '%s' to DAT format..." % (args[0],args[0]))
					dat.compile(args[1])
					print(" - '%s' written succesfully" % args[1])
			except PyMSError as e:
				print(repr(e))

if __name__ == '__main__':
	main()