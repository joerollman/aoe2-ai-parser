# `up-log-data`

[All symbols](../ai-symbol-reference.md)

<a id="symbol-up-log-data"></a>

## `up-log-data`

- Kind: `command`
- Detail: Action - Debugging

Syntax: `(up-log-data <Option> <String> <typeOp> <Value>)`

Write a formatted text line to aoelog.txt. Set Option to 1 in order to write plain text. You must close the game in order to open aoelog.txt, which is located in the game folder, usually at "C:\Program Files (x86)\Microsoft Games\Age of Empires II". Please consider game performance when writing data. To log a message without referencing any data, simply leave the %d out of the chat message and use 'c: 0' as the last two parameters. In DE, this command does not write the data to an aoelog.txt file. Instead, you need to launch the game with the parameters 'LOGSYSTEMS=AIScript' and 'VERBOSELOGGING' (case sensitive)To do this with the Steam version, open your Steam games library with the Steam client, right click on Age of Empires II: Definitive Edition in the left sidebar that lists the games you own, and click Properties. In the Properties window, under the General tab, type the parameters above separated by spaces. Then, when you launch the game these parameters will be active. Unless you use the launch parameter CONSTANTLOGGING, DE will not create the log file until the game has closed. The log produced in DE will be found in the Steam user folder, usually something like "C:\Users\[user ID]\Games\Age of Empires 2 DE\logs" but note that this log isn't just used by the AI (it would be best to log something identifying the AI log at the start of the game), some of these logs with VERBOSELOGGING can get quite large so it might be a good idea to periodically clean out the folder. Here's a full list of recommended Steam launch parameters: SKIPINTRO DEBUGSPEEDS AIDEBUGGING LOGSYSTEMS=AIScript VERBOSELOGGING CONSTANTLOGGING. This allows you to skip the intro cinematic, increase the game speed up to 8.0 speed (beware that AI performance suffers noticeably past 2.0 speed and especially at 8.0 speed), allows for AI scripting logs, and writes to the log file continuously, rather than only when exiting the game.

[AIRef](https://airef.github.io/commands/commands-details.html#up-log-data)

Completion insert text:

```text
(up-log-data ${1:Option} ${2:String} ${3:typeOp} ${4:Value})
```

