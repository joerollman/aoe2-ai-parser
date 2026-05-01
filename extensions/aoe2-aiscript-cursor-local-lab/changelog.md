# Change Log

All notable changes to the "aoe2-ai-parser" extension will be documented in
this file. Version numbers are given as:

    <major>.<minor>.<patch>

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
