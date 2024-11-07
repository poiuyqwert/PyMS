
from .CodeTypes import *

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition

Playfram = CodeCommandDefinition('playfram', "Display Frame(1), adjusted for direction.", 0, (FrameCodeType(),))
Playframtile = CodeCommandDefinition('playframtile', "Display Frame(1) dependant on tileset.", 1, (FrameCodeType(),))
Sethorpos = CodeCommandDefinition('sethorpos', "Set the horizontal offset of the current image overlay to Byte(1).", 2, (SByteCodeType(),))
Setvertpos = CodeCommandDefinition('setvertpos', "Set the vertical position of an image overlay to Byte(1).", 3, (SByteCodeType(),))
Setpos = CodeCommandDefinition('setpos', "Set the horizontal and vertical position of the current image overlay to Byte(1) and Byte(2) respectively.", 4, (SByteCodeType(), SByteCodeType(),))
Wait = CodeCommandDefinition('wait', "Pauses script execution for a Byte(1) number of ticks.", 5, (ByteCodeType(),))
Waitrand = CodeCommandDefinition('waitrand', "Pauses script execution for a random number of ticks between Byte(1) and Byte(2).", 6, (ByteCodeType(), ByteCodeType(),))
Goto = CodeCommandDefinition('goto', "Unconditionally jumps to code block Label(1).", 7, (LabelCodeType(),), ends_flow=True)
Imgol = CodeCommandDefinition('imgol', "Display ImageID(1) as an active image overlay at an animation level higher than the current image overlay at offset position (Byte(1),Byte(2)).", 8, (ImageIDCodeType(), SByteCodeType(), SByteCodeType(),))
Imgul = CodeCommandDefinition('imgul', "Display ImageID(1) as an active image overlay at an animation level lower than the current image overlay at offset position (Byte(1),Byte(2)).", 9, (ImageIDCodeType(), SByteCodeType(), SByteCodeType(),))
Imgolorig = CodeCommandDefinition('imgolorig', "Display ImageID(1) as an active image overlay at an animation level higher than the current image overlay at the relative origin offset position.", 10, (ImageIDCodeType(),))
Switchul = CodeCommandDefinition('switchul', "Only for powerups, this is hypothesised to replace the image overlay that was first created by the current image overlay.", 11, (ImageIDCodeType(),))
Unknown__0C = CodeCommandDefinition('__0c', "Unknown.", 12)
Imgoluselo = CodeCommandDefinition('imgoluselo', "Displays an active image overlay at an animation level higher than the current image overlay, using a LO* file to determine the offset position.", 13, (ImageIDCodeType(), SByteCodeType(), SByteCodeType(),))
Imguluselo = CodeCommandDefinition('imguluselo', "Displays an active image overlay at an animation level lower than the current image overlay, using a LO* file to determine the offset position.", 14, (ImageIDCodeType(), SByteCodeType(), SByteCodeType(),))
Sprol = CodeCommandDefinition('sprol', "Spawns SpriteID(1) one animation level above the current image overlay at offset position (Byte(1),Byte(2)).", 15, (SpriteIDCodeType(), SByteCodeType(), SByteCodeType(),))
Highsprol = CodeCommandDefinition('highsprol', "Spawns SpriteID(1) at the highest animation level at offset position (Byte(1),Byte(2)).", 16, (SpriteIDCodeType(), SByteCodeType(), SByteCodeType(),))
Lowsprul = CodeCommandDefinition('lowsprul', "spawns SpriteID(1) at the lowest animation level at offset position (Byte(1),Byte(2)).", 17, (SpriteIDCodeType(), SByteCodeType(), SByteCodeType(),))
Uflunstable = CodeCommandDefinition('uflunstable', "Create FlingyID(1) with restrictions; supposedly crashes in most cases.", 18, (FlingyIDCodeType(),))
Spruluselo = CodeCommandDefinition('spruluselo', "Spawns SpriteID(1) one animation level below the current image overlay at offset position (Byte(1),Byte(2)). The new sprite inherits the direction of the current sprite. Requires LO* file for unknown reason.", 19, (SpriteIDCodeType(), SByteCodeType(), SByteCodeType(),))
Sprul = CodeCommandDefinition('sprul', "Spawns SpriteID(1) one animation level below the current image overlay at offset position (Byte(1),Byte(2)). The new sprite inherits the direction of the current sprite.", 20, (SpriteIDCodeType(), SByteCodeType(), SByteCodeType(),))
Sproluselo = CodeCommandDefinition('sproluselo', "Spawns SpriteID(1) one animation level above the current image overlay, using a specified LO* file for the offset position information. The new sprite inherits the direction of the current sprite.", 21, (SpriteIDCodeType(), OverlayIDCodeType(),))
End = CodeCommandDefinition('end', "Destroys the current active image overlay, also removing the current sprite if the image overlay is the last in one in the current sprite.", 22, ends_flow=True)
Setflipstate = CodeCommandDefinition('setflipstate', "Sets the flip state of the current image overlay to FlipState(1).", 23, (FlipStateCodeType(),))
Playsnd = CodeCommandDefinition('playsnd', "Plays SoundID(1).", 24, (SoundIDCodeType(),))
Playsndrand = CodeCommandDefinition('playsndrand', "Plays a random sound from a list containing Sounds(1) number of SoundID(1)'s.", 25, (SoundsCodeType(), SoundIDCodeType(),))
Playsndbtwn = CodeCommandDefinition('playsndbtwn', "Plays a random sound between SoundID(1) and SoundID(2) inclusively.", 26, (SoundIDCodeType(), SoundIDCodeType(),))
Domissiledmg = CodeCommandDefinition('domissiledmg', "Causes the damage of a weapon flingy to be applied according to its weapons.dat entry.", 27)
Attackmelee = CodeCommandDefinition('attackmelee', "Applies damage to target without creating a flingy and plays a random sound from a list containing Sounds(1) number of SoundID(1)'s..", 28, (SoundsCodeType(), SoundIDCodeType(),))
Followmaingraphic = CodeCommandDefinition('followmaingraphic', "Causes the current image overlay to display the same frame as the parent image overlay.", 29)
Randcondjmp = CodeCommandDefinition('randcondjmp', "Randomly jump to Label(1) with a chance of Byte(1) out of 255.", 30, (ByteCodeType(), LabelCodeType(),))
Turnccwise = CodeCommandDefinition('turnccwise', "Turns the flingy counterclockwise by Byte(1) direction units.", 31, (ByteCodeType(),))
Turncwise = CodeCommandDefinition('turncwise', "Turns the flingy clockwise by Byte(1) direction units.", 32, (ByteCodeType(),))
Turn1Cwise = CodeCommandDefinition('turn1cwise', "Turns the flingy clockwise by one direction unit.", 33)
Turnrand = CodeCommandDefinition('turnrand', "Turns the flingy by Byte(1) direction units in a random direction, with a heavy bias towards turning clockwise.", 34, (ByteCodeType(),))
Setspawnframe = CodeCommandDefinition('setspawnframe', "in specific situations, performs a natural rotation to the direction Byte(1).", 35, (ByteCodeType(),))
Sigorder = CodeCommandDefinition('sigorder', "Allows the current unit's order to proceed if it has paused for an animation to be completed.", 36, (SignalIDCodeType(),))
Attackwith = CodeCommandDefinition('attackwith', "Attack with either the ground or air weapon depending on Weapon(1).", 37, (WeaponCodeType(),))
Attack = CodeCommandDefinition('attack', "Attack with either the ground or air weapon depending on target.", 38)
Castspell = CodeCommandDefinition('castspell', "Identifies when a spell should be cast in a spellcasting animation. The spell is determined by the unit's current order.", 39)
Useweapon = CodeCommandDefinition('useweapon', "Makes the unit use WeaponID(1) on its target.", 40, (WeaponIDCodeType(),))
Move = CodeCommandDefinition('move', "Sets the unit to move forward Byte(1) pixels at the end of the current tick.", 41, (ByteCodeType(),))
Gotorepeatattk = CodeCommandDefinition('gotorepeatattk', "Signals to StarCraft that after this point, when the unit's cooldown time is over, the repeat attack animation can be called.", 42)
Engframe = CodeCommandDefinition('engframe', "Plays Frame(1), often used in engine glow animations.", 43, (BFrameCodeType(),))
Engset = CodeCommandDefinition('engset', "Plays the frame set Frameset(1), often used in engine glow animations.", 44, (FramesetCodeType(),))
Unknown__2D = CodeCommandDefinition('__2d', "Hypothesised to hide the current image overlay until the next animation.", 45)
Nobrkcodestart = CodeCommandDefinition('nobrkcodestart', "Holds the processing of player orders until a nobrkcodeend is encountered.", 46)
Nobrkcodeend = CodeCommandDefinition('nobrkcodeend', "Allows the processing of player orders after a nobrkcodestart instruction.", 47)
Ignorerest = CodeCommandDefinition('ignorerest', "Conceptually, this causes the script to stop until the next animation is called.", 48)
Attkshiftproj = CodeCommandDefinition('attkshiftproj', "Creates the weapon flingy at a distance of Byte(1) in front of the unit.", 49, (ByteCodeType(),))
Tmprmgraphicstart = CodeCommandDefinition('tmprmgraphicstart', "Sets the current image overlay state to hidden.", 50)
Tmprmgraphicend = CodeCommandDefinition('tmprmgraphicend', "Sets the current image overlay state to visible.", 51)
Setfldirect = CodeCommandDefinition('setfldirect', "Sets the current direction of the flingy to Byte(1).", 52, (ByteCodeType(),))
Call = CodeCommandDefinition('call', "Calls the code block Label(1).", 53, (LabelCodeType(),))
Return = CodeCommandDefinition('return', "Returns from call.", 54, ends_flow=True)
Setflspeed = CodeCommandDefinition('setflspeed', "Sets the flingy.dat speed of the current flingy to Short(1).", 55, (SpeedCodeType(),))
Creategasoverlays = CodeCommandDefinition('creategasoverlays', "Creates gas image overlay GasOverlay(1) at offsets specified by LO* files.", 56, (GasOverlayCodeType(),))
Pwrupcondjmp = CodeCommandDefinition('pwrupcondjmp', "Jumps to code block Label(1) if the current unit is a powerup and it is currently picked up.", 57, (LabelCodeType(),))
Trgtrangecondjmp = CodeCommandDefinition('trgtrangecondjmp', "Jumps to code block Label(1) depending on the distance to the target.", 58, (ShortCodeType(), LabelCodeType(),))
Trgtarccondjmp = CodeCommandDefinition('trgtarccondjmp', "Jumps to code block Label(1) depending on the current angle of the target.", 59, (ShortCodeType(), ShortCodeType(), LabelCodeType(),))
Curdirectcondjmp = CodeCommandDefinition('curdirectcondjmp', "Only for units. Jump to code block Label(1) if the current sprite is facing a particular direction.", 60, (ShortCodeType(), ShortCodeType(), LabelCodeType(),))
Imgulnextid = CodeCommandDefinition('imgulnextid', "Displays an active image overlay at the shadow animation level at a offset position (Byte(1),Byte(2)). The image overlay that will be displayed is the one that is after the current image overlay in images.dat.", 61, (SByteCodeType(), SByteCodeType(),))
Unknown__3E = CodeCommandDefinition('__3e', "Unknown.", 62)
Liftoffcondjmp = CodeCommandDefinition('liftoffcondjmp', "Jumps to code block Label(1) when the current unit is a building that is lifted off.", 63, (LabelCodeType(),))
Warpoverlay = CodeCommandDefinition('warpoverlay', "Hypothesised to display Frame(1) from the current image overlay clipped to the outline of the parent image overlay.", 64, (FrameCodeType(),))
Orderdone = CodeCommandDefinition('orderdone', "Most likely used with orders that continually repeat, like the Medic's healing and the Valkyrie's afterburners (which no longer exist), to clear the sigorder flag to stop the order.", 65, (SignalIDCodeType(),))
Grdsprol = CodeCommandDefinition('grdsprol', "Spawns SpriteID(1) one animation level above the current image overlay at offset position (Byte(1),Byte(2)), but only if the current sprite is over ground-passable terrain.", 66, (SpriteIDCodeType(), SByteCodeType(), SByteCodeType(),))
Unknown__43 = CodeCommandDefinition('__43', "Unknown.", 67)
Dogrddamage = CodeCommandDefinition('dogrddamage', 'Applies damage like domissiledmg when on ground-unit-passable terrain.', 68)

all_basic_commands: list[CodeCommandDefinition] = [
	Playfram,
	Playframtile,
	Sethorpos,
	Setvertpos,
	Setpos,
	Wait,
	Waitrand,
	Goto,
	Imgol,
	Imgul,
	Imgolorig,
	Switchul,
	Unknown__0C,
	Imgoluselo,
	Imguluselo,
	Sprol,
	Highsprol,
	Lowsprul,
	Uflunstable,
	Spruluselo,
	Sprul,
	Sproluselo,
	End,
	Setflipstate,
	Playsnd,
	Playsndrand,
	Playsndbtwn,
	Domissiledmg,
	Attackmelee,
	Followmaingraphic,
	Randcondjmp,
	Turnccwise,
	Turncwise,
	Turn1Cwise,
	Turnrand,
	Setspawnframe,
	Sigorder,
	Attackwith,
	Attack,
	Castspell,
	Useweapon,
	Move,
	Gotorepeatattk,
	Engframe,
	Engset,
	Unknown__2D,
	Nobrkcodestart,
	Nobrkcodeend,
	Ignorerest,
	Attkshiftproj,
	Tmprmgraphicstart,
	Tmprmgraphicend,
	Setfldirect,
	Call,
	Return,
	Setflspeed,
	Creategasoverlays,
	Pwrupcondjmp,
	Trgtrangecondjmp,
	Trgtarccondjmp,
	Curdirectcondjmp,
	Imgulnextid,
	Unknown__3E,
	Liftoffcondjmp,
	Warpoverlay,
	Orderdone,
	Grdsprol,
	Unknown__43,
	Dogrddamage,
]

IsId = CodeCommandDefinition('IsId', 'Set the ID of this scripts header', None, (HeaderIDCodeType(),))
Type = CodeCommandDefinition('Type', 'Set the Type of this scripts header', None, (HeaderTypeCodeType(),))
Init = CodeCommandDefinition('Init', 'Initial animation', None, (HeaderLabelCodeType(),))
Death = CodeCommandDefinition('Death', 'Death animation', None, (HeaderLabelCodeType(),))
Gndattkinit = CodeCommandDefinition('GndAttkInit', 'Initial ground attack animation', None, (HeaderLabelCodeType(),))
Airattkinit = CodeCommandDefinition('AirAttkInit', 'Initial air attack animation', None, (HeaderLabelCodeType(),))
Unused1 = CodeCommandDefinition('Unused1', 'Unknown/unused animation', None, (HeaderLabelCodeType(),))
Gndattkrpt = CodeCommandDefinition('GndAttkRpt', 'Repeated ground attack animation', None, (HeaderLabelCodeType(),))
Airattkrpt = CodeCommandDefinition('AirAttkRpt', 'Repeated air attack animation', None, (HeaderLabelCodeType(),))
Castspell = CodeCommandDefinition('CastSpell', 'Spell casting animation', None, (HeaderLabelCodeType(),))
Gndattktoidle = CodeCommandDefinition('GndAttkToIdle', 'Animation for returning to an idle state after a ground attack', None, (HeaderLabelCodeType(),))
Airattktoidle = CodeCommandDefinition('AirAttkToIdle', 'Animation for returning to an idle state after an air attack', None, (HeaderLabelCodeType(),))
Unused2 = CodeCommandDefinition('Unused2', 'Unknown/unused animation', None, (HeaderLabelCodeType(),))
Walking = CodeCommandDefinition('Walking', 'Walking/moving animation', None, (HeaderLabelCodeType(),))
Walkingtoidle = CodeCommandDefinition('WalkingToIdle', 'Animation for returning to an idle state after walking/moving', None, (HeaderLabelCodeType(),))
Specialstate1 = CodeCommandDefinition('SpecialState1', 'Some sort of category of special animations, in some cases an in-transit animation, sometimes used for special orders, sometimes having to do with the animation when something finishes morphing, or the first stage of a construction animation', None, (HeaderLabelCodeType(),))
Specialstate2 = CodeCommandDefinition('SpecialState2', 'Some sort of category of special animations, in some cases a burrowed animation, sometimes used for special orders, sometimes having to do with the animation when canceling a morph, or the second stage of a construction animation', None, (HeaderLabelCodeType(),))
Almostbuilt = CodeCommandDefinition('AlmostBuilt', 'An animation for one part of the building process', None, (HeaderLabelCodeType(),))
Built = CodeCommandDefinition('Built', 'Final animation before finishing being built', None, (HeaderLabelCodeType(),))
Landing = CodeCommandDefinition('Landing', 'Landing animation', None, (HeaderLabelCodeType(),))
Liftoff = CodeCommandDefinition('LiftOff', 'Lifting off animation', None, (HeaderLabelCodeType(),))
Isworking = CodeCommandDefinition('IsWorking', 'Animation for when researching an upgrade/technology or training/building units and some other animations for some sort of work being done', None, (HeaderLabelCodeType(),))
Workingtoidle = CodeCommandDefinition('WorkingToIdle', 'Animation for returning to an idle state after IsWorking', None, (HeaderLabelCodeType(),))
Warpin = CodeCommandDefinition('WarpIn', 'Warping in animation', None, (HeaderLabelCodeType(),))
Unused3 = CodeCommandDefinition('Unused3', 'Unknown/unused animation', None, (HeaderLabelCodeType(),))
Stareditinit = CodeCommandDefinition('StarEditInit', 'Previously called InitTurret, this is actually an alternate initial animation for StarEdit a.k.a. the Campaign Editor', None, (HeaderLabelCodeType(),))
Disable = CodeCommandDefinition('Disable', 'Animation for becoming disabled, either through the "Set Doodad State" trigger action or by not being in the psi field of any pylons', None, (HeaderLabelCodeType(),))
Burrow = CodeCommandDefinition('Burrow', 'Burrowing animation', None, (HeaderLabelCodeType(),))
Unburrow = CodeCommandDefinition('UnBurrow', 'Unburrowing animation', None, (HeaderLabelCodeType(),))
Enable = CodeCommandDefinition('Enable', 'Animation for becoming enabled, either through the "Set Doodad State" trigger action or by being in the psi field of a pylon', None, (HeaderLabelCodeType(),))

all_header_commands = [
	IsId,
	Type,
	Init,
	Death,
	Gndattkinit,
	Airattkinit,
	Unused1,
	Gndattkrpt,
	Airattkrpt,
	Castspell,
	Gndattktoidle,
	Airattktoidle,
	Unused2,
	Walking,
	Walkingtoidle,
	Specialstate1,
	Specialstate2,
	Almostbuilt,
	Built,
	Landing,
	Liftoff,
	Isworking,
	Workingtoidle,
	Warpin,
	Unused3,
	Stareditinit,
	Disable,
	Burrow,
	Unburrow,
	Enable,
]
