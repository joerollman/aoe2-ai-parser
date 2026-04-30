# Command Reference

This is the project-owned command reference for `.per` scripting. It is scoped
to commands we use or are actively testing. Use AIRef for the full command list,
then update this file with project-specific observations.

Status labels:

- `documented`: copied from public docs but not independently tested here.
- `observed`: confirmed by project in-game tests.
- `needs-test`: likely behavior that needs an isolated command probe.
- `risky`: easy to misuse or known to produce misleading results.

## Source Evidence

Use these local extracted sources before guessing names:

- `docs/extracted/raw/aoe2de/userpatch-sections/userpatch-sections.md`: best category
  index for UserPatch constants and UP command names.
- `docs/extracted/raw/aoe2de/aoe2de-ai-identifiers.txt`: broad list of identifier-shaped
  strings found in the local executable.
- `docs/extracted/raw/aoe2de/aoe2de-xs-function-signatures.txt`: best source for XS
  candidate function names and signatures.
- `docs/extracted/raw/aoe2de/aoe2de-ai-diagnostic-messages.txt`: useful runtime/parser
  diagnostic strings to search when debugging.

Evidence levels:

1. `binary-present`: string exists in the local executable.
2. `documented`: public/community docs describe it.
3. `parser-accepted`: installed script is accepted by the game.
4. `observed`: isolated in-game probe confirms behavior.

Do not mark command behavior `observed` from binary strings alone.

## State Commands

### defconst

Status: `observed`

Defines a symbolic name.

Project rules:

- Resolve the token locally before adding a new `defconst`. If the offline
  inventories already expose a built-in constant such as `villager-class`, use
  that name directly instead of creating a repo-local alias for the same id.
- Define every non-built-in identifier copied from another script.
- Missing constants commonly produce `ERR2005: Invalid identifier`.
- Constants for `c:` typed arguments, position names, object-data names, action
  IDs, and strategic numbers should live in the root package `.per`.

Example:

```lisp
(defconst livestock-class 958)
(defconst object-data-id 0)
```

### set-goal

Status: `observed`

Writes a value into a goal.

Project rules:

- Use named goal constants, not raw numeric IDs.
- Reserve consecutive goal ranges for multi-goal writers.

Example:

```lisp
(set-goal goal-sheep-control sheep-control-select)
```

### goal

Status: `observed`

Fact that checks whether a goal equals a value.

Example:

```lisp
(goal goal-sheep-control sheep-control-active)
```

### up-compare-goal

Status: `observed`

Compares a goal to a constant or typed value.

Examples:

```lisp
(up-compare-goal goal-active-sheep-id != -1)
(up-compare-goal goal-active-sheep-distance <= herdable-ready-distance)
```

### up-modify-goal

Status: `observed`

Assigns or modifies a goal using a typed operator.

Project rules:

- Use `g:=` to copy another goal.
- Use `c:+`, `g:+`, `c:*`, etc. with explicit type prefixes.

Example:

```lisp
(up-modify-goal active-eat-point-x g:= west-eat-point-x)
(up-modify-goal active-eat-point-x c:+ -2)
```

## Strategic Number Commands

### Shipped Suppression Reference: `E3-p2.per`

Status: `shipped-reference`

The DE install includes a small AI at:

```text
resources/_common/ai/E3-p2.per
```

It was built for an E3 showcase scenario. Its `.ai` descriptor is empty, and
the `.per` file is only about 2 KB.

Important finding:

- `E3-p2.per` is not an empty script. It suppresses normal behavior by setting
  strategic numbers, then leaves only scenario score/taunt signal logic active.

Villager suppression pattern:

```lisp
(set-strategic-number sn-maximum-food-drop-distance 0)
(set-strategic-number sn-maximum-wood-drop-distance 0)
(set-strategic-number sn-maximum-gold-drop-distance 0)
(set-strategic-number sn-maximum-hunt-drop-distance 0)
(set-strategic-number sn-maximum-stone-drop-distance 0)
(set-strategic-number sn-food-gatherer-percentage 0)
(set-strategic-number sn-wood-gatherer-percentage 0)
(set-strategic-number sn-gold-gatherer-percentage 0)
(set-strategic-number sn-stone-gatherer-percentage 0)
(set-strategic-number sn-cap-civilian-explorers 0)
(set-strategic-number sn-percent-civilian-explorers 0)
```

Military/exploration suppression pattern:

```lisp
(set-strategic-number sn-number-explore-groups 0)
(set-strategic-number sn-percent-attack-soldiers 0)
(set-strategic-number sn-task-ungrouped-soldiers 0)
(set-strategic-number sn-number-attack-groups 0)
(set-strategic-number sn-total-number-explorers 0)
(set-strategic-number sn-consecutive-idle-unit-limit 1)
(set-strategic-number sn-initial-attack-delay-type 0)
```

Other SNs used by `E3-p2.per`:

- `sn-percent-enemy-sighted-response 50`
- `sn-enemy-sighted-response-distance 12`
- `sn-sentry-distance 10`
- `sn-minimum-town-size 1`
- `sn-maximum-town-size 1`

Project use:

- Use this as a baseline suppression reference for probe AIs.
- It may not be sufficient for all default opening behavior in random-map
  starts; our probes have still seen villagers retask unless the fixture removes
  villagers or applies repeated explicit stops.
- Test borrowed SNs in isolation before adding them to `p`.

### set-strategic-number

Status: `observed`

Sets a built-in AI engine control.

Project rules:

- Define SN names with `defconst`.
- Use SNs as engine controls, not arbitrary custom storage.
- During precise opening tests, suppress generic exploration and gatherers.

Example:

```lisp
(set-strategic-number sn-percent-civilian-gatherers 0)
```


### sn-target-point-adjustment

Status: `observed`

Community-sourced note: set this SN to `5` immediately before
`up-target-point` to adjust the exact point targeted within the destination
tile.

Second community-sourced note: for more exact placement, use a "precise point".
Coordinates are scaled by `100`: target goals `(8342, 2163)` represent map
location `(83.42, 21.63)`.

Important correction from project probes:

- `sn-target-point-adjustment` must be defined as `292` in our DE runtime.
- The value inferred from the local executable string order, `294`, is wrong in
  practice. With `294`, point goals such as `8400,5300` are treated as normal
  tile coordinates and converted to internal move targets `840000,530000`.
- With `292` set to `6`, `up-target-point` treats point goals as already
  precise. A target `8400,5300` becomes internal move target `8400,5300`.
- Reset precise blocks back to `5` (`adjust-middle`), matching sample-corpus,
  sample-corpus, and sample-corpus. Do not reset to `0` unless testing default behavior.
- Both direct precise targeting and `up-set-precise-target-point` worked in the
  scout probe. Direct precise targeting also worked for the sheep `-1.5,+1.5`
  probe.

Local evidence:

- Name exists in the executable's UserPatch Extended Strategic Numbers section.
- Community scripts define it as `292`.
- Project probe `precise_point_probe` confirmed that `292` is the effective DE
  runtime value in our install. The inferred value `294` did not activate
  precise interpretation.

Project rules:

- Define it as `(defconst sn-target-point-adjustment 292)`.
- Define `(defconst adjust-middle 5)` and `(defconst adjust-precise 6)`.
- Set it before commands that need the corresponding point interpretation.
- Reset it to `adjust-middle` after the precise-point block unless following
  commands intentionally need precise interpretation.
- Keep precise points integer-only. For example, tile offset `(-1, +1)` becomes
  precise offset `(-100, +100)` after multiplying the base point by `100`.
- Use direct precise movement when issuing a point move:
  `(up-target-point precise-point-x action-move -1 -1)`.
- Use `up-set-precise-target-point` when a search/filter needs the active
  target point in precise coordinates, or when testing target-point state.

Example:

```lisp
(set-strategic-number sn-target-point-adjustment 5)
(up-target-point active-eat-point-x action-move -1 -1)
```

Precise point example:

```lisp
(up-modify-goal active-eat-point-x c:* 100)
(up-modify-goal active-eat-point-y c:* 100)
(up-modify-goal active-eat-point-x c:+ -100)
(up-modify-goal active-eat-point-y c:+ 100)
(set-strategic-number sn-target-point-adjustment adjust-precise)
(up-target-point active-eat-point-x action-move -1 -1)
(set-strategic-number sn-target-point-adjustment adjust-middle)
```

## Timer Commands

### enable-timer

Status: `observed`

Starts or restarts a timer.

Example:

```lisp
(enable-timer sheep-retask-timer 2)
```

### disable-timer

Status: `observed`

Disables a timer before restarting or stopping it.

Example:

```lisp
(disable-timer sheep-retask-timer)
```

### timer-triggered

Status: `observed`

Fact that gates a rule on a timer.

Project rules:

- Use timers around repeated DUC searches and retask logic.
- Do not run expensive searches every rule pass.

## Point Commands

### Building Side Offsets

Status: `partly-observed`

AoE2 uses map coordinates that do not align with the rendered isometric screen
directions. Around a building anchor point, tested TC offsets map as follows:

- visual south: `x - 1, y + 1`
- visual east: `x + 1, y + 1`
- visual west: `x - 1, y - 1`
- inferred visual north: `x + 1, y - 1`

The Town Center is a 4x4 building. For a side point farther from the center,
use half the building dimension as the offset magnitude. For the TC:

- south side: `x - 2, y + 2`
- east side: `x + 2, y + 2`
- west side: `x - 2, y - 2`
- north side: `x + 2, y - 2`

For an `n x n` building, the inferred side-offset magnitude is `n / 2`:

- south side: `x - n/2, y + n/2`
- east side: `x + n/2, y + n/2`
- west side: `x - n/2, y - n/2`
- north side: `x + n/2, y - n/2`

Notes:

- This was tested with sheep movement around the TC using
  `rms/rms_test_single_sheep.rms` and `ai/basic_command_probe`.
- For odd-sized buildings, test whether integer offsets should round down,
  round up, or use a nearby passable perimeter tile.
- Gates are not `n x n` and should be treated as a separate special case.

### up-get-point

Status: `needs-test`

Writes a point into two consecutive goals: x, then y.

Known position constants used by this project:

- `position-center`
- `position-self`
- `position-object`
- `position-curr-object`

Project rules:

- Use goal `41+`.
- Reserve the next goal for the y coordinate.
- Define copied position constants locally or the game can report `ERR2005`.

Open questions:

- How closely `position-self` corresponds to the visible TC center.
- Whether `position-object` for a TC differs from `position-self`.
- Whether livestock object points are coarse anchors or visible positions.

Probe:

- `ai/command_probe` logs center/self/TC/livestock points.

Example:

```lisp
(up-get-point position-self point-x)
```

### up-set-target-point

Status: `needs-test`

Sets the active DUC target point used by distance filtering and searches.

Expert-sourced note, untested:

- For point building placement, set this to the intended build point
  immediately before calling `up-build` with `place-point`.
- This may prevent `up-build` from using a stale or implicit target point.
- Needs an isolated placement probe before being marked `observed`.

Example:

```lisp
(up-set-target-point point-self-x)
```

Build placement sketch:

```lisp
(up-set-target-point build-point-x)
(up-build place-point goal-build-escrow-state c: house)
```

Observed project warning:

- Do not pass the coordinate goal as the second argument, as in
  `(up-build place-point point-x c: house)`. DE interprets that value as escrow
  state, logs `up-build: Invalid escrow state (...)`, and falls back to generic
  placement.
- The valid `place-point` shape is to set the target point first, then pass an
  escrow state or escrow-state goal as the third argument:
  `(up-set-target-point point-x)` followed by
  `(up-build place-point 0 c: house)` or
  `(up-build place-point goal-build-escrow-state c: house)`.
- For exact starting-house placement, prefer `up-build-line point-x point-x`.
  `house_placement_probe` showed `up-build place-point` was unreliable in the
  isolated two-house start test, while `up-build-line` placed for all players.

### up-build-line

Status: `observed`

Requests a building at a point or along a line. For a single exact point, pass
the same point block for start and end.

Validated project pattern:

```lisp
(up-assign-builders c: house c: 1)
(up-reset-placement c: house)
(up-build-line point-x point-x c: house)
```

Project notes:

- Use `up-can-build-line point-x point-x c: house` as the build-stage guard
  after the target point has been computed.
- `house_placement_probe build 6` validated this for starting houses across
  eight players on the blank test RMS.
- `up-can-build-line` only validates the candidate point against the current
  world. If multiple build commands are issued in sequence, the second command
  can still be too close to the first requested foundation. Save prior build
  points and check separation with `up-get-point-distance` before issuing the
  next `up-build-line`.
- After issuing multiple build commands, wait for the expected pending count,
  e.g. `(up-pending-objects c: house c:>= 2)`, before advancing into unrelated
  task logic.

### up-set-precise-target-point

Status: `observed`

Sets the active DUC target point using precise coordinates scaled by `100`.

Local evidence:

- The command name exists in the local executable command table.
- sample-corpus, sample-corpus, and sample-corpus use it in micro/search routines.
- sample-corpus comments label `object-data-precise-x` as `coordinate * 100`.

Project interpretation:

- Use with `sn-target-point-adjustment 6`.
- Point goals should contain scaled coordinates, e.g. `(8342,2163)` for
  `(83.42,21.63)`.
- `precise_point_probe` confirmed that setting a precise target point, then
  calling `(up-target-point 0 action-move -1 -1)`, produces the intended
  internal precise move target for a scout.
- Direct precise `(up-target-point precise-x action-move -1 -1)` also works
  and is simpler for movement when the point is already computed.

Example:

```lisp
(set-strategic-number sn-target-point-adjustment adjust-precise)
(up-set-precise-target-point precise-point-x)
(up-target-point 0 action-move -1 -1)
(set-strategic-number sn-target-point-adjustment adjust-middle)
```

### up-bound-precise-point

Status: `needs-test`

Appears to clamp or project a precise point relative to map/building/pathing
constraints.

Local evidence:

- The command name exists in the local executable command table.
- sample-corpus uses it after computing a precise point and before
  `up-set-precise-target-point`.

Observed community-AI pattern:

```lisp
(up-lerp-tiles gl-temp-x gl-position-self-x c: -75)
(up-bound-precise-point gl-temp-x 1 c: 20)
(up-set-precise-target-point gl-temp-x)
```

Open questions:

- Meaning of the second argument.
- Whether the third argument is a max bound/radius.
- Whether it is needed for livestock placement or only for combat/resource
  micro.

### up-get-point-distance

Status: `partially-tested`

Writes the distance between two point blocks into a goal.

Example:

```lisp
(up-get-point-distance scout-point-x gaia-point-x goal-scout-gaia-distance)
```

Project notes:

- If the measured distance drives branching and is also logged, branch on this
  stored goal with `up-compare-goal`.
- Build 42 of `basic_command_probe` showed that recomputing the same decision
  with `up-point-distance` can disagree or fail in a tie-sensitive livestock
  selector.

### up-point-distance

Status: `needs-test`

Fact that compares distance between point blocks directly.

Project note:

- Treat this as unvalidated for exact/tie-sensitive decisions.
- Prefer `up-get-point-distance` plus `up-compare-goal` when the exact measured
  distance needs to drive the branch.

Example:

```lisp
(up-point-distance tc-point-x gaia-point-x <= start-herdable-near-tc-distance)
```

Typed goal comparison example:

```lisp
(up-point-distance gaia-point-x center-point-x g:< goal-self-center-distance)
```

## DUC Search Commands

### up-reset-search

Status: `observed`

Resets selected DUC search lists.

Project rules:

- After reset, repopulate `search-local` before any target command.
- Use `up-reset-filters` too unless preserving filters intentionally.

Example:

```lisp
(up-reset-search 1 1 1 1)
```

### up-full-reset-search

Status: `observed`

Full search reset.

Project rule:

- Treat it like a reset that clears local scope. Add/find/set a local object
  before targeting.

### up-reset-filters

Status: `observed`

Clears DUC filters.

Project rule:

- Filters persist; clear them at the start of independent searches.

### up-find-local

Status: `observed`

Finds own local objects into `search-local`.

Example:

```lisp
(up-find-local c: livestock-class c: 10)
```

### up-find-remote

Status: `observed`

Finds remote objects into `search-remote`.

Project use:

- Visible Gaia livestock for scout/villager pickup.

Example:

```lisp
(up-find-remote c: livestock-class c: 20)
```

### up-find-resource

Status: `observed`

Finds a resource object for selected local units to target.

Project use:

- Temporary straggler task while active herdable is not ready.

Example:

```lisp
(up-find-resource c: wood c: 1)
```

### up-clean-search

Status: `needs-test`

Sorts/cleans a search list by object data.

Project use:

- Sort livestock by distance after setting a target point.

Example:

```lisp
(up-clean-search search-local object-data-distance search-order-asc)
```

### up-remove-objects

Status: `risky`

Removes objects from a search list by object data comparison.

Project rules:

- After sorting, use `object-data-index != 0` to try to narrow to one object.
- Validate narrowing with `up-get-search-state` in command probes.
- Removing by active object ID is required before moving/stopping spare
  herdables.

Example:

```lisp
(up-remove-objects search-local object-data-index != 0)
```

### up-get-search-state

Status: `needs-test`

Writes four consecutive goals:

- local total
- local last search count
- remote total
- remote last search count

Project rules:

- Pass the first goal of a reserved four-goal block.
- Use goal `41+`.
- Do not put unrelated state in the next three goals.

Probe:

- `ai/command_probe` logs all four outputs after a livestock search.

Example:

```lisp
(up-get-search-state search-state-first)
```

### up-set-target-object

Status: `documented`

Selects an object from a search list as the current target object for later
object-data or point reads.

Documentation note:

- AIRef documents this as `Fact/Action`, not action-only.
- It can be used in either the facts or the actions section of a rule.
- If the provided index is invalid, the current target object remains unchanged.

Project warning:

- This does not necessarily shrink the whole search list. If only one object
  should receive a command, remove non-zero `object-data-index` entries first.
- Action-form use should normally follow retained evidence that the relevant
  search list exists, for example `up-find-local`, `up-set-group search-local`,
  or a passing fact-form `up-set-target-object search-local c: 0`.
- The project linter treats action-form `up-set-target-object` without retained
  evidence for that list as `unsafe-set-target-object`.
- Retained evidence is cleared only for the affected list when `up-reset-search`
  resets that list. `up-full-reset-search` clears both lists.
- When using it as a fact, a true result proves the indexed object exists in
  the referenced search list for that rule pass.

Example:

```lisp
(up-set-target-object search-local c: 0)
```

Fact-form example:

```lisp
(defrule
    (up-set-target-object search-local c: 0)
=>
    (up-get-object-data object-data-unique-id goal-target-id)
)
```

### up-set-target-by-id

Status: `observed`

Sets local target object by stored object ID.

Project use:

- Command exactly one active livestock object.

Example:

```lisp
(up-set-target-by-id g: goal-active-sheep-id)
```

### up-add-object-by-id

Status: `observed`

Adds an object by ID to a search list.

Project use:

- Put the active herdable in `search-remote` for villager targeting.

Example:

```lisp
(up-add-object-by-id search-remote g: goal-active-sheep-id)
```

## DUC Target Commands

### up-target-point

Status: `needs-test`

Orders local search objects to a point.

Project rules:

- Local list must be explicitly populated in the same rule after the most recent
  search reset.
- Use `action-move` for livestock point movement.
- Avoid `action-default` for livestock point movement.
- When only one object should move, save `object-data-id`, rebuild the local
  search list, then remove every object whose ID is not the saved ID:
  `up-remove-objects search-local object-data-id g:!= <id>`.
- For precise livestock movement, the same fresh-local-list rule matters. A
  successful probe selected the active sheep ID, rebuilt `search-local`,
  filtered with `object-data-id g:!= active-id`, then used precise
  `up-target-point`.
- Narrowing a search list by `object-data-index`, using only
  `up-set-target-by-id`, and rebuilding only with `up-add-object-by-id` all
  moved multiple livestock during project probes.
- Owned livestock can briefly follow each other even when only one sheep is the
  active target. Practical pattern: move the active sheep, then immediately
  select all livestock except the active ID and issue `action-stop` to the
  spares.
- For villager readiness gates after precise sheep movement, store a normal
  tile target point separately from the precise scaled movement target. Use the
  normal point with `up-get-point-distance`; use the precise point only for
  movement.
- `action-stop` is a valid target action in the local executable's UserPatch
  target-action registration table, and community AIs use
  `(up-target-point 0 action-stop -1 -1)` after selecting local units.

Example:

```lisp
(up-set-target-by-id g: goal-active-sheep-id)
(up-target-point active-eat-point-x action-move -1 -1)
```

TC transport note:

- When the TC itself is the local object, `up-set-target-point` followed by
  `up-target-point 0 action-gather -1 -1` can preset the TC target before a
  villager fully garrisons.
- In `tc_transport_probe` build `23`, this pre-garrison preset was the key
  difference that enabled controlled unload-side behavior. Earlier attempts
  that changed the TC target only after garrison did not work reliably.

Single-object livestock pattern:

```lisp
(up-find-local c: livestock-class c: 10)
(up-clean-search search-local object-data-distance search-order-asc)
(up-remove-objects search-local object-data-index != 0)
(up-set-target-object search-local c: 0)
(up-get-object-data object-data-id goal-active-sheep-id)
(up-full-reset-search)
(up-find-local c: livestock-class c: 10)
(up-remove-objects search-local object-data-id g:!= goal-active-sheep-id)
(up-target-point active-eat-point-x action-move -1 -1)
```

Move active livestock and stop spares:

```lisp
(up-find-local c: livestock-class c: 1)
(up-set-target-object search-local c: 0)
(up-get-object-data object-data-id goal-active-sheep-id)
(up-target-point active-eat-point-x action-move -1 -1)
(up-reset-search 1 1 0 0)
(up-reset-filters)
(up-find-local c: livestock-class c: 10)
(up-remove-objects search-local object-data-id g:== goal-active-sheep-id)
(up-target-point 0 action-stop -1 -1)
```

Stop selected local units:

```lisp
(up-find-local c: villager-class c: 10)
(up-target-point 0 action-stop -1 -1)
```

### up-target-objects

Status: `observed` for TC garrison; otherwise `needs-test`

Orders local search objects to remote target objects.

Project use:

- Villagers in `search-local`, active herdable in `search-remote`, then
  `action-default` to gather.
- Confirmed villager-to-TC garrison pattern:
  - local villager selected by unique id
  - `up-set-target-by-id <tc-id>`
  - `up-target-objects 1 action-garrison -1 -1`

Project rules:

- For real garrison, use object targeting. The local reference for
  `action-garrison` says point targeting is only move-equivalent.
- Keep the TC garrison path separate from unload-side experiments.

Example:

```lisp
(up-find-local c: villager-class c: 6)
(up-add-object-by-id search-remote g: goal-active-sheep-id)
(up-target-objects 0 action-default -1 -1)
```

TC garrison example:

```lisp
(up-full-reset-search)
(up-add-object-by-id search-local g: goal-villager-id)
(up-set-target-by-id g: goal-tc-id)
(up-target-objects 1 action-garrison -1 -1)
```

## Object Data Commands

### up-get-object-data

Status: `observed`

Writes data from the current target object into a goal.

Example:

```lisp
(up-get-object-data object-data-id goal-active-sheep-id)
```

### up-object-data

Status: `observed`

Fact that compares data from the current target object.

Project use:

- Check active herdable food/carry threshold.

Example:

```lisp
(up-object-data object-data-carry < herdable-stage-food-threshold)
```

## Counts And Production

### unit-type-count

Status: `observed`

Counts currently owned units of a type/class.

Example:

```lisp
(unit-type-count livestock-class > 0)
```

### building-type-count

Status: `observed`

Counts owned buildings of a type.

Example:

```lisp
(building-type-count house == 0)
```

### up-pending-objects

Status: `observed`

Checks pending object count.

Example:

```lisp
(up-pending-objects c: house c:< 2)
```

### can-train / train

Status: `observed`

Used for simple villager production.

Example:

```lisp
(defrule
    (can-train villager)
    (population-headroom > 1)
=>
    (train villager)
)
```

### up-can-build / build

Status: `observed`

Checks and requests construction.

Project rule:

- Do not use literal `0` as the escrow argument to `up-can-build`; DE logs
  `Invalid goal used (0)`. Use a real goal set to `without-escrow`.
- AIRef documents literal `0` as valid for `EscrowGoalId`, and community AIs
  use it heavily. Keep this as a default-profile project hygiene warning, not a
  corpus-profile package defect, until an isolated in-game test settles the
  behavior.

Example:

```lisp
(up-can-build goal-build-escrow-state c: house)
```

## Logging Commands

### chat-to-all

Status: `observed`

Visible in-game chat. Use only for sparse milestones.

### up-log-data

Status: `observed`

Writes to DE AIScript logs when launch flags enable AI logging.

Project rules:

- Prefer for noisy debug values.
- Keep messages scoped to the current test.
- Include package marker.

Example:

```lisp
(up-log-data 0 "sample_ai active sheep %d" g: goal-active-sheep-id)
```

## Scout Commands

### up-reset-scouts

Status: `observed`

Resets scout control groups before sending scout orders.

### up-send-scout

Status: `observed`

Sends configured scout group to a position.

Example:

```lisp
(up-send-scout group-type-land-explore position-self)
```

## Updating This Reference

When a command probe confirms behavior:

- Change status from `needs-test` to `observed`.
- Add the exact probe setup.
- Add the practical project rule.
- Add linter checks for recurring dangerous misuse.

## Verifying Candidate Strings

Unofficial references can disagree or lag behind DE patches. Before trusting a
new command, object-data name, launch option, or XS helper name, use three
evidence levels:

1. `scan-strings`: confirms the local executable contains the candidate string.
2. Lint/install: confirms our project syntax and constants are coherent.
3. In-game probe: confirms the parser accepts it and the behavior/log output is
   what we expect.

Example:

```powershell
$env:PYTHONPATH='src'
python -m aoe2_ai_lab scan-strings "C:\path\to\AoE2DE_s.exe" --query up-get-point
```

External dump option:

```powershell
strings.exe -nobanner -n 3 -o "C:\path\to\AoE2DE_s.exe" | findstr /i "up-get-point"
```

A string match is not enough to mark a command `observed`; it only moves the
candidate from "random community claim" to "present in this installed binary".
