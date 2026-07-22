# Command Reference
This page documents every command in the IScript language. The same documentation is shown as tooltips when hovering a command in the [IScript Editor](/Help/Programs/PyICE/Code_Editor.md).
Signatures are shown in the flat command style — the parenthesis style is equally valid (see [Commands](/Help/Programs/PyICE/IScript_Language.md#commands)). The parameter names used in the signatures are descriptive; what matters is each parameter's type, listed in [Parameter Types](#parameter-types). As a general guide: `image`, `sprite`, `flingy`, `sound`, and `weapon` parameters are the IDs of entries in the corresponding `.dat` file, `block` parameters are block labels, `x`/`y` parameters are SByte pixel offsets, and other numeric parameters are Bytes unless noted otherwise.

## Frames and Display

### `playfram`
`playfram frame` — Display Frame `frame`, adjusted for direction. See [Frames and Framesets](/Help/Programs/PyICE/IScript_Language.md#frames-and-framesets).

### `playframtile`
`playframtile frame` — Display Frame `frame` dependant on tileset.

### `engframe`
`engframe frame` — Plays BFrame `frame`, often used in engine glow animations.

### `engset`
`engset frameset` — Plays the Frameset `frameset`, often used in engine glow animations.

### `followmaingraphic`
`followmaingraphic` — Causes the current image overlay to display the same frame as the parent image overlay.

### `warpoverlay`
`warpoverlay frame` — Hypothesised to display Frame `frame` from the current image overlay clipped to the outline of the parent image overlay.

### `setflipstate`
`setflipstate flipstate` — Sets the flip state of the current image overlay to `flipstate`.

### `tmprmgraphicstart`
`tmprmgraphicstart` — Sets the current image overlay state to hidden.

### `tmprmgraphicend`
`tmprmgraphicend` — Sets the current image overlay state to visible.

## Positioning

### `sethorpos`
`sethorpos x` — Set the horizontal offset of the current image overlay to `x`.

### `setvertpos`
`setvertpos y` — Set the vertical position of an image overlay to `y`.

### `setpos`
`setpos x y` — Set the horizontal and vertical position of the current image overlay to `x` and `y` respectively.

## Image Overlays

### `imgol`
`imgol image x y` — Display `image` as an active image overlay at an animation level higher than the current image overlay at offset position (`x`,`y`).

### `imgul`
`imgul image x y` — Display `image` as an active image overlay at an animation level lower than the current image overlay at offset position (`x`,`y`).

### `imgolorig`
`imgolorig image` — Display `image` as an active image overlay at an animation level higher than the current image overlay at the relative origin offset position.

### `imgoluselo`
`imgoluselo image x y` — Displays an active image overlay at an animation level higher than the current image overlay, using a LO* file to determine the offset position.

### `imguluselo`
`imguluselo image x y` — Displays an active image overlay at an animation level lower than the current image overlay, using a LO* file to determine the offset position.

### `imgulnextid`
`imgulnextid x y` — Displays an active image overlay at the shadow animation level at offset position (`x`,`y`). The image overlay that will be displayed is the one that is after the current image overlay in `images.dat`.

### `switchul`
`switchul image` — Only for powerups, this is hypothesised to replace the image overlay that was first created by the current image overlay with `image`.

### `creategasoverlays`
`creategasoverlays overlay` — Creates gas image overlay `overlay` (a GasOverlay ID) at offsets specified by LO* files.

## Sprites

### `sprol`
`sprol sprite x y` — Spawns `sprite` one animation level above the current image overlay at offset position (`x`,`y`).

### `highsprol`
`highsprol sprite x y` — Spawns `sprite` at the highest animation level at offset position (`x`,`y`).

### `lowsprul`
`lowsprul sprite x y` — Spawns `sprite` at the lowest animation level at offset position (`x`,`y`).

### `sprul`
`sprul sprite x y` — Spawns `sprite` one animation level below the current image overlay at offset position (`x`,`y`). The new sprite inherits the direction of the current sprite.

### `sproluselo`
`sproluselo sprite overlay` — Spawns `sprite` one animation level above the current image overlay, using a specified LO* file (OverlayID `overlay`) for the offset position information. The new sprite inherits the direction of the current sprite.

### `spruluselo`
`spruluselo sprite x y` — Spawns `sprite` one animation level below the current image overlay at offset position (`x`,`y`). The new sprite inherits the direction of the current sprite. Requires LO* file for unknown reason.

### `grdsprol`
`grdsprol sprite x y` — Spawns `sprite` one animation level above the current image overlay at offset position (`x`,`y`), but only if the current sprite is over ground-passable terrain.

### `uflunstable`
`uflunstable flingy` — Create `flingy` with restrictions; supposedly crashes in most cases.

## Movement and Turning

### `move`
`move pixels` — Sets the unit to move forward `pixels` pixels at the end of the current tick.

### `turnccwise`
`turnccwise amount` — Turns the flingy counterclockwise by `amount` direction units.

### `turncwise`
`turncwise amount` — Turns the flingy clockwise by `amount` direction units.

### `turn1cwise`
`turn1cwise` — Turns the flingy clockwise by one direction unit.

### `turnrand`
`turnrand amount` — Turns the flingy by `amount` direction units in a random direction, with a heavy bias towards turning clockwise.

### `setspawnframe`
`setspawnframe direction` — In specific situations, performs a natural rotation to the direction `direction`.

### `setfldirect`
`setfldirect direction` — Sets the current direction of the flingy to `direction`.

### `setflspeed`
`setflspeed speed` — Sets the `flingy.dat` speed of the current flingy to Speed `speed`.

## Flow Control

### `wait`
`wait ticks` — Pauses script execution for a `ticks` number of ticks.

### `waitrand`
`waitrand min max` — Pauses script execution for a random number of ticks between `min` and `max`.

### `goto`
`goto block` — Unconditionally jumps to code block `block`.

### `call`
`call block` — Calls the code block `block`.

### `return`
`return` — Returns from call.

### `end`
`end` — Destroys the current active image overlay, also removing the current sprite if the image overlay is the last one in the current sprite.

### `ignorerest`
`ignorerest` — Conceptually, this causes the script to stop until the next animation is called.

### `nobrkcodestart`
`nobrkcodestart` — Holds the processing of player orders until a `nobrkcodeend` is encountered.

### `nobrkcodeend`
`nobrkcodeend` — Allows the processing of player orders after a `nobrkcodestart` instruction.

### `randcondjmp`
`randcondjmp chance block` — Randomly jump to `block` with a chance of `chance` out of 255.

### `pwrupcondjmp`
`pwrupcondjmp block` — Jumps to code block `block` if the current unit is a powerup and it is currently picked up.

### `trgtrangecondjmp`
`trgtrangecondjmp distance block` — Jumps to code block `block` depending on the distance to the target compared to Short `distance`.

### `trgtarccondjmp`
`trgtarccondjmp angle1 angle2 block` — Jumps to code block `block` depending on the current angle of the target being between Shorts `angle1` and `angle2`.

### `curdirectcondjmp`
`curdirectcondjmp angle1 angle2 block` — Only for units. Jump to code block `block` if the current sprite is facing a particular direction between Shorts `angle1` and `angle2`.

### `liftoffcondjmp`
`liftoffcondjmp block` — Jumps to code block `block` when the current unit is a building that is lifted off.

## Sounds

### `playsnd`
`playsnd sound` — Plays `sound`.

### `playsndrand`
`playsndrand sounds sound1 sound2` — Plays a random sound from a list containing a `sounds` number of sound IDs (`sounds` is followed by that many SoundID parameters).

### `playsndbtwn`
`playsndbtwn firstsound lastsound` — Plays a random sound between `firstsound` and `lastsound` inclusively.

## Attacks and Spells

### `attack`
`attack` — Attack with either the ground or air weapon depending on target.

### `attackwith`
`attackwith weapon` — Attack with either the ground or air weapon depending on `weapon` (1 for ground attack, or not 1 for air attack).

### `attackmelee`
`attackmelee sounds sound1 sound2` — Applies damage to target without creating a flingy and plays a random sound from a list containing a `sounds` number of sound IDs (`sounds` is followed by that many SoundID parameters).

### `useweapon`
`useweapon weapon` — Makes the unit use `weapon` (a `weapons.dat` ID) on its target.

### `domissiledmg`
`domissiledmg` — Causes the damage of a weapon flingy to be applied according to its `weapons.dat` entry.

### `dogrddamage`
`dogrddamage` — Applies damage like `domissiledmg` when on ground-unit-passable terrain.

### `attkshiftproj`
`attkshiftproj distance` — Creates the weapon flingy at a distance of `distance` in front of the unit.

### `castspell`
`castspell` — Identifies when a spell should be cast in a spellcasting animation. The spell is determined by the unit's current order.

### `gotorepeatattk`
`gotorepeatattk` — Signals to StarCraft that after this point, when the unit's cooldown time is over, the repeat attack animation can be called.

### `sigorder`
`sigorder signal` — Allows the current unit's order to proceed if it has paused for an animation to be completed.

### `orderdone`
`orderdone signal` — Most likely used with orders that continually repeat, like the Medic's healing, to clear the `sigorder` flag to stop the order.

## Unknown Commands

### `__0c`
`__0c` — Unknown.

### `__2d`
`__2d` — Hypothesised to hide the current image overlay until the next animation.

### `__3e`
`__3e` — Unknown.

### `__43`
`__43` — Unknown.

## Header Commands
These commands can only be used inside a script header, between `.headerstart` and `.headerend` (see [Script Headers](/Help/Programs/PyICE/IScript_Language.md#script-headers)):

- `IsId id` — Set the ID of this script's header. Each header has a unique ID, which is referenced by `images.dat`.
- `Type type` — Set the type of this script's header, which determines the number of animations it contains.
- The 28 animation entry point commands (`Init block`, `Death block`, `GndAttkInit block`, etc.), each naming the block where that animation starts, or `[NONE]`. The full list is documented in [Animations](/Help/Files/iscript.bin.md#animations).

## Parameter Types
- **Frame**: The index of a frame in a GRP, in decimal or hexadecimal, in the range 0 to 65535. Framesets are increments of 17, so 17 or `0x11`, 34 or `0x22`, 51 or `0x33`, etc.
- **Frameset**: The index of a frame set in a GRP, in the range 0 to 255.
- **BFrame**: The index of a frame in a GRP, in the range 0 to 255.
- **Byte**: A number in the range 0 to 255.
- **SByte**: A number in the range -128 to 127.
- **Short**: A number in the range 0 to 65535.
- **Label**: A label name of a block in the script.
- **ImageID**: The ID of an [images.dat](/Help/Files/DAT/images.dat.md) entry.
- **SpriteID**: The ID of a [sprites.dat](/Help/Files/DAT/sprites.dat.md) entry.
- **FlingyID**: The ID of a [flingy.dat](/Help/Files/DAT/flingy.dat.md) entry.
- **SoundID**: The ID of a [sfxdata.dat](/Help/Files/DAT/sfxdata.dat.md) entry.
- **Sounds**: How many sounds to pick from (the number of SoundID parameters that follow).
- **WeaponID**: The ID of a [weapons.dat](/Help/Files/DAT/weapons.dat.md) entry.
- **Weapon**: Either 1 for ground attack, or not 1 for air attack.
- **OverlayID**: The ID of an overlay.
- **GasOverlay**: The ID of a gas overlay.
- **FlipState**: The flip state to set on the current image overlay.
- **SignalID**: A signal order ID.
- **Speed**: The speed to set on the `flingy.dat` entry of the current flingy.

## See Also
- [IScript Language](/Help/Programs/PyICE/IScript_Language.md)
- [IScript Editor](/Help/Programs/PyICE/Code_Editor.md)
