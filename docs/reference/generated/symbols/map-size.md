# `map-size`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-map-size"></a>

## `map-size`

- Kind: `command`
- Detail: Fact - Game Info

Syntax: `(map-size <MapSize>)`

Checks the map size. The map sizes can be tiny, small, medium, normal, large, giant, or ludikris (DE only). To get the actual dimensions of the map, you can use up-get-point with position-map-size, which will store the coordinates of the rightmost point on the map.

[AIRef](https://airef.github.io/commands/commands-details.html#map-size)

Completion insert text:

```text
(map-size ${1:MapSize})
```

