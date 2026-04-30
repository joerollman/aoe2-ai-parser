# Offline Reference Map

This is the shortest path from a scripting question to the right local data.

## If The Token Looks Like...

### A command or fact-like rule token

Examples:

- `build`
- `set-strategic-number`
- `up-target-point`

Use:

- `resolve-reference <token>`
- expect `command-inventory` first unless the project has an observed
  `validated-command`

### A parameter or parameter family

Examples:

- `BuildingId`
- `AnyPlayer`
- `compareOp`

Use:

- `resolve-reference <token>`
- expect `parameter-inventory` or `value-entry`

### An enum/operator/value token

Examples:

- `action-garrison`
- `less-than`
- `villager-class`
- `position-self`
- `object-data-id`

Use:

- `resolve-reference <token> --kind value-entry`

Most of these come from:

- `DUCAction`
- `compareOp`
- `mathOp`
- `ClassId`
- `Resource`
- `FactId`
- `ActionId`
- `ObjectData`
- `PositionType`

### A strategic number

Examples:

- `sn-target-point-adjustment`

Use:

- `resolve-reference <token>`
- expect `strategic-number-inventory`

### An XS function

Examples:

- `xsChatData`
- `xsCreateFile`
- `xsGetUnitPosition`

Use:

- `resolve-reference <token> --kind xs-function-inventory`

### An XS constant

Examples:

- `cDarkAge`
- `cOriginVector`

Use:

- `resolve-reference <token> --kind xs-constant-inventory`

### An RMS guide topic

Examples:

- `Conditionals`
- `Math Expressions`
- `PLAYER_SETUP`

Use:

- `resolve-reference <token> --kind rms-topic-inventory`

### A unit, building, or projectile name

Examples:

- `Archer`
- `Town Center`

Use:

- `resolve-reference <token> --kind object-inventory`

### A technology

Examples:

- `Fletching`
- `Loom`

Use:

- `resolve-reference <token> --kind tech-inventory`

## If The Question Is About Behavior

Examples:

- how `up-build-line` behaves in this project
- what preconditions `up-target-point` needs
- what failed before with `up-build place-point`

Use:

- `resolve-reference <token>`
- prefer `validated-command`
- then inspect linked `project-command-note` if present

## If The Token Is Missing From Structured Inventories

Use:

- `search-registry <token> --kind binary-token`
- `search-registry <token> --kind binary-family`

That is evidence only, not validated behavior.
