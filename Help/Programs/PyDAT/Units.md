# Units Tab
The Units tab of [PyDAT](/Help/Programs/PyDAT.md) edits [units.dat](/Help/Files/DAT/units.dat.md), which contains the settings for all the units in the game.
Units have far more settings than any other DAT type, so the tab is split into six sub-tabs. **Copy Sub-Tab to Clipboard** (`Ctrl+Y`, in the **Entry** menu or the entry lists right click menu) copies only the properties of the active sub-tab, which is handy for copying just a units sounds or graphics to another unit.
Unit names are not stored in `units.dat` — they are the first 228 strings in `stat_txt.tbl` (expanded units use `unitnames.tbl`, see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)).

## Basic
The core gameplay statistics of the unit:

- **Vital Statistics**: Hit Points (with a Fraction field for the hidden fractional part), Shields (and whether they are enabled), and Armor with its armor [Upgrade](/Help/Programs/PyDAT/Upgrades.md).
- **Build Cost**: Minerals, Vespene, and build Time (shown in game frames and in seconds on Fastest game speed), plus the BroodWar flag, which only StarEdit reads (the game uses the BroodWar Only flag on the [StarEdit](#staredit) sub-tab).
- **Weapons**: The Ground and Air [Weapons](/Help/Programs/PyDAT/Weapons.md) (130 = none) and the Max Hits for each (only shown by StarEdit; the game never reads them).
- **Supply**: The supply the unit requires and provides (the game counts in halves; the `+0.5` checkboxes add a half, like Zerglings), and Zerg/Terran/Protoss checkboxes setting which race the unit belongs to, and so which supply pool it uses (shared with the Group flags on the [StarEdit](#staredit) sub-tab).
- **Space**: The transport space the unit requires and provides.
- **Score**: The score awarded for building and for destroying the unit.
- **Other**: The Unit Size (Independent, Small, Medium, or Large — with the weapon's damage type it sets how much damage the unit takes; Independent takes 0%), Sight range (in tiles, 0 to 11), and Target Acquisition Range (in tiles, the range at which the unit looks for targets by itself).

## Advanced
The units type and ability flags: Building, Addon, Flyer, Hero, Organic, Mechanical, Robotic, Detector, Subunit, Resource Container, Resource Depot, Resource Miner, Has Energy, Regenerate, Permanently Cloaked, Cloakable, Burrowable, Invincible, Requires Psi, Requires Creep, Two Units in One Egg, Powerup, Can Move, Can Turn, and more. Hover over each flag for an explanation of what it does. Several flags were known by older names that do not match what the game does with them (for example Click Any Image was "Animated Idle", Larger Creep was "Produces Units", Can Move and Can Turn were "Battle Reactions" and "Full Auto-Attack").
The **Other Properties** section has the Infestation unit (the unit this building becomes when infested by a Queen — only stored for units 106 to 201, and only the Command Center can be infested), Subunit 1 (a turret, like the Siege Tank's; only used for units 0 to 105) and Subunit 2 (never read by the game), the units requirements index (ReqIndex, leave it at 65535), and the eight movement flag bits (the game only tests the whole value 0xC1, which Spider Mines ignore).

## Sounds
The units voice lines, referencing [Sfxdata](/Help/Programs/PyDAT/Sfxdata.md) entries: the Ready sound (played when the unit is completed), and the What, Yes, and Annoyed sound ranges. Each range is a First and Last sound ID. The game picks What and Yes sounds randomly from the range, and plays the Annoyed sounds in order when you keep clicking the unit. Sounds that a unit type does not store (for example buildings have no Annoyed sounds) show as disabled fields.

## Graphics
The units visuals and physical footprint:

- **Sprite Graphics**: The units [Flingy](/Help/Programs/PyDAT/Flingy.md) graphics, its Construction animation [Image](/Help/Programs/PyDAT/Images.md), its [Portrait](/Help/Programs/PyDAT/Portdata.md), its Elevation level (the order sprites are drawn in, and below 12 it moves like a ground unit, from 12 like an air unit), and the Direction it faces when completed.
- **Unit Dimensions**: The Left/Right/Up/Down extents of the units collision box, also used for weapon ranges.
- **Addon Position**: For add-ons, where the add-on attaches: the offset from the parent building's placement box to the add-on's.
- **Preview**: A live preview of the units graphics. Checkboxes overlay the Dimensions box (green), the StarEdit Placement box (red), and for addons the Addon Placement (yellow) attached to a parent building of your choice.

## StarEdit
How the unit appears in map editors (StarEdit) and what map settings apply to it:

- **Availability Flags**: Where the unit is available in the editor — Non-Neutral, Unit Listing&Palette, Mission Briefing, Player Settings, All Races, Set Doodad State, Non-Location Triggers, Location Triggers, Unit&Hero Settings, and BroodWar Only.
- **Group Flags**: The editor groups the unit belongs to — Men, Building, Factory, Independent, and Neutral.
- **String Properties**: The units Rank/Sublabel string (shown under the name of Terran units; StarEdit does not use it), and its Map String — when set, the units name is read from the loaded maps own strings instead of `stat_txt.tbl`.
- **Placement Box (Pixels)**: The width and height of the box used when placing the unit, in the game and in the editor (for buildings, divided by 32 to give the tiles they take up), with a preview showing the placement box over the units graphics.

## AI Actions
The orders the unit uses, and how the computer AI treats it:

- The [Orders](/Help/Programs/PyDAT/Orders.md) used for Computer Idle, Human Idle (the first order of a completed unit, by owner), Return to Idle, Attack Unit, and Attack Location.
- The Right-Click Action, which determines how the unit responds to right clicks (values above 6 crash the game).
- AI flags: whether the AI leaves the unit out of its attack groups, and whether the unit joins the AI's town instead of becoming a guard.

The **AI Force Values** section shows how the AI calculates the strength of the unit, with each part of the formula (weapon damage, cooldown, range, health, shields, and unit specific adjustments) color coded. Click a part of the formula to jump to the field it comes from.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [units.dat](/Help/Files/DAT/units.dat.md)
- [Editing a Unit](/Help/Tutorials/Editing_a_Unit.md)
