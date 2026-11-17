---
paths:
  - "PyMS/**/*.py"
---

# Code structure

## Where functions live

Prefer methods on the owning class over module-level functions:

- A function whose first parameter is an instance of `X` (or that only reads `X`'s fields) is an instance method on `X` (`hs.tooltip_runs(...)`, not `tooltip_runs(hs, ...)`).
- A function that builds an `X` is a classmethod on `X` named `from_*`/`for_*` or a descriptive constructor name (`TextLayout.from_runs`, `TooltipCosts.for_unit`, `TextStyle.ingame`), returning `cls(...)`.
- A non-trivial helper used by only one class is a private (`_name`) static/instance method on it (trivial ones are inlined, see below). Nested functions are fine when they need the enclosing function's locals.
- Constants that belong to one class and are used in several places are class attributes on it (`ClassVar[...]` on dataclasses so they don't become fields). Single-use values are inlined (see below).
- Write each kind's method out explicitly (`for_unit`, `for_upgrade`, ...), adding a small dispatcher (`for_kind`) only when callers need one. Method names must not shadow fields (`effective_space_width()` beside the `space_width` field).
- **Layering decides the class.** Never add a method that makes a lower layer import a higher one (`FileFormats` may use core `Utilities` like `IO`, `Struct`, `BytesScanner`, `PyMSError`, `CodeHandlers`, `DataContext`, but must not import `UIKit`, dialogs, or program packages; shared `Utilities` must not import program packages). When the obvious class is in a lower layer, put the method on the higher-layer type it produces (`Race.from_staredit_group_flags(flags)`, not `DATUnit.race()`).
- Shared `Utilities` APIs take plain values rather than program/format objects when that's all they use (`TooltipCosts.for_kind(kind, entry_id, ...)`, not `(button, ...)`).
- Program glue that needs editor state is a method on the view/delegate that owns that state; child widgets reach it through their delegate `Protocol` (`self.delegate.button_tooltip(button)`), not free functions with context passed in.
- Top-level functions are only for pure, stateless helpers over builtin types with several unrelated callers and no natural owner, placed beside similar helpers in their domain module (`TBL.compile_string`, `TBL.end_at_null`). Don't create static-only namespace classes just to avoid module functions.
- Before adding a function, look for an existing method or near-duplicate (e.g. a sibling lookup on the same class, or the same object built elsewhere) and extend or reuse it instead.

## Don't add superfluous abstractions

Every new function, class, type, constant or table must have a concrete reason to exist beyond "naming" or "tidiness". These have all been asked for and then removed:

- **Inline trivial helpers.** No function/method whose body is ~1–3 lines unless it has many callers *and* names a non-obvious concept. Write the expression at each call site (`fit('', cmd_def.full_help_text())`, not a `command_help()`; build an opcode lookup inline, not via `_opcodes_by_id()`).
- **No single-value wrapper classes.** Don't wrap one value (an ID, a flag) in a class/dataclass so the type "says what it means"; the parameter name does that (`owner_unit_id: int | None`, not `ButtonSetOwner`). Do derived lookups (e.g. the unit's race) where they're used.
- **No convenience widget subclasses** that only bundle existing widgets (Button + Tooltip). Compose them at the call site, following the existing pattern (e.g. how `find_icon_button` is built).
- **One source of truth.** Never write a data table, enum or dataclass list that then gets converted into another structure (`ReqOpcode`/`ButtonFunction`/`ParamKind` → `CodeCommandDefinition`). Put the data directly on the final structure. Check how the sibling format (AIBIN, IScriptBIN) does it first and match it.
- **No empty or pass-through subclasses/layers.** A subclass must add state or behaviour that is actually used; otherwise use the base class directly. Don't add `create()`/`create_with_param()` factories when calling the constructor works.
- **Concrete classes, not type factories or generic wrappers.** Write one class per kind (no `id_type(...)` returning a class, no generic `OptionalCodeType`). Shared code goes in an `_`-prefixed, unexported base that is only used as a base.
- **Write lists/tables out explicitly** rather than building them with helper functions, filtering or set arithmetic over other lists (no `check_allowed_opcode_commands()`; each opcode list is written out in full).
- **No constants for single-use or fixed values.** Inline literals used once; hardcode counts that never change (`range(1, 10)`, not a `SLOT_COUNT` derived dynamically).
- **Fix the shared utility, not a local wrapper.** If a core class (`BytesScanner`, `Assets`, UIKit) lacks a feature, extend it rather than wrapping it locally (bounds checking went into `BytesScanner`, not a `scan_word()`).
- **No speculative machinery.** No caching, fallback/escape-hatch types (`Raw`, `RawCondition`), duplicate validation stages or unused fields without a concrete, current need. Prefer reporting an error, and validate in one place (when parsing, not again on load).
- **Self-audit before reporting.** For each new function/class/type/constant/table in the diff, ask: "if the user asks *why does this exist?*, is the answer more than naming or tidiness?" If not, inline or remove it before finishing. If you keep it, state the concrete reason in the report.

## Key events

Key event checks compare keysyms: `Keysym(event.keysym) == Key.Return` (via the barrel: `UI.Keysym(...) == UI.Key.Return`). Never compare `event.keycode` to numbers (platform-specific — Return is 13 on Windows, 36 on macOS) or `event.keysym` to `.name()`/string literals. A keysym alone can't verify modifiers, so `== Ctrl.Return` is always False — modifier combos need real event bindings.

## Image types

- `PIL.Image` is for pixel construction only (FileFormats) — never handed to widgets. FileFormats converters (`GRP.frame_to_photo`, `Tileset.megatile_to_photo`/`minitile_to_photo`, `FNT.letter_to_photo`, ...) return plain `ImageTk.PhotoImage` so callers need no casts.
- `tkinter.PhotoImage` is only for bundled GIF assets (`Assets.get_image`) and UIKit component icon params.
- For GUI-layer annotations meaning "any displayable image" (caches, delegate protocols, `Canvas.create_image`) use `UI.AnyPhotoImage` (= `tk.PhotoImage | ImageTk.PhotoImage`, in `UIKit/Types.py`) — prefer it over `UI.ImageTk.PhotoImage`, which needs a `type: ignore`. Don't reintroduce `tkinter.Image`/`BitmapImage` or casts between image types.
- Gotchas: `Assets.py` must import `AnyPhotoImage` under `if TYPE_CHECKING:` (a runtime import from the UIKit barrel is circular), and keep strong references to Tk images (e.g. caches like `canvas_images`) or Tk garbage-collects them out from under widgets.
