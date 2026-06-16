#!/usr/bin/env python
# pylint: disable=consider-using-f-string

from PyMS.Utilities.Compatibility import check_compat
check_compat('PyICE')

def main(): # type: () -> None
	from PyMS.PyICE.PyICE import PyICE, LONG_VERSION

	from PyMS.FileFormats.IScriptBIN import IScriptBIN
	from PyMS.FileFormats.IScriptBIN.CodeHandlers import DataContext, ICESerializeContext, ICEParseContext, ICELexer
	from PyMS.FileFormats import TBL, DAT

	from PyMS.Utilities import Assets, IO
	from PyMS.Utilities.PyMSError import PyMSError

	import os, optparse, sys

	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pyice.py','pyice.pyw','pyice.exe']):
		gui = PyICE()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyICE [options] <inp|iscriptin> [out|iscriptout]', version='PyICE %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile iscripts from iscript.bin [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile iscripts to an iscript.bin")
		p.add_option('-a', '--weapons', help="Specify your own weapons.dat file for weapon data lookups [default: Libs\\MPQ\\arr\\weapons.dat]", default=Assets.mpq_file_path('arr', 'weapons.dat'))
		p.add_option('-l', '--flingy', help="Specify your own flingy.dat file for flingy data lookups [default: Libs\\MPQ\\arr\\flingy.dat]", default=Assets.mpq_file_path('arr', 'flingy.dat'))
		p.add_option('-i', '--images', help="Specify your own images.dat file for image data lookups [default: Libs\\MPQ\\arr\\images.dat]", default=Assets.mpq_file_path('arr', 'images.dat'))
		p.add_option('-p', '--sprites', help="Specify your own sprites.dat file for sprite data lookups [default: Libs\\MPQ\\arr\\sprite.dat]", default=Assets.mpq_file_path('arr', 'sprites.dat'))
		p.add_option('-f', '--sfxdata', help="Specify your own sfxdata.dat file for sound data lookups [default: Libs\\MPQ\\arr\\sfxdata.dat]", default=Assets.mpq_file_path('arr', 'sfxdata.dat'))
		p.add_option('-x', '--stattxt', help="Used to signify the stat_txt.tbl file to use [default: Libs\\MPQ\\rez\\stat_txt.tbl]", default=Assets.mpq_file_path('rez','stat_txt.tbl'))
		p.add_option('-m', '--imagestbl', help="Used to signify the images.tbl file to use [default: Libs\\MPQ\\arr\\images.tbl]", default=Assets.mpq_file_path('arr', 'images.tbl'))
		p.add_option('-t', '--sfxdatatbl', help="Used to signify the sfxdata.tbl file to use [default: Libs\\MPQ\\arr\\sfxdata.tbl]", default=Assets.mpq_file_path('arr', 'sfxdata.tbl'))
		p.add_option('-s', '--scripts', help="A list of iscript ID's to decompile (seperated by commas) [default: All]", default='')
		p.add_option('-b', '--iscript', help="Used to signify the base iscript.bin file to compile on top of", default='')
		p.add_option('-r', '--reference', action='store_true', help="Deprecated: no longer has any effect", default=False)
		p.add_option('-w', '--hidewarns', action='store_true', help="Hides any warning produced by compiling your code [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyICE(opt.gui)
			gui.startup()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'bin'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			warnings = []
			try:
				print("Loading weapons.dat '%s', flingy.dat '%s', images.dat '%s', sprites.dat '%s', sfxdata.dat '%s', stat_txt.tbl '%s', images.tbl '%s', and sfxdata.tbl '%s'" % (opt.weapons,opt.flingy,opt.images,opt.sprites,opt.sfxdata,opt.stattxt,opt.imagestbl,opt.sfxdatatbl))
				weapons_dat = DAT.WeaponsDAT()
				weapons_dat.load(opt.weapons)
				flingy_dat = DAT.FlingyDAT()
				flingy_dat.load(opt.flingy)
				images_dat = DAT.ImagesDAT()
				images_dat.load(opt.images)
				sprites_dat = DAT.SpritesDAT()
				sprites_dat.load(opt.sprites)
				sounds_dat = DAT.SoundsDAT()
				sounds_dat.load(opt.sfxdata)
				stat_txt_tbl = TBL.TBL()
				stat_txt_tbl.load_file(opt.stattxt)
				images_tbl = TBL.TBL()
				images_tbl.load_file(opt.imagestbl)
				sounds_tbl = TBL.TBL()
				sounds_tbl.load_file(opt.sfxdatatbl)
				data_context = DataContext(weapons_dat=weapons_dat, flingy_dat=flingy_dat, images_dat=images_dat, sprites_dat=sprites_dat, sounds_dat=sounds_dat, stat_txt_tbl=stat_txt_tbl, images_tbl=images_tbl, sounds_tbl=sounds_tbl)
				print(" - Loading finished successfully")
				if opt.convert:
					if opt.scripts:
						ids = [int(i) for i in opt.scripts.split(',')]
					else:
						ids = None
					print("Reading BIN '%s'..." % args[0])
					ibin = IScriptBIN.IScriptBIN()
					ibin.load(args[0])
					print(" - BIN read successfully\nWriting iscript entries to '%s'..." % args[1])
					with IO.OutputTextFile(args[1]) as output:
						serialize_context = ICESerializeContext(output, data_context)
						ibin.decompile(serialize_context, script_ids=ids)
					print(" - '%s' written succesfully" % args[1])
				else:
					ibin = IScriptBIN.IScriptBIN()
					if opt.iscript:
						print("Loading base iscript.bin '%s'..." % os.path.abspath(opt.iscript))
						ibin.load(os.path.abspath(opt.iscript))
						print(" - iscript.bin read successfully")
					print("Interpreting file '%s'..." % args[0])
					with IO.InputText(args[0]) as input_text:
						code = input_text.read()
					parse_context = ICEParseContext(ICELexer(code), data_context)
					new_scripts = IScriptBIN.IScriptBIN.compile(parse_context)
					warnings.extend(parse_context.warnings)
					ibin.add_scripts(new_scripts)
					print(" - '%s' read successfully\nCompiling file '%s' to iscript.bin '%s'..." % (args[0], args[0], args[1]))
					ibin.save(args[1])
					print(" - iscript.bin '%s' written succesfully" % args[1])
				if not opt.hidewarns:
					for warning in warnings:
						print(repr(warning))
			except PyMSError as e:
				if warnings and not opt.hidewarns:
					for warning in warnings:
						print(repr(warning))
				print(repr(e))

if __name__ == '__main__':
	main()
