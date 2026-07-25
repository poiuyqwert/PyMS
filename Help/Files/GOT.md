# GOT
Game Template `.got` files contain the settings for the game modes listed in StarCraft, like `Melee`, `Free For All`, and `Greed`. Each template stores its listed name and ordering IDs, its variation info, and its game rule settings (victory conditions, starting resources and units, fog of war, teams, and so on).
Game modes with multiple variations (like the mineral targets of `Greed`) have one `.got` file per variation, sharing the same template name and ID. The games templates are stored at `templates\*.got` inside the [MPQs](/Help/Files/MPQ.md), and the [triggers](/Help/Files/TRG.md) that initialize the game modes are stored in a GOT compatible format at `triggers\*.trg`.

Edited by [PyGOT](/Help/Programs/PyGOT.md)
