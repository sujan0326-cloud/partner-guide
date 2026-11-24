"""박스 규격 그림 만들기: python tools/draw_box_sizes.py 출력폴더 → HTML을 만든 뒤 브라우저로 캡처해 images/에 저장 (box_sizes.jpg, box_가로x세로x높이.jpg)"""
import math
C=math.cos(math.radians(30)); S=0.5
BOXES=[('보관용 소','용품 사용 권장',45,30,30,''),('출고용 소','',47,35,21,''),
       ('중','보관용 · 출고용 (S/S 권장)',59,40.5,28,''),('대','보관용 · 출고용 · 신발 OUT (F/W 권장)',56.5,50.5,34.5,'')]
def P(x,y,z,s,ox,oy): return (ox+(x-y)*C*s, oy+(x+y)*S*s-z*s)
def box(w,d,h,s,ox,oy):
    p=lambda x,y,z:P(x,y,z,s,ox,oy); pts=lambda L:' '.join(f'{a:.1f},{b:.1f}' for a,b in L)
    top=[p(0,0,h),p(w,0,h),p(w,d,h),p(0,d,h)]
    left=[p(0,d,0),p(w,d,0),p(w,d,h),p(0,d,h)]   # 가로 면 (긴 면)
    right=[p(w,0,0),p(w,d,0),p(w,d,h),p(w,0,h)]  # 세로 면 (좁은 면)
    tape=[p(0,d/2-3,h),p(w,d/2-3,h),p(w,d/2+3,h),p(0,d/2+3,h)]
    tape2=[p(w,d/2-3,h),p(w,d/2+3,h),p(w,d/2+3,h-7),p(w,d/2-3,h-7)]
    seam=[p(0,d/2,h),p(w,d/2,h)]
    sh=[p(-3,-3,0),p(w+6,-3,0),p(w+6,d+6,0),p(-3,d+6,0)]
    o=f'<polygon points="{pts(sh)}" fill="#000" opacity=".06" filter="url(#b)"/>'
    o+=f'<polygon points="{pts(left)}" fill="#c9a06a" stroke="#8a6a3e" stroke-width="1.2" stroke-linejoin="round"/>'
    o+=f'<polygon points="{pts(right)}" fill="#b88f5c" stroke="#8a6a3e" stroke-width="1.2" stroke-linejoin="round"/>'
    o+=f'<polygon points="{pts(top)}" fill="#e2c595" stroke="#8a6a3e" stroke-width="1.2" stroke-linejoin="round"/>'
    o+=f'<polygon points="{pts(tape)}" fill="#f3e7cf" opacity=".75"/><polygon points="{pts(tape2)}" fill="#e9d9b8" opacity=".8"/>'
    o+=f'<line x1="{seam[0][0]:.1f}" y1="{seam[0][1]:.1f}" x2="{seam[1][0]:.1f}" y2="{seam[1][1]:.1f}" stroke="#8a6a3e" stroke-width=".8" opacity=".6"/>'
    # dimension lines
    def dim(a,b,lab,dx,dy,anchor='middle'):
        (x1,y1),(x2,y2)=a,b
        x1+=dx;x2+=dx;y1+=dy;y2+=dy
        mx,my=(x1+x2)/2,(y1+y2)/2
        r=f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#33415e" stroke-width="1.3" marker-start="url(#a)" marker-end="url(#a)"/>'
        return r,(mx,my)
    out=[]
    l1,m1=dim(p(0,d,0),p(w,d,0),'',-9,11)   # 가로
    l2,m2=dim(p(w,d,0),p(w,0,0),'',9,11)    # 세로
    l3,m3=dim(p(0,d,0),p(0,d,h),'',-16,0)    # 높이 (왼쪽 모서리)
    o+=l1+l2+l3
    return o,(m1,m2,m3)
def card(name,sub,w,d,h,cx,cy,cw,ch,s):
    bw=(w+d)*C*s; bh=(w+d)*S*s+h*s
    ox=cx+cw/2+30-(w-d)*C*s/2; oy=cy+ch-46-(w+d)*S*s
    g,(m1,m2,m3)=box(w,d,h,s,ox,oy)
    t=lambda x,y,txt,a='middle',sz=15,wt=600,col='#162036':f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{a}" font-size="{sz}" font-weight="{wt}" fill="{col}">{txt}</text>'
    f=lambda v:('%g'%v)
    o=f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="18" fill="#f6f7f9" stroke="#e3e6eb"/>'
    o+=t(cx+22,cy+34,name,'start',19,700)+ (t(cx+22,cy+56,sub,'start',12.5,400,'#6b7385') if sub else '')
    o+=t(cx+cw-22,cy+34,f'{f(w)} × {f(d)} × {f(h)}','end',16,700,'#33415e')+t(cx+cw-22,cy+53,'가로 × 세로 × 높이 (cm)','end',11,400,'#8a93a6')
    o+=g
    o+=t(m1[0]-14,m1[1]+22,f'가로 {f(w)}','middle',13,600,'#33415e')
    o+=t(m2[0]+16,m2[1]+22,f'세로 {f(d)}','middle',13,600,'#33415e')
    o+=t(m3[0]-10,m3[1]+5,f'높이 {f(h)}','end',13,600,'#33415e')
    return o
W,H=900,720; cw,ch=432,342; s=2.5
cells=[(12,12),(456,12),(12,366),(456,366)]
body=''.join(card(n,sb,w,d,h,x,y,cw,ch,s) for (n,sb,w,d,h,_),(x,y) in zip(BOXES,cells))
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Noto Sans CJK KR, sans-serif">
<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M5 0v10" stroke="#33415e" stroke-width="2"/></marker><filter id="b"><feGaussianBlur stdDeviation="4"/></filter></defs>
<rect width="{W}" height="{H}" fill="#fff"/>{body}</svg>'''
OUT=__import__('sys').argv[1] if len(__import__('sys').argv)>1 else '.'
# 1) 한눈에 보기
open(OUT+'/boxes.html','w').write(f'<html><body style="margin:0">{svg}</body></html>')

# 2) 박스별 그림 (박스·스티커 페이지 카드·크게 보기용)
def single(w,d,h,W=520,H=340,s=3.1):
    ox=W/2+30-(w-d)*C*s/2; oy=H-42-(w+d)*S*s
    g,(m1,m2,m3)=box(w,d,h,s,ox,oy)
    f=lambda v:('%g'%v)
    t=lambda x,y,txt,a:f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{a}" font-size="15" font-weight="600" fill="#33415e">{txt}</text>'
    body=g+t(m1[0]-14,m1[1]+24,f'가로 {f(w)}','middle')+t(m2[0]+16,m2[1]+24,f'세로 {f(d)}','middle')+t(m3[0]-10,m3[1]+5,f'높이 {f(h)}','end')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Noto Sans CJK KR, sans-serif"><defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M5 0v10" stroke="#33415e" stroke-width="2"/></marker><filter id="b"><feGaussianBlur stdDeviation="4"/></filter></defs><rect width="{W}" height="{H}" fill="#f4f6f9"/>{body}</svg>'''
for dims in [(45,30,30),(59,40.5,28),(56.5,50.5,34.5),(47,35,21)]:
    name='box_%sx%sx%s'%tuple(('%g'%v).replace('.','_') for v in dims)
    open(f'{OUT}/{name}.html','w').write('<html><body style="margin:0">'+single(*dims)+'</body></html>')
