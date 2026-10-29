---
name: version
description: Bump PyMS/versions.json patch versions and add a Help/Programs/Change_Log.md entry for the user facing changes made since the last version bump. Use when the user runs /version or asks to bump versions / update the change log.
---

# /version

Maintains `PyMS/versions.json` and `Help/Programs/Change_Log.md` together. Paths are relative to the repo root (the directory containing the `.pyw` launchers). Never commit; leave the edits for the user to review.

## 1. Collect the changes

Walk back from `HEAD` on the current branch and **stop before (excluding)** whichever comes first:

- the most recent commit that touches `PyMS/versions.json`: `git log -1 --format=%H -- PyMS/versions.json`
- the fork point from the base branch: `git merge-base HEAD origin/master`

```bash
git log --reverse --format='%H %s' <stop>..HEAD
```

Also include the **uncommitted** changes (staged, unstaged and untracked): `git status --porcelain` and `git diff HEAD`, plus reading any untracked files that matter. Ignore untracked scratch files that aren't part of the project (notes, drafts).

For each commit, read the message **and** the diff (`git show --stat <sha>`, then `git show <sha> -- <paths>` as needed). Messages are often terse or misleading; the diff decides what actually changed for users.

If there are no commits and no uncommitted changes, say so and stop without editing anything.

## 2. Keep only user facing changes

Keep: bug fixes, improvements and new features that a user of the programs could notice (behavior, UI, shortcuts, file format support, error messages, performance they would feel, new or substantially expanded help content).

Drop: tests (`PyMS/Tests/`, `PyMS/UITests/`), refactors, typing/lint fixes, renames with no visible effect, developer tooling, `.claude/`, CI, comments, and help-doc formatting/link fixes. A single commit can mix both; keep only the user facing part.

If nothing user facing remains, say so and stop without editing anything.

## 3. Attribute each change to a program

Decide by the files changed and, above all, by which program's users see the effect:

- `PyMS/<Program>/`, `<Program>.pyw` and `Help/Programs/<Program>*` belong to `<Program>`.
- `PyMS/FileFormats/<Format>/` belongs to the program(s) whose behavior changes (e.g. `AIBIN` → PyAI, `IScriptBIN` → PyICE, `TRG` → PyTRG).
- A change that affects two or more programs, or lives in shared code (`PyMS/Utilities/`, UIKit, settings, themes, the help viewer, update checks) and is felt by every program, is a `PyMS` change.
- Only use keys that already exist in `PyMS/versions.json`. Never add new keys.

Merge duplicates: several commits that make one feature are one change. Drop changes that a later change in the same range reverts or makes irrelevant.

## 4. Bump the versions

For each program with at least one change (including `PyMS`), increase the **patch** number by exactly one (`2.9.8` → `2.9.9`), once per run regardless of how many changes it has. **Never** change the major or minor numbers, even for large features.

Edit `PyMS/versions.json` in place: keep its tab indentation, `"Key":"value"` spacing, and key order. Don't touch programs without changes.

## 5. Update the change log

Insert a new section at the top of `Help/Programs/Change_Log.md`, directly under the `# Change Log` title (there is no intro paragraph):

```markdown
# Change Log

# October 29, 2026

## PyMS v2.3.9
- Short sentence about a change.

## PyAI v2.9.9
- Short sentence about a change.
- Another short sentence.
```

- The date header is today's date as `# <Month> <D>, <YYYY>` (full month name, no leading zero on the day).
- One `## <Program> v<new version>` sub-header per bumped program: `PyMS` first, then the rest in `versions.json` order.
- Leave one blank line between headers and lists.
- **Headings must be unique within the file.** If the newest existing date section already has today's date, add the new sub-headers into that section (PyMS first, then `versions.json` order, among the new and existing sub-headers) instead of creating a second header with the same date. Since the versions were just bumped, the new sub-header text will not clash.
- Never edit or reorder older sections.

## 6. Write the bullets

- One short sentence per bullet, ending in a period.
- Write for non-technical modders: say what changed for them, not how. No class, function or file names, no commit hashes, issue numbers or internal jargon.
- Start fixes with what now works ("Opening a file with spaces in its name no longer fails."), and features with what you can now do ("You can now jump to a block's definition with `Ctrl+Click`.").
- Follow the `Help/` authoring rules in `.claude/CLAUDE.md`: `**bold**` is the only emphasis, no italics, tables or HTML. Write keyboard shortcuts as Windows-form code spans (`Ctrl+Shift+A`), and put anything containing underscores in a code span (`stat_txt`). Links must be root-absolute `/Help/....md` or full `https://` URLs.

## 7. Validate and report

```bash
pyenv exec python -m unittest PyMS.Tests.Help.test_help_links
```

Fix any failure. Then show the user:

- each version bump (`PyAI 2.9.8 → 2.9.9`), and
- the new change log section.

Also list any changes you were unsure about, whether you kept or dropped them or how you attributed them, so the user can adjust. Do not commit.
