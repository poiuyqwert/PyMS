---
paths:
  - "PyMS/Tests/**"
  - "PyMS/UITests/**"
---

# Writing tests

## Organization

- `PyMS/Tests/` — `unittest` suite mirroring the format/utility modules. One folder per subject named after the source module (`Tests/CHK/`, `Tests/UIKit/`, `Tests/PyDAT/`), each an empty-`__init__.py` package; `Tests/Utilities/` is the catch-all for loose `Utilities/*.py` modules that don't warrant their own folder. Folder-local fixture helpers go in an unprefixed `utils.py` (skipped by `test_*.py` discovery); `Tests/utils.py` holds the suite-wide `resource_path`/`data_to_hex`.
- `PyMS/UITests/` — organized the same way as `Tests/`: one folder per program (`UITests/PyPAL/`, `UITests/PySPK/`, ...) plus `UITests/UIKit/` and `UITests/Utilities/` for the shared widgets and dialogs, with tests split by concern inside each. A folder's `utils.py` holds its `Py<PROG>TestCase` subclass (the `make_*`/`open_*`/`with_*` window builders), its uppercase patch-target constants, and its fixture builders — hoist something there only once a second module in the folder needs it, otherwise leave it in the module that uses it.

## Rules

- Test names/comments should describe the invariant, not the bug.
- **Tests that assert a `PyMSError` is raised must validate it's the *expected* error**, not just that some `PyMSError` occurred. Capture the exception and assert on a distinctive substring of its message — bare `with self.assertRaises(PyMSError):` is not enough:
  ```python
  with self.assertRaises(PyMSError) as cm:
      some_call()
  self.assertIn('<distinctive part of the expected message>', str(cm.exception))
  ```
  Pick a stable substring (prefer the static, non-interpolated part of the `raise PyMSError('Type', '...')` message, specific enough to identify that error path), and run the test to confirm it matches the actual message.
- **Tests must not write generated test data to disk.** Don't create temp files/dirs (or write into `Settings/`, bundled data, etc.) to feed or capture test data. Instead keep it in-memory: use the `Utilities/IO.py` helpers (`IO.InputText`/`IO.InputBytes` accept a path, a file-like object, *or* a raw `str`/`bytes`; `IO.output_to_text`/`IO.output_to_bytes` capture a writer's output), `io.StringIO`/`io.BytesIO`, or `unittest.mock` to stub the I/O boundary. When a class reads/writes files through a small overridable seam (e.g. `Config._read`/`_write`), mock that method to supply or capture data rather than going through the filesystem. Reading committed read-only fixtures under `PyMS/Tests/` is fine; producing new on-disk files during a test run is not.
