from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
s=Path('preview.py').read_text()
exec(s[s.index('def render('):s.index('sheet=Image.new')].replace('scale = min(11, (size-18)/max(np.ptp(corners[:,0]),np.ptp(corners[:,1])))','scale = 5.1'))
sheet=Image.new('RGB',(1056,679),'#131c22')
d=ImageDraw.Draw(sheet)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans'
def text(x,y,t,size,bold=False,color='#e7f0f1',anchor=None):
    f=font+('-Bold.ttf' if bold else '.ttf')
    d.text((x,y),t,fill=color,font=ImageFont.truetype(f,size),anchor=anchor)
text(29,17,'Nether Salvage Echoes',43,True)
text(32,73,'BEARFRAME BEDROCK 0.7.7   /   ADULT AND BABY MODEL COMPARISON',16,color='#9bc9ca')
p='Bearframe_Resources/'
units=[('piglin','Foundry Salvager'),('zombie_pigman','Scorched Salvager'),('piglin_brute','Vault Warden')]
with ZipFile('deliverables/Bearframe_Bedrock_0.7.7.mcaddon') as z:
    for i,(key,title) in enumerate(units):
        x=28+(i%2)*504
        y=111+(i//2)*281
        d.rounded_rectangle((x,y,x+486,y+264),14,fill='#26353d',outline='#415b62',width=2)
        text(x+17,y+12,title,22,True)
        d.line((x+25,y+226,x+463,y+226),fill='#4a6269',width=1)
        geo=json.loads(z.read(p+'models/entity/vanilla_'+key+'.geo.json'))['minecraft:geometry']
        atlas=np.array(Image.open(BytesIO(z.read(p+'textures/bearframe/vanilla/'+key+'.png'))).convert('RGBA'))
        for j,g in enumerate(geo):
            cubes=[c for b in g['bones'] for c in b.get('cubes',[])]
            im=render(cubes,atlas,25)
            im=im.crop(im.getbbox())
            cx=x+(243 if len(geo)==1 else 135 if j==0 else 349)
            sheet.paste(im,(cx-im.width//2,y+226-im.height),im)
            text(cx,y+236,'ADULT' if j==0 else 'BABY',13,True,'#b9ccce','mt')
sheet.save('deliverables/Bearframe_0.7.7_Nether_Echo_Preview.png')
