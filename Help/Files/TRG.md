# TRG
`.trg` files contain triggers used to control what happens in UMS (Use Map Settings) [maps](/Help/Files/Maps.md) as well as to initialize the other [game modes](/Help/Files/GOT.md).
A file stores a list of triggers — each with the players it runs for, up to 16 conditions, and up to 64 actions — along with the strings and unit properties its actions use. Mission briefing screens are stored as triggers of briefing actions. The trigger files that initialize the game modes (stored at `triggers\*.trg` in the [MPQs](/Help/Files/MPQ.md)) use a GOT compatible variant of the format, which has no file header, strings, or unit properties.

Edited by [PyTRG](/Help/Programs/PyTRG.md)