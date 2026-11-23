# Orders Tab
The Orders tab of [PyDAT](/Help/Programs/PyDAT.md) edits [orders.dat](/Help/Files/DAT/orders.dat.md), which contains the settings for all the orders in the game — the commands units carry out, like Move, Attack Unit, or Gather.

## Order Properties
- **Weapon**: The [Weapon](/Help/Programs/PyDAT/Weapons.md) of a spell or ability: fired by the castspell iscript command, and giving the casting range, cooldown and (with Use Weapon Targeting) the targeting rules.
- **Tech**: The [Technology](/Help/Programs/PyDAT/Techdata.md) of a spell or ability: its energy cost is used, and its use requirements replace the order's own.
- **Obscured**: On the orders a unit gets for a target under the fog of war, the order it is given once it sees the target. None means the order can't target units under the fog.
- **Label**: The orders name string in `stat_txt.tbl` (not used by the game).
- **Animation**: The [IScript animation](/Help/Files/iscript.bin.md#animations) played when the order is cast as a spell.
- **Highlight**: The icon highlighted on the command card while the order runs (or None) — pick it by ID, or click the preview or find button to browse all the icons visually.
- **ReqIndex**: Where the order's requirements start in the order requirement list built into StarCraft.exe. The requirements themselves (such as which buildings are needed) are in that list and cannot be edited in the dat files; this value only picks a position in it. Keep 65535 (0xFFFF). Orders with a Technology use that technology's use requirements instead.
  - **65535**: As soon as the game checks an order that holds 65535, it looks up every order that has an entry in the built-in list and stores the position of that entry, replacing what the file had. Every order still holding 65535 is then set to 0. So once that has happened, the file's value only survives for orders that have no entry in the list.
  - **Other values**: Until the game checks an order holding 65535, and always if none holds 65535, each value is used as it is. 0 means the order is never allowed. Any other number is a position in the built-in list, and the game reads conditions from there until it reaches the end of an entry. The start of the order's own entry gives its normal requirements, and the start of another order's entry gives that order's requirements. A position inside an entry gives the rest of that entry, and may read a unit number meant for one condition as a condition of its own. A position on the end of an entry gives no requirements, so the order is allowed whenever the game's other checks pass. A position past the end of the list reads whatever memory follows it. Nothing checks the value, and PyDAT cannot show the built-in list.

## Flags
The orders behavior flags: Use Weapon Targeting, Changes Subunit Order, Can be Interrupted, Waypoints Slowdown, Can be Queued, Disabled Maintain Unit Target, Obstructable, and Flee Unreturnable Damage. A few flags are unused by the game and labeled as such: Secondary Order, Allow Non-Subunits, Allow Subunits, and Requires Movable Unit. Hover over each flag for an explanation.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units using the order in their AI Actions.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [orders.dat](/Help/Files/DAT/orders.dat.md)
