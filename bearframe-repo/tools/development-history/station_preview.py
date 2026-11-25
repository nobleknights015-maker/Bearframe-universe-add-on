from pathlib import Path
from zipfile import ZipFile
from PIL import Image,ImageDraw,ImageFont
from bedrock_nbt import Site,blank
source=Path('render_structures.py').read_text()
exec(source[source.index('palette={'):source.index('W,H=')])
z=ZipFile('deliverables/Bearframe_Bedrock_0.6.2.mcaddon')
prefix='Bearframe_Behavior/structures/bearframe/'
center=Site(z.read(prefix+'orbital_city.mcstructure'))
combined=blank(center,111,12,77)
ids={}
for name,dx,dz in [('orbital_city',0,27),('orbit_commons',60,14),('orbit_farfield',10,0),('orbit_operations',10,50)]:
    s=Site(z.read(prefix+name+'.mcstructure'))
    for i,idx in enumerate(s.blocks):
        if idx<0:continue
        x,y,zp=s.xyz(i)
        block=s.label(idx)
        if block not in ids:ids[block]=combined.block(block)
        combined.blocks[combined.index(x+dx,y,zp+dz)]=ids[block]
for x,zp in [(59,zp) for zp in range(36,41)]+[(x,zp) for x in (26,27,28) for zp in (27,28,48,49)]:
    for y in range(2,6):combined.blocks[combined.index(x,y,zp)]=ids['air']

# Check links all the way from the original docking area using the combined
# structure, including the three new module entrances.
from collections import deque
q=deque([(2,38)])
seen=set()
while q:
    x,zp=q.popleft()
    if (x,zp) in seen or not (0<=x<111 and 0<=zp<77):continue
    if combined.get(x,1,zp) in ('void','air') or any(combined.get(x,y,zp)!='air' for y in (2,3)):continue
    seen.add((x,zp))
    q.extend(((x-1,zp),(x+1,zp),(x,zp-1),(x,zp+1)))
for pt in ((82,33),(95,46),(21,12),(34,63)):
    assert pt in seen,(pt,len(seen))

sheet=Image.new('RGB',(1220,1130),'#141b20')
draw=ImageDraw.Draw(sheet)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans'
def title(s,y,size,bold=True):
    draw.text((30,y),s,font=ImageFont.truetype(font+('-Bold.ttf' if bold else '.ttf'),size),fill='#e6efee')
title('Bearframe Station',18,48)
title('BEDROCK 0.6.2   /   STATION TEMPLATES RENDERED TOGETHER',80,19,False)
for y,heading,high in ((120,'Exterior',11),(623,'Interior cutaway',5)):
    title(heading,y,26)
    sheet.paste(render(combined,0,high,(1160,447)),(30,y+41))
sheet.save('deliverables/Bearframe_0.6.2_Station_Preview.png')
print('Verified connected docking route to all four added staff posts.')
