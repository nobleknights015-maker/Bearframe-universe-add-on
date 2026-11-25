from struct import pack,unpack
from io import BytesIO
class NBT:
    def __init__(self,bytes_=b''): self.f=BytesIO(bytes_)
    def get(self,fmt): return unpack('<'+fmt,self.f.read(__import__('struct').calcsize('<'+fmt)))[0]
    def put(self,fmt,val): self.f.write(pack('<'+fmt,val))
    def string(self): return self.f.read(self.get('H')).decode()
    def text(self,val):
        b=val.encode()
        self.put('H',len(b)); self.f.write(b)
    def read(self,t):
        if t in FORMATS: return self.get(FORMATS[t])
        if t==8: return self.string()
        if t==7: return self.f.read(self.get('i'))
        if t==9:
            elem,n=self.get('B'),self.get('i')
            return elem,[self.read(elem) for _ in range(n)]
        if t==10:
            d={}
            while kind:=self.get('B'):
                name=self.string()
                d[name]=(kind,self.read(kind))
            return d
        if t in (11,12): return [self.get(FORMATS[t]) for _ in range(self.get('i'))]
        raise ValueError(t)
    def write(self,t,v):
        if t<=6: self.put(FORMATS[t],v)
        elif t==8: self.text(v)
        elif t==7: self.put('i',len(v)); self.f.write(v)
        elif t==9:
            kind,items=v
            self.put('B',kind); self.put('i',len(items))
            for item in items: self.write(kind,item)
        elif t==10:
            for name,(kind,val) in v.items():
                self.put('B',kind); self.text(name); self.write(kind,val)
            self.put('B',0)
        elif t in (11,12):
            self.put('i',len(v))
            for item in v: self.put(FORMATS[t],item)
        else: raise ValueError(t)
FORMATS={1:'b',2:'h',3:'i',4:'q',5:'f',6:'d',11:'i',12:'q'}
def decode(raw):
    reader=NBT(raw)
    assert reader.get('B')==10
    name=reader.string()
    return name,reader.read(10)
def encode(name,data):
    writer=NBT()
    writer.put('B',10); writer.text(name); writer.write(10,data)
    return writer.f.getvalue()

class Site:
    def __init__(self,raw):
        self.name,self.root=decode(raw)
        self.w,self.h,self.d=self.root['size'][1][1]
        st=self.root['structure'][1]
        self.layers=st['block_indices'][1][1]
        self.blocks=self.layers[0][1]
        p=st['palette'][1]['default'][1]
        self.palette=p['block_palette'][1][1]
        self.metadata=p['block_position_data'][1]
    def index(self,x,y,z): return (x*self.h+y)*self.d+z
    def xyz(self,i): return i//(self.h*self.d),(i//self.d)%self.h,i%self.d
    def label(self,i): return 'void' if i<0 else self.palette[i]['name'][1].split(':',1)[-1]
    def get(self,x,y,z): return self.label(self.blocks[self.index(x,y,z)])
    def block(self,name,states=None):
        name=name if ':' in name else 'minecraft:'+name
        states=states or {}
        for i,b in enumerate(self.palette):
            if b['name'][1]==name and b['states'][1]==states: return i
        ver=self.palette[0]['version'][1]
        self.palette.append({'name':(8,name),'states':(10,states),'version':(3,ver)})
        return len(self.palette)-1
    def raw(self): return encode(self.name,self.root)

def blank(sample,w,h,d):
    from copy import deepcopy
    root=deepcopy(sample.root)
    root['size']=(9,(3,[w,h,d]))
    st=root['structure'][1]
    st['block_indices']=(9,(9,[(3,[-1]*(w*h*d)),(3,[-1]*(w*h*d))]))
    st['entities']=(9,(10,[]))
    st['palette'][1]['default'][1]['block_position_data']=(10,{})
    return Site(encode(sample.name,root))
