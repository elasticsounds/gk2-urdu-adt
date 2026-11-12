import numpy as np, cv2
from PIL import Image
A=np.load('qa/pages_native.npy')
N,H,W,_=A.shape
x0,x1,y0,y1=200,620,330,740
R=A[:,y0-30:y1+30,x0-30:x1+30].astype(np.float32)
gray=R.mean(-1); sat=R.max(-1)-R.min(-1)
ds=[];ok=[]
for i in range(N):
    g=gray[i]
    wfrac=cv2.blur((g>=246).astype(np.float32),(41,41))
    dark=cv2.blur((g<150).astype(np.float32),(25,25))
    smax=cv2.dilate(sat[i],np.ones((9,9),np.uint8))
    white=(wfrac>0.55)&(dark<0.004)&(smax<16)
    ds.append((255-R[i])[30:-30,30:-30]); ok.append(white[30:-30,30:-30])
ds=np.stack(ds); ok=np.stack(ok)   # N,h,w,3
T=np.zeros(ds.shape[1:],np.float32)
for c in range(3):
    dm=np.ma.masked_array(ds[...,c],mask=~ok)
    T[...,c]=np.ma.median(dm,axis=0).filled(0)
cnt=ok.sum(0); print('cnt min',cnt.min(),'med',np.median(cnt),'Tmax',T.max(0).max(0))
Tg=T.mean(-1); Tg[Tg<2.5]=0
np.save('qa/T.npy',Tg); np.save('qa/Trgb.npy',T)
Image.fromarray(np.clip(255-Tg*3,0,255).astype(np.uint8)).save('qa/T0.png')
core=Tg>45
print('core rgb darkness',[float(np.median(T[...,c][core])) for c in range(3)], 'core px',core.sum())
# colored-bg pages: estimate watermark colour c. w = B - a(B-c), on white: d=a(255-c)
for pg in [2,3,5,15,21,45]:
    P=A[pg-1,y0:y1,x0:x1].astype(np.float32)
    ring=(Tg==0)&(cv2.dilate(core.astype(np.uint8),np.ones((7,7),np.uint8))>0)
    out=[]
    for c in range(3):
        B=np.median(P[...,c][ring]); w=np.median(P[...,c][core]); out.append((round(float(B)),round(float(w))))
    print(pg,out)
