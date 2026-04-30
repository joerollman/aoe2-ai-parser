# `sell-commodity`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sell-commodity"></a>

## `sell-commodity`

- Kind: `command`
- Detail: Action - Economy, Trading

Syntax: `(sell-commodity <Commodity>)`

Sells one lot of a given commodity. The AI will sell 100 of the given commodity (wood, food, or stone) in return for gold at the current commodity-selling-price. The commodity selling price is the amount of gold that will be added to the gold stockpile when 100 of the specified commodity (wood, food, or stone) is sold. This price can range between 14 and infinity without Guilds, between 17 and infinity with Guilds, and between 19 and infinity when playing Saracens.

[AIRef](https://airef.github.io/commands/commands-details.html#sell-commodity)

Completion insert text:

```text
(sell-commodity ${1:Commodity})
```

