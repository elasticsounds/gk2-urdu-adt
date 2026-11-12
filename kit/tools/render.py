import pymupdf, sys, os
src=sys.argv[1]; out='adt/assets'
doc=pymupdf.open(src)
rep=[]
for i,page in enumerate(doc):
    n=i+1; removed=0
    for img in page.get_images(full=True):
        xref=img[0]; w,h=img[2],img[3]; cs=img[5]
        if (w,h) in [(1272,207),(1272,512)] or (cs=='Indexed' and w==1272):
            page.delete_image(xref); removed+=1
    rep.append((n,removed,len(page.get_images())))
for i,page in enumerate(doc):
    n=i+1
    pix=page.get_pixmap(dpi=150)
    pix.save(f'{out}/pages/p{n:03d}.jpg', jpg_quality=82)
    one=pymupdf.open(); one.insert_pdf(doc,from_page=i,to_page=i)
    one.save(f'{out}/pdf/p{n:03d}.pdf',garbage=4,deflate=True); one.close()
print(rep)
