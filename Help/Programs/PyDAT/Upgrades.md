# Upgrades Tab
The Upgrades tab of [PyDAT](/Help/Programs/PyDAT.md) edits [upgrades.dat](/Help/Files/DAT/upgrades.dat.md), which contains the settings for all the upgrades in the game (armor, weapon, and ability upgrades).

## Upgrade Display
The **Icon** is shown in the status panel while the upgrade is researched, and as the armor icon of units using the upgrade (command buttons have their own icons) — pick it by ID, or click the preview or find button to browse all the icons visually. The **Label** is the upgrades name string in `stat_txt.tbl`.

## Base Cost and Factor Cost
The **Base Cost** is the Minerals, Vespene, and research Time of the first level of the upgrade. For multi-level upgrades, the **Factor Cost** is added for each additional level (level 2 costs base + factor, level 3 costs base + 2x factor, and so on). Times are shown in ticks and in seconds on Fastest game speed.

## Misc.
- **Max Repeats**: The number of levels the upgrade can be researched. StarEdit hides upgrades with 0.
- **ReqIndex**: Where the upgrade's requirements start in the upgrade requirement list built into StarCraft.exe. The requirements themselves (such as which buildings are needed) are in that list and cannot be edited in the dat files; this value only picks a position in it. Keep 65535 (0xFFFF).
  - **65535**: As soon as the game checks an upgrade that holds 65535, it looks up every upgrade that has an entry in the built-in list and stores the position of that entry, replacing what the file had. Every upgrade still holding 65535 is then set to 0. So once that has happened, the file's value only survives for upgrades that have no entry in the list.
  - **Other values**: Until the game checks an upgrade holding 65535, and always if none holds 65535, each value is used as it is. 0 means the upgrade is never allowed. Any other number is a position in the built-in list, and the game reads conditions from there until it reaches the end of an entry. The start of the upgrade's own entry gives its normal requirements, and the start of another upgrade's entry gives that upgrade's requirements. A position inside an entry gives the rest of that entry, and may read a unit number meant for one condition as a condition of its own. A position on the end of an entry gives no requirements, so the upgrade is allowed whenever the game's other checks pass. A position past the end of the list reads whatever memory follows it. Nothing checks the value, and PyDAT cannot show the built-in list.
- **Race**: The race StarEdit lists the upgrade under (None hides it in StarEdit). The game ignores it.
- **BroodWar**: StarEdit only shows the upgrade for BroodWar maps. The game ignores it.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units using the upgrade for their armor and the weapons using it for their damage.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [upgrades.dat](/Help/Files/DAT/upgrades.dat.md)
