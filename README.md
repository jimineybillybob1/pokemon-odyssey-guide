# Pokémon Odyssey Journal

A local companion for Pokémon Odyssey v4.1.1, with 409 Pokédex entries, encounters, team planning, bosses, sidequests and naval references. Designed for iPad and PC; spoilers are shown by default.

Public preview: https://jimineybillybob1.github.io/pokemon-odyssey-guide/

This is an unofficial fan guide with ongoing source checks. Hard Mode and difficulty-unspecified boss rosters are separate; Normal/Picnic rosters are not inferred. Some item locations/effects, evolution rules and move compatibility still require source verification. Artwork credits are in artwork-review/CREDITS.md. No game ROM is included.

On iPad, open the public link in Safari and choose Share → Add to Home Screen. Progress stays in that browser/device. Export a save before moving devices; cloud sync is not enabled.

## Open locally
Run `python -m http.server 49273 --bind 127.0.0.1` in this directory, then open http://127.0.0.1:49273/. This local address works on the hosting PC only; use the public preview on other devices.

## Rebuild from saved sources
Requires Python with openpyxl, Node, and the bundled Codex sharp package for app-icon generation.

```text
python scripts/import-odyssey.py
python scripts/configure-companion.py
python scripts/refine-controls.py
npm run build:data
npm run validate
npm run audit:assets
node scripts/test-companion.mjs
node scripts/build-offline.mjs
```

The pinned baseline is already downloaded. Use `npm run baseline:fetch` only to restore its snapshot. Never hand-edit generated final data. Overrides and repeatable importers are the source of truth.

Progress is stored in this browser. Use Save & Export for a backup; journal notes and completed quests/Strata are included. Cloud sync is not configured.

See SETUP_STATUS.md for validation and pending checks, sources/source-inventory.md for attribution, and sources/import-report.json for conflicts. Source records are not yet certified field-by-field for v4.1.1. Hard and unspecified battle rosters remain distinct; Normal/Picnic rosters are absent rather than inferred.

Artwork styling: run python scripts/style-odyssey.py after other configuration scripts and before node scripts/build-offline.mjs. Source and attribution details are in artwork-review/CREDITS.md.

Native item icons: scripts/extract-rom-items.py reads a user-supplied patched ROM without copying or modifying it. Run python scripts/apply-rom-item-icons.py after import-odyssey.py and before build:data to restore the exact-name icon mappings. ROM hashes and offsets are recorded in artwork-review/rom-item-icons.json; unmatched names are listed in rom-icon-mapping.json.
