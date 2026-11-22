# Techdata Tab
The Techdata tab of [PyDAT](/Help/Programs/PyDAT.md) edits [techdata.dat](/Help/Files/DAT/techdata.dat.md), which contains the settings for all the technologies (researchable abilities) in the game.

## Technology Display
The **Icon** is shown in the status panel while the technology is researched (command buttons have their own icons) — pick it by ID, or click the preview or find button to browse all the icons visually. The **Label** is the technologys name string in `stat_txt.tbl`.

## Technology Cost
The Minerals, Vespene, and research Time (shown in ticks and in seconds on Fastest game speed), and the Energy cost of using the ability (some of the games checks only use the low byte, so keep it at 255 or less).

## Technology Properties
- **ResearchReq** and **UseReq**: Positions in the games built-in requirement lists for researching the technology and for using it. Leave them at 65535 (0xFFFF), which makes the game fill them in; 0 means never allowed.
- **Race**: The race StarEdit lists the technology under (None hides it in StarEdit). The game ignores it.
- **Researched**: Unused by the game and StarEdit. Which technologies a player starts with is set by the map.
- **BroodWar**: StarEdit only shows the technology for BroodWar maps. The game ignores it.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the orders using the technology for their energy cost, and the weapons referencing it in their unused technology field.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [techdata.dat](/Help/Files/DAT/techdata.dat.md)
