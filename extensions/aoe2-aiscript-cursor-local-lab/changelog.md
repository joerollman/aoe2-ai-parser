# Change Log

All notable changes to the "aoe2-ai-parser" extension will be documented in
this file. Version numbers are given as:

    <major>.<minor>.<patch>

## v0.1.70

- Remove unused legacy `aiName` and `aiDirectory` extension settings.
- Default `maxErrorsReported` to `-1`, meaning diagnostics are uncapped unless
  the user explicitly sets a cap.
- Rename AutoFormat palette entries to clarify current-file formatting versus
  nearest-package formatting.

## v0.1.69

- Stream `lint-package --trace-progress` output into the output panel while
  package/folder linting is still running.

## v0.1.68

- Add a `Lint trace` tree to package/folder lint command output showing the
  input path, resolved roots, reachable `.per` and `.xs` files, and
  load/include edges.

## v0.1.67

- Show a visible progress notification while parser commands such as linting,
  report generation, and package formatting are running.

## v0.1.66

- Rewrite command output after parser commands finish so the output panel starts
  with a clear `complete` header, final status, and duration.

## v0.1.65

- Make package-aware live diagnostics opt-in by defaulting
  `aoe2_AiScript.usePackageLint` to `false`; command-palette package linting is
  unchanged. This avoids repeated full-package Python validation when opening or
  saving large AI files.

## v0.1.64

- Add `AoE2: AutoFormat Package`, which formats every `.ai` and `.per` file in
  the nearest AI package folder.

## v0.1.63

- Keep users' normal editor theme colors by default by making parser-specific
  semantic coloring opt-in through `aoe2_AiScript.enableSemanticColors`.
- Add `AOE2 AiScript Classic`, an opt-in theme based on the original
  extension's TextMate scopes.

## v0.1.62

- Add `AoE2: AutoFormat` for active `.per` and `.ai` files.
- Add opt-in `aoe2_AiScript.formatOnSave` plus formatter settings for maximum
  comment line length and chat-line formatting.

## v0.1.61

- Resolve package load paths from the root entry file's folder first, with the
  including file folder retained only as a fallback for compatibility.

## v0.1.60

- Prefer VS Code's Markdown preview command when opening package-lint reports
  from `Lint Package`, `Lint Folder`, and report commands.

## v0.1.59

- Make `Lint Package` and `Lint Folder` write Markdown reports and open them in
  a side Markdown Preview when validation finishes.

## v0.1.58

- Fix command-palette lint commands in the packaged JavaScript by using native
  `async` functions instead of a missing TypeScript `__awaiter` helper.

## v0.1.57

- Make symbol definition and Markdown preview navigation target the generated
  `symbol-*` anchors in the combined reference.
- Contribute default semantic-token color customization entries for both parser
  themes so users can discover and edit individual parser token colors.
- Run command-palette lint commands asynchronously so hover/help providers are
  not blocked while package validation is running.
- Open generated package reports in a side Markdown Preview when report
  generation or latest-report lookup completes.

## v0.1.56

- Add `AOE2 AI Parser Light` as a contributed color theme.
- Refine the dark theme palette and keep strategic numbers visually distinct
  from local constants.
- Document theme-scoped semantic-token overrides so users can customize each
  parser color individually.

## v0.1.55

- Make hover handling fail fast through the local registry and avoid the slower
  legacy hover fallback that could leave popups stuck loading.

## v0.1.54

- Clarify that VS Code's built-in symbol definition gesture is Ctrl+Click, not
  Ctrl+Alt+Click.
- Make registry-symbol definition navigation return the exact Markdown source
  range instead of relying on URI fragments.

## v0.1.53

- Make symbol documentation navigation target Markdown heading fragments, which
  Cursor/VS Code Markdown Preview handles more reliably than raw HTML anchors.

## v0.1.52

- Add inline suppression support with `aoe2-ai-parser-disable-line` and
  `aoe2-ai-parser-disable-next-line` comments.
- Add editor quick fixes that suppress a diagnostic on the current line.
- Add the `suppress-finding` CLI helper for inserting suppression comments.

## v0.1.51

- Add `AoE2: Lint Folder`, which runs package validation against the folder
  containing the active file.
- Make package/folder lint default to info-level findings in the extension.
- Clarify the difference between current-file lint, package lint, and folder
  lint in user docs.
- Document semantic-token color customization for VS Code/Cursor users.

## v0.1.50

- Make command-palette lint output more visible by opening the AOE2 AI Parser
  output channel in the foreground.
- Write explicit output-channel messages when package commands cannot run
  because no workspace, `.ai`, or `.per` package context is available.

## v0.1.49

- Cap hover documentation previews so large command reference entries do not
  leave VS Code/Cursor hover popups stuck loading. Full documentation remains
  available through Markdown Preview links.

## v0.1.48

- Add `aoe2_AiScript.packageFailLevel` so package commands, generated reports,
  and package-aware diagnostics can surface `error`, `warning`, or `info`
  findings.
- Document lint-on-save behavior and package fail-level settings for editor
  users.

## v0.1.47

- Add the `AOE2 AI Parser Dark` color theme with semantic-token colors and
  TextMate fallback colors for parser-specific token categories.
- Replace the extension icon with a simple text logo for AOE2 AI Parser.
- Remove stale upstream extension snapshot files from the parser repository.
- Reframe README guidance for marketplace users first.

## v0.1.46

- Harden extension packaging so common local credential files, key material, and
  dependency test fixtures are excluded from the VSIX.

## v0.1.45

- Add package graph output for reachable `.per` load/load-random edges and
  `.xs` include edges.
- Add package warnings for `load`/`load-random` directives after `include`
  directives and duplicate reachable `.per` load targets.
- Add include and XS validation improvements, including duplicate include
  warnings and include target go-to-definition.
- Improve diagnostic documentation actions and generated diagnostic registry
  coverage.
- Document the feedback-gated boundary for future semantic warnings and
  severity changes.

## v0.1.44

- Rebrand the packaged extension as AOE2 AI Parser under the AOE2 AI Scripters
  publisher.
- Bundle the parser/linter runtime and local reference data so users do not need
  a repository checkout for diagnostics.
- Add package-aware diagnostics, generated Markdown reference navigation,
  semantic coloring, contextual completions, signature help, quick fixes, and
  package reports.

## v0.1.7

- Rename 'cc-add-resources' to correct value of 'cc-add-resource' [#15]
- Fix issue where `#load-X` like directives were not recognized in completions
  and signature help [#16]
- Add missing parameters of the form `my-X` [#16]
- Add `defconst` to list of signatures [#6]
- Make boolean values more discriptive [#7]
- Minor backend improvements

## v0.1.6

- Add tech, unit, and building ID numbers to resources
- Add a lot of missing resource objects (also fix some incorrect ones)
- Setup hierarchy of identifier IDs, to improve error detection and prevent
  false positives
- Add experimental error detection (off by default)
- Remove completion, hover, and signature help from experimental to released
- Set completion, hover, and signature help ON by default

## v0.1.5

- Add additional resource information and add additional categories
- Fix signatures issue where signatures would highlight the wrong variable
  [issue [#8](https://github.com/Jvinniec/aoe2-aiscript/issues/8)]
- Add leveled parameter help (added 'parametersOnly' option) to prevent
  saturating the screen with text

## v0.1.4

- Add tutorial for defining custom colors
- Add additional syntax highlighting groups for finer grained coloring
- Fix several incorrect civilization IDs

## v0.1.3

- Implement hover help text
- Implement command parameter help (a.k.a. signatures)
- Add experimental 'completion suggestions' with help text
- Add resource files (under 'languageExtension/src/resources') to augment
  experimental completions
- Extend syntax highlighting to all facts/rules
- Add snippet 'actrule' to provide a rule with a user selectable action to take
- Add snippet 'researchrule' providing a rule that can research a given tech

## v0.1.2

- Add snippets capability ("addrule", "buildrule", "trainrule")
- Add icon for the extension

## v0.1.1

- Fix image size in README.md

## v0.1.0

- Initial alpha release of the extension
- Very basic syntax highlighting capabilities are enabled
