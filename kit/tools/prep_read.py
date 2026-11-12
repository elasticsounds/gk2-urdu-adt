from PIL import Image, ImageDraw, ImageFont
import glob, os
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',15)
for f in sorted(glob.glob('adt/assets/pages/p*.jpg')):
    n=os.path.basename(f)[:4]
    im=Image.open(f).convert('RGB'); W,H=im.size
    big=im.resize((W*2,H*2),Image.LANCZOS)
    big.crop((0,0,W*2,int(H*1.06))).save(f'qa/read/{n}_top.jpg',quality=90)
    big.crop((0,int(H*0.94),W*2,H*2)).save(f'qa/read/{n}_bottom.jpg',quality=90)
    g=im.copy(); d=ImageDraw.Draw(g,'RGBA')
    for k in range(1,20):
        x=W*k/20; y=H*k/20; major=(k%2==0)
        col=(0,90,255,150) if major else (0,90,255,60)
        d.line([(x,0),(x,H)],fill=col,width=1); d.line([(0,y),(W,y)],fill=col,width=1)
        if major:
            t=f'.{k//2}'
            for pos in [(x+2,2),(x+2,H-18)]:
                d.rectangle([pos[0]-1,pos[1],pos[0]+18,pos[1]+16],fill=(255,255,255,210)); d.text(pos,t,fill=(0,0,200),font=font)
            for pos in [(2,y+2),(W-22,y+2)]:
                d.rectangle([pos[0]-1,pos[1],pos[0]+18,pos[1]+16],fill=(255,255,255,210)); d.text(pos,t,fill=(0,0,200),font=font)
    g.save(f'qa/grid/{n}.jpg',quality=85)
