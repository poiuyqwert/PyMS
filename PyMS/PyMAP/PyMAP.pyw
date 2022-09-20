from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs.SFmpq import *
from Libs import TBL, AIBIN, DAT, Tilesets, GRP, PAL, PCX
from Libs.CHK import *
from Libs.analytics import *

from Tkinter import *
from tkMessageBox import *
import tkFileDialog,tkColorChooser
from Libs.SpecialLists import TreeList
from PIL import Image as PILImage
from PIL import ImageDraw as PILDraw
from PIL import ImageTk

from thread import start_new_thread
from math import ceil
import optparse, os, webbrowser, sys, time, random

LONG_VERSION = 'v%s-DEV' % Assets.version('PyMAP')

FRAME_DELAY = 42

TERRAIN_DETAILS = {
	CHKSectionERA.BADLANDS:{
		'name':CHKSectionERA.TILESET_NAME(CHKSectionERA.BADLANDS),
		'types':[
			{
				'name':'Rocky Ground',
				'ranges':[
					{
						'groups':(12,13),
						'tiles':(0,11),
						'messy':None
					}
				]
			},
			{
				'name':'Asphalt',
				'ranges':[
					{
						'groups':(16,17),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Structure',
				'ranges':[
					{
						'groups':(18,19),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'High Grass',
				'ranges':[
					{
						'groups':(10,11),
						'tiles':(0,6),
						'messy':(8,10)
					}
				]
			},
			{
				'name':'Grass',
				'ranges':[
					{
						'groups':(8,9),
						'tiles':(0,6),
						'messy':(8,10)
					}
				]
			},
			{
				'name':'Water',
				'ranges':[
					{
						'groups':(6,7),
						'tiles':(0,5),
						'messy':None
					}
				]
			},
			{
				'name':'High Dirt',
				'ranges':[
					{
						'groups':(4,5),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			},
			{
				'name':'Mud',
				'ranges':[
					{
						'groups':(20,21),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			},
			{
				'name':'Dirt',
				'ranges':[
					{
						'groups':(2,3),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			}
		]
	},
	CHKSectionERA.SPACE:{
		'name':CHKSectionERA.TILESET_NAME(CHKSectionERA.SPACE),
		'types':[
			{
				'name':'Elevated Catwalk',
				'ranges':[
					{
						'groups':(20,21),
						'tiles':(0,3),
						'messy':(5,6)
					}
				]
			},
			{
				'name':'High Plating',
				'ranges':[
					{
						'groups':(10,11),
						'tiles':(0,5),
						'messy':(7,14)
					}
				]
			},
			{
				'name':'High Platform',
				'ranges':[
					{
						'groups':(8,9),
						'tiles':(0,5),
						'messy':(7,14)
					}
				]
			},
			{
				'name':'Solar Array',
				'ranges':[
					{
						'groups':(12,13),
						'tiles':(0,0),
						'messy':None
					}
				]
			},
			{
				'name':'Plating',
				'ranges':[
					{
						'groups':(6,7),
						'tiles':(0,5),
						'messy':(7,14)
					}
				]
			},
			{
				'name':'Dark Platform',
				'ranges':[
					{
						'groups':(16,17),
						'tiles':(0,5),
						'messy':(7,14)
					}
				]
			},
			{
				'name':'Platform',
				'ranges':[
					{
						'groups':(4,5),
						'tiles':(0,5),
						'messy':(7,14)
					}
				]
			},
			{
				'name':'Rusty Pit',
				'ranges':[
					{
						'groups':(18,19),
						'tiles':(0,9),
						'messy':None
					}
				]
			},
			{
				'name':'Low Platform',
				'ranges':[
					{
						'groups':(14,15),
						'tiles':(0,5),
						'messy':(7,14)
					}
				]
			},
			{
				'name':'Space',
				'ranges':[
					{
						'groups':(2,3),
						'tiles':(0,0),
						'messy':None
					}
				]
			}
		]
	},
	CHKSectionERA.INSTALLATION:{
		'name':CHKSectionERA.TILESET_NAME(CHKSectionERA.INSTALLATION),
		'types':[
			{
				'name':'Bottomless Pit',
				'ranges':[
					{
						'groups':(12,13),
						'tiles':(0,0),
						'messy':None
					}
				]
			},
			{
				'name':'Sunstructure Panels',
				'ranges':[
					{
						'groups':(14,15),
						'tiles':(0,3),
						'messy':None
					}
				]
			},
			{
				'name':'Plating',
				'ranges':[
					{
						'groups':(10,11),
						'tiles':(0,5),
						'messy':None
					}
				]
			},
			{
				'name':'Substructure Plating',
				'ranges':[
					{
						'groups':(4,5),
						'tiles':(0,5),
						'messy':None
					}
				]
			},
			{
				'name':'Roof',
				'ranges':[
					{
						'groups':(8,9),
						'tiles':(0,0),
						'messy':None
					}
				]
			},
			{
				'name':'Floor',
				'ranges':[
					{
						'groups':(6,7),
						'tiles':(0,0),
						'messy':None
					}
				]
			},
			{
				'name':'Substructure',
				'ranges':[
					{
						'groups':(2,3),
						'tiles':(0,0),
						'messy':None
					}
				]
			}
		]
	},
	CHKSectionERA.ASHWORLD:{
		'name':CHKSectionERA.TILESET_NAME(CHKSectionERA.ASHWORLD),
		'types':[
			{
				'name':'High Shale',
				'ranges':[
					{
						'groups':(12,13),
						'tiles':(0,7),
						'messy':(9,10)
					}
				]
			},
			{
				'name':'High Lava',
				'ranges':[
					{
						'groups':(8,9),
						'tiles':(0,9),
						'messy':None
					}
				]
			},
			{
				'name':'High Dirt',
				'ranges':[
					{
						'groups':(6,7),
						'tiles':(0,7),
						'messy':(9,14)
					}
				]
			},
			{
				'name':'Broken Rock',
				'ranges':[
					{
						'groups':(16,17),
						'tiles':(0,12),
						'messy':None
					}
				]
			},
			{
				'name':'Shale',
				'ranges':[
					{
						'groups':(10,11),
						'tiles':(0,7),
						'messy':(9,10)
					}
				]
			},
			{
				'name':'Lava',
				'ranges':[
					{
						'groups':(4,5),
						'tiles':(0,9),
						'messy':None
					}
				]
			},
			{
				'name':'Dirt',
				'ranges':[
					{
						'groups':(2,3),
						'tiles':(0,7),
						'messy':(9,14)
					}
				]
			},
			{
				'name':'Magma',
				'ranges':[
					{
						'groups':(14,15),
						'tiles':(0,7),
						'messy':(9,14)
					}
				]
			}
		]
	},
	CHKSectionERA.JUNGLE:{
		'name':CHKSectionERA.TILESET_NAME(CHKSectionERA.JUNGLE),
		'types':[
			{
				'name':'High Temple',
				'ranges':[
					{
						'groups':(24,25),
						'tiles':(0,4),
						'messy':None
					}
				]
			},
			{
				'name':'High Raised Jungle',
				'ranges':[
					{
						'groups':(22,23),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'High Ruins',
				'ranges':[
					{
						'groups':(20,21),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'High Jungle',
				'ranges':[
					{
						'groups':(18,19),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'High Dirt',
				'ranges':[
					{
						'groups':(4,5),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			},
			{
				'name':'Temple',
				'ranges':[
					{
						'groups':(16,17),
						'tiles':(0,4),
						'messy':None
					}
				]
			},
			{
				'name':'Raised Jungle',
				'ranges':[
					{
						'groups':(12,13),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Ruins',
				'ranges':[
					{
						'groups':(14,15),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Rocky Ground',
				'ranges':[
					{
						'groups':(10,11),
						'tiles':(0,11),
						'messy':None
					}
				]
			},
			{
				'name':'Jungle',
				'ranges':[
					{
						'groups':(8,9),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Mud',
				'ranges':[
					{
						'groups':(26,27),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			},
			{
				'name':'Dirt',
				'ranges':[
					{
						'groups':(2,3),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			},
			{
				'name':'Water',
				'ranges':[
					{
						'groups':(6,7),
						'tiles':(0,5),
						'messy':None
					}
				]
			}
		]
	},
	CHKSectionERA.DESERT:{
		'name':CHKSectionERA.TILESET_NAME(CHKSectionERA.DESERT),
		'types':[
			{
				'name':'High Compound',
				'ranges':[
					{
						'groups':(24,25),
						'tiles':(0,4),
						'messy':None
					}
				]
			},
			{
				'name':'High Sandy Sunken Pit',
				'ranges':[
					{
						'groups':(22,23),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'High Crags',
				'ranges':[
					{
						'groups':(20,21),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'High Sand Dunes',
				'ranges':[
					{
						'groups':(18,19),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'High Dirt',
				'ranges':[
					{
						'groups':(4,5),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			},
			{
				'name':'Compund',
				'ranges':[
					{
						'groups':(16,17),
						'tiles':(0,4),
						'messy':None
					}
				]
			},
			{
				'name':'Sandy Sunken Pit',
				'ranges':[
					{
						'groups':(12,13),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Crags',
				'ranges':[
					{
						'groups':(14,15),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Rocky Ground',
				'ranges':[
					{
						'groups':(10,11),
						'tiles':(0,11),
						'messy':None
					}
				]
			},
			{
				'name':'Sand Dunes',
				'ranges':[
					{
						'groups':(8,9),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Dried Mud',
				'ranges':[
					{
						'groups':(26,27),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			},
			{
				'name':'Dirt',
				'ranges':[
					{
						'groups':(2,3),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			},
			{
				'name':'Tar',
				'ranges':[
					{
						'groups':(6,7),
						'tiles':(0,2),
						'messy':(4,6)
					}
				]
			}
		]
	},
	CHKSectionERA.ARCTIC:{
		'name':CHKSectionERA.TILESET_NAME(CHKSectionERA.ARCTIC),
		'types':[
			{
				'name':'High Outpost',
				'ranges':[
					{
						'groups':(24,25),
						'tiles':(0,2),
						'messy':(4,5)
					}
				]
			},
			{
				'name':'High Water',
				'ranges':[
					{
						'groups':(22,23),
						'tiles':(0,5),
						'messy':None
					}
				]
			},
			{
				'name':'High Grass',
				'ranges':[
					{
						'groups':(20,21),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'High Dirt',
				'ranges':[
					{
						'groups':(18,19),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'High Snow',
				'ranges':[
					{
						'groups':(4,5),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			},
			{
				'name':'Outpost',
				'ranges':[
					{
						'groups':(16,17),
						'tiles':(0,2),
						'messy':(4,5)
					}
				]
			},
			{
				'name':'Water',
				'ranges':[
					{
						'groups':(12,13),
						'tiles':(0,5),
						'messy':None
					}
				]
			},
			{
				'name':'Grass',
				'ranges':[
					{
						'groups':(14,15),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Rocky Snow',
				'ranges':[
					{
						'groups':(10,11),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Dirt',
				'ranges':[
					{
						'groups':(8,9),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Moguls',
				'ranges':[
					{
						'groups':(26,27),
						'tiles':(0,5),
						'messy':(7,14)
					}
				]
			},
			{
				'name':'Snow',
				'ranges':[
					{
						'groups':(2,3),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			},
			{
				'name':'Ice',
				'ranges':[
					{
						'groups':(6,7),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			}
		]
	},
	CHKSectionERA.TWILIGHT:{
		'name':CHKSectionERA.TILESET_NAME(CHKSectionERA.TWILIGHT),
		'types':[
			{
				'name':'High Basilica',
				'ranges':[
					{
						'groups':(24,25),
						'tiles':(0,4),
						'messy':None
					}
				]
			},
			{
				'name':'High Sunken Ground',
				'ranges':[
					{
						'groups':(22,23),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'High Flagstones',
				'ranges':[
					{
						'groups':(20,21),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'High Crushed Rock',
				'ranges':[
					{
						'groups':(18,19),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'High Dirt',
				'ranges':[
					{
						'groups':(4,5),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			},
			{
				'name':'Basilica',
				'ranges':[
					{
						'groups':(16,17),
						'tiles':(0,4),
						'messy':None
					}
				]
			},
			{
				'name':'Sunken Ground',
				'ranges':[
					{
						'groups':(12,13),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Flagstones',
				'ranges':[
					{
						'groups':(14,15),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Crevices',
				'ranges':[
					{
						'groups':(10,11),
						'tiles':(0,11),
						'messy':None
					}
				]
			},
			{
				'name':'Crushed Rock',
				'ranges':[
					{
						'groups':(8,9),
						'tiles':(0,5),
						'messy':(7,12)
					}
				]
			},
			{
				'name':'Mud',
				'ranges':[
					{
						'groups':(26,27),
						'tiles':(0,8),
						'messy':(10,14)
					}
				]
			},
			{
				'name':'Dirt',
				'ranges':[
					{
						'groups':(2,3),
						'tiles':(0,7),
						'messy':(9,14)
					}
				]
			},
			{
				'name':'Water',
				'ranges':[
					{
						'groups':(6,7),
						'tiles':(0,5),
						'messy':None
					}
				]
			}
		]
	}
}

def z_position(y, elevation, img_offset=0):
	if elevation < 2:
		return elevation
	return ((int(y / 32.0) + 1) * (256*256)) + (128 + elevation * 256) + img_offset
def z_position_unit(unit, unitsdat):
	elevation = unitsdat.get_value(unit.unit_id, 'ElevationLevel')
	return z_position(unit.position[1], elevation)	
def compare_z(unit1, unit2, unitsdat, reverse=False):
	zorder1 = z_position_unit(unit1, unitsdat)
	zorder2 = z_position_unit(unit2, unitsdat)
	if zorder1 < zorder2:
		return 1 if reverse else -1
	if zorder1 > zorder2:
		return -1 if reverse else 1
	return 0

class BWImage:
	GRP_CACHE = {}
	FRAME_CACHE = {}

	@staticmethod
	def purge_frames(grpFile=None, player_color_id=None, flipHor=None, draw_function_id=None, draw_remapping=None, index=None):
		keys = [grpFile, player_color_id, flipHor, draw_function_id, draw_remapping, index]
		while keys[-1] == None:
			del keys[-1]
		def do_purge(cache, keys):
			if key[0] == None:
				for k in cache.keys():
					do_purge(cache[k], keys[1:])
			elif len(keys) == 1:
				del cache[key[0]]
			else:
				do_purge(cache[k], keys[1:])
		if not keys:
			BWImage.FRAME_CACHE = {}
		else:
			do_purge(BWImage.FRAME_CACHE, keys)

	def __init__(self, ui, ref, image_id, pos, parent=None, grpPath='', elevation=4, pos_offset=(0,0), elevation_offset=0, unit_ref=None):
		self.ui = ui
		self.ref = ref
		self.unit_ref = unit_ref
		self.image_id = image_id
		self.parent = parent
		self.children = []
		self.iscript_id = self.ui.imagesdat.get_value(self.image_id,'IscriptID')
		self.header_jump(0)
		self.iscript_wait = 0
		self.iscript_turns = self.ui.imagesdat.get_value(self.image_id,'GfxTurns')
		self.iscript_direction = 0
		if self.iscript_turns:
			self.iscript_direction = int(random.uniform(0,16))
		self.draw_function = GRP.rle_normal
		self.draw_info = None
		self.draw_function_id = self.ui.imagesdat.get_value(self.image_id, 'DrawFunction')
		self.draw_remapping = self.ui.imagesdat.get_value(self.image_id, 'Remapping')
		self.iscript_opcodes = {
			0: self.op_playfram,
			1: self.op_playframtile,
# sethorpos
			3: self.op_setvertpos,
# setpos
			5: self.op_wait,
			6: self.op_waitrand,
			7: self.op_goto,
			8: self.op_imgol,
			9: self.op_imgul,
# imgolorig
# switchul
# __0c
# imgoluselo
# imguluselo
# sprol
# highsprol
			17: self.op_lowsprul,
# uflunstable
# spruluselo
# sprul
# sproluselo
			22: self.op_end,
# setflipstate
# playsnd
# playsndrand
# playsndbtwn
# domissiledmg
# attackmelee
			29: self.op_followmaingraphic,
			30: self.op_randcondjmp,
			31: self.op_turnccwise,
			32: self.op_turncwise,
# turnlcwise
			34: self.op_turnrand,
# setspawnframe
# sigorder
# attackwith
# attack
# castspell
# useweapon
# move
# gotorepeatattk
# engframe
# engset
# __2d
# nobrkcodestart
# nobrkcodeend
# ignorerest
# attkshiftproj
# tmprmgraphicstart
# tmprmgraphicend
			52: self.op_setfldirect,
# call
# return
# setflspeed
# creategasoverlays
# pwrupcondjmp
# trgtrangecondjmp
# trgtarccondjmp
# curdirectcondjmp
# imgulnextid
# __3e
# liftoffcondjmp
# warpoverlay
# orderdone
# grdsprol
# __43
# dogrddamage
		}
		self.position = list(pos)
		self.position_offset = list(pos_offset)
		self.frame = 0
		self.grpFile = None
		self.grp = None
		self.player_color_id = None
		self.elevation = elevation
		self.elevation_offset = elevation_offset
		self.pal = 'Terrain'
		string_id = self.ui.imagesdat.get_value(self.image_id,'GRPFile')
		if string_id:
			self.grpFile = grpPath + self.ui.imagestbl.strings[string_id-1][:-1]
		if self.draw_function_id == 9 and 0 < self.draw_remapping < 4:
			self.pal = ['o','b','g'][self.draw_remapping-1] + 'fire'
		elif self.draw_function_id == 10:
			self.draw_function = GRP.rle_shadow
		elif self.draw_function_id == 13:
			self.draw_function = GRP.rle_outline
			self.draw_info = GRP.OUTLINE_ALLY
			print((1, self.parent))
			print((2, self.parent.unit_ref))
			if self.parent != None and self.parent.unit_ref != None:
				units = self.ui.chk.get_section(CHKSectionUNIT.NAME)
				unit = units.get_unit(self.parent.unit_ref)
				if unit:
					print((3,unit.owner))
					ownr = self.ui.chk.get_section(CHKSectionOWNR.NAME)
					print((4,ownr.owners[unit.owner]))
					owner = ownr.owners[unit.owner]
					if owner == CHKSectionOWNR.HUMAN:
						self.draw_info = GRP.OUTLINE_SELF
					elif owner == CHKSectionOWNR.COMPUTER:
						self.draw_info = GRP.OUTLINE_ENEMY
					else:
						self.draw_info = GRP.OUTLINE_ALLY
		elif self.unit_ref != None:
			units = self.ui.chk.get_section(CHKSectionUNIT.NAME)
			unit = units.get_unit(self.unit_ref)
			if unit:
				self.player_color_id = self.ui.chk.player_color(unit.owner)
				if self.player_color_id != None:
					start_index = self.player_color_id * 8
					if start_index+7 < len(self.ui.tunitpcx.image[0]):
						self.draw_info = []
						for n in range(start_index,start_index+8):
							i = self.ui.tunitpcx.image[0][n]
							self.draw_info.append(self.ui.palettes['Units'][i])

	def z_position(self):
		return z_position(self.position[1], self.elevation, self.elevation_offset)

	def render_position(self):
		return (self.position[0] + self.position_offset[0], self.position[1] + self.position_offset[1])

	def get_grp(self):
		if self.grp == None:
			if self.grpFile in BWImage.GRP_CACHE:
				self.grp = BWImage.GRP_CACHE[self.grpFile]
			else:
				grp_file = self.ui.mpqhandler.get_file('MPQ:' + self.grpFile)
				try:
					grp = GRP.CacheGRP()
					grp.load_file(grp_file)
				except PyMSError as e:
					return None
				self.grp = grp
				BWImage.GRP_CACHE[self.grpFile] = grp
		return self.grp

	def current_frame(self):
		frame = None
		if self.grpFile:
			flipHor = False
			index = self.frame
			if self.iscript_turns:
				flipHor = (self.iscript_direction > 16)
				if flipHor:
					index += 33 - self.iscript_direction
				else:
					index += self.iscript_direction
			if self.grpFile in BWImage.FRAME_CACHE \
			and self.player_color_id in BWImage.FRAME_CACHE[self.grpFile] \
			and flipHor in BWImage.FRAME_CACHE[self.grpFile][self.player_color_id] \
			and self.draw_function_id in BWImage.FRAME_CACHE[self.grpFile][self.player_color_id][flipHor] \
			and self.draw_remapping in BWImage.FRAME_CACHE[self.grpFile][self.player_color_id][flipHor][self.draw_function_id]:
				frame = BWImage.FRAME_CACHE[self.grpFile][self.player_color_id][flipHor][self.draw_function_id][self.draw_remapping].get(index)
			if frame == None:
				grp = self.get_grp()
				if grp:
					frame = GRP.frame_to_photo(self.ui.palettes[self.pal], grp, index, True, False, True, 0, flipHor, self.draw_function, self.draw_info)
					if not self.grpFile in BWImage.FRAME_CACHE:
						BWImage.FRAME_CACHE[self.grpFile] = {}
					if not self.player_color_id in BWImage.FRAME_CACHE[self.grpFile]:
						BWImage.FRAME_CACHE[self.grpFile][self.player_color_id] = {}
					if not flipHor in BWImage.FRAME_CACHE[self.grpFile][self.player_color_id]:
						BWImage.FRAME_CACHE[self.grpFile][self.player_color_id][flipHor] = {}
					if not self.draw_function_id in BWImage.FRAME_CACHE[self.grpFile][self.player_color_id][flipHor]:
						BWImage.FRAME_CACHE[self.grpFile][self.player_color_id][flipHor][self.draw_function_id] = {}
					if not self.draw_remapping in BWImage.FRAME_CACHE[self.grpFile][self.player_color_id][flipHor][self.draw_function_id]:
						BWImage.FRAME_CACHE[self.grpFile][self.player_color_id][flipHor][self.draw_function_id][self.draw_remapping] = {}
					BWImage.FRAME_CACHE[self.grpFile][self.player_color_id][flipHor][self.draw_function_id][self.draw_remapping][index] = frame
		return frame

	def die(self):
		if not self.header_jump(1):
			self.op_end()

	def header_jump(self, header):
		headers = self.ui.iscriptbin.headers[self.iscript_id][2]
		if header < len(headers):
			iscript_offset = headers[header]
			if iscript_offset != None:
				self.iscript_wait = 0
				self.op_goto(iscript_offset)
				for child in self.children:
					child.header_jump(header)
				return True
			# elif header == 1:
			# 	self.op_end()
		return False

	def op_playfram(self, frame):
		self.frame = frame
		return True

	def op_playframtile(self, frame):
		era = self.ui.chk.get_section(CHKSectionERA.NAME)
		frame += era.tileset
		if frame < self.get_grp().frames:
			self.frame = frame
		return True

	def op_setvertpos(self, y_offset):
		self.position_offset[1] = y_offset
		return True

	def op_wait(self, ticks):
		self.iscript_wait += FRAME_DELAY * ticks
		return True

	def op_waitrand(self, min_ticks, max_ticks):
		ticks = random.randint(min_ticks, max_ticks)
		return self.op_wait(ticks)

	def op_goto(self, offset):
		self.iscript_cmd = self.ui.iscriptbin.code.index(offset)
		return False

	def op_imgol(self, image_id, offset_x,offset_y):
		ref = self.ref + '-child%d' % len(self.children)
		image = BWImage(self.ui, ref, image_id, (self.position[0], self.position[1]), self, 'unit\\', self.elevation, (offset_x,offset_y), 1)
		self.children.append(image)
		self.ui.maplayer_images.add_image(image)
		return True

	def op_imgul(self, image_id, offset_x,offset_y):
		ref = self.ref + '-child%d' % len(self.children)
		image = BWImage(self.ui, ref, image_id, (self.position[0], self.position[1]), self, 'unit\\', self.elevation, (offset_x,offset_y), -1)
		self.children.append(image)
		self.ui.maplayer_images.add_image(image)
		return True

	def op_lowsprul(self, sprite_id, offset_x,offset_y):
		ref = 'sprite%d' % sprite_id
		image_id = self.ui.spritesdat.get_value(sprite_id,'ImageFile')
		image = BWImage(self.ui, ref, image_id, (self.position[0], self.position[1]), None, 'unit\\', 1, (offset_x,offset_y))
		self.ui.maplayer_images.add_image(image)
		return True

	def op_end(self):
		self.iscript_wait = sys.maxint
		self.ui.maplayer_images.remove_image(self)
		for child in self.children:
			child.parent = None
			# self.ui.maplayer_images.remove_image(child)
		return False

	def op_followmaingraphic(self):
		if self.parent:
			self.frame = self.parent.frame
			self.iscript_direction = self.parent.iscript_direction
		else:
			self.op_end()
		return True

	def op_randcondjmp(self, chance, offset):
		rand = random.randint(0,255)
		if rand <= chance:
			return self.op_goto(offset)
		return True

	def op_turnccwise(self, delta):
		return self.op_setfldirect(self.iscript_direction - delta)

	def op_turncwise(self, delta):
		return self.op_setfldirect(self.iscript_direction + delta)

	def op_turnrand(self, delta):
		rand = random.randint(0,65535)
		if rand & 3 == 1:
			return self.op_turnccwise(delta)
		return self.op_turncwise(delta)

	def op_setfldirect(self, direction):
		while direction < 0:
			direction += 34
		self.iscript_direction = direction % 34
		return True

	def tick(self, dt):
		# return
		if self.iscript_wait > 0:
			self.iscript_wait -= dt
			if self.iscript_wait < 0:
				self.iscript_wait = 0
		dirty = False
		while self.iscript_wait == 0:
			cmd = self.ui.iscriptbin.code.getitem(self.iscript_cmd)
			opcode = self.iscript_opcodes.get(cmd[0])
			inc = True
			if opcode:
				dirty = True
				inc = opcode(*cmd[1:])
			# else:
			# 	print((self.iscript_id, cmd))
			if inc:
				self.iscript_cmd += 1
		return dirty

class ActionUpdateLocation(ActionUpdateValues):
	def __init__(self, ui, location_id, location, attrs):
		ActionUpdateValues.__init__(self, location, attrs)
		self.ui = ui
		self.location_id = location_id

	def get_obj(self):
		locations = self.ui.chk.get_section(CHKSectionMRGN.NAME)
		return locations.locations[self.location_id]

	def update_display(self, info):
		if self.ui.current_editlayer == self.ui.editlayer_locations:
			self.ui.current_editlayer.update_location(self.location_id)
		if 'name' in self.start_values or 'name' in self.end_values:
			self.ui.listlayer_locations.clear_list()
			self.ui.listlayer_locations.populate_list()

class ActionUpdateString(Action):
	def __init__(self, ui, string_id, start_text):
		self.ui = ui
		self.string_id = string_id
		self.start_text = start_text
		self.end_text = None

	def update_end_text(self):
		strings = self.ui.chk.get_section(CHKSectionSTR.NAME)
		string = strings.get_string(self.string_id)
		if string:
			self.end_text = string.text

	def undo(self):
		strings = self.ui.chk.get_section(CHKSectionSTR.NAME)
		if self.end_text != None and self.start_text == None:
			strings.delete_string(self.string_id)
		else:
			strings.set_string(self.string_id, self.start_text)

	def redo(self):
		strings = self.ui.chk.get_section(CHKSectionSTR.NAME)
		if self.start_text != None and self.end_text == None:
			strings.delete_string(self.string_id)
		else:
			strings.set_string(self.string_id, self.end_text)

def resize_event(location, mouseX,mouseY):
	event = []
	x1,y1,x2,y2 = location.normalized_coords()
	if x1-5 <= mouseX <= x2+5 and y1-5 <= mouseY <= y2+5:
		event.append(EditLayer.EDIT_MOVE)
		dist_left = abs(location.start[0] - mouseX)
		dist_right = abs(location.end[0] - mouseX)
		if dist_left < dist_right and dist_left <= 5:
			event = [EditLayer.EDIT_RESIZE_LEFT,EditLayer.EDIT_NONE]
		elif dist_right < dist_left and dist_right <= 5:
			event = [EditLayer.EDIT_RESIZE_RIGHT,EditLayer.EDIT_NONE]
		dist_top = abs(location.start[1] - mouseY)
		dist_bot = abs(location.end[1] - mouseY)
		if dist_top < dist_bot and dist_top <= 5:
			if len(event) == 1:
				event = [EditLayer.EDIT_NONE,EditLayer.EDIT_RESIZE_TOP]
			else:
				event[1] = EditLayer.EDIT_RESIZE_TOP
		elif dist_bot < dist_top and dist_bot <= 5:
			if len(event) == 1:
				event = [EditLayer.EDIT_NONE,EditLayer.EDIT_RESIZE_BOTTOM]
			else:
				event[1] = EditLayer.EDIT_RESIZE_BOTTOM
	return event

class EditLayer:
	INACTIVE = 0
	ACTIVE = 1

	MOUSE_LEFT = 1
	MOUSE_MIDDLE = 2
	MOUSE_RIGHT = 3

	MODIFIER_SHIFT = (1 << 0)
	MODIFIER_CTRL = (1 << 1)
	MOUSE_DOWN = (1 << 2)
	MOUSE_MOVE = (1 << 3)
	MOUSE_UP = (1 << 4)
	MOUSE_DOUBLE = (1 << 5)

	EDIT_NONE = 0
	EDIT_MOVE = 1
	EDIT_RESIZE_LEFT = 2
	EDIT_RESIZE_TOP = 3
	EDIT_RESIZE_RIGHT = 4
	EDIT_RESIZE_BOTTOM = 5

	def __init__(self, ui, name):
		self.ui = ui
		self.name = name
		self.list_group = None
		self.mode = EditLayer.INACTIVE

	def list_select(self, info):
		pass

	def set_mode(self, mode, x1,y1, x2,y2):
		isNew = mode != self.mode
		self.mode = mode
		return isNew

	def update_display(self, x1,y1, x2,y2, mouseX,mouseY):
		pass

	def mouse_event(self, button, button_event, x1,y1, x2,y2, mouseX,mouseY):
		pass

class EditLayerTerrain(EditLayer):
	EDIT_RECTANGULAR = 0
	EDIT_INDEXED = 1

	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Terrain")
		self.type_id = 0
		self.messy = False

	def list_select(self, type_id):
		self.type_id = type_id

	def set_mode(self, mode, x1,y1, x2,y2):
		if EditLayer.set_mode(self, mode, x1,y1, x2,y2):
			tag = 'tile_border'
			if self.mode == EditLayer.INACTIVE:
				self.ui.mapCanvas.delete(tag)
			else:
				self.ui.mapCanvas.create_rectangle(0,0,0,0, outline='#FF0000', tags=tag)

	def update_display(self, x1,y1, x2,y2, mouseX,mouseY):
		if self.mode == EditLayer.ACTIVE:
			tag = 'tile_border'
			x = nearest_multiple(x1+mouseX,32,math.floor)
			y = nearest_multiple(y1+mouseY,32,math.floor)
			self.ui.mapCanvas.coords(tag, x,y, x+32,y+32)
			self.ui.mapCanvas.tag_raise(tag)

	def mouse_event(self, button, button_event, x1,y1, x2,y2, mouseX,mouseY):
		if self.mode == EditLayer.ACTIVE and (button_event & EditLayer.MOUSE_DOWN or button_event & EditLayer.MOUSE_MOVE):
			x = int((x1+mouseX) / 32.0)
			y = int((y1+mouseY) / 32.0)
			era = self.ui.chk.get_section(CHKSectionERA.NAME)
			details = TERRAIN_DETAILS[era.tileset]['types'][self.type_id]
			options = details.get('options')
			if options == None:
				options = []
				details['options'] = options
				for range_details in details['ranges']:
					for group in range(*range_details['groups']):
						for tile in range(*range_details['tiles']):
							options.append([group,tile])
						if range_details['messy'] != None and self.messy:
							for tile in range(*range_details['messy']):
								options.append([group,tile])
			option = random.choice(options)
			tiles = self.ui.chk.get_section(CHKSectionTILE.NAME)
			tiles.map[y][x] = option
			self.ui.maplayer_terrain.update_tile(x,y)

class EditLayerDoodads(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Doodads")

class EditLayerFogOfWar(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Fog of War")

class EditLayerLocations(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Locations")
		self.snap_to_grid = True
		self.always_display = self.ui.settings.get('always_show_locations', False)
		self.show_anywhere = False
		self.locations = {}
		self.zOrder = None
		self.old_cursor = None
		self.current_event = []
		self.mouse_offset = [0,0]
		self.resize_location = None
		self.action = None

	def raise_location(self, location_id):
		self.ui.mapCanvas.tag_raise('location%d' % location_id)
		self.zOrder.remove(location_id)
		self.zOrder.insert(0, location_id)

	def list_select(self, location_id):
		self.raise_location(location_id)
		dims = self.ui.chk.get_section(CHKSectionDIM.NAME)
		map_width = dims.width * 32
		map_height = dims.height * 32
		view_width = self.ui.mapCanvas.winfo_width()
		view_height = self.ui.mapCanvas.winfo_height()
		locations = self.ui.chk.get_section(CHKSectionMRGN.NAME)
		location = locations.locations[location_id]
		x1,y1,x2,y2 = location.normalized_coords()
		loc_width = x2-x1
		loc_height = y2-y1
		x = x1
		y = y1
		if loc_width < view_width:
			x -= (view_width - loc_width) / 2.0
		if loc_height < view_height:
			y -= (view_height - loc_height) / 2.0
		self.ui.mapCanvas.xview_moveto(x / float(map_width))
		self.ui.mapCanvas.yview_moveto(y / float(map_height))

	def set_mode(self, mode, x1,y1, x2,y2):
		if EditLayer.set_mode(self, mode, x1,y1, x2,y2):
			if self.mode == EditLayer.ACTIVE:
				self.old_cursor = self.ui.mapCanvas.cget('cursor')
				# dims = self.chk.get_section(CHKSectionDIM.NAME)
				locations = self.ui.chk.get_section(CHKSectionMRGN.NAME)
				if not self.zOrder:
					self.zOrder = list(range(len(locations.locations)))
				for l in self.zOrder:
					if l == 63 and not self.show_anywhere:
						continue
					self.update_location(l)
			else:
				self.ui.mapCanvas.config(cursor=self.old_cursor)
				for tag in self.locations.keys():
					self.ui.mapCanvas.delete(tag)
					self.ui.mapCanvas.delete(tag + '-name')
				self.locations = {}

	def update_display(self, x1,y1, x2,y2, mouseX,mouseY):
		if self.mode == EditLayer.ACTIVE:
			x = x1+mouseX
			y = y1+mouseY
			locations = self.ui.chk.get_section(CHKSectionMRGN.NAME)
			cursor = [self.old_cursor]
			found = None
			for l in self.zOrder:
				if l == 63 and not self.show_anywhere:
					continue
				location = locations.locations[l]
				if location.in_use():
					x1,y1,x2,y2 = location.normalized_coords()
					event = resize_event(location,x,y)
					if event:
						if event[0] == EditLayer.EDIT_MOVE:
							cursor.extend(['crosshair','fleur','size'])
						elif event[0] == EditLayer.EDIT_RESIZE_LEFT:
							cursor.extend(['left_side','size_we','resizeleft','resizeleftright'])
						elif event[0] == EditLayer.EDIT_RESIZE_RIGHT:
							cursor.extend(['right_side','size_we','resizeright','resizeleftright'])
						if len(event) == 2:
							if event[1] == EditLayer.EDIT_RESIZE_TOP:
								cursor.extend(['top_side','size_ns','resizeup','resizeupdown'])
							elif event[1] == EditLayer.EDIT_RESIZE_BOTTOM:
								cursor.extend(['bottom_side','size_ns','resizedown','resizeupdown'])
							if event[0] == EditLayer.EDIT_RESIZE_LEFT and event[1] == EditLayer.EDIT_RESIZE_TOP:
								cursor.extend(['top_left_corner','size_nw_se','resizetopleft'])
							elif event[0] == EditLayer.EDIT_RESIZE_RIGHT and event[1] == EditLayer.EDIT_RESIZE_TOP:
								cursor.extend(['top_right_corner','size_ne_sw','resizetopright'])
							elif event[0] == EditLayer.EDIT_RESIZE_LEFT and event[1] == EditLayer.EDIT_RESIZE_BOTTOM:
								cursor.extend(['bottom_left_corner','size_ne_sw','resizebottomleft'])
							elif event[0] == EditLayer.EDIT_RESIZE_RIGHT and event[1] == EditLayer.EDIT_RESIZE_BOTTOM:
								cursor.extend(['bottom_right_corner','size_nw_se','resizebottomright'])
						found = location
						break
			if found:
				strings = self.ui.chk.get_section(CHKSectionSTR.NAME)
				name = strings.get_text(location.name-1, '')
				self.ui.edit_status.set('Edit Location: ' + TBL.decompile_string(name))
			else:
				self.ui.edit_status.set('Create new Location')
			apply_cursor(self.ui.mapCanvas, cursor)

	def update_location(self, location_id):
		locations = self.ui.chk.get_section(CHKSectionMRGN.NAME)
		location = locations.locations[location_id]
		tag = 'location%d' % location_id
		tag_name = tag + '-name'
		loc_rect = self.ui.mapCanvas.find_withtag(tag)
		loc_name = self.ui.mapCanvas.find_withtag(tag_name)
		if location.in_use():
			strings = self.ui.chk.get_section(CHKSectionSTR.NAME)
			name = strings.get_text(location.name-1, '')
			name = TBL.decompile_string(name)
			x1,y1,x2,y2 = location.normalized_coords()
			if loc_rect:
				self.ui.mapCanvas.coords(loc_rect, x1,y1,x2,y2)
			else:
				self.locations[tag] = self.ui.mapCanvas.create_rectangle(x1,y1, x2,y2, width=2, outline='#0080ff', stipple='gray75', tags=tag) #, fill='#5555FF'
			if loc_name:
				self.ui.mapCanvas.coords(loc_name, x1+2,y1+2)
				self.ui.mapCanvas.itemconfig(loc_name, text=name, width=x2-x1-4)
			else:
				self.ui.mapCanvas.create_text(x1+2,y1+2, anchor=NW, text=name, font=('courier', -10, 'normal'), fill='#00FF00', width=x2-x1-4, tags=tag_name)
		else:
			if loc_rect:
				self.ui.mapCanvas.delete(loc_rect)
			if loc_name:
				self.ui.mapCanvas.delete(loc_name)

	def mouse_event(self, button, button_event, x1,y1, x2,y2, mouseX,mouseY):
		if self.mode == EditLayer.ACTIVE:
			x = x1+mouseX
			y = y1+mouseY
			locations = self.ui.chk.get_section(CHKSectionMRGN.NAME)
			if button_event & EditLayer.MOUSE_DOWN or button_event & EditLayer.MOUSE_DOUBLE:
	 			self.current_event = []
	 			unused = None
	 			for l in self.zOrder:
	 				if l == 63 and not self.show_anywhere:
						continue
					location = locations.locations[l]
	 				if location.in_use():
						x1,y1,x2,y2 = location.normalized_coords()
						if button_event & EditLayer.MOUSE_DOWN:
							event = resize_event(location,x,y)
							if event:
								self.current_event = event
								if self.current_event[0] == EditLayer.EDIT_MOVE:
									self.mouse_offset = [x1 - x,y1 - y]
								self.resize_location = l
								self.ui.action_manager.start_group()
								self.action = ActionUpdateLocation(self.ui, l, location, ('start','end'))
								self.ui.action_manager.add_action(self.action)
								break
						elif x1 <= x <= x2 and y1 <= y <= y2:
							print('Edit Location')
							return
					elif unused == None:
						unused = l
				if not self.current_event and unused != None and button_event & EditLayer.MOUSE_DOWN:
					location = locations.locations[unused]
					self.ui.action_manager.start_group()
					strings = self.ui.chk.get_section(CHKSectionSTR.NAME)
					name = 'Location %d' % (unused+1)
					string = strings.lookup_string(name)
					if not string:
						string = strings.add_string(name)
						action = ActionUpdateString(self.ui, string.string_id, None)
						action.update_end_text()
						self.ui.action_manager.add_action(action)
					self.action = ActionUpdateLocation(self.ui, unused, location, ('name','elevation','start','end'))
					self.ui.action_manager.add_action(self.action)
					location.name = string.string_id+1
					location.start[0] = nearest_multiple(x,32,math.floor)
					location.start[1] = nearest_multiple(y,32,math.floor)
					location.end[0] = location.start[0] + 32
					location.end[1] = location.start[1] + 32
					location.elevation = CHKLocation.ALL_ELEVATIONS
					self.update_location(unused)
					self.ui.listlayer_locations.clear_list()
					self.ui.listlayer_locations.populate_list()
					self.current_event = [EditLayer.EDIT_RESIZE_RIGHT,EditLayer.EDIT_RESIZE_BOTTOM]
					self.mouse_offset = [0,0]
					self.resize_location = unused
			if self.current_event and self.resize_location != None:
				self.raise_location(self.resize_location)
				location = locations.locations[self.resize_location]
				if self.current_event[0] == EditLayer.EDIT_MOVE:
					x1,y1,x2,y2 = location.normalized_coords()
					dx = (x + self.mouse_offset[0]) - x1
					dy = (y + self.mouse_offset[1]) - y1
					location.start[0] += dx
					location.start[1] += dy
					location.end[0] += dx
					location.end[1] += dy
				else:
					if self.current_event[0] == EditLayer.EDIT_RESIZE_LEFT:
						location.start[0] = x
					elif self.current_event[0] == EditLayer.EDIT_RESIZE_RIGHT:
						location.end[0] = x
					if self.current_event[1] == EditLayer.EDIT_RESIZE_TOP:
						location.start[1] = y
					elif self.current_event[1] == EditLayer.EDIT_RESIZE_BOTTOM:
						location.end[1] = y
				if self.snap_to_grid:
					location.start[0] = nearest_multiple(location.start[0],32)
					location.start[1] = nearest_multiple(location.start[1],32)
					location.end[0] = nearest_multiple(location.end[0],32)
					location.end[1] = nearest_multiple(location.end[1],32)
				self.update_location(self.resize_location)
				if button_event & EditLayer.MOUSE_UP:
					self.current_event = []
					self.resize_location = None
					self.action.set_end_values(location, self.action.start_values.keys())
					self.action = None
					self.ui.end_undo_group()

class EditLayerUnits(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Units")
		self.selected_images = []
		self.selection_images = {}
		self.selecting_start = None
		self.selecting_images = None
		self.selection_box = None
		self.selecting_moved = False

	def set_mode(self, mode, x1,y1, x2,y2):
		if EditLayer.set_mode(self, mode, x1,y1, x2,y2):
			if self.mode != EditLayer.ACTIVE:
				self.deselect_all()

	def deselect(self, image):
		if image in self.selected_images:
			self.selected_images.remove(image)
			if image.ref in self.selection_images:
				selection_image = self.selection_images.get(image.ref)
				if selection_image != None:
					self.ui.maplayer_images.remove_image(selection_image)
					del self.selection_images[image.ref]

	def deselect_all(self):
		for image in list(self.selected_images):
			self.deselect(image)
			self.ui.mapCanvas.tag_raise('selection_box')

	def select(self, image):
		if image.unit_ref != None:
			self.selected_images.append(image)
			unit_sect = self.ui.chk.get_section(CHKSectionUNIT.NAME)
			selected_unit = unit_sect.get_unit(image.unit_ref)
			flingy_id = self.ui.unitsdat.get_value(selected_unit.unit_id, 'Graphics')
			sprite_id = self.ui.flingydat.get_value(flingy_id, 'Sprite')
			selection_image_id = self.ui.spritesdat.get_value(sprite_id, 'SelectionCircleImage')
			y_offset = self.ui.spritesdat.get_value(sprite_id, 'SelectionCircleOffset')
			selection_image = BWImage(self.ui, '%s-sel%d' % (image.unit_ref,selection_image_id), 561 + selection_image_id, (selected_unit.position[0], selected_unit.position[1]), image, 'unit\\', elevation=0, pos_offset=(0,y_offset))
			self.ui.maplayer_images.add_image(selection_image)
			self.selection_images[image.ref] = selection_image
			self.ui.mapCanvas.tag_raise('selection_box')

	def mouse_event(self, button, button_event, x1,y1, x2,y2, mouseX,mouseY):
		print(flags(button_event,8))
		if button == EditLayer.MOUSE_LEFT:
			x = x1 + mouseX
			y = y1 + mouseY
			if button_event & EditLayer.MOUSE_DOWN:
				self.selecting_start = (x,y)
				self.selecting_images = set()
				print(('Reset', flags(button_event,8)))
			elif self.selecting_start != None:
				if not button_event & (EditLayer.MODIFIER_SHIFT | EditLayer.MODIFIER_CTRL):
					self.deselect_all()
				if button_event & EditLayer.MOUSE_MOVE:
					self.selecting_moved = True
				sx1 = min(self.selecting_start[0],x)
				sy1 = min(self.selecting_start[1],y)
				sx2 = max(self.selecting_start[0],x)
				sy2 = max(self.selecting_start[1],y)
				if self.selecting_moved:
					if self.selection_box == None:
						self.selection_box = self.ui.mapCanvas.create_rectangle(sx1,sy1,sx2,sy2, outline='#FF0000', tags='selection_box')
					else:
						self.ui.mapCanvas.coords(self.selection_box, sx1,sy1,sx2,sy2)
				selecting = []
				unit_sect = self.ui.chk.get_section(CHKSectionUNIT.NAME)
				units = sorted(unit_sect.units.values(), cmp=lambda u1,u2,dat=self.ui.unitsdat: compare_z(u1,u2,dat,True))
				for unit in units:
					w = self.ui.unitsdat.get_value(unit.unit_id, 'StarEditPlacementBoxWidth')
					h = self.ui.unitsdat.get_value(unit.unit_id, 'StarEditPlacementBoxHeight')
					ux1 = unit.position[0] - w/2.0
					uy1 = unit.position[1] - h/2.0
					ux2 = ux1 + w
					uy2 = uy1 + h
					if not (sx1 > ux2 or ux1 > sx2 or sy1 > uy2 or uy1 > sy2):
						ref = 'unit%d' % unit.ref_id
						image = self.ui.maplayer_images.images.get(ref)
						if image:
							selecting.append(image)
				select = set(selecting)
				if not self.selecting_moved and selecting:
					select = set((selecting[0],))
				to_deselect = self.selecting_images - select
				to_select = select - set(self.selected_images)
				if not self.selecting_moved and select and not to_deselect and not to_select and button_event & (EditLayer.MODIFIER_SHIFT | EditLayer.MODIFIER_CTRL):
					to_deselect = select
				for image in to_deselect:
					self.deselect(image)
				for image in to_select:
					self.select(image)
				self.selecting_images = select
				if button_event & EditLayer.MOUSE_UP:
					self.ui.mapCanvas.delete(self.selection_box)
					self.selecting_start = None
					self.selecting_images = None
					self.selection_box = None
					self.selecting_moved = False

class EditLayerSprites(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Sprites")

class EditLayerPreviewFog(EditLayer):
	def __init__(self, ui):
		EditLayer.__init__(self, ui, "Preview Fog")

class MinimapLayer:
	def __init__(self, ui):
		self.ui = ui
		self.image = None
		self.scaled_raw = None
		self.scaled = None
		self.size = None

	def redraw(self):
		self.image = None
		if not self.ui.chk:
			return
		dims = self.ui.chk.get_section(CHKSectionDIM.NAME)
		points = min(256 / dims.width, 256 / dims.height)
		size = (dims.width*points,dims.height*points)
		self.image = PILImage.new('RGBA', size)
		drawer = PILDraw.ImageDraw(self.image)
		self.draw(drawer, size, points)

	def draw(self, drawer, size, points):
		pass

	def get_image(self, size):
		if size == self.size and self.scaled:
			return self.scaled
		if not self.image:
			return None
		scale = min(size[0] / float(self.image.size[0]),size[1] / float(self.image.size[1]))
		self.size = (int(round(self.image.size[0] * scale)), int(round(self.image.size[1] * scale)))
		self.scaled_raw = self.image.resize(self.size)
		self.scaled = ImageTk.PhotoImage(self.scaled_raw)
		return self.scaled

class MinimapLayerTerrain(MinimapLayer):
	def draw(self, drawer, size, points):
		dims = self.ui.chk.get_section(CHKSectionDIM.NAME)
		tiles = self.ui.chk.get_section(CHKSectionTILE.NAME)
		for y in range(dims.width):
			for x in range(dims.height):
				tile = [0,0]
				if y < len(tiles.map) and x < len(tiles.map[y]):
					tile = tiles.map[y][x]
				group = self.ui.tileset.cv5.groups[tile[0]]
				mega = group[13][tile[1]]
				minis = self.ui.tileset.vx4.graphics[mega]
				mini = minis[0]
				mini_image = self.ui.tileset.vr4.images[mini[0]]
				index = mini_image[7][2 if mini[1] else 6]
				color = self.ui.tileset.wpe.palette[index] + [255]
				drawer.rectangle((x*points,y*points,x*points+points,y*points+points), fill=tuple(color))

class MinimapLayerUnits(MinimapLayer):
	def draw(self, drawer, size, points):
		dims = self.ui.chk.get_section(CHKSectionDIM.NAME)
		unit = self.ui.chk.get_section(CHKSectionUNIT.NAME)
		units = sorted(unit.units.values(), cmp=lambda u1,u2,dat=self.ui.unitsdat: compare_z(u1,u2,dat))
		colors = CHKSectionCOLR.DEFAULT_COLORS
		colr = self.ui.chk.get_section(CHKSectionCOLR.NAME)
		if colr:
			colors = colr.colors
		for unit in units:
			w = self.ui.unitsdat.get_value(unit.unit_id, 'StarEditPlacementBoxWidth') / (dims.width*32.0) * size[0]
			h = self.ui.unitsdat.get_value(unit.unit_id, 'StarEditPlacementBoxHeight') / (dims.height*32.0) * size[0]
			x = unit.position[0] / (dims.width*32.0) * size[0] - w/2.0
			y = unit.position[1] / (dims.height*32.0) * size[1] - h/2.0
			color = CHKSectionCOLR.NEUTRAL
			if unit.owner < 8:
				color = colors[unit.owner]
			color = self.ui.tileset.wpe.palette[CHKSectionCOLR.PALETTE_INDICES(color)] + [255]
			drawer.rectangle((x, y, x+w, y+h), fill=tuple(color))

class MapLayer:
	def __init__(self, ui):
		self.ui = ui

	def update_display(self, x1,y1, x2,y2):
		pass

	def tick(self, dt):
		pass

class MapLayerTerrain(MapLayer):
	def __init__(self, ui):
		MapLayer.__init__(self, ui)
		self.tile_cache = {}
		self.map = {}

	def update_tile(self, x,y):
		tiles = self.ui.chk.get_section(CHKSectionTILE.NAME)
		tag = '%s,%s' % (x,y)
		if tag in self.map:
			self.ui.mapCanvas.delete(tag)
		tile = [0,0]
		if y < len(tiles.map) and x < len(tiles.map[y]):
			tile = tiles.map[y][x]
		group = self.ui.tileset.cv5.groups[tile[0]]
		mega = group[13][tile[1]]
		image = self.tile_cache.get(mega)
		if image == None:
			image = Tilesets.megatile_to_photo(self.ui.tileset, mega)
			self.tile_cache[mega] = image
		self.map[tag] = self.ui.mapCanvas.create_image((x+0.5) * 32, (y+0.5) * 32, image=image, tags=tag)
		self.ui.mapCanvas.tag_lower(tag)

	def update_display(self, x1,y1, x2,y2):
		tx1 = int(x1 / 32.0)
		ty1 = int(y1 / 32.0)
		tx2 = int(ceil(x2 / 32.0))
		ty2 = int(ceil(y2 / 32.0))
		for y in range(ty1,ty2):
			for x in range(tx1,tx2):
				tag = '%s,%s' % (x,y)
				item = self.map.get(tag)
				if not item:
					self.update_tile(x,y)

class MapLayerImages(MapLayer):
	def __init__(self, ui):
		MapLayer.__init__(self, ui)
		self.images = None

	def update_zorder(self):
		zorder = sorted(self.images.values(), key=lambda img: img.z_position())
		for image in zorder:
			self.ui.mapCanvas.tag_raise(image.ref)

	def add_image(self, image, update=True):
		self.images[image.ref] = image
		frame = image.current_frame()
		position = image.render_position()
		self.ui.mapCanvas.create_image(position[0],position[1], image=frame, tags=image.ref)
		if update:
			self.update_zorder()

	def remove_image(self, image):
		del self.images[image.ref]
		self.ui.mapCanvas.delete(image.ref)

	def update_display(self, x1,y1, x2,y2):
		if self.images == None:
			units = self.ui.chk.get_section(CHKSectionUNIT.NAME)
			self.images = {}
			for n in range(units.unit_count()):
				unit = units.nth_unit(n)
				flingy_id = self.ui.unitsdat.get_value(unit.unit_id, 'Graphics')
				sprite_id = self.ui.flingydat.get_value(flingy_id, 'Sprite')
				image_id = self.ui.spritesdat.get_value(sprite_id,'ImageFile')
				elevation = self.ui.unitsdat.get_value(unit.unit_id, 'ElevationLevel')
				ref = 'unit%d' % unit.ref_id
				image = BWImage(self.ui, ref, image_id, unit.position, None, 'unit\\', elevation, unit_ref=unit.ref_id)
				self.add_image(image, update=False)
			self.update_zorder()

	def tick(self, dt):
		for ref in self.images.keys():
			image = self.images.get(ref)
			if image and image.tick(dt):
				frame = image.current_frame()
				self.ui.mapCanvas.itemconfig(ref, image=frame)

class ListLayer:
	NAME = None

	def __init__(self, ui):
		self.ui = ui
		self.groupId = None
		self.options = {}

	def setup_group(self):
		self.groupId = self.ui.listbox.insert('-1', self.NAME, False)
		self.populate_list()
		return self.groupId

	def clear_list(self):
		self.ui.listbox.delete('%s.%s' % (self.groupId,ALL))
		self.options = {}

	def get_event(self, index):
		return self.options.get(index, (None,None))

	def option_name(self, option):
		pass

	def update_option(self, option):
		index = None
		for i,o in self.groups.iteritems():
			if o == option:
				index = i
				break
		if index:
			self.ui.listbox.set(index, self.option_name(option))

	def populate_list(self):
		pass

class ListLayerTerrain(ListLayer):
	NAME = 'Terrain'

	def option_name(self, option):
		era = self.ui.chk.get_section(CHKSectionERA.NAME)
		details = TERRAIN_DETAILS[era.tileset]
		return details['types'][option]['name']

	def populate_list(self):
		era = self.ui.chk.get_section(CHKSectionERA.NAME)
		details = TERRAIN_DETAILS[era.tileset]
		for t,ttype in enumerate(details['types']):
			name = self.option_name(t)
			listId = self.ui.listbox.insert(self.groupId + '.-1', name)
			self.options[listId] = (self.ui.editlayer_terrain, t)

class ListLayerLocations(ListLayer):
	NAME = 'Locations'

	def option_name(self, option):
		locations = self.ui.chk.get_section(CHKSectionMRGN.NAME)
		location = locations.locations[option]
		strings = self.ui.chk.get_section(CHKSectionSTR.NAME)
		name = strings.get_text(location.name-1, '')
		return TBL.decompile_string(name)

	def populate_list(self):
		locations = self.ui.chk.get_section(CHKSectionMRGN.NAME)
		for l,location in enumerate(locations.locations):
			if l == 63 and not self.ui.editlayer_locations.show_anywhere:
				continue
			if location.in_use():
				name = self.option_name(l)
				listId = self.ui.listbox.insert(self.groupId + '.-1', name)
				self.options[listId] = (self.ui.editlayer_locations, l)

class ListLayerUnits(ListLayer):
	NAME = 'Units'

	def option_name(self, option):
		# TODO: Custom names
		name = self.ui.stat_txt.strings[option]
		return TBL.decompile_string(name)

	def populate_list(self):
		groups = {}
		for u in range(self.ui.unitsdat.count):
			race = 'Neutral'
			flags = self.ui.unitsdat.get_value(u,'StarEditGroupFlags')
			if flags & 1:
				race = 'Zerg'
			elif flags & 2:
				race = 'Terran'
			elif flags & 4:
				race = 'Protoss'
			raceGroup = groups.get(race, {})
			if not race in groups:
				groups[race] = raceGroup
			name = self.ui.stat_txt.strings[u]
			split = name.split('\0')
			if len(split) == 4:
				groupName = split[-2]
			else:
				groupName = 'Other'
			items = raceGroup.get(groupName, [])
			if not groupName in raceGroup:
				raceGroup[groupName] = items
			items.append({'name':self.option_name(u), 'id':u})
		for raceName in sorted(groups.keys(), reverse=True):
			raceGroupId = self.ui.listbox.insert(self.groupId + '.-1', raceName, False)
			for groupName in sorted(groups[raceName]):
				subGroupId = self.ui.listbox.insert(raceGroupId + '.-1', groupName, False)
				for info in groups[raceName][groupName]:
					listId = self.ui.listbox.insert(subGroupId + '.-1', info['name'])
					self.options[listId] = (self.ui.editlayer_units, info['id'])

class ListLayerSprites(ListLayer):
	NAME = 'Sprites'

	def option_name(self, option):
		return ''

	def populate_list(self):
		pass

class ListLayerDoodads(ListLayer):
	NAME = 'Doodads'

	def option_name(self, option):
		return ''

	def populate_list(self):
		pass

class PyMAP(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyMAP',
			{
				'profiles':{
					'Default':{
						'stat_txt':'MPQ:rez\\stat_txt.tbl',
						'aiscript':'MPQ:scripts\\aiscript.bin',
						'imagestbl':'MPQ:arr\\images.tbl',
						'sfxdatatbl':'MPQ:arr\\sfxdata.tbl',
						'portdatatbl':'MPQ:arr\\portdata.tbl',
						'mapdatatbl':'MPQ:arr\\mapdata.tbl',
						'iscriptbin':'MPQ:scripts\\iscript.bin',
						'unitsdat':'MPQ:arr\\units.dat',
						'flingydat':'MPQ:arr\\flingy.dat',
						'spritesdat':'MPQ:arr\\sprites.dat',
						'imagesdat':'MPQ:arr\\images.dat',
						'tunitpcx':'MPQ:game\\tunit.pcx'
					}
				},
				'profile':'Default'
			}
		)
		#Window
		Tk.__init__(self)
		self.set_icon('PyMAP')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyMAP', Assets.version('PyMAP'))
		ga.track(GAScreen('PyMAP'))
		setup_trace('PyMAP', self)

		self.action_manager = ActionManager()

		self.status = StringVar()
		self.edit_status = StringVar()

		# self.dosave = [False,False]
		self.profile = self.settings['profiles'][self.settings['profile']]
		self.stat_txt = None
		self.imagestbl = None
		self.unitsdat = None
		self.flingydat = None
		self.spritesdat = None
		self.imagesdat = None
		self.aibin = None
		self.iscriptbin = None
		self.palettes = None
		self.tunitpcx = None

		self.map = None
		self.chk = None
		self.file = None
		self.edited = False
		self.tileset = None

		self.editlayer_terrain = EditLayerTerrain(self)
		self.editlayer_doodads = EditLayerDoodads(self)
		self.editlayer_fogofwar = EditLayerFogOfWar(self)
		self.editlayer_locations = EditLayerLocations(self)
		self.editlayer_units = EditLayerUnits(self)
		self.editlayer_sprites = EditLayerSprites(self)
		self.editlayer_previewfog = EditLayerPreviewFog(self)
		self.edit_layers = [self.editlayer_terrain,self.editlayer_doodads,self.editlayer_fogofwar,self.editlayer_locations,self.editlayer_units,self.editlayer_sprites,self.editlayer_previewfog]
		self.current_editlayer = None

		self.minimaplayer_terrain = MinimapLayerTerrain(self)
		self.minimaplayer_units = MinimapLayerUnits(self)
		self.minimap_layers = [self.minimaplayer_terrain,self.minimaplayer_units]

		self.maplayer_terrain = MapLayerTerrain(self)
		self.maplayer_images = MapLayerImages(self)
		self.map_layers = [self.maplayer_terrain,self.maplayer_images]

		self.listlayer_terrain = ListLayerTerrain(self)
		self.listlayer_locations = ListLayerLocations(self)
		self.listlayer_units = ListLayerUnits(self)
		self.listlayer_sprites = ListLayerSprites(self)
		self.listlayer_doodads = ListLayerDoodads(self)
		self.list_layers = [self.listlayer_terrain, self.listlayer_locations, self.listlayer_units, self.listlayer_sprites, self.listlayer_doodads]
		self.list_layer_indices = {}

		self.last_tick = None
		self.tick_delay = FRAME_DELAY
		self.tick_alarm = None

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			2,
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			2,
			('undo', self.do_undo, 'Undo (Ctrl+Z)', DISABLED, 'Ctrl+Z'),
			('redo', self.do_redo, 'Redo (Ctrl+Y)', DISABLED, 'Ctrl+Y'),
			2,
			('asc3topyai', self.file_settings, 'Manage data files (Ctrl+M)', NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default map editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyMAP', NORMAL, ''),
			10,
			('exit', self.exit, 'Exit (Alt+F4)', NORMAL, 'Alt+F4'),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				Tooltip(button, btn[2])
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
				a = btn[4]
				if a:
					if not a.startswith('F'):
						self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					else:
						self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		self.edit_layer_index = IntVar(0)
		self.edit_layer_index.trace('w', self.change_edit_layer)
		self.edit_layer_dropdown = DropDown(toolbar, self.edit_layer_index, [l.name for l in self.edit_layers], width=25)
		self.edit_layer_dropdown.pack(side=LEFT, padx=2)
		toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.panes = PanedWindow(self, orient=HORIZONTAL)
		self.panes.pack(fill=BOTH, expand=1)

		left = Frame(self.panes)
		self.panes.add(left)
		minimap_wide_container = Frame(left, bd=1, relief=SUNKEN)
		def place_minimap_wide_container(initial=False):
			width = left.winfo_width()
			minimap_wide_container.place(in_=left, x=0,y=0, width=width,height=min(width,262))
			if initial:
				minimap_wide_container.update()
		place_minimap_wide_container()
		minimap_container = Frame(left, bd=1, relief=SUNKEN)
		def place_minimap_container(initial=False):
			size = minimap_wide_container.winfo_height() - 6
			pad = (minimap_wide_container.winfo_width() - size)/2.0
			minimap_container.place(in_=minimap_wide_container, x=pad,y=2, width=size,height=size)
			if initial:
				minimap_container.update()
			self.resized_minimap()
		self.minimap = Canvas(minimap_container, background='#000000', highlightthickness=0)
		self.minimap.bind('<Button-1>', self.minimap_move)
		self.minimap.bind('<B1-Motion>', self.minimap_move)
		self.minimap.pack(fill=BOTH, expand=1)
		place_minimap_container()
		details = Frame(left)
		# listbox
		self.listbox = TreeList(details, groupsel=False)
		self.listbox.pack(fill=BOTH, expand=True)
		self.listbox.bind('<Button-1>', self.list_select)
		def place_details(initial=False):
			y = minimap_wide_container.winfo_height() + 5
			details.place(in_=left, x=0,y=y, width=left.winfo_width(),height=left.winfo_height()-y)
			if initial:
				details.update()
		place_details()
		def place_left_children(event=None, initial=False):
			place_minimap_wide_container(initial)
			place_minimap_container(initial)
			place_details(initial)
		left.bind('<Configure>', place_left_children)

		self.panes.paneconfigure(left, minsize=128)

		right = Frame(self.panes, bd=1, relief=SUNKEN)
		self.panes.add(right)

		self.mapCanvas = Canvas(right, background='#000000', highlightthickness=0)
		self.mapCanvas.grid(sticky=NSEW)
		self.mapCanvas.focus_set()
		def scroll_map(event):
			if self.chk:
				horizontal = False
				if hasattr(event, 'state') and getattr(event, 'state', 0):
					horizontal = True
				view = self.mapCanvas.yview
				if horizontal:
					view = self.mapCanvas.xview
				if event.delta > 0:
					view('scroll', -1, 'units')
				else:
					view('scroll', 1, 'units')
		self.mapCanvas.bind('<MouseWheel>', scroll_map)
		self.mapCanvas.bind('<Leave>', lambda e: self.edit_status.set(''))
		self.mapCanvas.bind('<Motion>', self.edit_update)
		mouse_events = (
			('<%sButton-%d>', EditLayer.MOUSE_DOWN),
			('<%sB%d-Motion>', EditLayer.MOUSE_MOVE),
			('<%sButtonRelease-%d>', EditLayer.MOUSE_UP),
			('<%sDouble-Button-%d>', EditLayer.MOUSE_DOUBLE)
		)
		mouse_buttons = (
			(1,EditLayer.MOUSE_LEFT),
			(2,EditLayer.MOUSE_MIDDLE),
			(3,EditLayer.MOUSE_RIGHT)
		)
		mouse_modifiers = (
			('',0),
			('Shift-',EditLayer.MODIFIER_SHIFT),
			('Control-',EditLayer.MODIFIER_CTRL)
		)
		for name,etype in mouse_events:
			for b,btn in mouse_buttons:
				for n,mod in mouse_modifiers:
					self.mapCanvas.bind(name % (n,b), lambda e,b=btn,t=(etype | mod): self.edit_mouse(e,b,t))

		xscrollbar = Scrollbar(right, orient=HORIZONTAL, command=self.mapCanvas.xview)
		xscrollbar.grid(sticky=EW)
		yscrollbar = Scrollbar(right, command=self.mapCanvas.yview)
		yscrollbar.grid(sticky=NS, row=0, column=1)
		def scroll(l,h,bar):
			bar.set(l,h)
			self.update_viewport()
		self.mapCanvas.config(xscrollcommand=lambda l,h,s=xscrollbar: scroll(l,h,s),yscrollcommand=lambda l,h,s=yscrollbar: scroll(l,h,s))
		right.grid_rowconfigure(0,weight=1)
		right.grid_columnconfigure(0,weight=1)

		if 'pane' in self.settings:
			self.panes.sash_place(0, *self.settings['pane'])

		#Statusbar
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=75, anchor=W).pack(side=LEFT, padx=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.edit_status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a Map.')
		statusbar.pack(side=BOTTOM, fill=X)

		self.update_title()

		if 'window' in self.settings:
			loadsize(self, self.settings, 'window', True)

		self.update()
		place_left_children(True)
		self.action_states()

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings['mpqs'] = self.mpqhandler.mpq_paths()
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self, 'PyMAP'))

		if e:
			self.file_settings(err=e)

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			stat_txt = TBL.TBL()
			stat_txt.load_file(self.mpqhandler.get_file(self.profile['stat_txt']))
			imagestbl = TBL.TBL()
			imagestbl.load_file(self.mpqhandler.get_file(self.profile['imagestbl']))
			unitsdat = DAT.UnitsDAT(stat_txt)
			unitsdat.load_file(self.mpqhandler.get_file(self.profile['unitsdat']))
			flingydat = DAT.FlingyDAT(stat_txt)
			flingydat.load_file(self.mpqhandler.get_file(self.profile['flingydat']))
			spritesdat = DAT.SpritesDAT(stat_txt)
			spritesdat.load_file(self.mpqhandler.get_file(self.profile['spritesdat']))
			imagesdat = DAT.ImagesDAT(stat_txt)
			imagesdat.load_file(self.mpqhandler.get_file(self.profile['imagesdat']))
			aibin = AIBIN.AIBIN(bwscript=None, units=unitsdat, upgrades=None, techs=None, stat_txt=stat_txt)
			aibin.load_file(self.mpqhandler.get_file(self.profile['aiscript']))
			iscriptbin = IScriptBIN.IScriptBIN(weaponsdat=None, flingydat=flingydat, imagesdat=imagesdat, spritesdat=spritesdat, soundsdat=None, stat_txt=stat_txt, imagestbl=imagestbl, sfxdatatbl=None)
			iscriptbin.load_file(self.mpqhandler.get_file(self.profile['iscriptbin']))
			palettes = {}
			pal = PAL.Palette()
			for p in ['Units','bfire','gfire','ofire','Terrain']:#,'Icons']:
				try:
					pal.load_file(self.settings.get('%s.pal' % p,os.path.join(BASE_DIR, 'Palettes', '%s%spal' % (p,os.extsep))))
				except:
					if p == 'Units':
						raise
					continue
				palettes[p] = pal.palette
			tunitpcx = PCX.PCX()
			tunitpcx.load_file(self.mpqhandler.get_file(self.profile['tunitpcx']))
		except PyMSError as e:
			err = e
		else:
			self.stat_txt = stat_txt
			self.imagestbl = imagestbl
			self.unitsdat = unitsdat
			self.flingydat = flingydat
			self.spritesdat = spritesdat
			self.imagesdat = imagesdat
			self.aibin = aibin
			self.iscriptbin = iscriptbin
			self.palettes = palettes
			self.tunitpcx = tunitpcx
		self.mpqhandler.close_mpqs()
		return err

	def tick(self, start=False):
		if self.tick_alarm or start:
			if self.chk:
				now = int(time.time() * 1000)
				if self.last_tick == None:
					self.last_tick = now
				dt = now - self.last_tick
				self.last_tick = now
				for layer in self.map_layers:
					layer.tick(dt)
				self.mapCanvas.update_idletasks()
				self.tick_alarm = self.after(FRAME_DELAY,self.tick)
			else:
				self.tick_alarm = None

	def stop_tick(self):
		if self.tick_alarm != None:
			cancel = self.tick_alarm
			self.tick_alarm = None
			self.after_cancel(cancel)

	def file_settings(self, key=None, err=None):
		data = [
			('File Settings',[
				('stat_txt.tbl', 'Contains Unit and AI Script names', ('profile','stat_txt'), 'TBL'),
				('aiscript.bin', "Contains AI ID's and references to names in stat_txt.tbl", ('profile','aiscript'), 'AIBIN'),
			])
		]
		SettingsDialog(self, data, (340,215), err, mpqhandler=self.mpqhandler)

	def add_undo(self, action):
		self.action_manager.add_action(action)
		self.action_states()

	def end_undo_group(self):
		self.action_manager.end_group()
		self.action_states()

	def do_undo(self):
		self.action_manager.undo()
		self.action_states()

	def do_redo(self):
		self.action_manager.redo()
		self.action_states()

	def change_edit_layer(self, *args):
		self.set_editmode(self.edit_layers[self.edit_layer_index.get()])

	def set_editmode(self, layer):
		coords = self.viewport_coords()
		if self.current_editlayer:
			self.current_editlayer.set_mode(EditLayer.INACTIVE, *coords)
		self.current_editlayer = layer
		self.current_editlayer.set_mode(EditLayer.ACTIVE, *coords)
		self.edit_layer_index.set(self.edit_layers.index(self.current_editlayer))

	def edit_update(self, event):
		if not self.chk:
			return
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		map_size = (dims.width*32, dims.height*32)
		x1,x2 = self.mapCanvas.xview()
		y1,y2 = self.mapCanvas.yview()
		x1 *= map_size[0]
		y1 *= map_size[1]
		x2 *= map_size[0]
		y2 *= map_size[1]
		for layer in self.edit_layers:
			layer.update_display(x1,y1,x2,y2, event.x,event.y)

	def edit_mouse(self, event, btn, etype):
		if not self.chk:
			return
		if self.current_editlayer:
			dims = self.chk.get_section(CHKSectionDIM.NAME)
			map_size = (dims.width*32, dims.height*32)
			x1,x2 = self.mapCanvas.xview()
			y1,y2 = self.mapCanvas.yview()
			x1 *= map_size[0]
			y1 *= map_size[1]
			x2 *= map_size[0]
			y2 *= map_size[1]
			if etype == EditLayer.MOUSE_MOVE:
				self.current_editlayer.update_display(x1,y1,x2,y2, event.x,event.y)
			self.current_editlayer.mouse_event(btn, etype, x1,y1, x2,y2, event.x,event.y)

	def minimap_move(self, event):
		if not self.chk:
			return
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		points = min(256 / dims.width, 256 / dims.height)
		size = (dims.width*points,dims.height*points)
		minimap_size = (self.minimap.winfo_width(), self.minimap.winfo_height())
		scale = min(minimap_size[0] / float(size[0]),minimap_size[1] / float(size[1]))
		map_size = (int(round(size[0] * scale)), int(round(size[1] * scale)))
		offset = ((minimap_size[0]-map_size[0])/2.0,(minimap_size[1]-map_size[1])/2.0)
		x = (event.x - offset[0]) / float(map_size[0])
		y = (event.y - offset[1]) / float(map_size[1])
		l,h = self.mapCanvas.xview()
		x -= (h - l) / 2.0
		l,h = self.mapCanvas.yview()
		y -= (h - l) / 2.0
		self.mapCanvas.xview_moveto(x)
		self.mapCanvas.yview_moveto(y)

	def redraw_minimap(self):
		for layer in self.minimap_layers:
			layer.redraw()
		self.resized_minimap()

	def viewport_coords(self):
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		x1,x2 = self.mapCanvas.xview()
		y1,y2 = self.mapCanvas.yview()
		map_size = (dims.width*32, dims.height*32)
		return (map_size[0]*x1,map_size[1]*y1, map_size[0]*x2,map_size[1]*y2)

	def update_viewport(self):
		if self.chk:
			dims = self.chk.get_section(CHKSectionDIM.NAME)
			points = min(256 / dims.width, 256 / dims.height)
			size = (dims.width*points,dims.height*points)
			minimap_size = (self.minimap.winfo_width(), self.minimap.winfo_height())
			scale = min(minimap_size[0] / float(size[0]),minimap_size[1] / float(size[1]))
			map_size = (int(round(size[0] * scale)), int(round(size[1] * scale)))
			offset = ((minimap_size[0]-map_size[0])/2.0,(minimap_size[1]-map_size[1])/2.0)
			x1,x2 = self.mapCanvas.xview()
			y1,y2 = self.mapCanvas.yview()
			self.minimap.coords('viewport', offset[0]+map_size[0]*x1,map_size[1]*y1, offset[1]+map_size[0]*x2,map_size[1]*y2)
			map_size = (dims.width*32, dims.height*32)
			coords = (map_size[0]*x1,map_size[1]*y1, map_size[0]*x2,map_size[1]*y2)
			for layer in self.map_layers:
				layer.update_display(*coords)

	def resized_minimap(self):
		self.minimap.delete(ALL)
		for layer in self.minimap_layers:
			image = layer.get_image((self.minimap.winfo_width(),self.minimap.winfo_height()))
			if image:
				self.minimap.create_image(self.minimap.winfo_width()/2.0, self.minimap.winfo_height()/2.0, image=image)
		self.minimap.create_rectangle(0, 0, 0, 0, outline='#FFFFFF', tags='viewport')
		self.update_viewport()

	def setup_list(self):
		self.list_layer_indices = {}
		for list_layer in self.list_layers:
			self.list_layer_indices[list_layer.setup_group()] = list_layer

	def list_select(self, event=None):
		selected = self.listbox.cur_selection()
		if selected and selected[0] > -1:
			list_index = self.listbox.index(selected[0])
			groupId = list_index.split('.')[0]
			list_layer = self.list_layer_indices.get(groupId)
			if list_layer:
				layer,select = list_layer.get_event(list_index)
				if layer:
					if layer != self.current_editlayer:
						self.set_editmode(layer)
					layer.list_select(select)

	def unsaved(self):
		if self.chk and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.scx'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.scx', filetypes=[('BroodWar Map','*.scx'),('StarCraft Map','*.scm'),('Raw Map','*.chk'),('All Files','*')], parent=None):
		if parent == None:
			parent = self
		path = self.settings.get('lastpath', BASE_DIR)
		parent._pyms__window_blocking = True
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](title=title, defaultextension=ext, filetypes=filetypes, initialdir=path, parent=parent)
		parent._pyms__window_blocking = False
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		map_open = [NORMAL,DISABLED][not self.chk]
		for btn in ['save','saveas','close']:
			self.buttons[btn]['state'] = map_open
		self.edit_layer_dropdown['state'] = map_open
		self.buttons['undo']['state'] = [DISABLED,NORMAL][self.action_manager.can_undo()]
		self.buttons['redo']['state'] = [DISABLED,NORMAL][self.action_manager.can_redo()]
		self.buttons['asc3topyai']['state'] = [DISABLED,NORMAL][not self.chk]

	def update_title(self, file=None):
		title = 'PyMAP %s' % LONG_VERSION
		if file == None and self.file:
			file = os.path.basename(self.file)
		if file:
			title += ' (%s)' % file
		self.title(title)

	def new(self, key=None):
		if not self.unsaved():
			self.chk = CHK()
			self.file = None
			self.status.set('Editing new Map.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.update_title('Unnamed.scx')
			self.action_states()

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.select_file('Open Map')
				if not file:
					return
			scmap = None
			if not file.endswith('.chk'):
				scmap = MpqOpenArchiveForUpdateEx(file)
				if SFInvalidHandle(scmap):
					scmap = None
			chk = CHK()
			chkfile = None
			tileset = None
			try:
				if scmap:
					chkfile = SFileOpenFileEx(scmap, 'staredit\\scenario.chk')
					if not SFInvalidHandle(chkfile):
						data,_ = SFileReadFile(chkfile)
						chk.load_data(data)
						SFileCloseFile(chkfile)
						chkfile = None
					SFileCloseArchive(scmap)
				else:
					chk.load_file(file)
				era = chk.get_section(CHKSectionERA.NAME)
				if era:
					tilesetName = CHKSectionERA.TILESET_FILE(era.tileset)
					tilesetPaths = [
						'MPQ:tileset\\%s.cv5',
						'MPQ:tileset\\%s.vf4',
						'MPQ:tileset\\%s.vx4',
						'MPQ:tileset\\%s.vr4',
						'MPQ:tileset\\%s\\dddata.bin',
						'MPQ:tileset\\%s.wpe'
					]
					tilesetFiles = []
					self.mpqhandler.open_mpqs()
					for pathFormat in tilesetPaths:
						path = pathFormat % tilesetName
						tilesetFile = self.mpqhandler.get_file(path)
						# if isinstance(tilesetFile, BadFile):
						# 	path = pathFormat % (tilesetName + '-nc')
						# 	tilesetFile = self.mpqhandler.get_file(path)
						# 	if isinstance(tilesetFile, BadFile):
						# 		path = pathFormat % (tilesetName[0].upper() + tilesetName[1:])
						# 		tilesetFile = self.mpqhandler.get_file(path)
						if isinstance(tilesetFile, BadFile):
							break
						tilesetFiles.append(tilesetFile)
					if len(tilesetFiles) == len(tilesetPaths):
						tileset = Tilesets.Tileset()
						tileset.load_file(*tilesetFiles)
					self.mpqhandler.close_mpqs()
			except PyMSError as e:
				self.mpqhandler.close_mpqs()
				if not SFInvalidHandle(chkfile):
					SFileCloseFile(chkfile)
				if scmap:
					SFileCloseArchive(scmap)
				ErrorDialog(self, e)
				return
			if not chk or not chk.sections:
				askquestion(parent=self, title='Open', message='"%s" is not a valid map.' % file, type=OK)
				return
			if not tileset:
				askquestion(parent=self, title='Open', message='"%s" has an invalid tileset.' % file, type=OK)
				return
			self.scmap = scmap
			self.chk = chk
			self.tileset = tileset
			self.file = file
			self.edited = False
			dims = self.chk.get_section(CHKSectionDIM.NAME)
			self.mapCanvas.config(scrollregion=(0,0,dims.width*32,dims.height*32))
			self.update_title()
			self.status.set('Load successful!')
			self.editstatus['state'] = DISABLED
			self.action_states()
			self.setup_list()
			self.redraw_minimap()
			self.set_editmode(self.editlayer_terrain)
			self.tick(True)

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.chk.save_file(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError as e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.select_file('Save Map As', False)
		if not file:
			return True
		self.file = file
		self.save()

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.edited = False
			self.chk = None
			self.file = None
			self.edited = False
			self.update_title()
			self.status.set('Load or create a Map.')
			self.editstatus['state'] = DISABLED
			self.action_states()
			self.listbox.delete(ALL)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyMAP.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyMAP', LONG_VERSION, [('staredit.net','CHK file specs.')])

	def exit(self, e=None):
		if not self.unsaved():
			savesize(self, self.settings)
			self.settings['pane'] = self.panes.sash_coord(0)
			savesettings('PyMAP', self.settings)
			self.stop_tick()
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pymap.py','pymap.pyw','pymap.exe']):
		gui = PyMAP()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyMAP [options]', version='PyMAP %s' % LONG_VERSION)
		# p.add_option('-v', '--vf4', metavar='FILE', help='Choose a palette for GRP to BMP conversion [default: %default]', default='')
		# p.add_option('-p', '--palette', metavar='FILE', help='Choose a palette for GRP to BMP conversion [default: %default]', default='Units.pal')
		# p.add_option('-g', '--grptobmps', action='store_true', dest='convert', help="Converting from GRP to BMP's [default]", default=True)
		# p.add_option('-b', '--bmpstogrp', action='store_false', dest='convert', help="Converting from BMP's to GRP")
		# p.add_option('-u', '--uncompressed', action='store_true', help="Used to signify if the GRP is uncompressed (both to and from BMP) [default: Compressed]", default=False)
		# p.add_option('-o', '--onebmp', action='store_true', help='Used to signify that you want to convert a GRP to one BMP file. [default: Multiple]', default=False)
		# p.add_option('-f', '--frames', type='int', help='Used to signify you are using a single BMP with alll frames, and how many frames there are.', default=0)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyMAP(opt.gui)
			gui.startup()

if __name__ == '__main__':
	# import profile
	# profile.run('main()')
	main()
