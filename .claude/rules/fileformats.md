---
paths:
  - "PyMS/FileFormats/**"
  - "PyMS/Utilities/CodeHandlers/**"
---

# FileFormats and text formats

Most `PyMS/FileFormats/` modules do double duty: they parse/write the raw binary game file **and** serialize to / parse from a human-editable **text format** (the decompiled source the GUI and CLI round-trip — e.g. AI/IScript scripts, `.dat` text dumps, `.trg` triggers). The shared `PyMS/Utilities/CodeHandlers/` framework (lexer → parser → compiler → serializer) backs the scriptable ones. Editing-program logic should call into these, not reimplement parsing.

**This is the highest-risk surface in the project.** Both the binary and text formats round-trip real user data and real game files: a parsing change can silently corrupt saved work or produce files BroodWar can't load.

- **Changes here must stay backwards compatible unless the task explicitly says otherwise.** Text that parsed before must still parse; binary that loaded before must still load. Don't rename, reorder, or repurpose existing tokens, keywords, or struct fields, and don't tighten parsing so previously-valid input now errors — add new syntax/fields additively.
- Verify with round-trips: parse → serialize → parse should be stable, and binary load → save should stay byte-identical where it was before. Prefer adding/adjusting a `PyMS/Tests/` case over manual verification.
- `FileFormats` may use core `Utilities` (`IO`, `Struct`, `BytesScanner`, `PyMSError`, `CodeHandlers`, `DataContext`, ...) but must not import `UIKit`, dialogs, or program packages (see the layering rule in `code-structure.md`). `Palette.py`'s `UIKit` import is a known legacy exception — don't copy it.
