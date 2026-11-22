# Orders Tab
The Orders tab of [PyDAT](/Help/Programs/PyDAT.md) edits [orders.dat](/Help/Files/DAT/orders.dat.md), which contains the settings for all the orders in the game — the commands units carry out, like Move, Attack Unit, or Gather.

## Order Properties
- **Weapon**: The [Weapon](/Help/Programs/PyDAT/Weapons.md) of a spell or ability: fired by the castspell iscript command, and giving the casting range, cooldown and (with Use Weapon Targeting) the targeting rules.
- **Tech**: The [Technology](/Help/Programs/PyDAT/Techdata.md) of a spell or ability: its energy cost is used, and its use requirements replace the order's own.
- **Obscured**: On the orders a unit gets for a target under the fog of war, the order it is given once it sees the target. None means the order can't target units under the fog.
- **Label**: The orders name string in `stat_txt.tbl` (not used by the game).
- **Animation**: The [IScript animation](/Help/Files/iscript.bin.md#animations) played when the order is cast as a spell.
- **Highlight**: The icon highlighted on the command card while the order runs (or None) — pick it by ID, or click the preview or find button to browse all the icons visually.
- **ReqIndex**: Where the order's requirements start in the game's built-in requirement list. Keep 65535, which lets the game fill it in.

## Flags
The orders behavior flags: Use Weapon Targeting, Changes Subunit Order, Can be Interrupted, Waypoints Slowdown, Can be Queued, Disabled Maintain Unit Target, Obstructable, and Flee Unreturnable Damage. A few flags are unused by the game and labeled as such: Secondary Order, Allow Non-Subunits, Allow Subunits, and Requires Movable Unit. Hover over each flag for an explanation.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units using the order in their AI Actions.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [orders.dat](/Help/Files/DAT/orders.dat.md)
