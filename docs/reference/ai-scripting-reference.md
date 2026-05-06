# AoE2 DE AI Scripting Reference For Future Work

This is a working reference for implementing custom AIs in Age of Empires II:
Definitive Edition. It is intentionally written for future coding sessions in
this repo, not as a full public tutorial.

Primary sources:

- AoE2 AI Scripting Encyclopedia: https://airef.github.io/
- Commands intro: https://airef.github.io/resources/articles/intro-to-commands.html
- Commands index: https://airef.github.io/commands/commands-index.html
- Logical operators: https://airef.github.io/resources/articles/logical-operators.html
- Strategic number index: https://airef.github.io/strategic-numbers/sn-index.html
- Strategic number defaults:
  https://airef.github.io/resources/articles/sn-defaults-to-change.html
- Data limits: https://airef.github.io/resources/articles/data-limits.html
- Community resource index:
  https://airef.github.io/resources/res-index.html
- HD AI script example:
  https://gist.github.com/mayerwin/ac4a5ec62f51e94a3fa9
- Community guide:
  https://docs.google.com/document/d/1jnhZXoeL9mkRUJxcGlKnO98fIwFKStP_OBozpr0CHXo/edit

Community references can be outdated or pre-DE. Use them as leads, then verify
with local lint/install checks and in-game behavior before turning them into
project rules.

## Core Mental Model

AoE2 AI scripts are rule systems. The game repeatedly evaluates `defrule`
blocks. If every fact before `=>` is true, the actions after `=>` execute.

Basic rule shape:

```lisp
(defrule
    (fact-command arg ...)
    (another-fact arg ...)
=>
    (action-command arg ...)
    (disable-self)
)
```

Implementation implications:

- Almost all behavior must live inside rules.
- Facts are gates; actions mutate state or request game behavior.
- Rules without state guards can fire repeatedly.
- One-shot initialization or transition rules should usually end with
  `(disable-self)`.
- Long-running behavior rules, such as train/build loops, should be guarded by
  counts, resources, age, strategy goals, and `can-*` facts.

## Files And Loading

Common DE custom AI package:

- `<name>.ai`: descriptor/entry file.
- `<name>.per`: personality/rule script.

This repo currently keeps source AI files under `ai/<bot-name>/`. For manual DE
testing, copy both `.ai` and `.per` files into the local game AI folder.

Use `#load` and conditional load directives carefully:

- Keep load nesting shallow; documented limit is 10 nested file loads.
- Avoid deeply nested `#load-if` blocks. The documented limit is 50, but
  community notes warn practical limits may be lower.
- Do not install raw `#load "file"` directives inside a `.per`. DE reports
  `ERR3001` for that form. In this project, source roots may use `#load` as a
  component marker only because `install-ai` flattens them before copying to the
  game directory.

## Constants, Goals, And Strategic Numbers

`defconst` maps a readable name to a value. The engine ultimately operates on
numbers, so names are for script maintainability.

Use defconsts for:

- goal IDs
- custom enum values
- civ/opening/strategy state labels
- magic numbers that need meaning
- object/resource constants used by UP commands, such as `forage-bush`,
  `forage-food`, or object-class IDs

Goals are script-controlled integer state. Use them for AI decisions:

```lisp
(defconst goal-opening 1)
(defconst opening-feudal-archers 20)

(set-goal goal-opening opening-feudal-archers)
(goal goal-opening opening-feudal-archers)
```

Strategic numbers, or SNs, control built-in AI engine behavior. Treat active
SNs as engine knobs, not arbitrary variables.

Important SN guidance:

- Check the SN index before using an SN as custom storage.
- The community recommendation is to use currently unused high SN IDs as extra
  state, starting near 510 and moving downward.
- Avoid SN 511 in DE for custom state because community docs note bugs.
- Prefer regular goals for custom state unless there is a clear reason to use
  spare SNs.
- Do not assume an SN's full 32-bit range is meaningful; check required min/max
  in the SN index.

## Missing Identifier Rule

DE parser errors like `ERR2005: Invalid identifier` often mean the script copied
a symbolic constant from another AI without copying that AI's `defconst`.

Project rule:

- Every non-built-in symbolic value used after a typed prefix like `c:` must be
  defined locally with `defconst`.
- Bare symbolic command parameters copied from another AI, such as
  `position-curr-object` in `up-get-point`, also need local `defconst` entries.
- Do not assume identifiers found in sample-corpus, HD AI, or another corpus script
  are globally available.
- Before installing an AI into the game folder, always run:

```powershell
python -m aoe2_ai_lab lint ai/<name>/<name>.per
```

Example:

```lisp
; Required before this can be used as c: forage-bush.
(defconst forage-bush 59)

(defrule
    (up-gaia-type-count c: forage-bush > 3)
=>
    (do-nothing)
)
```

The linter checks common missing-symbol cases, including `c:` constants,
strategic number names, and `up-get-point` position constants, because these
failures otherwise waste an in-game launch.

## Data Limits That Affect This Project

Sources:

- [AIRef Data Limits](https://airef.github.io/resources/articles/data-limits.html)
- AoE2 AI Expert documentation for `defconst`, which describes numeric
  `defconst` values as C++ `short` values.

Important limits for `sample_ai` work:

- DE allows 32 elements per rule. Elements include facts, actions, and logical
  operators; `defrule` and `=>` do not count. UserPatch compatibility requires
  16, so prefer staged rules even when DE would allow a larger block.
- Rules are limited to 10,000 total.
- Timers are 1-50.
- Preprocessor conditional loading commands can nest up to 50 levels.
- Numeric `defconst` values were historically documented as signed 16-bit
  integers, but local DE probes validated larger values including `32768`,
  `65536`, `350000`, `2000000`, and `-32769`. The validator now treats numeric
  `defconst` values as signed 32-bit integers and reports
  `defconst-value-out-of-range` only outside that range.
- Compact same-line constants such as `(defconst a 1)(defconst b 2)` are treated
  as separate declarations by the local parser.
- Lines are limited to 255 characters, comments included. The validator reports
  `source-line-too-long` for active source lines above this limit.
- DUC local search list holds up to 240 own-unit IDs.
- DUC remote search list holds up to 40 target IDs.
- A script pass above roughly 20 ms can create lag.

Goal ranges matter:

- Goals `1-40` are unsafe for point, cost, search-state, and guard-state
  commands because those commands write multiple consecutive goals.
- Point commands write x/y into the requested goal and the next goal.
- `position-object` can be a coarse object/tile anchor. For remote search
  results, tournament AIs commonly select the remote object, then use
  `up-get-point position-curr-object` or set a target point and read/sort
  `object-data-distance`.
- `up-get-search-state` writes four consecutive goals:
  local total, local last search count, remote total, remote last search count.
- Avoid using the last few goals for multi-goal writers because they can write
  beyond the valid goal range.

Project rule:

- Use goals `1-40` only for simple scalar state.
- Use goals `41+` for points and DUC search-state blocks.
- Define search-state goals as a four-goal block, not as unrelated individual
  values.
- Pass the first goal of that four-goal block to `up-get-search-state`, never
  one of the derived goals.
- Reserve the full range written by any multi-goal command. For example, if
  `up-get-point` writes to `point-x`, then `point-y` is owned by that same point
  block and should not be reused for unrelated state.
- Run the linter before installing. It now flags rules above DE's 32-element
  parser limit.

## DUC Search And Targeting

Source: Enmipho's Introduction to DUC.

DUC has two working lists:

- `search-local`: own units we want to inspect or command.
- `search-remote`: targets for an order, which can include own, allied, enemy,
  or Gaia objects.

Practical model:

1. Reset search and filters before a new independent search.
2. Populate the local list with units to command.
3. Populate the remote list with the target object, if targeting an object.
4. Use `up-target-point` for point orders or `up-target-objects` for object
   target orders.
5. Use `up-get-search-state` after searches when later rules need to branch on
   whether anything was found.

Never issue a DUC target command against an implicit or stale local list. In the
same rule, after the most recent search reset, the script should explicitly use
one of:

- `up-find-local`
- `up-add-object-by-id search-local ...`
- `up-set-target-by-id`

Then issue `up-target-point` or `up-target-objects`. Otherwise the command can
act on an old local list or on undefined state, which is especially dangerous
for villagers and herdables.

`up-get-search-state` is not just a boolean. If called with `goal-search-state`,
it writes:

- `goal-search-state`: local total
- `goal-search-state + 1`: local last search count
- `goal-search-state + 2`: remote total
- `goal-search-state + 3`: remote last search count

Filters persist until reset. If a rule calls `up-filter-distance`, later
searches will still use that filter unless `up-reset-filters` or a full search
reset clears it. For timed routines, reset intentionally at the start of every
stage unless preserving a filter is the point of the stage.

Performance rule:

- Do not run repeated DUC searches every rule pass. Use timers. The DUC intro
  recommends no more often than about every 2 seconds for repeated searches.
- `up-target-point` can imply pathing work; avoid issuing the same point order
  every tick unless it is correcting a real state problem.

## External AI Logging

Source: AoE2 AI Scripting Encyclopedia, `up-log-data`; AoE2 DE Update 58259
patch notes.

`up-log-data` writes formatted debug text from AI scripts. In DE, it does not
write to the old `aoelog.txt` path. The game must be launched with AI logging
flags enabled:

```text
LOGSYSTEMS=AIScript VERBOSELOGGING
```

Recommended debug launch flags while actively working on AI scripts:

```text
SKIPINTRO DEBUGSPEEDS AIDEBUGGING LOGSYSTEMS=AIScript VERBOSELOGGING CONSTANTLOGGING
```

`CONSTANTLOGGING` makes DE write the log continuously. Without it, the log may
not be created until the game exits.

The DE log is written under the user game logs folder, commonly:

```text
C:\Users\<user>\Games\Age of Empires 2 DE\logs
```

Syntax:

```lisp
(up-log-data 0 "Player number: %d" c: my-player-number)
(up-log-data 0 "Scout herd distance: %d" g: goal-scout-gaia-distance)
(up-log-data 0 "A message without data." c: 0)
```

Parameters:

- First argument is option `0` or `1`; option `1` writes plain text.
- The string can include `%d` or `%s`, replaced by the final value.
- The third argument is a type prefix: `c:`, `g:`, or `s:`.
- The fourth argument is the const, goal, or strategic number to write.

Project rule:

- Prefer `up-log-data` for noisy coordinate and distance traces.
- Keep `chat-to-all` for sparse high-level breadcrumbs that need to be visible
  while testing.
- Add an identifying line near game start so the shared DE log can be filtered
  for `sample_ai`.
- Keep logging scoped to the subsystem under test. In `sample_ai`, flip
  `scout-debug-logging-default` for scout distance/front-back traces and
  `xs-debug-logging-default` for XS-derived opening-state traces. Leave broad
  `debug-logging-default` for sparse shared diagnostics.
- For multi-player debug runs, encode the player number into single-value log
  payloads as `player * 1000000 + value`. Example: `5060060` means player 5,
  payload `60060`.
- Be careful with performance and log size; do not run logging every rule pass.

Project log cleanup helper:

```powershell
python -m aoe2_ai_lab clean-logs --keep-latest 3
python -m aoe2_ai_lab clean-logs --keep-latest 3 --delete
```

The command preserves the newest timestamped DE log folders, then proposes older
run folders and older `SlowLog` text files for deletion. Without `--delete`, it
is a dry run.

## XS Data Files

Source: Forgotten Empires XS scripting reference; AoE2DE UGC Guide XS
programmer reference.

XS can create profile-local `.xsdat` files with `xsCreateFile`. These files are
not plain text logs by default; they are typed data streams. The writer chooses
the stream layout by calling functions such as:

```xs
xsWriteString("label");
xsWriteInt(25);
xsWriteFloat(12.34);
xsWriteVector(vector(2.0, 2.0, 2.0));
```

XS reads the same stream back with matching typed calls:

```xs
string label = xsReadString();
int value = xsReadInt();
float amount = xsReadFloat();
vector position = xsReadVector();
```

Implications for external parsing:

- `.xsdat` is machine-readable only if we define and preserve a schema.
- A parser should not guess arbitrary `.xsdat` structure. It should parse a
  project-owned format such as records of `(tag string, player int, time int,
  unit int, x float, y float, targetX float, targetY float, group int)`.
- If we want text-like output, write string records intentionally and parse them
  as string entries; otherwise prefer fixed typed records for easier validation.
- Files are limited to about 1 MB, so XS data logging must be gated and scoped.
- `.xsdat` creation uses the current scenario/random-map derived filename and is
  unique to each player profile. Look under the player profile area after a test
  run, not only in the AI folder.

Project rule:

- Use `up-log-data` for normal noisy AI debugging.
- Use `.xsdat` only when chat/log formatting is too limited and we need actual
  unit state from XS, such as unit positions, move targets, group IDs, or target
  unit IDs.
- If we add `.xsdat`, add the XS writer and Python parser together so the stream
  schema is explicit and testable.
- Current `sample_ai` finding: an AI-loaded XS function called through
  `xs-script-call` can execute `xsChatData`, but `xsCreateFile(false)` returns
  false and no `.xsdat` is created under the DE user folder when called without
  setting XS context player first.
- AoE2 DE AI XS patch notes say file storage from AI XS requires
  `xsSetContextPlayer(playerNumber)` before opening/writing the file and
  `xsSetContextPlayer(-1)` before closing/resetting. Test this before declaring
  AI-context `.xsdat` unavailable.

## XS Library References

Source: mardaravicius `aoe2de_xslibs`
(`https://github.com/mardaravicius/aoe2de_xslibs`).

This repository provides reusable XS libraries for AoE2 DE, including:

- dynamic lists for `int`, `float`, `bool`, `string`, and `vector`
- dictionary/map variants across primitive key/value types
- bitwise helper functions
- Mersenne Twister random-number helpers

Usage patterns from the repo:

- Place generated `.xs` files in an AoE2-loadable `resources\_common\xs`
  folder.
- Include them from another XS script with normal XS syntax:

```xs
include "intList.xs";
include "intIntDict.xs";
include "binaryFunctions.xs";
```

- Use `xsChatData` and library `ToString` helpers for readable diagnostics.

Project note:

- This repo is useful for XS style, data structures, stringifying debug state,
  and avoiding hand-written list/dictionary logic.
- It does not currently document or demonstrate `.xsdat` file I/O, so keep using
  the official XS file I/O reference for `xsCreateFile`, `xsWrite*`, and
  `xsRead*`.
- General XS references include functions that may not be accepted in AI
  `xs-script-call` context. In `sample_ai` testing, `xsGetUnitTargetId(...)`
  caused an AI XS parse failure, so the project linter blocks it. Prefer
  AI-specific patch notes or in-game validation before using new XS functions in
  AI scripts.
- AI `include` directives should include the `.xs` file extension. The validator
  reports `include-missing-xs-extension` for quoted include targets without it.
- `xs-script-call` can only call included XS functions that take no parameters.
  Package validation reports `xs-script-call-parameterized-function` when a
  reachable AI script calls an included XS function that has parameters.

## Escrow Goal Arguments

Source: AoE2 AI Scripting Encyclopedia, `up-can-build`; local DE AIScript logs.

AIRef documents the first `up-can-build` argument as an escrow goal ID and says
literal `0` can mean without escrow:

```lisp
(up-can-build 0 c: house)
```

In DE with AIScript logging enabled, this can emit:

```text
[sample_ai]: (up-can-build): Invalid goal used (0)
```

Project rule:

- Define `with-escrow` as `0` and `without-escrow` as `1`.
- Initialize a real goal, such as `goal-build-escrow-state`, to
  `without-escrow`.
- Use that goal in `up-can-build` / related DUC commands instead of literal
  `0` when we want clean DE logs.
- The linter flags `(up-can-build 0 ...)` because this warning can drown out
  useful `up-log-data` output.
- This is not treated as authoritative for imported community AIs. AIRef
  documents literal `0` as valid for `EscrowGoalId`, so the package validator's
  `corpus` profile suppresses this warning until a targeted in-game test proves
  whether the DE log message is harmless or indicates real behavior.

## Binary-Observed Strategic Numbers

Source: local DE binary string extracts; AIRef strategic-number version table.

Some `sn-target-evaluation-*` names appear in
`docs/extracted/raw/aoe2de/aoe2de-strategic-number-strings.txt`, but AIRef's
version table marks them as non-DE/AoE1. The validator treats these as known
strategic-number identifiers so imported community AIs are not flagged for
missing `defconst`s. sample-corpus uses these examples:

- `sn-target-evaluation-ally-proximity`
- `sn-target-evaluation-damage-capability`
- `sn-target-evaluation-hitpoints`
- `sn-target-evaluation-range`

This only proves the names are present in the DE binary string set. It does not
prove the behavior of each SN, so keep behavior-sensitive usage in the
needs-test bucket until an isolated in-game probe confirms it.

## Villager Retasking Model

Source: AoE2 AI Scripting Encyclopedia, Helpful Info.

Villager retasking is not purely script-driven. The engine can retask villagers
when:

- gatherer percentage SNs require another resource,
- the villager cannot reach the current target,
- a building finishes,
- a villager has just been trained,
- a villager is attacked.

Implications for opening scripts:

- New villagers and house builders are high-risk retask points.
- If food gatherer SNs are enabled while multiple herdables are near the TC,
  the engine may make a decision before our DUC correction runs.
- During one-herdable staging, keep generic food gathering suppressed and give
  non-builder villagers a temporary non-food task, such as a nearby straggler,
  until the active herdable is confirmed under the TC.
- After a building completes, explicitly retask its builder if the build order
  depends on that villager's next job.

## Initial SN Defaults To Consider

The community reference recommends overriding several awkward defaults early in
every AI. Consider an initialization module that sets these once:

```lisp
(defrule
    (true)
=>
    (set-strategic-number sn-cap-civilian-builders 200)
    (set-strategic-number sn-consecutive-idle-unit-limit 1)
    (set-strategic-number sn-do-not-scale-for-difficulty-level 1)
    (set-strategic-number sn-enable-boar-hunting 1)
    (set-strategic-number sn-enable-offensive-priority 1)
    (set-strategic-number sn-enable-patrol-attack 1)
    (set-strategic-number sn-initial-exploration-required 0)
    (set-strategic-number sn-maximum-fish-boat-drop-distance 30)
    (set-strategic-number sn-maximum-food-drop-distance 20)
    (set-strategic-number sn-maximum-gold-drop-distance 20)
    (set-strategic-number sn-maximum-hunt-drop-distance 30)
    (set-strategic-number sn-maximum-stone-drop-distance 20)
    (set-strategic-number sn-scale-minimum-attack-group-size 0)
    (set-strategic-number sn-task-ungrouped-soldiers 0)
    (set-strategic-number sn-zero-priority-distance 255)
    (set-strategic-number sn-dropsite-separation-distance 3)
    (disable-self)
)
```

Notes:

- `sn-initial-exploration-required 0` prevents early building delays on larger
  maps.
- `sn-enable-boar-hunting 1` allows boar and deer hunting.
- `sn-enable-offensive-priority 1` is required for offense priorities to matter.
- `sn-enable-patrol-attack 1` helps soldiers engage along the path to targets.
- `sn-task-ungrouped-soldiers 0` avoids idle military wandering away from town.
- `sn-zero-priority-distance 255` avoids distance-based target priority
  surprises.
- `sn-dropsite-separation-distance 3` makes resource drop placement less rigid.
- `sn-gate-type-for-wall 1` is mainly a Return of Rome gate concern, not a
  default AoE2 DE requirement.

## Command Parameters And Operators

Commands take 0 to 4 parameters. Reference command pages list parameter
direction and type.

Parameter direction:

- `in`: value consumed by command
- `out`: value written by command, usually a goal
- `io`: value read and written

Parameter type:

- `Const`: constant value or defconst
- `Goal`: goal ID
- `Sn`: strategic number
- `Player`: player selector
- `Text`: quoted string
- `Op`: operator whose type controls the next value

Operator prefixes matter:

- Constant compare: `>`, `<`, `==`, or explicit `c:>`
- Goal compare: `g:>`
- Strategic number compare: `s:>`
- Math operators need explicit type prefixes, such as `c:+`, `g:+`, `s:+`.
- `typeOp` values are `c:`, `g:`, or `s:` and tell commands how to interpret
  the next argument.

When adding linter rules, validate arity and operator/value compatibility
against command metadata where possible.

Parser-backed diagnostics should attach exact token spans whenever a command
argument is known. Prefer the parsed expression's command-head span for arity
and role errors, and the argument atom span for bad parameter values. The CLI
and editor extension use these spans for precise squiggles and fall back to
line-text heuristics only when older checks do not provide structured spans.

Direct `UnitId`, `BuildingId`, `ObjectId`, `TechId`, and `ClassId` slots are
validated against local DE reference inventories when the argument is a literal
symbol. Numeric IDs, reachable `defconst`s, and dynamic typed sources such as
`g:`/`s:` operands remain valid because they cannot be resolved statically with
the same certainty. Object aliases mentioned in inventory notes, such as
`villager-wood` and `trebuchet-set` in "Can be counted with ..." notes, are
treated as documented object names for counting and typed constant slots. The
validator also accepts `villager-food`, sourced from the bundled AoE2 AiScript
unit-id data as id 978, because AIRef omits that aggregate food-gatherer alias
while documenting the other gatherer aliases.

The local non-DE object, tech, and strategic-number archives are used for
explanation, not validation. If a script uses an archived object or tech symbol
in a DE-validated slot, the validator still reports `command-argument-mismatch`,
but the message identifies the symbol as archived non-DE instead of simply
unknown. Archived strategic numbers similarly remain `undefined-strategic-number`
warnings with a non-DE archive explanation. The same archive explanation is
used for archived symbols that appear after a generic `c:` typed constant
prefix.

`map-type` is validated against the local MapType registry plus narrow
supplements for values seen in modern DE scripts where the scraped registry is
behind the game, currently `custom`. `michi` is observed in community AI
scripts, but the local docs found so far point to Michi detection through the
RMS `ai_info_map_type` Michi flag / `UP-MICHI-STYLE` rather than a documented
standalone MapType value, so `(map-type michi)` remains a warning until verified
in game or documentation.

Documented value-family constants such as attack stances are accepted after
`c:` without requiring local `defconst`s. Scraped value-family names ending in
`*`, such as `scout-cavalry-class*`, are also available through their plain
alias (`scout-cavalry-class`) when used as built-in class constants.

Command-specific argument rules are also allowed when the command documentation
is explicit. For example, `up-set-placement-data`, `up-get-player-color`,
`up-get-upgrade-id`, `up-store-player-chat`, and `up-store-player-name` reject
`any-*` and `every-*` player wildcards in their `PlayerNumber` slots. The same
restriction is enforced for `up-get-player-fact` only when used as an action;
use an exact player, `my-player-number`, `scenario-player-#`, `lobby-player-#`,
or a `this-any-*` rule variable instead.
`up-find-player-flare` has a different documented restriction: `any-*` is
allowed, but `this-any-*` and `every-*` are reported because flare ownership
does not identify the actual sender reliably.

## Logical Operators

Supported logical commands:

- `not`: one nested fact must be false
- `and`: both nested facts must be true
- `nand`: at least one nested fact must be false
- `or`: at least one nested fact must be true
- `nor`: both nested facts must be false
- `xor`: exactly one nested fact must be true
- `xnor`: both nested facts match

Important syntax rule: binary logical operators accept exactly two facts. For
three or more alternatives, nest operators.

Correct pattern:

```lisp
(or
    (players-civ target-player incan)
    (or
        (players-civ target-player mayan)
        (players-civ target-player aztec)
    )
)
```

Linter opportunities:

- Count logical operators toward rule element limits.
- Prefer indentation that makes nesting obvious.

Current linter behavior:

- `empty-fact` reports rules that have no facts before `=>`.
- `empty-action` reports rules that have no actions after `=>`.
- `logical-operator-arity-mismatch` reports `not` with anything other than one
  direct child fact.
- `logical-operator-arity-mismatch` reports `and`, `or`, `nand`, `nor`, `xor`,
  and `xnor` with anything other than two direct child facts.
- Multi-line logical blocks are scanned as rule fragments, because the parser
  preserves some multi-line expressions as line fragments for compatibility.

## Limits Worth Designing Around

DE limits from the community reference:

- Rules: 10,000
- Elements per rule: 32 in DE, 16 in UserPatch
- Goals: 1 to 512
- Strategic numbers: 0 to 511
- Timers: 1 to 50
- Defconst values: observed signed 32-bit integer range, or a text string
- Goal/SN values: signed 32-bit integer range
- Taunts: 1 to 255
- Characters per line: 255, including comments
- Nested file loads: 10
- DUC local search list: 240
- DUC remote search list: 40

Engineering defaults for this repo:

- Keep lines under 120 chars in source, even though the game allows 255.
- Try to keep rules under 16 elements unless DE-only behavior benefits from the
  larger 32-element limit.
- Use named defconsts for every goal and custom enum.
- Reserve goal ranges by subsystem once the AI grows.
- Add linter checks before adding large strategy modules.

## Practical Rule Patterns

Initialization:

```lisp
(defrule
    (true)
=>
    (set-goal goal-some-state state-ready)
    (disable-self)
)
```

State transition:

```lisp
(defrule
    (current-age == feudal-age)
    (goal goal-opening opening-dark-age-eco)
=>
    (set-goal goal-opening opening-feudal-archers)
    (disable-self)
)
```

Production loop:

```lisp
(defrule
    (current-age >= feudal-age)
    (unit-type-count-total archer-line < 20)
    (can-train archer)
=>
    (train archer)
)
```

Building loop:

```lisp
(defrule
    (current-age == feudal-age)
    (building-type-count-total archery-range < 2)
    (can-build archery-range)
=>
    (build archery-range)
)
```

Threat response:

```lisp
(defrule
    (players-unit-type-count any-enemy scout-cavalry-line > 3)
    (unit-type-count-total spearman-line < 6)
    (can-train spearman-line)
=>
    (train spearman-line)
)
```

Avoid:

- Unguarded chat rules.
- Unguarded expensive commands that run every pass.
- One-shot setup rules without `disable-self`.
- Strategy transitions that can flip back and forth every script pass.
- Reusing a goal ID for unrelated concepts.

## Lessons From The HD AI Example

The HD AI script is large and heavily state-driven. Patterns worth borrowing:

- It defines named constants for goal IDs and strategy/unit state.
- It uses goals to track opening, enemy behavior, unit composition, resource
  control, attack intent, and special-case map/civ conditions.
- It changes strategy based on age, enemy population, enemy buildings, map type,
  randomization, taunts, team position, and civilization.
- It frequently uses `disable-self` for one-time choices.
- It uses chat messages as debugging/visibility for selected strategy changes.
- It has many civ-specific and map-specific branches; those should be modular in
  this repo rather than allowed to accumulate in one huge file.

Future architecture should split the same broad concerns into explicit modules:

- `init`: defaults, difficulty handling, constants
- `opening`: dark-age economy and age-up triggers
- `scouting`: exploration, sheep/boar/deer behavior, DUC later if needed
- `economy`: gatherer percentages, dropsites, farms, TCs, market use
- `military-production`: unit-line decisions and production caps
- `threat-response`: counters based on observed enemy units/buildings
- `attack`: group sizing, timing, priorities, target selection
- `civ`: civilization-specific choices
- `map`: water, nomad, arena/closed-map, and team-position behavior
- `debug`: controlled chat/status output

## Linter Roadmap

Useful checks to add to `aoe2_ai_lab`:

- Max line length below 255.
- Balanced parentheses with rule-aware diagnostics.
- `defrule` must contain `=>`.
- Preprocessor conditional nesting depth above 50.
- Empty facts/actions.
- Repeated chat without `disable-self`, timer, or goal guard.
- Logical operator child count.
- Rule element count.
- Duplicate `defconst` names and duplicate goal IDs.
- Numeric `defconst` values outside signed 16-bit range.
- Missing symbolic constants after typed prefixes such as `c:`.
- Goal IDs outside 1-512.
- Suspicious direct numeric goal IDs where a defconst should be used.
- `set-goal` missing goal/value.
- `set-strategic-number` missing SN/value.
- Unknown command names once a command metadata list exists.
- Optional DE-vs-UP compatibility mode for 16 vs 32 element rule limits.

## Research Workflow

When scripting:

1. Check the command page for exact syntax and parameter types.
2. Check parameter pages for valid constants and special cases.
3. Check SN index before changing a strategic number.
4. Add a small rule or module.
5. Run the linter.
6. Test in-game with a fixed map/civ/opponent setup.
7. Record the result in an experiment log before changing more behavior.
