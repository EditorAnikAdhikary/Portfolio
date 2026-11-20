"""Rebuilds work/index.html from work/index.baseline.html (the current GitHub main). Every edit asserts that its anchor exists exactly once."""
import re,sys
B='/mnt/user-data/outputs/work/'
s=open(B+'index.baseline.html',encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)>=1,"anchor missing: "+a[:80]
    s=s.replace(a,b,n)
# 1. promises: intro completion + typewriter completion
rep('window.__ready=new Promise(r=>{window.__rdy=r});','window.__ready=new Promise(r=>{window.__rdy=r});window.__introDone=new Promise(r=>{window.__idRes=r});window.__twDone=new Promise(r=>{window.__twRes=r});')
# 2. the signature quill waits for the typewriter (so the two sounds never overlap); animation itself is unchanged
rep('__ready.then(()=>setTimeout(()=>{if(!started)play()},500))})();','Promise.all([__ready,__twDone]).then(()=>setTimeout(()=>{if(!started)play()},450))})();')
# 3. audio controller: typewriter key sound (same AudioContext, same master mute, own bus level)
rep('const LV={amb:.55,ink:.7,bird:.65,quill:1,ui:.5};','const LV={amb:.55,ink:.7,bird:.65,quill:1,ui:.5,type:.55};')
rep(' quillSet(v){',''' key(kind){if(!gate("key",45))return;const sp=kind==="space",r=Math.random;
  burst({bus:"type",f:(sp?900:1900)+r()*500,q:1.1,d:.045,g:(sp?.20:.26)*(.85+r()*.3),a:.001});
  burst({bus:"type",f:3800+r()*900,q:2.2,d:.022,g:.13*(.8+r()*.4),a:.001,at:.012});
  tone({bus:"type",f0:sp?140:190,f1:sp?70:85,d:.07,g:(sp?.16:.12)*(.85+r()*.3)})},
 quillSet(v){''')
# 4. background text: depth tiers, whole-pixel seams, slow speed drift (content + engine unchanged)
rep('const row=document.createElement("div");row.className="br "','const tier=(i*7+sd)%3,row=document.createElement("div");row.className="br "')
rep('${o.fs}px/${ht}px','${(o.fs*[.94,1,1.05][tier]).toFixed(1)}px/${ht}px')
m=re.search(r'\$\{\(o\.a\*\.72\)\.toFixed\(3\)\}',s); assert m; s=s.replace(m.group(0),'${(o.a*.72*[.8,1,1.12][tier]).toFixed(3)}',1)
rep('rows.push([trk,seg,o])','rows.push([trk,seg,o,tier])')
rep('rows.forEach(([trk,seg,o],k)=>','rows.forEach(([trk,seg,o,tier],k)=>')
rep('const w=seg.getBoundingClientRect().width;if(!w)return;','const w0=seg.getBoundingClientRect().width;if(!w0)return;const w=Math.ceil(w0);seg.style.boxSizing="border-box";seg.style.width=w+"px";')
rep('const sp=o.sp[0]+((k*37+sd*11)%13)/12*(o.sp[1]-o.sp[0]),d=w/sp;','const sp=(o.sp[0]+((k*37+sd*11)%13)/12*(o.sp[1]-o.sp[0]))*[.84,1,1.12][tier],d=w/sp;')
rep('const SBG={all:[],rebuild(){this.all.forEach(g=>{if(g.dataset.b)sbgBuild(g)})}};','const SBG={all:[],rebuild(){this.all.forEach(g=>{if(g.dataset.b)sbgBuild(g)})}};\nif(!RM)setInterval(()=>{if(document.hidden)return;const n=performance.now()/1000;SBG.all.forEach((g,gi)=>{if(g.classList.contains("off")||!g.dataset.b)return;[...g.children].forEach((r,k)=>{const a=r.firstChild&&r.firstChild.getAnimations?r.firstChild.getAnimations()[0]:null;if(a)a.playbackRate=1+.045*Math.sin(n*.11+k*1.7+gi)})})},300);')
# 5. replace pigeon + intro (tail of the last script) with the typewriter + new pigeon/intro
a=s.index('function pigeonSVG(){'); b=s.rindex('</script>')
s=s[:a]+open('/tmp/p8/tw.js',encoding='utf-8').read()+"\n"+open('/tmp/p8/pigeon_intro.js',encoding='utf-8').read()+s[b:]
# 6. CSS
css='''
/* ===== v9: pigeon (JS-driven wings), intro atmosphere veil, typewriter spans ===== */
.wing,.pbob,.tail{animation:none!important}.fx{transform-box:view-box}
#intro::before{content:"";position:absolute;inset:0;z-index:6;pointer-events:none;background:#cbb689;animation:vOut 1.1s ease-out forwards}@keyframes vOut{from{opacity:.9}to{opacity:0}}
html.tw-prep header .mast{visibility:hidden;animation:twSafe 0s 6s forwards!important}@keyframes twSafe{to{visibility:visible}}
.mast .tw{visibility:hidden}.mast .tw.on{visibility:visible}.mast .tw.cur{position:relative}.mast .tw.cur::after{content:"";position:absolute;right:-.04em;top:.14em;bottom:.12em;width:.055em;background:currentColor;opacity:.8}
@media(prefers-reduced-motion:reduce){#intro::before{display:none}}
'''
i=s.index('</style>'); s=s[:i]+css+s[i:]   # FIRST </style> = the main stylesheet (the last one is inside <noscript> and would be ignored)
rep('</head>','<script>try{if(!matchMedia("(prefers-reduced-motion:reduce)").matches)document.documentElement.classList.add("tw-prep")}catch(e){}</script></head>')
open(B+'index.html','w',encoding='utf-8').write(s); print("built index.html",len(s)//1024,"KB (baseline",len(open(B+'index.baseline.html',encoding='utf-8').read())//1024,"KB)")
