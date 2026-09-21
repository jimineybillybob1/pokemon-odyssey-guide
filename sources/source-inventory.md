# Source inventory

Inspected and imported 2026-09-20; build reviewed 2026-09-21. Public snapshots are hashed; per-field release alignment remains unverified.

| Source | Authority/format | Observed coverage and limitations |
|---|---|---|
| https://eeveeexpo.com/odyssey/ | Developer PacoScarso release thread | v4.1.1 Expanded Bag and v4.0.3 compatibility option; FireRed U 1.0; links to all three supplied workbooks |
| https://talrega.epieffe.dev/ | User-supplied interactive Pokédex | Public data.json imported: 409 species, 443 moves, abilities, evolution and compatibility. Exact release alignment unverified |
| https://docs.google.com/spreadsheets/d/1-duiiF5TXQtI3E9BdyXEViYYYVel_sUstNk1lZCqHsE/edit | Developer-linked Google workbook, public XLSX readable | Pokémon; Pokémon (Postgame); Naval Explorations; Wonder Trade; Items; Items (Shop); Items (Pickup); GatheringMining; TM Location; Move Tutors |
| https://docs.google.com/spreadsheets/d/1Es1clPMUhEEqZRHW0tgAmvxqSzVXiXmD/edit | Developer-linked Google workbook, public XLSX readable | Type Chart; Etrian Variants; New Moves & Abilities; #1-151; #152-251; #252-386; 4th Gen; Paradox; Pokédex. Aether present; type multipliers not recoverable from plain CSV alone |
| https://docs.google.com/spreadsheets/d/1XsXn87pb3vMSFTrtQerWnfmf1SAAMRzVoeT1wQ9uwug/edit | Developer-linked Google workbook, public XLSX readable | Level Caps; Bosses (Hard Mode); Bosses (Hard Mode) - Postgame; Abyssal God - Bossfight guide; Lords of the sea; Sea Bosses; Sea Map; Sidequests |
| https://www.hackdex.app/hack/pokemon-odyssey | User-supplied secondary listing | Web reader returned 403; details not inspected |
| https://www.steamgriddb.com/game/5445119 | User-supplied artwork collection | Page identified, no individual art/creator/permission metadata inspected |

## Import cautions
- Inspect styled type-chart cells and map imagery, not only text exports.
- Preserve side-by-side encounter blocks, regional-variant markers, rods, rates, levels, event requirements, and location hierarchy.
- Treat Hard Mode roster scope explicitly; other difficulties need their own evidence.
- Scarlet/Violet fallback profile approved; exact 296-form baseline pinned. Later-generation Pokémon/moves do not prove a uniform generation mechanics profile.
- All three workbooks and Talrega dataset imported. Synced root sources/ has not been modified.

Difficulty scope confirmed by user: all supported modes. Audit each source for mode-specific coverage; do not extrapolate Hard Mode teams to other modes.

## Local snapshots and inspection
- Downloaded all three developer-linked workbooks on 2026-09-20 into sources/inbox/. SHA256 values recorded in snapshot-hashes.json.
- Sampled every worksheet. Pokédex has numbered species records; species sheets have types, abilities, evolution and learnsets; encounters contain methods, levels, rates and events.
- Sidequests include names, location, description and rewards. Hard Mode boss sheets contain individual team builds.
- Sea Map and shiny variant artwork extracted. Type multipliers decoded from workbook cell fills; custom move numeric fields imported, category/type retained from Talrega where shown as image badges.
- Current developer links establish source authority, but exact v4.1.1 field alignment remains unverified. Import source rows retained; one Murkrow stat conflict resolved in favour of developer workbook. See import-report.json for counts and conflicts.

