# Upgrades Tab
The Upgrades tab of [PyDAT](/Help/Programs/PyDAT.md) edits [upgrades.dat](/Help/Files/DAT/upgrades.dat.md), which contains the settings for all the upgrades in the game (armor, weapon, and ability upgrades).

## Upgrade Display
The **Icon** is shown in the status panel while the upgrade is researched, and as the armor icon of units using the upgrade (command buttons have their own icons) — pick it by ID, or click the preview or find button to browse all the icons visually. The **Label** is the upgrades name string in `stat_txt.tbl`.

## Base Cost and Factor Cost
The **Base Cost** is the Minerals, Vespene, and research Time of the first level of the upgrade. For multi-level upgrades, the **Factor Cost** is added for each additional level (level 2 costs base + factor, level 3 costs base + 2x factor, and so on). Times are shown in ticks and in seconds on Fastest game speed.

## Misc.
- **Max Repeats**: The number of levels the upgrade can be researched. StarEdit hides upgrades with 0.
- **ReqIndex**: Position in the games built-in upgrade requirement list. Leave it at 65535 (0xFFFF), which makes the game fill it in; 0 means never allowed.
- **Race**: The race StarEdit lists the upgrade under (None hides it in StarEdit). The game ignores it.
- **BroodWar**: StarEdit only shows the upgrade for BroodWar maps. The game ignores it.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units using the upgrade for their armor and the weapons using it for their damage.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [upgrades.dat](/Help/Files/DAT/upgrades.dat.md)
