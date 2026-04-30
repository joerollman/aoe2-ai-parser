# `sheep-and-forage-too-far`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sheep-and-forage-too-far"></a>

## `sheep-and-forage-too-far`

- Kind: `command`
- Detail: Fact - Economy

Syntax: `(sheep-and-forage-too-far)`

Checks whether the computer player has any forage site(s) and/or sheep within 8 tiles of the drop-off location (Mill or Town Center). If not, this fact is true. To check if any resource is within a certain distance of a dropsite, you can use dropsite-min-distance instead, which is usually more flexible. You can check if the AI can currently see any particular resource with up-gaia-type-count.

[AIRef](https://airef.github.io/commands/commands-details.html#sheep-and-forage-too-far)

Completion insert text:

```text
(sheep-and-forage-too-far)
```

