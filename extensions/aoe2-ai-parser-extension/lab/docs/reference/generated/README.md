# Generated Reference

This folder contains formatted local documentation generated from the compact
registry data used by Cursor completions, hovers, signatures, and definition
navigation.

- [ai-symbol-reference.md](./ai-symbol-reference.md): all known AI scripting
  symbols from the local completion registry, with a generated table of
  contents and stable per-symbol anchors.
- [symbols/](./symbols/): compatibility per-symbol files generated from the
  same entries. Prefer the combined reference for cross-navigation.

Regenerate with:

```powershell
npm run generate:symbol-docs
```
