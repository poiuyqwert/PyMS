# AI Basics
Contributed by Nekron


Starcraft's AIscript code (used in [PyAI](/Help/Programs/PyAI.md)) is a procedural (meaning it executes code in the order it's written, top-down) scripting language used only in the original Starcraft game. In structure, it's fairly similar to assembly - and similarly can have labels referenced by other parts of code and subroutines. Script labels for most operations may require owners - meaning, they have to be started in an AI "town", or else Starcraft just crashes.
The code consists of opcodes that may set flags used by the AI as global parameters, increment requests used by the AI to build towns and research technologies, or overall influence the AI or the map in some way. 


Opcodes can be categorized into [Flag Commands](#flag-commands), [Header Commands](#header-commands), [Request Commands](#request-commands), [Flow Commands](#flow-commands), [Editor Commands](#editor-commands), and a few Other Commands sprinkled in-between that may be hard to categorize.


## Flag Commands
Flags are simple booleans that the AIscript may check against during its operation; some of them are static and cannot be changed after being set once (with the notable mention of "start_campaign", that not only is irreversible but also always True in the Use Map Settings Mode), and some others may be very temporary in their nature, and back to False very frequently - for instance, an opcode that can be used to have AI Players defend each other - "help_iftrouble" - will only affect regions once, and needs to be refreshed afterwards to maintain the effect.
A single flag can affect many parts of the AIs functionality - the already-mentioned campaign flag influences everything from how the AI attacks and defends down to how it's going to be producing transports and spending money.


## Header Commands
Headers are a few opcodes that you will most likely always run in an AI script - you always need to "start_town" or "start_areatown" for an AI player to create a town array that can process requests. This sometimes involves single-frame waits, since structure assignment for UMS maps happens in a specific order - Areatowns need to be initialized 1 frame after the main Town.


## Request Commands
Request opcodes are operations that, in one way or another, interact with the Town array for an AI - they tell the AI what to build, at what priority and order and in what number. Not all of these parameters can necessarily always be set - for example, the "train" opcode is always processed at priority 50 - but they out of necessity always exist in the background. The most basic requests are building, upgrade and tech requests - the AI can be told to `build(1, command_center, 80)`, which has it require from its workers to construct a single Command Center with the priority of 80. This is then subjected to spending checks and priority checks against what the AI already has requested, but keep in mind that it will also use just any worker - if the AI's workers can't all build this building, it may just pick an invalid one and repeatedly fail to construct anything.

**Notable bugs:**
- In unmodded Starcraft, the AI will automatically request certain units if it has above 500 resources of both types and any missing Guard-type units while a "train" request is called for. This severely decreases this opcodes' usefulness and damages the AI's performance.
- In unmodded Starcraft, the AI will never fulfill request if a higher-priority request is still pending, even if it has resources to cover both of them at once.
- In unmodded Starcraft, the AI may end up in situations where certain unit Morphs are called for in invalid unit states (morphing burrowed Hydras into Lurkers) which makes the AI waste money and fail to train the requested unit.


## Flow Commands
Flow operations are related to moving within the constraints of the script or flagging parts of it in an explicitly non-user-facing way. `call` can jump to a subroutine code block until you `return` from it, `goto` can straight up jump to another part of code, whereas `multirun` can simultaneously run code from a label in parallel. For some less straightforward examples, there are also more involved comparisons such as `region_size`, that compare against the pathfinder region count for the town that the scripts' current label is owned by and jump if the comparison is false.

**Notable bug:**
- In unmodded Starcraft, only one Player at once call have their call return point stored, and only for one label at a time.


## Editor Commands
Some opcodes are just made to be used with the editor. They will usually be recognizable from Campaign scenarios, such as `create_nuke` that creates a nuke immediately in a free silo, or `move_dt` that moves Hero Dark Templar to a Location.
