# Techdata Tab
The Techdata tab of [PyDAT](/Help/Programs/PyDAT.md) edits [techdata.dat](/Help/Files/DAT/techdata.dat.md), which contains the settings for all the technologies (researchable abilities) in the game.

## Technology Display
The **Icon** is shown in the status panel while the technology is researched (command buttons have their own icons) — pick it by ID, or click the preview or find button to browse all the icons visually. The **Label** is the technologys name string in `stat_txt.tbl`.

## Technology Cost
The Minerals, Vespene, and research Time (shown in ticks and in seconds on Fastest game speed), and the Energy cost of using the ability (some of the games checks only use the low byte, so keep it at 255 or less).

## Technology Properties
- **ResearchReq** and **UseReq**: Where the technology's requirements for researching it and for using it start, in two requirement lists built into StarCraft.exe. The requirements themselves (such as which buildings are needed) are in those lists and cannot be edited in the dat files; each value only picks a position in its list. Keep both at 65535 (0xFFFF). The two fields work the same way, each with its own list:
  - **65535**: As soon as the game checks a technology that holds 65535, it looks up every technology that has an entry in the built-in list and stores the position of that entry, replacing what the file had. Every technology still holding 65535 is then set to 0. So once that has happened, the file's value only survives for technologies that have no entry in the list.
  - **Other values**: Until the game checks a technology holding 65535, and always if none holds 65535, each value is used as it is. 0 means the technology is never allowed. Any other number is a position in the built-in list, and the game reads conditions from there until it reaches the end of an entry. The start of the technology's own entry gives its normal requirements, and the start of another technology's entry gives that technology's requirements. A position inside an entry gives the rest of that entry, and may read a unit number meant for one condition as a condition of its own. A position on the end of an entry gives no requirements, so the technology is allowed whenever the game's other checks pass. A position past the end of the list reads whatever memory follows it. Nothing checks the value, and PyDAT cannot show the built-in list.
- **Race**: The race StarEdit lists the technology under (None hides it in StarEdit). The game ignores it.
- **Researched**: Unused: neither the game nor StarEdit reads it. It looks like a "starts researched" flag (the shipped file has 1 for the technologies that need no research, such as Scanner Sweep and Healing), but changing it does nothing.
- **BroodWar**: StarEdit only shows the technology for BroodWar maps. The game ignores it.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the orders using the technology for their energy cost, and the weapons referencing it in their unused technology field.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [techdata.dat](/Help/Files/DAT/techdata.dat.md)
