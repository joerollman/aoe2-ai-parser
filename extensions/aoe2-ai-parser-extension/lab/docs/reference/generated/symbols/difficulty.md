# `difficulty`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-difficulty"></a>

## `difficulty`

- Kind: `command`
- Detail: Fact - Game Info

Syntax: `(difficulty <compareOp> <Difficulty>)`

Checks the difficulty setting. The ordering of difficulty settings is the opposite of what one would expect! Make sure that this is taken in account when using facts to compare difficulties. easiest &gt; easy &gt; moderate &gt; hard &gt; hardest (ie; treat easiest as a difficulty value of 4, easy as 3, moderate as 2, hard as 1, hardest as 0, and extreme as -1). For testing certain difficulty levels see the code examples. It is counter intuitive!(difficulty == easiest)True if the difficulty is easiest(difficulty &gt; easiest)WRONG: This will never be true, Easiest is the &quot;highest&quot; number!(difficulty &lt; hardest)WRONG: This will never be true, Hardest is the &quot;lowest&quot; number (Extreme is the lowest number in DE)!(difficulty &lt;= moderate)This is true if the difficulty is Moderate, Hard, Hardest, or Extreme.(difficulty &gt;= easy)This is true if the difficulty is Easy or Easiest.(difficulty &gt; hard)Counter-intuitive - avoid (you probably want the opposite in fact, see below), this is true if the difficulty is Moderate, Easy or Easiest.(difficulty &lt;= hard)This is true if the difficulty is Hard, Hardest, or Extreme.(difficulty &gt; hardest)This is true if the difficulty is Hard, Moderate, Easy or EasiestBecause of the counter-intuitive ordering of difficulties, you may find it helpful to use #load-if-defined or #load-if-not-defined to check difficulty settings instead, such as #load-if-defined DIFFICULTY-HARD or #load-if-not-defined DIFFICULTY-HARDEST.Full information on difficulty affecting aspectsRemember that easy is referred to as Standard in the game. This information about difficulty is from the CPSB about the hardcoded changes. Automatic changes to some sn values can be stopped with snDoNotScaleForDifficultyLevel; see this SN for more information.Distance an enemy unit must be within when the computer player unit looks for a new target:easiest: LOS (can be modified by snEasiestReactionPercentage)easy: LOS (can be modified by snEasierReactionPercentage)moderate: LOS * 2hard: LOS * 2hardest: LOS * 2Computer players ignore relics on the easiest level.Computer players do not attack villagers on the easiest and easy difficulty levels.If a non-exploring computer unit gets attacked, the computer player's attack delay for attack-group settings is modified:easiest: allow attacking one minute earliereasy: allow attacking two minutes earliermoderate: allow attacking immediatelyhard: allow attacking immediatelyhardest: allow attacking immediatelyAfter a wolf kills a unit, have it gorge itself (not attack again) for:easiest: 35 secondseasy: 30 secondsmoderate: 25 secondshard: 20 secondshardest: 15 secondsDistance a unit must be within when a wolf looks for a new target (UP only):DE removed the reaction distance modifier for predator animals (like Wolves, Snow Leopards) depending on difficulty and made it so that predator animals always find villagers within 6 tiles and other units within 4 tiles. Easiest difficulty on scenarios and campaigns will still use 4 tiles.easiest: LOS * 0.5easy: LOS * 0.75moderate: LOS * 2hard: LOS * 2hardest: LOS * 2Unit build (using villager for example) and research time (including age advancement):easiest: 200% (0:25 to 0:50)easy/standard: 133% (0:25 to 0:33)moderate: 100% (for DE it's 114% (0:25 to 0:28))hard: 100% (for DE it's 105% (0:25 to 0:26))hardest: 100%Building construction appears to be unaffected. For non-DE game versions, Hardest difficulty adds a hardcoded 500 of each resource at the beginning of the game and on reaching each new age. This cannot be disabled, but you can remove these resources with a negative cc-add-resource or up-cc-add-resource command. Also note that starting the game in later ages adds these bonuses incrementally (so up to 2000 for starting in the Imperial Age or Post-Imperial Age). Each difficulty level will change certain SN values automatically (including when set manually) unless sn-do-not-scale-for-difficulty-level is set to 1. See snDoNotScaleForDifficultyLevel for these values. Small additional note is that Hard also still makes SN changes, so it is recommended for a non-cheating AI to use sn-do-not-scale-for-difficulty-level so it can perform well on Hard.

[AIRef](https://airef.github.io/commands/commands-details.html#difficulty)

Completion insert text:

```text
(difficulty ${1:compareOp} ${2:Difficulty})
```

