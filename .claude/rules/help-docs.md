---
paths:
  - "Help/**/*.md"
---

# Help docs (`Help/`)

Help content is Markdown rendered in two places: on GitHub, and in-app by the custom viewer (`PyMS/Utilities/Markdown.py` + `MarkdownView.py`). Every page must render correctly and have working links in **both**.

## Finding pages to update

- Find the affected pages by grepping `Help/` for the program name, feature name, menu label, or shortcut you touched — don't assume one page. Coverage spans `Help/Programs/<Program>.md` plus its `Help/Programs/<Program>/` sub-pages, `Help/Files/` (format/reference pages, e.g. command and field references), and `Help/Tutorials/` (step-by-step walkthroughs, which go stale fastest because they name concrete UI elements).
- Reference pages that mirror a registry (command references, `.dat` field lists) must be re-checked against the code when the registry changes — a new command or field is a doc change too.

## Authoring rules

Write GitHub Flavored Markdown restricted as follows:

- **Never use** (unsupported by the in-app parser): tables, raw HTML, setext headings (ATX `#` only), reference links (`[text][ref]`), autolinks (`<url>`/bare URLs — always `[text](url)`), task lists, footnotes, and backslash escapes (use a code span to show a literal `*`, `_`, etc.).
- **Also avoid** (parsed but rendered wrong in-app): thematic breaks (`---` renders as nothing), block quotes (`>` renders as an unstyled paragraph), and italic/strikethrough (markers are stripped but no styling applied — `**bold**` is the only emphasis that renders).
- **Links**: cross-page links are root-absolute with the `.md` extension, e.g. `[units.dat](/Help/Files/DAT/units.dat.md)` or `[...](/Help/Files/iscript.bin.md#animations)` — the in-app resolver (`Assets.HelpFolder.index()`) only accepts `/Help/...` paths, and GitHub resolves them too. File-relative links (`PyAI.md`, `../Files/GRP.md`) are silently dead in-app. Same-page links are `[text](#anchor)`. External links need an explicit scheme (`https://...`). Never put a code span inside link text (it's parsed first and destroys the link).
- **Heading anchors**: the in-app slugger (`ATXHeading.anchor()`) matches GitHub's: lowercase; letters, digits, underscores, hyphens, and spaces are kept (all other punctuation dropped, including backticks — a code-span heading like `` ### `wait_build` `` anchors as `#wait_build`); spaces become hyphens. Heading text must be unique within its file: GitHub deduplicates repeated headings with `-1` suffixes, but the in-app viewer does not. The underscore rule from the Code bullet applies to headings too — put identifiers with underscores in code spans, or paired `_` will be eaten as italic markers and change both the rendering and the anchor.
- **Paragraphs**: the in-app viewer turns every source newline into a line break (GitHub joins them with a space), so keep each paragraph on a single source line. For a deliberate break inside a paragraph end the line with two trailing spaces — never `\`, which renders literally.
- **Lists**: number ordered lists sequentially from `1.` (the in-app viewer numbers by position, ignoring source numbers). Indent nested lists/continuation lines to the parent item's text column — unindented (lazy) continuation closes the list in-app. At most 3 nesting levels render distinctly.
- **Code**: fenced and 4-space-indented blocks both work; a fence language is ignored in-app but fine for GitHub highlighting. Code blocks don't wrap in-app, so keep lines short. Write keyboard shortcuts as code spans in Windows form (`` `Ctrl+Shift+A` ``) — the viewer converts them to Mac symbols automatically. Put identifiers containing underscores in code spans (`some_var_name` would otherwise be mis-italicized in-app).
- **Images**: `![alt](/Help/path/image.png)` — resolved under `Help/` by `Assets.help_image()`, file extension required; alt/title become the tooltip.

## Anchor and link stability

The `Help/` pages are read on GitHub, so every heading is a public URL people link to and share. **Treat existing heading text and page paths as a stable API** and make a best effort to keep them as-is:

- Prefer editing a section's body over re-titling it, and prefer adding a new heading over renaming an existing one. Rewording a heading changes its anchor (see the Heading anchors rule) and breaks every external link to it.
- Don't rename or move a `.md` file, or reshuffle a page's heading hierarchy, for tidiness alone. Adding new sections is free — it doesn't disturb existing anchors.
- If a rename/move really is required, update every in-repo link to it (the link test finds the broken ones) and call out in your report that previously shared external links will break.

## Validating links

Any change to a heading, a link, an image path, or a page filename must be verified with the link validation test:

```
pyenv exec python -m unittest PyMS.Tests.Help.test_help_links
```

It parses every `Help/**/*.md` with `Markdown.Document.parse` and checks that links are same-page `#anchor`, root-absolute `/Help/....md`, or external with a scheme; that cross-page targets resolve through `Assets.help_tree().index()`; that every `#anchor` matches a real heading in the target page; that heading anchors are unique per page; and that image paths point at files that exist. It's part of the full suite, but run it directly after touching docs — it's fast and names the offending page and link.
