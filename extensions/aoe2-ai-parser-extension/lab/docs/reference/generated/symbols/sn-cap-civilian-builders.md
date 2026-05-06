# `sn-cap-civilian-builders`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-sn-cap-civilian-builders"></a>

## `sn-cap-civilian-builders`

- Kind: `strategic-number`
- Detail: SN 4 - Buildings

Caps the number of builders allocated. Factored in after the percentage is calculated. Some previous documentation says this strategic number is ignored when set to -1, but using -1 has the same effect as setting the SN to 0. This is an SN that you should change from its default value. Set it high, like 200, but really any reasonably high number is fine. The default is 2, but there is no real reason to cap the number of builders your AI can use at once. The AI will only assign builders as necessary, so setting this SN to a huge number like 200 won't tell your AI to send all of its villagers to construct buildings. Instead, the AI will automatically assign one builder at minimum to every building foundation unless you place the building with up-build-line and you set up-assign-builders to -1 for that building beforehand (setting up-assign-builders to 0 still assigns one builder). Then, it will assign builders to that building type until the number for up-assign-builders is reached for that whole building type or sn-cap-civilian-builders is reached. For example, if you use (up-assign-builders c: farm c: 4) and you order two farms to be built, the AI will distribute four builders total to build those two farms, usually two to each farm. By default up-assign-builders is set to 1 for each building type. sn-percent-civilian-builders won't affect how many builders are assigned, so you can ignore sn-percent-civilian-builders.

Default: `2`

Required range: `-1 to Max`

Range: `Min to Max`

[AIRef](https://airef.github.io/strategic-numbers/sn-details.html#sn-cap-civilian-builders)

