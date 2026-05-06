# `enable-wall-placement`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-enable-wall-placement"></a>

## `enable-wall-placement`

- Kind: `command`
- Detail: Action - Buildings, Walls & Gates

Syntax: `(enable-wall-placement <Perimeter>)`

Enables wall placement for the given perimeter, either perimeter 1 or perimeter 2. Walls cannot be built with the build-wall command at the given perimeter unless this command is used. Enabled wall placement causes the rest of the placement code to do some planning and place all structures at least one tile away from the future wall lines. If you are planning to build a wall, you have to explicitly define which perimeter wall you plan to use when the game starts. This is a one-time action and should be used during the initial setup. Perimeter 1 is usually between 10 and 20 tiles from the starting Town Center. Perimeter 2 is usually between 18 and 30 tiles from the starting Town Center.

[AIRef](https://airef.github.io/commands/commands-details.html#enable-wall-placement)

Completion insert text:

```text
(enable-wall-placement ${1:Perimeter})
```

