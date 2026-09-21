# Baseline and overrides

The guide uses a complete-by-default data model:

```text
final guide = pinned mainline baseline + hack overrides + hack additions - explicit deletions
```

The baseline supplies pinned definitions for exact Pokémon/forms documented in the target hack, plus explicitly requested fallback move/item definitions. It does not decide which Pokémon, moves or items exist in the hack; ROM-hack documentation does.

## Choose the mechanics profile

Set `versionGroup` in `config/baseline-config.json` to the closest supported mainline mechanics version group. This identifies a definition fallback; it is not simply the base ROM name and does not grant baseline learnsets. Keep `pokemonScope` as `hack-only` and populate `includedPokemonKeys` with exact PokeAPI form keys supported by the hack. `maxNationalDex` is only an optional fetch limit, never a substitute for this allowlist.

`downloadSprites: true` stores normal and shiny sprites in the project so the deployed guide is not dependent on a live sprite host. Missing or custom forms can be supplied in hack overrides.

## Fetch and pin the baseline

```powershell
npm run baseline:fetch
```

The importer resolves exact revisions of `PokeAPI/api-data` and `PokeAPI/sprites`, records them in `baseline.lock.json`, and writes normalized data under `data/baseline/`. Later builds reuse those revisions. Use `--refresh` only when intentionally upgrading the baseline and reviewing the resulting differences.

Never manually edit `data/baseline/`. Re-fetch it from the lock/config instead.

## Write hack-specific overrides

Use:

- `data/overrides/guide-data.json` for Pokémon, move and encounter changes;
- `data/overrides/abilities-data.json` for altered, new or removed abilities;
- `data/overrides/items-data.json` for altered, new or removed items;
- the other ordinary data files for hack-only acquisition, eggs, battles and curated builds.

Patch records only need an identity plus changed fields. Omitted fields inherit from the baseline. Objects merge recursively; arrays replace the baseline array. A record with `$delete: true` removes the matching record.

Example Pokémon stat and ability change:

```json
{
  "key": "bulbasaur",
  "stats": [50, 55, 55, 45, 70, 70],
  "bst": 345,
  "abilities": ["Overgrow", "Chlorophyll"]
}
```

Example move change:

```json
{ "id": 33, "name": "Tackle", "power": 50, "description": "Hack-specific effect text." }
```

Example removal:

```json
{ "name": "An ability not present in this hack", "$delete": true }
```

Locations are hack-specific and are not inherited from the mainline baseline.

## Build and inspect provenance

```powershell
npm run build:data
npm run validate
npm run audit:provenance
```

The merge writes the browser-ready final files in `data/` and adds `_provenance` to records. `origin` is `baseline`, `override`, or `added`; `overriddenFields` shows which top-level values came from hack documentation. The provenance audit warns when sensitive fields such as stats, types, abilities, learnsets or evolutions still come entirely from the baseline.

Those warnings are review prompts, not proof of an error. Silence in hack documentation does not prove that a mainline field is unchanged—or that a Pokémon, move or item is included at all.

## Defaults that are usually safe

- National Dex number and canonical mainline name for an already confirmed hack form;
- a default normal/shiny sprite for an unchanged, confirmed form;
- ordinary mainline move/item/ability descriptions only for an explicitly hack-referenced record and only as clearly identified fallback data.

## Data that must be checked against the hack

- types, stats, abilities and evolution methods;
- moves, move effects and every learnset;
- custom/regional forms and sprite identity;
- availability, encounter tables and acquisition methods;
- items, shops, held-item behaviour and trainer battles;
- custom type matchups, difficulty modes and special rules.

When evidence conflicts, prefer current hack documentation and keep unresolved uncertainty explicit.
