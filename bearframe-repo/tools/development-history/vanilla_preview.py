from pathlib import Path
import json
import numpy as np
from io import BytesIO
from zipfile import ZipFile
from PIL import Image,ImageDraw,ImageFont
s=Path('preview.py').read_text()
exec(s[s.index('def render('):s.index('sheet=Image.new')])
groups=[
 ('Echo Frames · Village life',[('villager_v2','Echo villager'),('wandering_trader','Echo wayfarer')]),
 ('Echo Frames · Hostile units',[('zombie','Lost Echo'),('husk','Dustbound Echo'),('drowned','Submerged Echo'),('zombie_villager_v2','Fractured Ward Echo'),('skeleton','Echo marksman'),('stray','Frostbound Echo'),('bogged','Marsh Echo')]),
 ('Nullframes · Raid units',[('pillager','Nullframe raider'),('vindicator','Nullframe breacher'),('evocation_illager','Nullframe signal officer')])
]
sheet=Image.new('RGB',(1120,1235),'#141c21')
d=ImageDraw.Draw(sheet)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans'
def text(x,y,s,size,color='#eaf1f1'):
    d.text((x,y),s,font=ImageFont.truetype(font+'-Bold.ttf',size),fill=color)
text(28,20,'Bearframe vanilla mob models',43)
text(30,77,'BEDROCK 0.7.3  /  PACKAGED REST-POSE RENDERS',17,'#a2c9c6')
p='Bearframe_Resources/'
y=126
with ZipFile('deliverables/Bearframe_Bedrock_0.7.3.mcaddon') as z:
    for title,entries in groups:
        text(29,y,title,25,'#86cec6')
        y+=42
        for i,(id_,label) in enumerate(entries):
            x=28+(i%4)*269
            top=y+(i//4)*222
            d.rounded_rectangle((x,top,x+256,top+209),13,fill='#25343b',outline='#435a60',width=2)
            text(x+12,top+9,label,17)
            g=json.loads(z.read(p+'models/entity/vanilla_'+id_+'.geo.json'))['minecraft:geometry'][0]
            folded=id_ in ('villager_v2','wandering_trader','vindicator','evocation_illager')
            cubes=[c for b in g['bones'] for c in b.get('cubes',[]) if not folded or b['name'] not in ('rightarm','leftarm')]
            raw=z.read(p+'textures/bearframe/vanilla/'+id_+'.png')
            pic=render(cubes,np.array(Image.open(BytesIO(raw)).convert('RGBA')),31)
            pic.thumbnail((172,172),Image.Resampling.LANCZOS)
            sheet.paste(pic,(x+43,top+30),pic)
        y+=((len(entries)+3)//4)*222+10
sheet.crop((0,0,1120,y+5)).save('deliverables/Bearframe_0.7.3_Vanilla_Frame_Preview.png')
