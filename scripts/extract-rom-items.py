"""Extract native 24px item tiles and palettes without modifying the source ROM.
FireRed layout reference: pret/pokefirered src/item_menu_icons.c.
Offsets validated for the supplied English Odyssey v4.1.1 ROM only.
"""
from pathlib import Path
import argparse,hashlib,json,re,struct,unicodedata
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('rom');args=ap.parse_args()
b=Path(args.rom).read_bytes();before=hashlib.sha256(b).hexdigest()
ITEMS=0x3DB028;ICONS=0x3D4294;COUNT=376
def decode(raw):
    out=''
    chars={0:' ',0x1B:'é',0xAB:'!',0xAC:'?',0xAD:'.',0xAE:'-',0xB0:'…',0xB4:"'",0xB8:',',0xBA:'/',0xF0:':'}
    for c in raw:
        if c==255:break
        out+=chr(c-0xBB+65) if 0xBB<=c<=0xD4 else chr(c-0xD5+97) if 0xD5<=c<=0xEE else str(c-0xA1) if 0xA1<=c<=0xAA else chars.get(c,f'[{c:02x}]')
    return out.strip()
def lz(offset,expected):
    assert b[offset]==0x10
    size=int.from_bytes(b[offset+1:offset+4],'little');assert size==expected,(hex(offset),size)
    pos=offset+4;out=bytearray()
    while len(out)<size:
        flags=b[pos];pos+=1
        for bit in range(7,-1,-1):
            if len(out)>=size:break
            if flags&(1<<bit):
                a,c=b[pos:pos+2];pos+=2;length=(a>>4)+3;distance=((a&15)<<8)+c+1
                assert distance<=len(out)
                for _ in range(length):out.append(out[-distance])
            else:out.append(b[pos]);pos+=1
    return out[:size]
def norm(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).lower())
assert decode(b[ITEMS+13*44:ITEMS+13*44+14])=='Medica','Unexpected ROM item layout'
records=[];folder=R/'assets/odyssey-items';folder.mkdir(exist_ok=True)
for i in range(COUNT):
    off=ITEMS+i*44;name=decode(b[off:off+14]);item_id=struct.unpack_from('<H',b,off+14)[0]
    # Hacks may redirect the internal effect ID while retaining the bag-table index.
    gfx,pal=struct.unpack_from('<II',b,ICONS+i*8);gfx-=0x8000000;pal-=0x8000000
    tiles=lz(gfx,288);palette=lz(pal,32)
    colours=[]
    for value in struct.unpack('<16H',palette):
        colours.append(tuple(round(((value>>shift)&31)*255/31) for shift in (0,5,10)))
    image=Image.new('RGBA',(24,24))
    for y in range(24):
        for x in range(24):
            tile=(y//8)*3+x//8;v=tiles[tile*32+(y%8)*4+(x%8)//2];index=(v>>(4*(x%2)))&15
            image.putpixel((x,y),(*colours[index],255 if index else 0))
    path=f'assets/odyssey-items/{i:03d}.png';image.save(R/path)
    records.append({'romItemId':i,'internalItemId':item_id,'name':name,'sprite':path,'nameOffset':hex(off),'iconTableOffset':hex(ICONS+i*8),'graphicsOffset':hex(gfx),'paletteOffset':hex(pal)})
out=R/'artwork-review';out.mkdir(exist_ok=True)
manifest={'romSha256':before,'romVersion':'User-supplied English Pokémon Odyssey v4.1.1','layoutReference':'https://github.com/pret/pokefirered/blob/master/src/item_menu_icons.c','items':records}
(out/'rom-item-icons.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
medica=[v for v in records if v['name'].startswith('Medica')]
sheet=Image.new('RGB',(len(medica)*120,140),'#f2eed9');draw=ImageDraw.Draw(sheet)
for i,rec in enumerate(medica):
    icon=Image.open(R/rec['sprite']).resize((96,96),Image.Resampling.NEAREST);sheet.paste(icon,(i*120+12,4),icon);draw.text((i*120+12,112),rec['name'],fill='#283620')
sheet.save(out/'medica-icons.png')
assert hashlib.sha256(Path(args.rom).read_bytes()).hexdigest()==before,'ROM changed unexpectedly'
print(json.dumps({'extracted':len(records),'medica':medica,'romUnchanged':True},ensure_ascii=False))
