# UI BIN
UI `.bin` files contain the UI used for most of the games menus and dialogs (the "glue screens"). Each file stores a single Dialog widget and its child widgets — buttons, labels, images, sliders, and so on — with their positions, sizes, strings, flags, and attached [SMK](/Help/Files/SMK.md) animations.

Edited by [PyBIN](/Help/Programs/PyBIN.md)

## Dialog Files
The dialog files are found in the `rez` folder of the games [MPQs](/Help/Files/MPQ.md). The file doesn't record which screen it belongs to; the game loads each screens dialog by name:

- `glumain.bin`: Main Menu
- `glucmpgn.bin`: Campaign Selection
- `gluexpcmpgn.bin`: Campaign Selection (BroodWar)
- `glulogin.bin`: Username Selection
- `gluconn.bin`: Multiplayer Connection Selection
- `gluchat.bin`: Game Lobby
- `glujoin.bin`: Games List
- `glucreat.bin`: Create Game (Multiplayer)
- `glucustm.bin`: Create Game (Singleplayer)
- `gluload.bin`: Save Games
- `glurdyt.bin`: Terran Mission Briefing
- `glurdyz.bin`: Zerg Mission Briefing
- `glurdyp.bin`: Protoss Mission Briefing
- `gluscore.bin`: Score Screen (all races, victory and defeat)
- `glumodem.bin`: Modem Connection

Note that not every `.bin` file in the games MPQs is a dialog in this format (for example `aiscript.bin` and `iscript.bin` are completely different formats).

## Legacy and Remastered Files
StarCraft: Remastered extended the format, and [PyBIN](/Help/Programs/PyBIN.md) detects which variant a file is automatically when opening it:

- Legacy files store strings in the Windows ANSI code page; Remastered files store UTF-8, so they can contain characters legacy files can't.
- Remastered widgets have an extra (currently unidentified) value.
- Remastered adds the HTML widget type.

A file only needs to be saved in the Remastered format if it uses Remastered-only features — otherwise it can be saved as a legacy file, which Remastered also understands.
