# AoE2 AI Script Cursor Extension

Local Cursor/VS Code extension for AoE2 `.per` and `.ai` files.

Features:

- TextMate syntax highlighting for comments, strings, commands, rules,
  constants, strategic numbers, typed operators, and numbers.
- Completion items generated from the local AIRef inventories in this repo.

Build completion data from the repo root:

```powershell
node extensions\aoe2-aiscript-cursor\scripts\build-completions.mjs
```

Package from the extension directory:

```powershell
npx @vscode/vsce package
```

