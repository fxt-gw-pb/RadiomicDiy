CSS = r"""
:root{
  --ground:#F1F2F4; --surface:#FFFFFF; --surface-2:#F7F8F9; --sunken:#E9EBEE;
  --ink:#15181C; --ink-2:#3D454F; --muted:#616B78; --faint:#8B95A1;
  --line:#DBDFE4; --line-soft:#E9ECEF;
  --overlay:#C03C28; --overlay-soft:#FBEDEA;
  --amber:#9C6A05; --amber-soft:#FAF1DE;
  --grid:#CFD4DA;
  --shadow:0 1px 2px rgba(17,20,24,.05), 0 8px 24px -16px rgba(17,20,24,.28);
  --serif:"Source Serif 4","Noto Serif SC",Georgia,"Songti SC",serif;
  --sans:"IBM Plex Sans","Noto Sans SC",-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --rail:290px; --measure:70ch;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#0B0D10; --surface:#131619; --surface-2:#191D21; --sunken:#0F1215;
    --ink:#E8EBEF; --ink-2:#C3CAD2; --muted:#96A0AC; --faint:#6C7683;
    --line:#242A31; --line-soft:#1C2126;
    --overlay:#FF7A62; --overlay-soft:#2A1714;
    --amber:#E3AB4C; --amber-soft:#241C0E;
    --grid:#252B33;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 12px 32px -18px rgba(0,0,0,.8);
  }
}
:root[data-theme="dark"]{
  --ground:#0B0D10; --surface:#131619; --surface-2:#191D21; --sunken:#0F1215;
  --ink:#E8EBEF; --ink-2:#C3CAD2; --muted:#96A0AC; --faint:#6C7683;
  --line:#242A31; --line-soft:#1C2126;
  --overlay:#FF7A62; --overlay-soft:#2A1714;
  --amber:#E3AB4C; --amber-soft:#241C0E;
  --grid:#252B33;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 12px 32px -18px rgba(0,0,0,.8);
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:var(--sans); font-size:16px; line-height:1.75;
  -webkit-font-smoothing:antialiased;
}
a{color:inherit}
button{font:inherit;color:inherit;background:none;border:none;cursor:pointer}
:focus-visible{outline:2px solid var(--overlay); outline-offset:2px; border-radius:3px}

/* ---------- shell ---------- */
.shell{display:grid; grid-template-columns:var(--rail) minmax(0,1fr); height:100vh; overflow:hidden}
@media (max-width:960px){ .shell{grid-template-columns:1fr} }

.rail{
  position:sticky; top:0; height:100vh; overflow:hidden;
  display:flex; flex-direction:column;
  background:var(--surface); border-right:1px solid var(--line);
}
@media (max-width:960px){
  .rail{position:fixed; z-index:60; width:min(88vw,var(--rail)); transform:translateX(-101%);
        transition:transform .22s ease; box-shadow:var(--shadow)}
  .rail.open{transform:none}
}
.brand{
  padding:22px 22px 16px; border-bottom:1px solid var(--line-soft);
  display:flex; gap:12px; align-items:center;
}
.mark{
  width:36px;height:36px;flex:none;object-fit:contain;display:block;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]) .mark,
  :root:not([data-theme="light"]) .hero-logo{filter:invert(1)}
}
:root[data-theme="dark"] .mark,
:root[data-theme="dark"] .hero-logo{filter:invert(1)}
.brand h1{font-family:var(--serif); font-size:17px; line-height:1.35; margin:0; font-weight:600; letter-spacing:.01em}
.brand p{margin:2px 0 0; font-size:11.5px; color:var(--faint); font-family:var(--mono); letter-spacing:.06em; text-transform:uppercase}

.search{padding:14px 18px 10px}
.search input{
  width:100%; padding:8px 11px; font:inherit; font-size:13.5px;
  background:var(--sunken); color:var(--ink);
  border:1px solid var(--line); border-radius:6px;
}
.search input::placeholder{color:var(--faint)}

.nav{flex:1; overflow-y:auto; padding:4px 12px 28px}
.nav::-webkit-scrollbar{width:9px}
.nav::-webkit-scrollbar-thumb{background:var(--line); border-radius:9px; border:3px solid var(--surface)}

.mod{margin-bottom:6px}
.mod-head{
  width:100%; display:flex; align-items:center; gap:10px; padding:9px 10px;
  border-radius:7px; text-align:left;
}
.mod-head:hover{background:var(--surface-2)}
.mod-num{
  font-family:var(--mono); font-size:11px; color:var(--faint);
  border:1px solid var(--line); border-radius:4px; padding:1px 5px; flex:none;
  font-variant-numeric:tabular-nums;
}
.mod-name{font-size:13.5px; font-weight:500; flex:1; line-height:1.3}
.ring{width:20px;height:20px;flex:none}
.ring circle{fill:none; stroke-width:3}
.ring .bg{stroke:var(--line)}
.ring .fg{stroke:var(--overlay); stroke-linecap:round; transform:rotate(-90deg); transform-origin:50% 50%}
.chev{width:12px;height:12px;color:var(--faint); transition:transform .18s ease; flex:none}
.mod[data-open="1"] .chev{transform:rotate(90deg)}
.mod-list{display:none; padding:2px 0 8px 12px; margin-left:12px; border-left:1px solid var(--line-soft)}
.mod[data-open="1"] .mod-list{display:block}
.ch{
  display:flex; gap:9px; align-items:baseline; padding:6px 9px; border-radius:6px;
  font-size:13px; color:var(--muted); text-decoration:none; line-height:1.45;
}
.ch:hover{background:var(--surface-2); color:var(--ink)}
.ch.active{background:var(--overlay-soft); color:var(--ink); font-weight:500}
.ch .dot{
  width:6px;height:6px;border-radius:50%;flex:none;
  border:1px solid var(--faint); margin-top:7px;
}
.ch.done .dot{background:var(--overlay); border-color:var(--overlay)}
.ch.active .dot{border-color:var(--overlay)}

.rail-foot{padding:12px 18px; border-top:1px solid var(--line-soft); display:flex; gap:8px; align-items:center}
.tbtn{padding:5px 9px; border:1px solid var(--line); border-radius:6px; font-size:12px; color:var(--muted)}
.tbtn:hover{color:var(--ink); border-color:var(--faint)}

/* ---------- main ---------- */
.main{min-width:0; display:flex; flex-direction:column; height:100vh; overflow:hidden; position:relative}
.topbar{
  position:sticky; top:0; z-index:40; height:52px; display:flex; align-items:center; gap:14px;
  padding:0 22px; background:color-mix(in srgb,var(--ground) 88%, transparent);
  backdrop-filter:blur(10px); border-bottom:1px solid var(--line-soft);
}
.menu{display:none}
@media (max-width:960px){ .menu{display:block; font-size:13px; color:var(--muted)} }
.crumb{font-size:12.5px; color:var(--faint); font-family:var(--mono); letter-spacing:.03em;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
.crumb b{color:var(--muted); font-weight:500}
.readbar{position:absolute; left:0; bottom:-1px; height:2px; background:var(--overlay); width:0}

.scroll{flex:1; overflow-y:auto; scroll-behavior:smooth}
.page{display:grid; grid-template-columns:minmax(0,1fr); gap:0}
@media (min-width:1300px){
  .page.reading{grid-template-columns:minmax(0,1fr) 230px; gap:44px;
    padding-right:34px}
}
.wrap{max-width:var(--measure); margin:0 auto; padding:40px 26px 96px; width:100%}
@media (min-width:1300px){ .page.reading .wrap{margin:0 0 0 auto} }

/* ---------- home ---------- */
.hero{border-bottom:1px solid var(--line); background:var(--surface)}
.hero-in{max-width:1120px; margin:0 auto; padding:56px 26px 44px;
  display:grid; grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr); gap:52px; align-items:center}
@media (max-width:900px){ .hero-in{grid-template-columns:1fr; gap:34px; padding:38px 22px 34px} }
.eyebrow{font-family:var(--mono); font-size:11.5px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--overlay); margin:0 0 16px}
.hero h2{
  font-family:var(--serif); font-weight:600; font-size:clamp(29px,3.4vw,40px); line-height:1.18;
  margin:0 0 18px; text-wrap:balance; letter-spacing:-.01em;
}
.hero-logo{width:64px;height:64px;display:block;margin:0 0 18px;object-fit:contain}
.hero .lede{font-size:16.5px; color:var(--ink-2); margin:0 0 26px; max-width:54ch}
.cta-row{display:flex; gap:12px; flex-wrap:wrap; align-items:center}
.cta{
  display:inline-flex; align-items:center; gap:8px; padding:11px 20px; border-radius:7px;
  background:var(--ink); color:var(--ground); font-size:14px; font-weight:500; text-decoration:none;
}
.cta:hover{opacity:.88}
.cta.ghost{background:transparent; color:var(--ink); border:1px solid var(--line)}
.cta.ghost:hover{border-color:var(--faint); opacity:1}

/* viewer */
.viewer{background:#08090B; border:1px solid var(--line); border-radius:10px; overflow:hidden; box-shadow:var(--shadow)}
.viewer-top{display:flex; justify-content:space-between; align-items:center; padding:8px 12px;
  border-bottom:1px solid #1B1E22; font-family:var(--mono); font-size:10.5px; letter-spacing:.08em;
  text-transform:uppercase; color:#6C7683}
.viewer canvas{display:block; width:100%; height:auto; background:#000; cursor:crosshair}
.viewer-hud{display:flex; justify-content:space-between; padding:7px 12px; border-top:1px solid #1B1E22;
  font-family:var(--mono); font-size:11.5px; color:#98A2AE; font-variant-numeric:tabular-nums}
.viewer-hud b{color:#E8EBEF; font-weight:500}
.sliders{display:grid; gap:11px; padding:13px 14px 15px; background:var(--surface-2);
  border-top:1px solid var(--line)}
.sl{display:grid; grid-template-columns:100px 1fr 56px; gap:11px; align-items:center;
  font-family:var(--mono); font-size:11.5px; color:var(--muted)}
.sl output{text-align:right; color:var(--ink); font-variant-numeric:tabular-nums}
.sl input[type=range]{-webkit-appearance:none; appearance:none; height:3px; background:var(--line); border-radius:3px}
.sl input[type=range]::-webkit-slider-thumb{-webkit-appearance:none; width:14px;height:14px;border-radius:50%;
  background:var(--overlay); cursor:pointer; border:2px solid var(--surface)}
.sl input[type=range]::-moz-range-thumb{width:14px;height:14px;border-radius:50%;background:var(--overlay);
  cursor:pointer; border:2px solid var(--surface)}
.presets{display:flex; gap:6px; flex-wrap:wrap; padding:0 14px 14px; background:var(--surface-2)}
.pz{padding:4px 10px; border:1px solid var(--line); border-radius:20px; font-size:11.5px;
  font-family:var(--mono); color:var(--muted)}
.pz:hover{border-color:var(--faint); color:var(--ink)}
.pz.on{background:var(--ink); color:var(--ground); border-color:var(--ink)}
.viewer-note{font-size:12.5px; color:var(--faint); margin:12px 2px 0; line-height:1.6}

/* home sections */
.home-wrap{max-width:1120px; margin:0 auto; padding:46px 26px 90px}
.sec-title{font-family:var(--mono); font-size:11.5px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--faint); margin:0 0 20px; display:flex; align-items:center; gap:12px}
.sec-title::after{content:""; flex:1; height:1px; background:var(--line)}

.pipeline{display:flex; gap:0; flex-wrap:wrap; margin-bottom:56px; border:1px solid var(--line);
  border-radius:10px; overflow:hidden; background:var(--surface)}
.pstep{flex:1 1 150px; padding:16px 18px; border-right:1px solid var(--line-soft); min-width:0}
.pstep:last-child{border-right:none}
.pstep .n{font-family:var(--mono); font-size:10.5px; color:var(--overlay); letter-spacing:.1em}
.pstep .t{font-size:14.5px; font-weight:500; margin:5px 0 3px; font-family:var(--serif)}
.pstep .d{font-size:12.5px; color:var(--muted); line-height:1.55}

.mods{display:grid; grid-template-columns:repeat(auto-fill,minmax(268px,1fr)); gap:16px; margin-bottom:56px}
.mcard{
  background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:20px 20px 16px;
  text-decoration:none; display:flex; flex-direction:column; gap:9px; transition:border-color .16s ease, transform .16s ease;
}
.mcard:hover{border-color:var(--faint); transform:translateY(-2px)}
.mcard .top{display:flex; align-items:center; justify-content:space-between; gap:10px}
.mcard .big{font-family:var(--mono); font-size:26px; color:var(--faint); font-variant-numeric:tabular-nums; line-height:1}
.mcard .tag{font-size:10.5px; font-family:var(--mono); letter-spacing:.1em; text-transform:uppercase;
  color:var(--overlay); background:var(--overlay-soft); padding:2px 8px; border-radius:20px}
.mcard h3{font-family:var(--serif); font-size:18px; margin:2px 0 0; font-weight:600}
.mcard p{margin:0; font-size:13.5px; color:var(--muted); line-height:1.6; flex:1}
.mcard .foot{display:flex; align-items:center; gap:9px; font-family:var(--mono); font-size:11.5px;
  color:var(--faint); padding-top:10px; border-top:1px solid var(--line-soft)}
.bar{flex:1; height:3px; background:var(--sunken); border-radius:3px; overflow:hidden}
.bar span{display:block; height:100%; background:var(--overlay); width:0}

.road{border:1px solid var(--line); border-radius:10px; overflow:hidden; background:var(--surface)}
.rrow{display:grid; grid-template-columns:52px minmax(0,1fr) auto; gap:16px; align-items:baseline;
  padding:11px 18px; border-bottom:1px solid var(--line-soft); font-size:13.5px}
.rrow:last-child{border-bottom:none}
.rrow .rn{font-family:var(--mono); color:var(--faint); font-size:12px; font-variant-numeric:tabular-nums}
.rrow .rt{font-weight:500}
.rrow .rd{display:block; font-size:12.5px; color:var(--muted); font-weight:400; margin-top:1px}
.rrow .rs{font-family:var(--mono); font-size:10.5px; letter-spacing:.08em; color:var(--faint);
  border:1px solid var(--line); border-radius:20px; padding:2px 9px; white-space:nowrap}

/* ---------- article ---------- */
.art-head{margin:0 0 30px}
.art-kicker{font-family:var(--mono); font-size:11.5px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--overlay); margin:0 0 12px}
.art-head h2{font-family:var(--serif); font-size:clamp(26px,3.4vw,36px); line-height:1.22; margin:0;
  font-weight:600; text-wrap:balance; letter-spacing:-.01em}

article{font-size:16px; line-height:1.82; color:var(--ink-2)}
article h2{font-family:var(--serif); font-size:23px; line-height:1.32; margin:52px 0 14px; color:var(--ink);
  font-weight:600; text-wrap:balance; scroll-margin-top:70px}
article h3{font-family:var(--serif); font-size:18.5px; margin:34px 0 10px; color:var(--ink); font-weight:600;
  scroll-margin-top:70px}
article h4{font-size:15px; margin:26px 0 8px; color:var(--ink); font-weight:600}
article p{margin:0 0 18px}
article strong{color:var(--ink); font-weight:600}
article ul,article ol{margin:0 0 20px; padding-left:1.35em}
article li{margin-bottom:7px}
article li::marker{color:var(--faint)}
article li.task{list-style:none; margin-left:-1.35em; padding-left:1.9em; position:relative}
article li.task::before{content:""; position:absolute; left:.15em; top:.62em; width:11px; height:11px;
  border:1.5px solid var(--faint); border-radius:3px}
article a.xref{color:var(--overlay); text-decoration:none; border-bottom:1px solid color-mix(in srgb,var(--overlay) 34%, transparent)}
article a.xref:hover{border-bottom-color:var(--overlay)}
article a.ext{color:var(--ink); text-decoration:none; border-bottom:1px solid var(--line);
  word-break:break-all}
article a.ext:hover{border-bottom-color:var(--faint)}
article .soft-link{color:var(--muted)}
article code{font-family:var(--mono); font-size:.875em; background:var(--sunken); padding:1.5px 5px;
  border-radius:4px; border:1px solid var(--line-soft)}

.tw{overflow-x:auto; margin:0 0 24px; border:1px solid var(--line); border-radius:8px; background:var(--surface)}
table{border-collapse:collapse; width:100%; font-size:14px}
th,td{text-align:left; padding:10px 14px; border-bottom:1px solid var(--line-soft); vertical-align:top}
th{background:var(--surface-2); font-weight:600; color:var(--ink); font-size:12.5px;
  letter-spacing:.02em; white-space:nowrap}
tbody tr:last-child td{border-bottom:none}
td code{background:transparent; border:none; padding:0}

.code{position:relative; margin:0 0 24px; border:1px solid var(--line); border-radius:8px;
  background:var(--sunken); overflow:hidden}
.code::before{content:attr(data-lang); position:absolute; top:0; left:0; font-family:var(--mono);
  font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--faint);
  padding:6px 10px}
.code pre{margin:0; padding:30px 14px 14px; overflow-x:auto}
.code code{font-family:var(--mono); font-size:13px; line-height:1.7; background:none; border:none;
  padding:0; color:var(--ink-2); white-space:pre}
.copy{position:absolute; top:4px; right:6px; font-family:var(--mono); font-size:10.5px;
  color:var(--faint); padding:4px 8px; border-radius:5px; opacity:0; transition:opacity .15s}
.code:hover .copy,.copy:focus-visible{opacity:1}
.copy:hover{background:var(--surface); color:var(--ink)}
.c-kw{color:var(--overlay)}
.c-str{color:var(--amber)}
.c-com{color:var(--faint); font-style:italic}
.c-num{color:var(--ink)}

blockquote.pull{margin:0 0 24px; padding:14px 20px; border-left:2px solid var(--overlay);
  background:var(--overlay-soft); border-radius:0 8px 8px 0}
blockquote.pull p{margin:0; color:var(--ink); font-family:var(--serif); font-size:16.5px; line-height:1.7}
blockquote.pull p+p{margin-top:10px}

.fig{margin:0 0 26px; padding:0}
.fig img{width:100%; height:auto; display:block; border:1px solid var(--line); border-radius:8px;
  background:var(--surface)}
.fig figcaption{font-size:12.5px; color:var(--faint); margin-top:9px; line-height:1.6; text-align:center}
.fig-missing{padding:26px; border:1px dashed var(--line); border-radius:8px; text-align:center;
  color:var(--faint); font-size:13px; font-family:var(--mono)}

.pending{margin:0 0 26px; padding:22px; border:1px dashed var(--line); border-radius:8px;
  text-align:center; color:var(--faint); font-size:12.5px; font-family:var(--mono)}
.eq{margin:0 0 24px; padding:18px 14px; background:var(--surface); border:1px solid var(--line);
  border-radius:8px; overflow-x:auto; text-align:center}
.math{font-family:var(--serif); font-size:1.02em; white-space:nowrap}
.math-display{font-size:1.15em}
.math i{font-style:italic; padding-right:.02em}
.math .mup{font-style:normal; font-family:var(--sans); font-size:.92em}
.math .mbold{font-weight:600}
.math .mop{padding:0 .22em}
.math .mthin{padding:0 .1em}
.math sub,.math sup{font-size:.68em}
.frac{display:inline-flex; flex-direction:column; vertical-align:-.55em; text-align:center;
  padding:0 .25em}
.frac .fnum{border-bottom:1px solid currentColor; padding:0 .3em .08em}
.frac .fden{padding:.08em .3em 0}
.mat{display:inline-flex; flex-direction:column; vertical-align:middle; padding:.1em .45em;
  border-left:1.5px solid currentColor; border-right:1.5px solid currentColor; margin:0 .15em}
.mat .mrow{line-height:1.5}

/* article footer */
.done-row{margin-top:56px; padding-top:24px; border-top:1px solid var(--line); display:flex;
  gap:12px; align-items:center; flex-wrap:wrap}
.done-btn{display:inline-flex; align-items:center; gap:9px; padding:9px 17px; border-radius:7px;
  border:1px solid var(--line); font-size:13.5px; color:var(--muted)}
.done-btn:hover{border-color:var(--faint); color:var(--ink)}
.done-btn.on{background:var(--overlay); border-color:var(--overlay); color:#fff}
.done-btn .tick{width:14px;height:14px}
.pager{display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:22px}
.pg{padding:14px 16px; border:1px solid var(--line); border-radius:8px; text-decoration:none;
  background:var(--surface); display:flex; flex-direction:column; gap:3px; min-width:0}
.pg:hover{border-color:var(--faint)}
.pg span{font-family:var(--mono); font-size:10.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--faint)}
.pg b{font-weight:500; font-size:14px; color:var(--ink); overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.pg.next{text-align:right; align-items:flex-end}
@media (max-width:600px){ .pager{grid-template-columns:1fr} }

/* mini toc */
.toc{position:sticky; top:76px; align-self:start; padding:40px 0 40px; display:none}
@media (min-width:1300px){ .page.reading .toc{display:block} }
.toc h4{font-family:var(--mono); font-size:10.5px; letter-spacing:.12em; text-transform:uppercase;
  color:var(--faint); margin:0 0 12px; font-weight:500}
.toc a{display:block; font-size:12.5px; color:var(--muted); text-decoration:none; padding:4px 0 4px 12px;
  border-left:1px solid var(--line-soft); line-height:1.5}
.toc a:hover{color:var(--ink)}
.toc a.on{color:var(--overlay); border-left-color:var(--overlay)}
.toc a.lv3{padding-left:24px; font-size:12px}

.empty{padding:60px 0; text-align:center; color:var(--faint); font-size:14px}
@media (prefers-reduced-motion:reduce){ *{animation:none!important; transition:none!important;
  scroll-behavior:auto!important} }
"""
