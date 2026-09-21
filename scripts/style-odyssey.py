from pathlib import Path
import re,json
r=Path(__file__).resolve().parents[1]
icons={'home':'exp-candy-xl','journey':'adventure-guide','atlas':'old-sea-map','available':'poke-radar','compare':'silph-scope','pokedex':'poke-radar','moves':'tm-case','items':'prop-case','locations':'town-map','team':'poke-ball','future':'poke-ball','favorites':'heart-scale','battle':'vs-seeker','trainer':'adventure-guide','progress':'adventure-guide','save':'card-key'}
p=r/'index.html';s=p.read_text(encoding='utf8')
def nav(m):
    content=m[0]
    def button(b):
        view=b[1];body=re.sub(r'<img[^>]*class="nav-sprite"[^>]*>','',b[2]);icon=icons.get(view,'adventure-guide')
        src='assets/odyssey-items/001.png' if view=='future' else f'assets/items/{icon}.png'
        return b[0].replace(b[2],f'<img class="nav-sprite" src="{src}" alt="" aria-hidden="true">'+body)
    return re.sub(r'<button[^>]*data-view="([^"]+)"[^>]*>(.*?)</button>',button,content,flags=re.S)
s=re.sub(r'<nav(?: class="mobile-nav")?>.*?</nav>',nav,s,flags=re.S)
s=s.replace('content="#160609"','content="#20271f"')
p.write_text(s,encoding='utf8')
p=r/'companion.js';s=p.read_text(encoding='utf8')
s=s.replace('<div class="hero-compass" aria-hidden="true"><span>Y</span><i></i></div>','<figure class="odyssey-cover"><img src="assets/art/odyssey-steamgriddb.jpg" width="267" height="400" alt="Pokémon Odyssey cover featuring its adventurers and Pokémon"><figcaption><a href="https://www.steamgriddb.com/game/5445119" target="_blank" rel="noopener">Artwork via SteamGridDB ↗</a></figcaption></figure>')
s=s.replace('The compass icon and journal graphics are original guide artwork.','The compass icon is original guide artwork. The cover preview is from <a href="https://www.steamgriddb.com/game/5445119" target="_blank" rel="noopener">SteamGridDB’s Pokémon Odyssey listing</a>; individual artist attribution and full-resolution art remain unverified. Menu icons are Pokémon item sprites from the pinned PokéAPI collection.')
p.write_text(s,encoding='utf8')
css='''
/* Palette informed by the Odyssey cover: forest, parchment, gold and plum. */
:root,[data-theme="dark"]{--bg:#191f19;--panel:#242d23;--panel2:#303b2d;--text:#f3eed6;--muted:#bfc5aa;--line:#465440;--red:#cbd68a;--gold:#e4c46b;--brand-primary:#cbd68a;--brand-accent:#e4c46b}
[data-theme="light"]{--bg:#f2eed9;--panel:#fffbed;--panel2:#e5e8ce;--text:#283620;--muted:#5d684f;--line:#c5c9ac;--red:#506b35;--gold:#88661b}
.sidebar nav button:before,.mobile-nav button:before{content:none!important}
.nav-sprite{display:inline-block!important;width:30px;height:30px;object-fit:contain;image-rendering:pixelated;flex-shrink:0;filter:drop-shadow(0 2px 2px #0004)}
.sidebar nav button{display:flex;align-items:center;gap:12px}.sidebar nav button[hidden],.mobile-nav button[hidden],.save-panel[hidden]{display:none!important}
.sidebar nav button.active{box-shadow:inset 3px 0 var(--gold);background:var(--panel2)}
.adventure-hero{background:radial-gradient(ellipse at 80% 0%,#78834a55,transparent 65%),linear-gradient(135deg,#273821,#45462b 70%,#45384c);border-color:#78805a;grid-template-columns:minmax(0,1fr) 240px;gap:35px;padding:38px;min-height:450px}
.adventure-hero p{color:#e0e4c9}.hero-actions .secondary{background:#303c29;border-color:#a0ab77}.adventure-hero .primary{background:#d5d998!important;color:#26331f!important}
.odyssey-cover{margin:0;justify-self:center;width:240px;max-width:100%}.odyssey-cover img{width:100%;height:auto;display:block;border-radius:8px;border:1px solid #e6d99788;box-shadow:0 14px 32px #0005}.odyssey-cover figcaption{text-align:center;font-size:11px;margin-top:10px}.odyssey-cover a{color:#ece5bd;text-decoration:underline;text-underline-offset:3px}
.feature-grid button:nth-child(3n){border-bottom-color:#8d789b}.primary,.caught-action{color:var(--bg)!important}
@media(max-width:1100px){.adventure-hero{grid-template-columns:minmax(0,1fr) 190px;gap:24px;padding:28px}.odyssey-cover{width:190px}.adventure-hero h1{font-size:42px}.hero-actions{flex-wrap:wrap}}
@media(max-width:900px){.mobile-nav button{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px}.mobile-nav .nav-sprite{width:26px;height:26px}}
@media(max-width:600px){.adventure-hero{grid-template-columns:1fr;padding:25px}.odyssey-cover{width:170px}.adventure-hero h1{font-size:40px}}
'''
p=r/'adventure.css';s=p.read_text(encoding='utf8');marker='/* Palette informed by the Odyssey cover:';s=s.split(marker)[0]+css;p.write_text(s,encoding='utf8')
(r/'artwork-review/CREDITS.md').write_text('''# Artwork sources

Cover: Pokémon Odyssey listing, https://www.steamgriddb.com/game/5445119
Image exposed by the listing’s Open Graph metadata: https://cdn2.steamgriddb.com/thumb/febccfbffd0db5ad1e07171ceac87b50.jpg
Retrieved 2026-09-21, unchanged 267 × 400 preview. Artist/full-resolution metadata could not be retrieved (public detail endpoint returned Forbidden). No artist or licence is inferred.

Town Map and Silph Scope: PokeAPI/sprites commit 0b133a62e914976d3d7ea33aaa1ac676ca248c30, sprites/items/town-map.png and sprites/items/silph-scope.png. Other menu sprites already bundled by the field-guide scaffold. Pokémon artwork belongs to its respective rights holders.

Palette visually derived from the cover; interface styling and compass are original guide work.
''',encoding='utf8')
print('Applied Odyssey cover palette and item menu icons.')
