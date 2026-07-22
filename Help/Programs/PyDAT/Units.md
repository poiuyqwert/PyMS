# Units Tab
The Units tab of [PyDAT](/Help/Programs/PyDAT.md) edits [units.dat](/Help/Files/DAT/units.dat.md), which contains the settings for all the units in the game.
Units have far more settings than any other DAT type, so the tab is split into six sub-tabs. **Copy Sub-Tab to Clipboard** (`Ctrl+Y`, or the entry lists right click menu) copies only the properties of the active sub-tab, which is handy for copying just a units sounds or graphics to another unit.
Unit names are not stored in `units.dat` — they are the first 228 strings in `stat_txt.tbl` (expanded units use `unitnames.tbl`, see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)).

## Basic
The core gameplay statistics of the unit:

- **Vital Statistics**: Hit Points (with a Fraction field for the hidden fractional part), Shields (and whether they are enabled), and Armor with its armor [Upgrade](/Help/Programs/PyDAT/Upgrades.md).
- **Build Cost**: Minerals, Vespene, and build Time (shown in ticks and in seconds on Fastest game speed), plus the BroodWar flag marking BroodWar-only units.
- **Weapons**: The Ground and Air [Weapons](/Help/Programs/PyDAT/Weapons.md) and the Max Hits for each.
- **Supply**: The supply the unit requires and provides (with `+0.5` checkboxes for half supply, like Zerglings), and Zerg/Terran/Protoss checkboxes setting which race the unit belongs to (shared with the Group flags on the [StarEdit](#staredit) sub-tab).
- **Space**: The transport space the unit requires and provides.
- **Score**: The score awarded for building and for destroying the unit.
- **Other**: The Unit Size (Independent, Small, Medium, or Large — used by damage types), Sight range, and Target Acquisition Range.

## Advanced
The units type and ability flags: Building, Addon, Flyer, Hero, Organic, Mechanical, Robotic, Detector, Subunit, Resource Container, Resource Depot, Resource Miner, Spellcaster, Regenerate, Permanently Cloaked, Cloakable, Burrowable, Invincible, Requires Psi, Requires Creep, Two Units in One Egg, Single Entity, and more. Hover over each flag for an explanation of what it does.
The **Other Properties** section has the Infestation unit (the unit this unit becomes when infested by a Queen — only stored for units 106 to 201), Subunit 1 and Subunit 2 (like Terran turrets), and the units requirements index (ReqIndex).

## Sounds
The units voice lines, referencing [Sfxdata](/Help/Programs/PyDAT/Sfxdata.md) entries: the Ready sound (played when the unit finishes building), and the What, Yes, and Annoyed sound ranges. Each range is a First and Last sound ID, and the game picks randomly from the range. Sounds that a unit type does not store (for example buildings have no Annoyed sounds) show as disabled fields.

## Graphics
The units visuals and physical footprint:

- **Sprite Graphics**: The units [Flingy](/Help/Programs/PyDAT/Flingy.md) graphics, its Construction animation [Image](/Help/Programs/PyDAT/Images.md), its [Portrait](/Help/Programs/PyDAT/Portdata.md), its Elevation level (which "height" it moves at), and the Direction it faces when placed.
- **Unit Dimensions**: The Left/Right/Up/Down extents of the units collision box.
- **Addon Position**: For buildings with addons, where the addon attaches (horizontal/vertical offset).
- **Preview**: A live preview of the units graphics. Checkboxes overlay the Dimensions box (green), the StarEdit Placement box (red), and for addons the Addon Placement (yellow) attached to a parent building of your choice.

## StarEdit
How the unit appears in map editors (StarEdit) and what map settings apply to it:

- **Availability Flags**: Where the unit is available in the editor — Non-Neutral, Unit Listing&Palette, Mission Briefing, Player Settings, All Races, Set Doodad State, Non-Location Triggers, Location Triggers, Unit&Hero Settings, and BroodWar Only.
- **Group Flags**: The editor groups the unit belongs to — Men, Building, Factory, Independent, and Neutral.
- **String Properties**: The units Rank/Sublabel string (shown under the unit name), and its Map String — when set, the units name is read from the loaded maps own strings instead of `stat_txt.tbl`.
- **Placement Box (Pixels)**: The width and height of the box used when placing the unit in the editor, with a preview showing the placement box over the units graphics.

## AI Actions
How the games AI controls the unit:

- The [Orders](/Help/Programs/PyDAT/Orders.md) used for Computer Idle, Human Idle, Return to Idle, Attack Unit, and Attack Move.
- The Right-Click Action, which determines how the unit responds to right clicks.
- AI flags: whether the unit ignores strategic suicide missions, and whether it doesn't become a guard.

The **AI Force Values** section shows how the AI calculates the strength of the unit, with each part of the formula (weapon damage, cooldown, range, health, shields, and unit specific adjustments) color coded. Click a part of the formula to jump to the field it comes from.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [units.dat](/Help/Files/DAT/units.dat.md)
- [Editing a Unit](/Help/Tutorials/Editing_a_Unit.md)
