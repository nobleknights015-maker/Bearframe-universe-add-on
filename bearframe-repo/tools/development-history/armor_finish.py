from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from PIL import Image
from collections import Counter
import json
import numpy as np

folder=Path('deliverables')
prefix='Bearframe_Resources/'
source=folder/'Bearframe_Bedrock_0.4.9.mcaddon'
output=folder/'Bearframe_Bedrock_0.4.10.mcaddon'

def polish(pixels, boxes, echo):
    reference=Counter(map(tuple,pixels[3:30,3:30,:3].reshape(-1,3))).most_common(1)[0][0]
    changes=0
    for x,y,w,h in boxes:
        if x<128 and (x,y)!=(0,0):
            continue
        tile=pixels[y:y+h,x:x+w]
        original=tile[:,:,:3].astype(int)
        offset=original-np.array(reference)
        # Identify only the original armor alloy. Keep optics, insignia,
        # accent bands, embedded damage and dark joint material intact.
        mask=(tile[:,:,3]==255)&(np.ptp(offset,axis=2)<=3)&(abs(offset[:,:,0])<=30)
        if mask.sum()<16:
            continue
        shade=np.zeros((h,w),int)
        for row in range(h):
            cols=np.flatnonzero(mask[row])
            if len(cols)<5:
                continue
            if row%2==0 and w>=12:
                shade[row,cols[1]]=7
                shade[row,cols[-2]]=-8
            if row in (h//4,3*h//4) and len(cols)>=8:
                shade[row,cols[2:-2]]=-12 if row>h//2 else 8
            if row in (h//4+1,3*h//4-1) and len(cols)>=8:
                shade[row,cols[2]]=-30
                shade[row,cols[-3]]=-30
            if echo and len(cols)>7 and row%5==3:
                shade[row,cols[(row*3)%(len(cols)-4)+2]]=-20
        # A restrained edge highlight also works on small armor patches.
        for col in range(2,w-2,2):
            rows=np.flatnonzero(mask[:,col])
            if len(rows)>=4 and shade[rows[0],col]==0:
                shade[rows[0],col]=10
        adjusted=np.clip(original+shade[:,:,None]*mask[:,:,None],0,255)
        changes+=np.count_nonzero(np.any(adjusted!=original,axis=2))
        tile[:,:,:3]=adjusted
    return changes

updates={}
with ZipFile(source) as old:
    for path in old.namelist():
        if not path.startswith(prefix+'models/entity/') or not path.endswith('.geo.json'):
            continue
        key=Path(path).name.removesuffix('.geo.json')
        if key.startswith('grid_'):
            continue
        geometry=json.loads(old.read(path))['minecraft:geometry'][0]
        boxes={tuple(f['uv']+f['uv_size']) for b in geometry['bones'] for c in b.get('cubes',[]) for f in c['uv'].values() if f['uv'][1]<128}
        tex=prefix+'textures/bearframe/'+key+'.png'
        pixels=np.array(Image.open(BytesIO(old.read(tex))).convert('RGBA'))
        base=pixels.copy()
        count=polish(pixels,sorted(boxes),key.startswith('echo_') or key=='ward_resident')
        assert count>0, (key,count)
        assert np.array_equal(base[:,:,3],pixels[:,:,3])
        assert np.array_equal(base[128:],pixels[128:])
        assert np.max(abs(base.astype(int)-pixels.astype(int)))<=30
        buf=BytesIO()
        Image.fromarray(pixels).save(buf,'PNG')
        updates[tex]=buf.getvalue()
    for name in ('Bearframe_Behavior/manifest.json','Bearframe_Resources/manifest.json'):
        data=json.loads(old.read(name))
        for entry in [data['header'],*data['modules'],*data.get('dependencies',[])]:
            if entry.get('version')==[0,4,9]:
                entry['version']=[0,4,10]
        updates[name]=(json.dumps(data,indent=2)+'\n').encode()
    assert len(updates)==19
    with ZipFile(output,'w',ZIP_DEFLATED) as new:
        for name in old.namelist():
            new.writestr(name,updates[name] if name in updates else old.read(name))
    with ZipFile(output) as new:
        assert new.testzip() is None and len(new.namelist())==237
        assert {name for name in new.namelist() if new.read(name)!=old.read(name)}==updates.keys()
print('Verified 17 updated armor textures and two manifest bumps, with identical geometry, clothing pixels, and gameplay.')
