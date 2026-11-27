import zipfile,struct,zlib,gzip,collections, numpy as np, json
from pathlib import Path
class NBT:
 def __init__(self,b): self.b=b;self.p=0
 def take(self,n): r=self.b[self.p:self.p+n];self.p+=n;return r
 def num(self,f): return struct.unpack('>'+f,self.take(struct.calcsize('>'+f)))[0]
 def string(self):return self.take(self.num('H')).decode('utf8','replace')
 def read(self,t):
  if t==10:
   d={}
   while (k:=self.num('B')): n=self.string();d[n]=self.read(k)
   return d
  if t==9:
   k=self.num('B');n=self.num('i');return [self.read(k) for _ in range(n)]
  if t==8:return self.string()
  if t in (7,11,12):return self.take(self.num('i')*{7:1,11:4,12:8}[t])
  return self.num({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[t])
 def root(self):assert self.num('B')==10;self.string();return self.read(10)
def chunks(z):
 for name in z.namelist():
  if '/region/' not in name or not name.endswith('.mca'):continue
  raw=z.read(name)
  for i in range(1024):
   off=int.from_bytes(raw[i*4:i*4+3],'big')*4096
   if not off:continue
   n=int.from_bytes(raw[off:off+4],'big');t=raw[off+4];b=raw[off+5:off+4+n]
   if t==2:b=zlib.decompress(b)
   elif t==1:b=gzip.decompress(b)
   elif t!=3:continue
   yield NBT(b).root()
def ids(s):
 bs=s.get('block_states',{});p=bs.get('palette',[])
 if len(p)==1:return np.zeros(4096,dtype=np.int16)
 bits=max(4,(len(p)-1).bit_length());q=64//bits
 a=np.frombuffer(bs['data'],dtype='>u8').astype('uint64');v=np.arange(4096,dtype=np.uint64);return ((a[v//q]>>((v%q)*bits))&((1<<bits)-1)).astype(np.int16)
