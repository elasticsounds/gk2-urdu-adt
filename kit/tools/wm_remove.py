import numpy as np, cv2, pymupdf, os
from PIL import Image
A=np.load('qa/pages_native.npy'); T=np.load('qa/T.npy')
N,H,W,_=A.shape
x0,x1,y0,y1=200,620,330,740
a=np.clip(T/255.0,0,0.6)
a0=a
AH=np.load('qa/T_half.npy')
mask=(cv2.dilate((T>0).astype(np.uint8),np.ones((5,5),np.uint8))>0)
core=T>45
def hp(g): return g-cv2.GaussianBlur(g,(0,0),4)
Th=hp(T)
rep=[]
os.makedirs('adt/assets/pages',exist_ok=True); os.makedirs('adt/assets/pdf',exist_ok=True)
for i in range(N):
    P=A[i].astype(np.float32).copy()
    R=P[y0:y1,x0:x1]
    g=R.mean(-1)
    L=-np.log(np.clip(g,8,255)/255.0); Lh=hp(L)
    best=None
    for sx in (0,1):
        av=a0 if sx==0 else AH
        Ah=hp(-np.log(1-av))
        r=(Lh*Ah)[mask].sum()/np.sqrt((Lh*Lh)[mask].sum()*(Ah*Ah)[mask].sum()+1e-6)
        if best is None or r>best[0]: best=(r,sx,av,Ah)
    r,sx,a,Ah=best
    sel=mask.copy(); score=1.0
    for it in range(4):
        score=float((Lh*Ah)[sel].sum()/(Ah*Ah)[sel].sum())
        res=np.abs(Lh-score*Ah); thr=np.percentile(res[mask],70)
        sel=mask&(res<=thr)
    if sx: rep.append((i+1,sx,round(score,2)))
    if score>0.3:
        s_=min(score,1.15)
        fixed=np.clip(R/((1-a[...,None])**s_),0,255)
        # mild cleanup of JPEG ringing: blend bilateral-smoothed version inside the mask only
        sm=cv2.bilateralFilter(fixed.astype(np.uint8),5,18,3).astype(np.float32)
        m=cv2.GaussianBlur(mask.astype(np.float32),(0,0),1.0)[...,None]
        P[y0:y1,x0:x1]=fixed*(1-m)+sm*m
    im=Image.fromarray(P.astype(np.uint8))
    fn=f'adt/assets/pages/p{i+1:03d}.jpg'; im.save(fn,quality=90)
    d=pymupdf.open(); pg=d.new_page(width=612,height=792); pg.insert_image(pg.rect,filename=fn); d.save(f'adt/assets/pdf/p{i+1:03d}.pdf',deflate=True); d.close()
print(rep)
