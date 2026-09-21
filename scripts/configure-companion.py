from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,d):(R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
c=read('config/game-config.json')
c['branding'].update(logo='assets/art/compass.svg',hero='assets/art/journal.svg',icon='assets/art/compass.svg',primary='#83cbb3',accent='#dfbd79')
c['features'].update(eggs=False,legendaries=False,maps=True)
c['encounterPeriodLabel']='Time not specified'
c['sources']=[{'name':n,'url':u} for n,u in [('Developer release thread','https://eeveeexpo.com/odyssey/'),('Talrega Pokédex','https://talrega.epieffe.dev/'),('Encounters, items and tutors','https://docs.google.com/spreadsheets/d/1-duiiF5TXQtI3E9BdyXEViYYYVel_sUstNk1lZCqHsE/edit'),('Pokémon and mechanics','https://docs.google.com/spreadsheets/d/1Es1clPMUhEEqZRHW0tgAmvxqSzVXiXmD/edit'),('Bosses, quests and naval map','https://docs.google.com/spreadsheets/d/1XsXn87pb3vMSFTrtQerWnfmf1SAAMRzVoeT1wQ9uwug/edit')]]
write('config/game-config.json',c)
overrides={'spriteFallbacks':{},'formSpriteFallbacks':{},'hiddenPokemonKeys':[],'pokemonAliases':{},'battleSpeciesAliases':{},'displayNames':{},'formLabels':{},'sharedLearnsets':[],'encounterMethodOrder':['Wild','Tree','Rock','Surf','Fish','Dive'],'fishingRodOrder':['Old Rod','Good Rod','Super Rod','Not specified'],'requireFishingRod':True,'starterChoices':[],'profileDefaults':{},'trainerCostumes':[],'rivalStarterCounters':{},'acquisitionNotes':{},'mapPositions':{},'typeChart':read('data/odyssey-type-chart.json')}
for p in read('data/overrides/guide-data.json')['pokemon']:
    overrides['displayNames'][p['key']]=p['name']
    if p.get('formLabel'):overrides['formLabels'][p['key']]=p['formLabel']
(R/'config/game-overrides.js').write_text('// Type chart from styled developer workbook cells; see import-odyssey.py.\nwindow.GUIDE_OVERRIDES = '+json.dumps(overrides,ensure_ascii=False)+';\n',encoding='utf8')
for p in ['journey-data']:(R/f'data/{p}.js').write_text('window.JOURNEY_DATA='+json.dumps(read(f'data/{p}.json'),ensure_ascii=False)+';\n',encoding='utf8')
icon='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="112" fill="#173c3c"/><circle cx="256" cy="256" r="175" fill="none" stroke="#dcbc7d" stroke-width="10"/><circle cx="256" cy="256" r="145" fill="none" stroke="#608c79" stroke-width="3"/><path d="M256 66L303 209L446 256L303 303L256 446L209 303L66 256L209 209Z" fill="#dcbc7d"/><path d="M256 118L283 229L394 256L283 283L256 394L229 283L118 256L229 229Z" fill="#173c3c"/><circle cx="256" cy="256" r="29" fill="#83cbb3"/></svg>'''
(R/'assets/art/compass.svg').write_text(icon)
(R/'assets/art/journal.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600"><rect width="1200" height="600" fill="#173c3c"/><g fill="none" stroke="#7ea28b" opacity=".3"><path d="M0 520L200 200L410 400L650 80L850 360L1030 150L1200 480"/><path d="M0 590L300 320L550 510L780 230L1200 540"/><circle cx="950" cy="220" r="150"/><circle cx="950" cy="220" r="120"/></g></svg>''')
s=(R/'app.js').read_text(encoding='utf8')
if 'const companion=window.createGuideCompanion' not in s:
    at='  function render(){'
    s=s.replace(at,"  const companion=window.createGuideCompanion({esc,storageKey,touchSave,navigate,data,openPokemon});\n"+at)
    s=s.replace("main.innerHTML=state.view==='pokedex'?", "main.innerHTML=state.view==='journey'?companion.journey():state.view==='atlas'?companion.atlas():state.view==='coverage'?companion.coverage():state.view==='pokedex'?")
    s=s.replace("state.view==='save'?renderSave():renderHome();", "state.view==='save'?renderSave():companion.home();")
    s=s.replace('    bind();bindDexFilters(main);','    companion.bind(main,render);bind();bindDexFilters(main);')
    s=s.replace('profile:state.profile,sync:{revision:', 'profile:state.profile,journey:companion.serialize(),sync:{revision:')
    s=s.replace('state.profile=save.profile;localStorage.setItem', 'state.profile=save.profile;companion.restore(save.journey);localStorage.setItem')
    s=s.replace('function typeEffectiveness(type,defenderTypes){const chart=', 'function typeEffectiveness(type,defenderTypes){if(guideOverrides.typeChart?.[type])return defenderTypes.reduce((value,def)=>value*(guideOverrides.typeChart[type][def]??1),1);const chart=')
    s=s.replace("const modes=[...new Set(battleGuideData.battles.map(battle=>battle.mode||'default'))];", "const modes=[...new Set([...(battleGuideData.meta?.modes||[]),...battleGuideData.battles.map(battle=>battle.mode||'default')])];")
    s=s.replace('No documented battles match these filters.', 'No verified rosters are available for this mode and filter. Other difficulty teams have not been substituted.')
    # Display evidence context in Pokémon detail rather than imply every field is verified.
    s=s.replace("<section class=\"pokemon-moves\"><h3>Moves</h3>","<section class=\"pokemon-moves\"><h3>Moves</h3><p class=\"pokemon-moves-note\">Workbook level-up moves; companion Dex supplies TM/tutor compatibility. Release alignment remains under review.</p>")
    (R/'app.js').write_text(s,encoding='utf8')
h=(R/'index.html').read_text(encoding='utf8')
if 'companion.js' not in h:
    h=h.replace('<link rel="stylesheet" href="refinements.css">','<link rel="stylesheet" href="refinements.css"><link rel="stylesheet" href="adventure.css">')
    h=h.replace('<script src="app.js"></script>','<script src="data/journey-data.js"></script><script src="companion.js"></script><script src="app.js"></script>')
    h=h.replace('<strong>Field Guide</strong>','<strong>Odyssey Journal</strong>')
    h=h.replace('<div class="source-card"><small>DATA SOURCES</small><p>Add and attribute this hack\'s Pokédex, encounter, item, battle and community sources in <code>sources/source-inventory.md</code>.</p></div>','<div class="source-card"><small>ODYSSEY v4.1.1</small><p>Your adventure companion.</p><button data-view="coverage">Sources &amp; coverage</button></div>')
    h=h.replace('<button data-view="pokedex">','<button data-view="journey">Journal</button><button data-view="atlas">Atlas</button><button data-view="pokedex">',1)
    h=h.replace('<nav class="mobile-nav">','<nav class="mobile-nav"><button data-view="journey"><small>Journal</small></button><button data-view="atlas"><small>Atlas</small></button>')
    h=h.replace('Save &amp; Sync','Save &amp; Export').replace('<small>Sync</small>','<small>Save</small>')
    h=h.replace('</header>','<button class="adventure-theme" id="themeToggle" aria-label="Switch colour theme">Light / dark</button></header>',1)
    h=h.replace('</body>',"<script>document.querySelector('#themeToggle').onclick=()=>{const next=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=next;localStorage.setItem('odyssey-display-theme',next)};document.documentElement.dataset.theme=localStorage.getItem('odyssey-display-theme')||'dark';</script></body>")
    h=h.replace('assets/art/placeholder-logo.svg','assets/art/compass.svg').replace('assets/art/placeholder-hero.svg','assets/art/journal.svg').replace('assets/art/placeholder-icon.svg','assets/art/compass.svg')
    (R/'index.html').write_text(h,encoding='utf8')
s=(R/'app.js').read_text(encoding='utf-8-sig')
if 'const encounterPeriodLabel=' not in s:
    s=s.replace("  const allDayEncounterModel", "  const encounterPeriodLabel=guideConfig.encounterPeriodLabel||'All day';\n  const allDayEncounterModel")
    s=s.replace("?'All day':", "?encounterPeriodLabel:")
    s=s.replace('<span>All day</span>','<span>Time not specified</span>')
    s=s.replace("?'ALL-DAY':", "?encounterPeriodLabel.toUpperCase():")
    (R/'app.js').write_text(s,encoding='utf8')
b=read('data/battle-data.json');b['meta']['modes']=['Hard','Normal','Picnic','Mode unspecified'];write('data/battle-data.json',b)
print('Companion UI and source configuration updated.')
