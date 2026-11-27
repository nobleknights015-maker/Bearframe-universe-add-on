import numpy as np,struct
class NBT:
 def __init__(self,b):self.b=b;self.p=0
 def take(self,n):v=self.b[self.p:self.p+n];self.p+=n;return v
 def num(self,f):return struct.unpack('<'+f,self.take(struct.calcsize('<'+f)))[0]
 def string(self):return self.take(self.num('H')).decode()
 def read(self,t):
  if t==10:
   d={}
   while (k:=self.num('B')):n=self.string();d[n]=self.read(k)
   return d
  if t==9:
   k=self.num('B');n=self.num('i');return np.frombuffer(self.take(4*n),dtype='<i4') if k==3 else [self.read(k) for _ in range(n)]
  if t==8:return self.string()
  if t in (7,11,12):return self.take(self.num('i')*{7:1,11:4,12:8}[t])
  return self.num({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[t])
 def root(self):assert self.num('B')==10;self.string();d=self.read(10);assert self.p==len(self.b);return d
