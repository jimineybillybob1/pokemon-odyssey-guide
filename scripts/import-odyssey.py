"""Repeatable Odyssey import. Workbook evidence outranks the companion Dex.
Keep raw snapshots untouched and preserve source rows and unresolved records.
"""
import base64, csv, json, re, unicodedata, datetime
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / 'sources/inbox'
def read(p): return json.loads((ROOT / p).read_text(encoding='utf-8-sig'))
def write(p, value):
    f = ROOT / p; f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def norm(s):
    s=str(s or '').replace('♀','f').replace('♂','m').replace('Nidoran (F)','Nidoran-f').replace('Nidoran (M)','Nidoran-m')
    return re.sub('[^a-z0-9]', '', unicodedata.normalize('NFKD',s).lower())
def clean(s):
    if isinstance(s,datetime.datetime):return f'{s.day}-{s.month}'
    if isinstance(s,float) and s.is_integer():return str(int(s))
    return str(s or '').replace('\ufffd', "'").replace('\xad','').strip()
def slug(s): return re.sub('[^a-z0-9]+','-',unicodedata.normalize('NFKD',clean(s)).lower()).strip('-')
DEX=read('sources/inbox/talrega-data.json')
books={n:openpyxl.load_workbook(INBOX/f,data_only=True) for n,f in [('pokemon','pokemon-mechanics.xlsx'),('encounters','encounters-items.xlsx'),('journey','progression-bosses.xlsx')]}
report={'conflicts':[], 'unresolved':[], 'notes':[], 'counts':{}}
def source(book,sheet,row): return {'file':{'pokemon':'pokemon-mechanics.xlsx','encounters':'encounters-items.xlsx','journey':'progression-bosses.xlsx'}[book],'sheet':sheet,'row':row}
aliases={'sandyshock':'sandyshocks','raticate':'ratreecate','nidoranfemale':'nidoranf','nidoranmale':'nidoranm','farfetchdgalar':'farfetchdgalar','mrmime':'mrmime','mimejr':'mimejr','hooh':'hooh'}
def normal(s):
    s=norm(re.sub(r'\(?⭐\)?','',str(s)).replace('(B.B.)','(Battle Bond)').replace('(B.B)','(Battle Bond)').replace('(BB)','(Battle Bond)'))
    return aliases.get(s,s)
species=list(DEX['species'].items())
byname={normal(v['key']):(k,v) for k,v in species}
byname.update({normal(v['name']):(k,v) for k,v in species if '(' not in v['key']})
byname['nidoranf']=next((k,v) for k,v in species if v['dexID']==29)
byname['nidoranm']=next((k,v) for k,v in species if v['dexID']==32)
def resolve(s):
    n=normal(s)
    if n in byname:return byname[n][0]
    for region in ['alola','hisui','galar']:
        if n.endswith(region) and n[:-len(region)] in byname:return byname[n[:-len(region)]][0]
    return None
national={norm(r['identifier']):int(r['id']) for r in csv.DictReader((INBOX/'pokemon-species.csv').open(encoding='utf8'))}
nat_alias={'ratreecate':'raticate','deepmaiden':'gyarados','narmer':'whiscash','tlachtga':'mismagius','dinogator':'feraligatr','aviddragon':'meganium'}
types=DEX['types']; colours={v['name']:v['color'] for v in types.values()}
moves=[]
for key,m in DEX['moves'].items():
    moves.append({'id':20000+int(key),'name':m['name'],'type':types[str(m['type'])]['name'],'typeColour':types[str(m['type'])]['color'],'category':DEX['splits'][str(m['split'])],'power':m['power'],'accuracy':m['accuracy'] if isinstance(m['accuracy'],(int,float)) and m['accuracy'] else None,'pp':m['pp'],'priority':m['priority'],'description':clean(m['description']),'source':{'url':'https://talrega.epieffe.dev/data.json','record':key},'verification':'Talrega companion Dex; release alignment pending'})
move_lookup={norm(m['name']):m['id'] for m in moves}
move_alias={'visegrip':'vicegrip','faintattack':'feintattack','hihorsepower':'highhorsepower','hijumpkick':'highjumpkick','eartquake':'earthquake','atonish':'astonish','defencecurl':'defensecurl'}
def moveid(s): return move_lookup.get(move_alias.get(norm(s),norm(s)))
# Import documented custom move effects and numeric fields; category/type remain
# companion evidence where the workbook encodes them only as image badges.
sh=books['pokemon']['New Moves & Abilities']
for row in sh:
    for cell in row:
        if clean(cell.value)!='Power':continue
        r,c=cell.row,cell.column; mid=moveid(sh.cell(r-3,c).value)
        if not mid:continue
        m=next(m for m in moves if m['id']==mid)
        for offset,field in [(0,'power'),(1,'accuracy'),(2,'pp')]:
            value=sh.cell(r+offset,c+1).value
            if isinstance(value,(int,float)):m[field]=int(value)
            elif field in ['power','accuracy'] and clean(value) in ['-','/']:m[field]=0 if field=='power' else None
        effect=clean(sh.cell(r+4,c).value)
        if effect:m['description']=effect
        m['source']=source('pokemon',sh.title,r-3)
abilities=[{'id':20000+int(k),'name':v['names'][0],'description':clean(v.get('description')),'source':{'url':'https://talrega.epieffe.dev/data.json','record':k}} for k,v in DEX['abilities'].items() if int(k)]
ability_lookup={norm(a['name']):a for a in abilities}
sheet_records={}; stats_records={}
for title in ['#1-151','#152-251','#252-386','4th Gen','Paradox']:
    sh=books['pokemon'][title]
    for row in sh:
        for c in row:
            if clean(c.value)=='Type:':
                r,col=c.row,c.column; name=clean(sh.cell(r-1,col).value); key=resolve(name)
                if not key: report['unresolved'].append({'kind':'species block','name':name,'source':source('pokemon',title,r)}); continue
                level=[]
                for rr in range(r+4,sh.max_row+1):
                    label=clean(sh.cell(rr,col).value); mn=sh.cell(rr,col+1).value
                    if label=='Type:' or (rr>r+4 and any(clean(sh.cell(rr+1,cc).value)=='Type:' for cc in [1,4,7])):break
                    if re.match(r'LV\.?\s*\d+',label,re.I) and mn:
                        mid=moveid(mn)
                        if mid: level.append({'level':int(re.search(r'\d+',label)[0]),'moveId':mid})
                        else: report['unresolved'].append({'kind':'level move','name':mn,'pokemon':name,'source':source('pokemon',title,rr)})
                sheet_records[key]={'types':clean(sh.cell(r,col+1).value).replace('Fight/','Fighting/').split('/'),'abilities':clean(sh.cell(r+1,col+1).value).split('/'),'evolutionNote':clean(sh.cell(r+2,col+1).value),'level':level,'regional':'⭐' in name,'source':source('pokemon',title,r-1)}
            if clean(c.value)=='Odyssey':
                vals=[sh.cell(c.row,c.column-i).value for i in range(7,1,-1)]
                name=sh.cell(c.row-2,c.column-7).value; key=resolve(name)
                if key and all(isinstance(v,(int,float)) for v in vals): stats_records[key]=[int(vals[i]) for i in [0,1,2,5,3,4]]

pokemon=[]; ids={k:20000+int(k) for k,v in species}; keys={k:slug(v['key'].replace('♀','-f').replace('♂','-m')) for k,v in species}
# Gender glyphs and source punctuation require explicit, stable identities.
keys[byname['nidoranf'][0]]='nidoran-f'; keys[byname['nidoranm'][0]]='nidoran-m'
baseline=[]
for k,v in species:
    rec=sheet_records.get(k,{}); n=normal(v['name']); nat=national.get(nat_alias.get(n,n),ids[k])
    abilities_raw=rec.get('abilities') or [DEX['abilities'][str(a[0])]['names'][0] for a in v['abilities'] if a[0]]
    aa=[{'name':a.strip(),'description':ability_lookup.get(norm(a),{}).get('description','Effect not yet verified in source documentation.')} for a in abilities_raw if a.strip()]
    ts=rec.get('types') or [types[str(t)]['name'] for t in v['type']]
    stats=stats_records.get(k,v['stats'])
    if stats != v['stats']: report['conflicts'].append({'pokemon':v['key'],'field':'stats','dex':v['stats'],'workbook':stats,'resolution':'workbook'})
    if rec.get('types') and ts != [types[str(t)]['name'] for t in v['type']]: report['conflicts'].append({'pokemon':v['key'],'field':'types','resolution':'workbook'})
    level=rec.get('level') or [{'moveId':20000+m,'level':l} for m,l in v.get('levelupMoves',[])]
    ev=[]
    for e in v.get('evolutions',[]):
        target=str(e[2]); method=DEX['evolutions'].get(str(e[0]),'Special evolution').strip('`').replace('${evo[1]}',str(e[1]))
        if target in ids: ev.append({'targetId':ids[target],'method':method})
    spr=f'assets/pokemon/odyssey-{k}.png'; raw=DEX['sprites'].get(str(v['ID']))
    if raw:
        f=ROOT/spr; f.parent.mkdir(parents=True,exist_ok=True); f.write_bytes(base64.b64decode(raw.split(',',1)[1]))
    else:spr='assets/art/placeholder-icon.svg'
    p={'id':ids[k],'dexId':nat,'gameDexId':v['dexID'],'key':keys[k],'name':v['key'],'isDefaultForm':not rec.get('regional') and '(' not in v['key'],'types':ts,'typeColours':[colours.get(t,'#888888') for t in ts],'stats':stats,'bst':sum(stats),'abilities':aa,'learnset':{'level':level,'tm':[20000+m for m in v.get('tmMoves',[]) if str(m) in DEX['moves']],'tutor':[20000+m for m in v.get('tutorMoves',[]) if str(m) in DEX['moves']]},'evolutions':ev,'sprite':spr,'shinySprite':'','evolutionNote':rec.get('evolutionNote',''),'source':rec.get('source',{'url':'https://talrega.epieffe.dev/data.json','record':k}),'verification':'Developer workbook fields take precedence; remaining Talrega fields require release cross-check','formLabel':'Etrian Variant' if rec.get('regional') else ('Battle Bond' if 'Battle Bond' in v['key'] else '')}
    # Fetch only exact ordinary mainline identities. Custom forms never borrow a base-form sprite.
    if not rec.get('regional') and '(' not in v['key'] and norm(v['name']) in national and n!='dudunsparce':
        baseline.append(next(r['identifier'] for r in csv.DictReader((INBOX/'pokemon-species.csv').open()) if int(r['id'])==nat))
    pokemon.append(p)

# Workbook images carry exact variant normal/shiny artwork and artist credit.
asset_credits=[]
sh=books['pokemon']['Etrian Variants']
for image in sh._images:
    r=image.anchor._from.row+1; col=image.anchor._from.col+1
    label=clean(sh.cell(r,1).value)
    if label!='SHINY':continue
    header=r-1 if label=='NORMAL' else r-2
    name=sh.cell(header,col).value; key=resolve(name)
    if not key:continue
    rel=f'assets/pokemon/{"shiny/" if label=="SHINY" else ""}odyssey-{key}.png'
    f=ROOT/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(image._data())
    next(p for p in pokemon if p['id']==ids[key])['shinySprite' if label=='SHINY' else 'sprite']=rel
    asset_credits.append({'path':rel,'source':source('pokemon',sh.title,r),'artist':clean(sh.cell(header+3,col).value),'preserveSourceBackground':True})

# Aether chart: use workbook cell colour legend, never a generic Fairy chart.
chart={}; sh=books['pokemon']['Type Chart']
for r in range(3,21):
    attacker=clean(sh.cell(r,2).value);chart[attacker]={}
    for c in range(3,21):
        defender=clean(sh.cell(2,c).value); colour=sh.cell(r,c).fill.fgColor.rgb
        chart[attacker][defender]={'FFE06666':0,'FFFFE599':0.5,'FF93C47D':2,'FFB6D7A8':2}.get(colour,1)
write('data/odyssey-type-chart.json',chart)

locations={}; acquisitions={'gifts':[],'trades':[],'special':[]}; items={}; tutors=[]
def item(name,place,note='',src=None):
    name=clean(name)
    if not name:return
    key=slug(name); entry=items.setdefault(key,{'id':30000+len(items),'name':name,'key':key,'category':'Odyssey reference','description':'See documented acquisition below. Item effect not yet verified.','sprite':'assets/art/placeholder-icon.svg','locations':[],'costs':[],'move':None,'source':src})
    entry['locations'].append(place+(' — '+clean(note) if note else ''))
methods={'TALL GRASS':'Wild','CAVE':'Wild','FLOOR':'Wild','HEADBUTT':'Tree','ROCK SMASH':'Rock','SURF':'Surf','SURFING':'Surf','FISHING':'Fish','OLD ROD':'Fish','GOOD ROD':'Fish','SUPER ROD':'Fish'}
for title in ['Pokémon','Pokémon (Postgame)','Naval Explorations','Wonder Trade']:
    sh=books['encounters'][title]
    # Each independent table begins at a POKÉMON header and ends at its next section.
    for row in sh:
        for cell in row:
            if normal(cell.value)!='pokemon':continue
            r,c=cell.row,cell.column
            before=[(rr,clean(sh.cell(rr,c).value)) for rr in range(1,r) if sh.cell(rr,c).value is not None]
            rod=next((s.title() for rr,s in reversed(before) if s in ['OLD ROD','GOOD ROD','SUPER ROD']),None)
            method=next((methods[s] for rr,s in reversed(before) if s in methods),'Wild')
            location_candidates=[(rr,s) for rr,s in before if s not in methods and s not in ['POKÉMON','LEVEL','ENCOUNTER %'] and '⭐' not in s and not resolve(s) and not re.match(r'^\d',s)]
            wide_headers=[]
            for merged in sh.merged_cells.ranges:
                if merged.min_row<r and merged.min_col<=c<=merged.max_col and merged.max_col-merged.min_col>=3:
                    val=clean(sh.cell(merged.min_row,merged.min_col).value)
                    if val and val not in methods and '⭐' not in val and 'POKÉMON'!=val and not val.startswith('EVENT'):wide_headers.append((merged.min_row,val))
            place=max(wide_headers,default=(0,location_candidates[-1][1] if location_candidates else title))[1]
            event='EVENT' in place.upper() or 'SPECIAL' in place.upper() or title=='Wonder Trade'
            event=event or any('EVENT' in s or 'F.O.E.' in s or 'SPECIAL' in s for rr,s in before[-2:])
            if title=='Wonder Trade':place='Wonder Trade — '+place
            for rr in range(r+1,sh.max_row+1):
                raw=clean(sh.cell(rr,c).value)
                if not raw:
                    if event:continue
                    break
                resolved=[resolve(part.strip()) for part in raw.split('/')]
                if not all(resolved):
                    if event:
                        if raw in ['POKÉMON','LEVEL'] or raw in methods:break
                        if moveid(raw) or raw=='Bullldoze':continue
                        if not raw.isupper():continue
                    if not raw.isupper() and raw not in methods and not moveid(raw):report['unresolved'].append({'kind':'encounter','name':raw,'source':source('encounters',title,rr)})
                    break
                level=clean(sh.cell(rr,c+1).value); rate=sh.cell(rr,c+2).value
                note='; '.join(clean(sh.cell(nr,j).value) for nr in [r-2,r-1,rr] if nr>0 for j in range(c+3,min(c+5,sh.max_column)+1) if sh.cell(nr,j).value is not None)
                for key in resolved:
                    encounter={'pokemon':keys[key],'method':method,'level':level or 'Not stated','rarity':round(rate*100,2) if isinstance(rate,(int,float)) and rate<=1 else None,'subarea':title if title in ['Pokémon (Postgame)','Naval Explorations'] else '', 'source':source('encounters',title,rr),'notes':note}
                    if method=='Fish':encounter['rod']=rod or 'Not specified'
                    if event or isinstance(rate,str) and any(x in rate.lower() for x in ['event','trade','sidequest']):
                        acquisitions['trades' if 'trade' in (title+' '+str(rate)).lower() else 'special'].append({'pokemon':keys[key],'location':place,'method':clean(rate) or title,'details':note,'level':level,'source':encounter['source']})
                    else:
                        loc=locations.setdefault(place,{'name':place,'region':'Talrega & Yggdrasil','periodModel':'all-day','periodNote':'Time of day is not specified by the source.','day':[],'night':[]})
                        if not any({k:v for k,v in e.items() if k!='source'}=={k:v for k,v in encounter.items() if k!='source'} for e in loc['day']):loc['day'].append(encounter)

for title in ['Items','Items (Shop)','Items (Pickup)','GatheringMining','TM Location']:
    sh=books['encounters'][title]
    if title=='TM Location':
        for r in range(1,sh.max_row+1):
            vals=[clean(c.value) for c in sh[r]]
            for c,v in enumerate(vals):
                if re.fullmatch(r'TM\d+',v):item(v+' — '+vals[c+1],vals[c+2],'TM',source('encounters',title,r))
        continue
    # Preserve full rows in the source reference for irregular gathering/shop tables.
    if title=='Items':
        for row in sh:
            for cell in row:
                if clean(cell.value)!='Items':continue
                col=cell.column;place=next((clean(sh.cell(rr,col).value) for rr in range(cell.row-1,0,-1) if sh.cell(rr,col).value),'Unspecified')
                for rr in range(cell.row+1,sh.max_row+1):
                    name=sh.cell(rr,col).value; how=sh.cell(rr,col+1).value
                    if not name:break
                    item(name,place,how,source('encounters',title,rr))

sh=books['encounters']['Move Tutors']
for r in range(1,sh.max_row+1):
    vals=[clean(c.value) for c in sh[r]]
    for c,v in enumerate(vals[:-1]):
        mid=moveid(v)
        if mid and vals[c+1] and not any(t['moveId']==mid for t in tutors):tutors.append({'id':'tutor-'+str(mid),'moveId':mid,'move':v,'location':vals[c+1],'source':source('encounters',sh.title,r)})

battles=[]
for title in ['Bosses (Hard Mode)','Bosses (Hard Mode) - Postgame','Lords of the sea','Sea Bosses']:
    sh=books['journey'][title]; current={}
    for row in sh:
        for cell in row:
            if clean(cell.value)=='Level:':
                r,c=cell.row,cell.column; name=clean(sh.cell(r-2,c).value) or clean(sh.cell(r-1,c).value); key=resolve(name)
                if not key: report['unresolved'].append({'kind':'battle species','name':name,'source':source('journey',title,r)});continue
                # Title is the nearest preceding populated merged heading spanning the team column.
                headers=[]
                for merged in sh.merged_cells.ranges:
                    if merged.min_row<r-1 and merged.min_col<=c<=merged.max_col:
                        label=clean(sh.cell(merged.min_row,merged.min_col).value)
                        if ' - ' in label or ' – ' in label:headers.append((merged.min_row,label))
                heading=max(headers,default=(0,title))[1]; parts=re.split(r'\s[-–]\s',heading,maxsplit=1)
                b=current.setdefault(heading,{'id':slug(title+'-'+heading),'trainer':parts[0].title(),'location':parts[-1].title() if len(parts)>1 else title,'category':'Postgame' if 'Postgame' in title else 'Boss battles','mode':'Hard' if 'Hard Mode' in title else 'Mode unspecified','difficulty':'Hard' if 'Hard Mode' in title else 'Unspecified','boss':True,'doubleBattle':True,'team':[],'source':source('journey',title,r),'notes':'Postgame' if 'Postgame' in title else ''})
                member={'name':keys[key],'level':sh.cell(r,c+1).value or 'Not stated','moves':[]}
                for rr in range(r+1,min(r+20,sh.max_row)+1):
                    label=clean(sh.cell(rr,c).value); value=clean(sh.cell(rr,c+1).value)
                    if label=='Level:':break
                    if label.rstrip(':').lower() in ['nature','ability','item']:member[label.rstrip(':').lower()]=value
                    if label=='ABILITY':member['ability']=clean(sh.cell(rr+1,c).value)
                    if label=='EVS':member['evs']=clean(sh.cell(rr+1,c).value)
                    for v in [label,value]:
                        if moveid(v) and v not in member['moves']:member['moves'].append(v)
                member['moves']=member['moves'][:4];b['team'].append(member)
    battles.extend(current.values())

quests=[]; sh=books['journey']['Sidequests']
for row in sh:
    vals=[clean(c.value) for c in row if c.value is not None]
    for c,v in enumerate(vals):
        if re.fullmatch(r'#\d+',v) and len(vals)>c+4:quests.append({'id':v,'name':vals[c+1],'location':vals[c+2],'description':vals[c+3],'reward':vals[c+4],'source':source('journey',sh.title,row[0].row)})
caps=[]
for row in books['journey']['Level Caps']:
    vals=[clean(c.value) for c in row if c.value is not None]
    if len(vals)>1 and re.search(r'LV\.?\s*\d+',vals[-1]):caps.append({'name':vals[0],'cap':int(re.search(r'\d+',vals[-1])[0])})
references=[]
for bn,titles in [('encounters',['Items (Shop)','Items (Pickup)','GatheringMining','Naval Explorations']),('journey',['Abyssal God - Bossfight guide'])]:
    for title in titles:
        sh=books[bn][title]; rows=[{'row':r[0].row,'cells':[{'column':c.column,'value':clean(c.value)} for c in r if c.value is not None]} for r in sh if any(c.value is not None for c in r)]
        references.append({'title':title,'rows':rows,'source':source(bn,title,1)})
maps=[]
for image in books['journey']['Sea Map']._images:
    f=f'assets/maps/sea-map-{len(maps)+1}.png';(ROOT/f).parent.mkdir(parents=True,exist_ok=True);(ROOT/f).write_bytes(image._data());maps.append({'name':'Naval exploration map','image':f,'source':source('journey','Sea Map',1)})
base=read('data/baseline/guide-data.json')
for p in pokemon:
    if p['isDefaultForm'] and not p['shinySprite']:
        match=next((x for x in base['pokemon'] if normal(x['name'])==normal(p['name'])),None)
        if match:p['shinySprite']=match.get('shinySprite','')
# Match Unicode gender names to baseline records while retaining stable -f/-m keys.
for p in pokemon:
    if p['key'] in ['nidoran-f','nidoran-m']:p['name']='Nidoran♀' if p['key'].endswith('-f') else 'Nidoran♂'
write('data/overrides/guide-data.json',{'meta':{'source':'Developer-linked Odyssey workbooks and Talrega Dex snapshots, 2026-09-20'},'pokemon':pokemon,'moves':moves,'locations':list(locations.values())})
write('data/overrides/abilities-data.json',abilities);write('data/overrides/items-data.json',list(items.values()))
write('data/overrides/move-tutor-data.json',{'tutors':tutors,'services':[]})
write('data/acquisition-data.json',acquisitions);write('data/battle-data.json',{'meta':{'source':'Odyssey developer workbook','sourceNote':'Hard Mode teams are documented. Normal and Picnic rosters are not verified; sea-boss difficulty is unspecified. Matchup scores are simplified estimates, not damage calculations.'},'battles':battles})
write('data/journey-data.json',{'quests':quests,'caps':caps,'maps':maps,'references':references})
write('sources/asset-credits.json',asset_credits)
cfg=read('config/baseline-config.json');cfg['includedPokemonKeys']=sorted(set(baseline));write('config/baseline-config.json',cfg)
write('sources/hack-allowlist.json',[{'id':p['id'],'key':p['key'],'gameDexId':p['gameDexId'],'source':p['source']} for p in pokemon])
report['counts']={'pokemon':len(pokemon),'moves':len(moves),'locations':len(locations),'encounters':sum(len(x['day']) for x in locations.values()),'acquisitions':sum(map(len,acquisitions.values())),'items':len(items),'tutors':len(tutors),'battles':len(battles),'quests':len(quests),'maps':len(maps),'workbookSpecies':len(sheet_records),'workbookStats':len(stats_records)}
write('sources/import-report.json',report)
print(json.dumps({'counts':report['counts'],'conflicts':len(report['conflicts']),'unresolved':len(report['unresolved'])}))
