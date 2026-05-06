# `map-type`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-map-type"></a>

## `map-type`

- Kind: `command`
- Detail: Fact - Game Info

Syntax: `(map-type <MapType>)`

Checks the map type. The map type is the map's name. See pMapType for a complete list of maps.For custom random maps, the map type is "custom_map" (yes, with the underscore). The exception is if the custom random map script uses ai_info_map_type. For example, if the random map script has ai_info_map_type ARABIA 0 0 0, then (map-type arabia) will be true instead of (map-type custom_map).

[AIRef](https://airef.github.io/commands/commands-details.html#map-type)

Completion insert text:

```text
(map-type ${1:MapType})
```

