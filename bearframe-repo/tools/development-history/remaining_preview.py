from pathlib import Path
import json
import numpy as np
from io import BytesIO
from zipfile import ZipFile
from PIL import Image,ImageDraw,ImageFont
s=Path('preview.py').read_text()
exec(s[s.index('def render('):s.index('sheet=Image.new')])
groups=[
 ('Shared drone chassis', [('vex','Nullframe Drone'),('allay','Blue Utility Drone')]),
 ('Legacy and raid units', [
    ('witch','Echo Chemist'),('iron_golem','Ghost Grid Protector'),('enderman','Longstride Echo'),
    ('warden','Deep Grid Sentinel'),('creaking','Rootbound Echo'),('ravager','Nullframe Siege Beast'),
 ])
]
sheet=Image.new('RGB',(846,1235),'#141c21')
d=ImageDraw.Draw(sheet)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans'
def text(x,y,s,size,color='#eaf1f1'):
    d.text((x,y),s,font=ImageFont.truetype(font+'-Bold.ttf',size),fill=color)
text(28,20,'Echoes and Machines',43)
text(30,77,'BEDROCK 0.7.9  /  PACKAGED REST-POSE RENDERS',17,'#a2c9c6')
p='Bearframe_Resources/'
y=126
with ZipFile('deliverables/Bearframe_Bedrock_0.7.9.mcaddon') as z:
    for title,entries in groups:
        text(29,y,title,25,'#86cec6')
        y+=42
        for i,(id_,label) in enumerate(entries):
            x=28+(i%3)*269
            top=y+(i//3)*222
            d.rounded_rectangle((x,top,x+256,top+209),13,fill='#25343b',outline='#435a60',width=2)
            text(x+12,top+9,label,17)
            g=json.loads(z.read(p+'models/entity/vanilla_'+id_+'.geo.json'))['minecraft:geometry'][0]
            cubes=[c for b in g['bones'] for c in b.get('cubes',[])]
            raw=z.read(p+'textures/bearframe/vanilla/'+id_+'.png')
            pic=render(cubes,np.array(Image.open(BytesIO(raw)).convert('RGBA')),31)
            pic.thumbnail((172,172),Image.Resampling.LANCZOS)
            sheet.paste(pic,(x+43,top+30),pic)
        y+=((len(entries)+2)//3)*222+10
sheet.crop((0,0,846,y+5)).save('deliverables/Bearframe_0.7.9_Remaining_Mob_Preview.png')
