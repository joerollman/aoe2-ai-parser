# `up-store-map-name`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-store-map-name"></a>

## `up-store-map-name`

- Kind: `command`
- Detail: Action - Game Info, Text Data

Syntax: `(up-store-map-name <Option>)`

Store the current map name in the internal buffer. For rms, this is the filename of the map. However, if the map is a dynamic loader, such as Full Random, Random Land Map, or Blind Random, this will be the loader name instead of the actual map name. For scenarios, this will be the original save filename instead of the current filename. The buffer can be referenced by the chat-data commands using %s instead of %d with c: 7031232 (7031232 cannot be stored in a defconst). This buffer is shared by all AIs, so please store data before using it in a rule pass. If the Option parameter is set to 1, the map name will be stored with the file extension in the name. If the Option parameter is set to 0, the map name will be stored without the file extension in the name.

[AIRef](https://airef.github.io/commands/commands-details.html#up-store-map-name)

Completion insert text:

```text
(up-store-map-name ${1:Option})
```

