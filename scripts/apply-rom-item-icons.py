"""Attach only unambiguous exact-name ROM icon matches; never infer availability."""
from pathlib import Path
import json,re,unicodedata
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'artwork-review/rom-item-icons.json').read_text(encoding='utf8'))
def norm(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).lower())
by_name={}
for rec in manifest['items']:
    by_name.setdefault(norm(rec['name']),[]).append(rec)
p=R/'data/overrides/items-data.json';items=json.loads(p.read_text(encoding='utf8'));matched=[];unmatched=[];generic_tms=[]
tm_icon=next(rec for rec in manifest['items'] if rec['name']=='TM01')
for item in items:
    if re.match(r'^TM\s*\d+',item['name'],re.I):
        item['sprite']=tm_icon['sprite']
        item['spriteSource']={'kind':'generic-tm-icon','romSha256':manifest['romSha256'],'romItemId':tm_icon['romItemId'],'note':'User-requested shared TM disc icon; not a claim about individual TM artwork.'}
        generic_tms.append(item['name']);continue
    found=by_name.get(norm(item['name']),[])
    if len(found)!=1:
        unmatched.append(item['name']);continue
    rec=found[0];item['sprite']=rec['sprite'];item['spriteSource']={'kind':'user-supplied-rom','romSha256':manifest['romSha256'],'romItemId':rec['romItemId'],'iconTableOffset':rec['iconTableOffset']}
    matched.append({'name':item['name'],'romItemId':rec['romItemId']})
p.write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(R/'artwork-review/rom-icon-mapping.json').write_text(json.dumps({'matched':matched,'genericTMs':generic_tms,'unmatched':unmatched},ensure_ascii=False,indent=2),encoding='utf8')
print(f'Applied {len(matched)} exact-name icons and {len(generic_tms)} shared TM icons; {len(unmatched)} unmatched item references retain their previous artwork.')
