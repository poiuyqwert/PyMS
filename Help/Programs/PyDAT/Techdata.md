# Techdata Tab
The Techdata tab of [PyDAT](/Help/Programs/PyDAT.md) edits [techdata.dat](/Help/Files/DAT/techdata.dat.md), which contains the settings for all the technologies (researchable abilities) in the game.

## Technology Display
The **Icon** is the command card icon — pick it by ID, or click the preview or find button to browse all the icons visually. The **Label** is the technologys name string in `stat_txt.tbl`.

## Technology Cost
The Minerals, Vespene, and research Time (shown in ticks and in seconds on Fastest game speed), and the Energy cost of using the ability.

## Technology Properties
- **ResearchReq** and **UseReq**: The requirements indexes for researching the technology and for using it.
- **Race**: The race the technology belongs to.
- **Researched**: Unused by the game.
- **BroodWar**: Marks BroodWar-only technologies.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the orders using the technology for their energy cost, and the weapons referencing it in their unused technology field.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [techdata.dat](/Help/Files/DAT/techdata.dat.md)
