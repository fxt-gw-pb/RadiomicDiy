from __future__ import annotations

import html
import json
import re
from pathlib import Path

import mdconv
from build_css import CSS
from structure import MODULES, ROADMAP, ROOT

OUT = Path(__file__).resolve().parent / "radiomics_site.html"

# ---------------------------------------------------------------- index pass
chapters: list[dict] = []
path_to_id: dict[str, str] = {}

for mod in MODULES:
    base = ROOT if mod["dir"] == "." else ROOT / mod["dir"]
    for n, fname in enumerate(mod["files"], 1):
        p = (base / fname).resolve()
        if not p.is_file():
            raise SystemExit(f"missing: {p}")
        cid = f"{mod['id']}-{n:02d}"
        path_to_id[str(p)] = cid
        chapters.append({"id": cid, "mod": mod["id"], "path": p, "file": fname})


def resolver(target: str):
    if target.startswith(("http://", "https://", "mailto:")):
        return target
    if target.startswith("#"):
        return target
    clean = target.split("#")[0]
    for cand in (
        (Path(current_dir[0]) / clean).resolve(),
        (ROOT / clean).resolve(),
    ):
        if str(cand) in path_to_id:
            return "#/" + path_to_id[str(cand)]
        if cand.is_dir():
            for mod in MODULES:
                if (ROOT / mod["dir"]).resolve() == cand:
                    first = [c for c in chapters if c["mod"] == mod["id"]]
                    if first:
                        return "#/" + first[0]["id"]
            return None
    return None


current_dir = [str(ROOT)]

# ---------------------------------------------------------------- convert
for ch in chapters:
    current_dir[0] = str(ch["path"].parent)
    title, body, heads = mdconv.convert_file(ch["path"], resolver)
    if ch["file"] == "README.md":
        title = "模块导览"
    ch["title"] = title
    ch["body"] = body
    ch["heads"] = heads

by_mod = {m["id"]: [c for c in chapters if c["mod"] == m["id"]] for m in MODULES}
order = [c["id"] for c in chapters]

# ---------------------------------------------------------------- nav markup
def ring(pid: str) -> str:
    return (f"<svg class='ring' viewBox='0 0 24 24' data-ring='{pid}' aria-hidden='true'>"
            "<circle class='bg' cx='12' cy='12' r='9'></circle>"
            "<circle class='fg' cx='12' cy='12' r='9' stroke-dasharray='56.5' "
            "stroke-dashoffset='56.5'></circle></svg>")


CHEV = ("<svg class='chev' viewBox='0 0 16 16' aria-hidden='true'>"
        "<path d='M6 3l5 5-5 5' fill='none' stroke='currentColor' stroke-width='1.6' "
        "stroke-linecap='round' stroke-linejoin='round'/></svg>")

nav_parts = []
for mod in MODULES:
    items = "".join(
        f"<a class='ch' href='#/{c['id']}' data-ch='{c['id']}'>"
        f"<i class='dot'></i><span>{html.escape(c['title'])}</span></a>"
        for c in by_mod[mod["id"]])
    nav_parts.append(
        f"<div class='mod' data-mod='{mod['id']}' data-open='{1 if mod['id'] == 'm00' else 0}'>"
        f"<button class='mod-head' type='button'>{CHEV}"
        f"<span class='mod-num'>{mod['num']}</span>"
        f"<span class='mod-name'>{html.escape(mod['name'])}</span>"
        f"{ring(mod['id'])}</button>"
        f"<div class='mod-list'>{items}</div></div>")
nav_html = "".join(nav_parts)

# ---------------------------------------------------------------- home
PIPELINE = [
    ("数据", "扫描出来的是什么", "DICOM、NIfTI、spacing 与方向"),
    ("表示", "计算机看到什么", "voxel、HU、三维数组与几何"),
    ("处理", "送进模型前做什么", "重采样、归一化、ROI"),
    ("学习", "模型学到什么", "特征、CNN、分割、Transformer"),
    ("评价", "结果可信吗", "AUC、校准、外部验证"),
    ("医学意义", "对病人有用吗", "临床问题与决策价值"),
]
pipeline_html = "".join(
    f"<div class='pstep'><div class='n'>{i+1:02d}</div><div class='t'>{t}</div>"
    f"<div class='d'>{q}<br>{d}</div></div>"
    for i, (t, q, d) in enumerate(PIPELINE))

mcards = "".join(
    f"<a class='mcard' href='#/{by_mod[m['id']][0]['id']}' data-card='{m['id']}'>"
    f"<div class='top'><span class='big'>{m['num']}</span>"
    f"<span class='tag'>{m['tag']}</span></div>"
    f"<h3>{html.escape(m['name'])}</h3><p>{html.escape(m['blurb'])}</p>"
    f"<div class='foot'><span data-count='{m['id']}'>0 / {len(by_mod[m['id']])}</span>"
    f"<span class='bar'><span data-fill='{m['id']}'></span></span></div></a>"
    for m in MODULES)

road_html = "".join(
    f"<div class='rrow'><span class='rn'>{n}</span>"
    f"<span class='rt'>{html.escape(t)}<span class='rd'>{html.escape(d)}</span></span>"
        f"<span class='rs'>规划中</span></div>"
    for n, t, d in ROADMAP)

total_ch = len(chapters)

HOME = f"""
<section class="hero">
  <div class="hero-in">
    <div>
      <p class="eyebrow">医学影像 AI · 自学知识库</p>
      <h2>一份 CT，在计算机眼里其实是<em>带着物理坐标的数字</em></h2>
      <p class="lede">这套知识库写给从医学、公共卫生或临床科研走进影像 AI 的人。
      不假设你写过深度学习代码，但假设你想真正弄懂每一步在做什么——
      而不是把别人的脚本跑通就算数。</p>
      <div class="cta-row">
        <a class="cta" href="#/{chapters[0]['id']}">从第一章开始</a>
        <a class="cta ghost" href="#modules">看看有哪些模块</a>
      </div>
    </div>
    <div>
      <div class="viewer">
        <div class="viewer-top"><span>AXIAL · SYNTHETIC PHANTOM</span><span id="vSlice">z 12 / 24</span></div>
        <canvas id="phantom" width="384" height="384" aria-label="可交互的合成 CT 断面"></canvas>
        <div class="viewer-hud"><span>光标处 <b id="vHU">—</b> HU</span><span id="vWin">C 40 / W 400</span></div>
        <div class="sliders">
          <label class="sl"><span>window center</span>
            <input id="wc" type="range" min="-1000" max="1000" step="10" value="40">
            <output id="wcOut">40</output></label>
          <label class="sl"><span>window width</span>
            <input id="ww" type="range" min="40" max="2000" step="20" value="400">
            <output id="wwOut">400</output></label>
        </div>
        <div class="presets">
          <button class="pz on" type="button" data-c="40" data-w="400">软组织窗</button>
          <button class="pz" type="button" data-c="-600" data-w="1500">肺窗</button>
          <button class="pz" type="button" data-c="400" data-w="1800">骨窗</button>
          <button class="pz" type="button" data-c="40" data-w="80">脑窗</button>
        </div>
      </div>
      <p class="viewer-note">拖动滑块，或点一个窗位预设。同一份数据、同一层，
      只因为显示区间不同就完全变了样——这正是第 01 模块要讲清楚的第一件事。
      把鼠标移到图上可以读出该点的 HU 值。</p>
    </div>
  </div>
</section>
<div class="home-wrap">
  <p class="sec-title">这套知识库怎么组织</p>
  <div class="pipeline">{pipeline_html}</div>

  <p class="sec-title" id="modules">现在可以学的模块</p>
  <div class="mods">{mcards}</div>

  <p class="sec-title">后续模块</p>
  <div class="road">{road_html}</div>
</div>
"""

# ---------------------------------------------------------------- docs
docs = []
for idx, c in enumerate(chapters):
    mod = next(m for m in MODULES if m["id"] == c["mod"])
    prev_c = chapters[idx - 1] if idx else None
    next_c = chapters[idx + 1] if idx + 1 < len(chapters) else None
    pager = ""
    if prev_c:
        pager += (f"<a class='pg prev' href='#/{prev_c['id']}'><span>上一篇</span>"
                  f"<b>{html.escape(prev_c['title'])}</b></a>")
    else:
        pager += "<span></span>"
    if next_c:
        pager += (f"<a class='pg next' href='#/{next_c['id']}'><span>下一篇</span>"
                  f"<b>{html.escape(next_c['title'])}</b></a>")
    toc = "".join(
        f"<a href='#{hid}' class='lv{lv}'>{html.escape(t)}</a>"
        for lv, t, hid in c["heads"] if lv in (2, 3))
    docs.append(
        f"<div class='doc' id='doc-{c['id']}' hidden>"
        f"<div class='page reading'><div class='wrap'>"
        f"<header class='art-head'><p class='art-kicker'>模块 {mod['num']} · {html.escape(mod['name'])}</p>"
        f"<h2>{html.escape(c['title'])}</h2></header>"
        f"<article>{c['body']}</article>"
        f"<div class='done-row'><button class='done-btn' type='button' data-done='{c['id']}'>"
        f"<svg class='tick' viewBox='0 0 16 16' aria-hidden='true'><path d='M3 8.5l3.5 3.5L13 5' "
        f"fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' "
        f"stroke-linejoin='round'/></svg><span>标记为已学完</span></button></div>"
        f"<nav class='pager'>{pager}</nav>"
        f"</div><aside class='toc'><h4>本页目录</h4>{toc}</aside></div></div>")

meta = {c["id"]: {"t": c["title"], "m": c["mod"],
                  "h": [t for lv, t, _ in c["heads"]]} for c in chapters}
mod_meta = {m["id"]: {"n": m["name"], "num": m["num"],
                      "ch": [c["id"] for c in by_mod[m["id"]]]} for m in MODULES}

JS = r"""
const META = __META__, MODS = __MODS__, ORDER = __ORDER__;
const KEY = 'mia.progress.v1', TKEY = 'mia.theme.v1';
let done = new Set();
try { done = new Set(JSON.parse(localStorage.getItem(KEY) || '[]')); } catch (e) {}
const save = () => { try { localStorage.setItem(KEY, JSON.stringify([...done])); } catch (e) {} };

const $ = (s, r) => (r || document).querySelector(s);
const $$ = (s, r) => [...(r || document).querySelectorAll(s)];

/* ---------- theme ---------- */
try { const t = localStorage.getItem(TKEY); if (t) document.documentElement.dataset.theme = t; } catch (e) {}
$('#themeBtn').addEventListener('click', () => {
  const cur = document.documentElement.dataset.theme
    || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem(TKEY, next); } catch (e) {}
  paintPhantom();
});

/* ---------- progress ---------- */
function refresh() {
  for (const id in MODS) {
    const list = MODS[id].ch, n = list.filter(c => done.has(c)).length;
    const ring = $(`[data-ring="${id}"] .fg`);
    if (ring) ring.style.strokeDashoffset = 56.5 * (1 - n / list.length);
    const cnt = $(`[data-count="${id}"]`);
    if (cnt) cnt.textContent = n + ' / ' + list.length;
    const fill = $(`[data-fill="${id}"]`);
    if (fill) fill.style.width = (100 * n / list.length) + '%';
  }
  $$('.ch').forEach(a => a.classList.toggle('done', done.has(a.dataset.ch)));
  $$('[data-done]').forEach(b => {
    const on = done.has(b.dataset.done);
    b.classList.toggle('on', on);
    $('span', b).textContent = on ? '已学完' : '标记为已学完';
  });
}
document.addEventListener('click', e => {
  const b = e.target.closest('[data-done]');
  if (!b) return;
  const id = b.dataset.done;
  done.has(id) ? done.delete(id) : done.add(id);
  save(); refresh();
});

/* ---------- nav ---------- */
$$('.mod-head').forEach(h => h.addEventListener('click', () => {
  const m = h.parentElement;
  m.dataset.open = m.dataset.open === '1' ? '0' : '1';
}));
$('#menuBtn').addEventListener('click', () => $('.rail').classList.toggle('open'));

/* ---------- search ---------- */
$('#q').addEventListener('input', e => {
  const v = e.target.value.trim().toLowerCase();
  if (!v) {
    $$('.ch').forEach(a => a.style.display = '');
    $$('.mod').forEach(m => m.dataset.open = m.dataset.open === '1' ? '1' : '0');
    return;
  }
  $$('.mod').forEach(m => {
    let hit = 0;
    $$('.ch', m).forEach(a => {
      const d = META[a.dataset.ch];
      const hay = (d.t + ' ' + d.h.join(' ')).toLowerCase();
      const ok = hay.includes(v);
      a.style.display = ok ? '' : 'none';
      if (ok) hit++;
    });
    m.dataset.open = hit ? '1' : '0';
  });
});

/* ---------- copy ---------- */
document.addEventListener('click', e => {
  const b = e.target.closest('.copy');
  if (!b) return;
  const code = $('code', b.parentElement);
  navigator.clipboard.writeText(code.innerText).then(() => {
    b.textContent = '已复制';
    setTimeout(() => (b.textContent = '复制'), 1400);
  }).catch(() => { b.textContent = '复制失败'; });
});

/* ---------- router ---------- */
const scroller = $('.scroll');
function route() {
  const h = location.hash.replace(/^#/, '');
  const id = h.startsWith('/') ? h.slice(1) : '';
  const doc = id && $('#doc-' + id);
  $('#home').hidden = !!doc;
  $$('.doc').forEach(d => (d.hidden = true));
  $$('.ch').forEach(a => a.classList.toggle('active', a.dataset.ch === id));
  if (doc) {
    doc.hidden = false;
    const m = MODS[META[id].m];
    $('#crumb').innerHTML = `模块 ${m.num} · ${m.n} <b>/</b> ${META[id].t}`;
    const mod = $(`[data-mod="${META[id].m}"]`);
    if (mod) mod.dataset.open = '1';
    buildSpy(doc);
  } else {
    $('#crumb').innerHTML = '<b>医学影像 AI 自学知识库</b>';
    if (h && h !== '/' && $('#' + h)) {
      $('#' + h).scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
  }
  scroller.scrollTop = 0;
  $('.rail').classList.remove('open');
}
addEventListener('hashchange', route);

/* keyboard: ← / → move between chapters */
addEventListener('keydown', e => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if (/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)) return;
  const id = location.hash.replace('#/', '');
  const i = ORDER.indexOf(id);
  if (i < 0) return;
  if (e.key === 'ArrowRight' && i + 1 < ORDER.length) location.hash = '#/' + ORDER[i + 1];
  if (e.key === 'ArrowLeft' && i > 0) location.hash = '#/' + ORDER[i - 1];
});

/* ---------- toc spy + read bar ---------- */
let spy = [];
function buildSpy(doc) {
  spy = $$('.toc a', doc).map(a => ({ a, el: $(a.getAttribute('href'), doc) })).filter(x => x.el);
}
scroller.addEventListener('scroll', () => {
  const max = scroller.scrollHeight - scroller.clientHeight;
  $('#readbar').style.width = (max > 40 ? (scroller.scrollTop / max) * 100 : 0) + '%';
  let cur = null;
  for (const s of spy) if (s.el.getBoundingClientRect().top < 120) cur = s;
  spy.forEach(s => s.a.classList.toggle('on', s === cur));
}, { passive: true });

document.addEventListener('click', e => {
  const a = e.target.closest('.toc a');
  if (!a) return;
  e.preventDefault();
  const el = $(a.getAttribute('href'));
  if (el) scroller.scrollTo({ top: el.offsetTop - 24, behavior: 'smooth' });
});

/* ---------- phantom viewer ---------- */
const N = 384, hu = new Float32Array(N * N);
(function build() {
  let seed = 20260827;
  const rnd = () => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
  const ell = (x, y, cx, cy, rx, ry) => ((x-cx)*(x-cx))/(rx*rx) + ((y-cy)*(y-cy))/(ry*ry);
  // physical field: 1 px = 1 mm, origin at image centre
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    const x = c - N/2, y = r - N/2;
    let v = -1000;                                   // air outside the patient
    if (ell(x, y, 0, 6, 170, 118) <= 1) v = -108;    // subcutaneous fat
    if (ell(x, y, 0, 6, 156, 104) <= 1) v = 44;      // muscle / soft tissue
    // lung fields
    const lL = ell(x, y, -78, 2, 62, 84), lR = ell(x, y, 78, 2, 62, 84);
    if (lL <= 1 || lR <= 1) {
      v = -830 + rnd() * 40;
      // pulmonary vessels: a few branching blobs
      const vs = [[-96,-46,7],[-66,26,6],[-52,-18,5],[-88,52,5],[86,-40,7],[62,22,6],
                  [96,34,5],[70,-58,5],[-74,-66,4],[80,60,4]];
      for (const [vx, vy, vr] of vs) if ((x-vx)*(x-vx)+(y-vy)*(y-vy) <= vr*vr) v = 35;
    }
    // mediastinum + heart
    if (ell(x, y, 6, 34, 54, 46) <= 1) v = 48;
    if (ell(x, y, -4, -44, 26, 22) <= 1) v = 32;     // trachea region soft tissue
    if (ell(x, y, -4, -44, 9, 8) <= 1) v = -960;     // trachea lumen (air)
    // vertebral body + canal
    if (ell(x, y, 0, 82, 28, 24) <= 1) v = 260;
    if (ell(x, y, 0, 82, 22, 18) <= 1) v = 160;
    if (ell(x, y, 0, 74, 9, 7) <= 1) v = 30;
    if (ell(x, y, 0, 82, 28, 24) <= 1 && ell(x, y, 0, 82, 25, 21) > 1) v = 950;
    // ribs: bright arcs on the body outline
    const ang = Math.atan2(y - 6, x), rad = Math.sqrt(ell(x, y, 0, 6, 152, 102));
    if (rad > 0.965 && rad < 1.005 && Math.abs(Math.sin(ang * 7)) > 0.9) {
      v = 720 + rnd() * 120;
      if (rad > 0.978 && rad < 0.992 && Math.abs(Math.sin(ang * 7)) > 0.965) v = 210;
    }
    // the nodule this whole site is about
    const d2 = (x + 62) * (x + 62) + (y - 44) * (y - 44);
    if (d2 <= 15 * 15) v = 62;
    if (d2 <= 6 * 6) v = 14;                          // small necrotic-looking core
    hu[r * N + c] = v + (rnd() - 0.5) * 22;
  }
})();
const cv = $('#phantom'), ctx = cv.getContext('2d'), img = ctx.createImageData(N, N);
let cur = null;
function paintPhantom() {
  const c0 = +$('#wc').value, w0 = +$('#ww').value, lo = c0 - w0 / 2;
  const d = img.data;
  for (let i = 0; i < N * N; i++) {
    let g = ((hu[i] - lo) / w0) * 255;
    g = g < 0 ? 0 : g > 255 ? 255 : g;
    d[i * 4] = d[i * 4 + 1] = d[i * 4 + 2] = g; d[i * 4 + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  if (cur) {
    ctx.strokeStyle = 'rgba(255,122,98,.85)'; ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(cur[0] + .5, 0); ctx.lineTo(cur[0] + .5, N);
    ctx.moveTo(0, cur[1] + .5); ctx.lineTo(N, cur[1] + .5);
    ctx.stroke();
  }
  $('#vWin').textContent = `C ${c0} / W ${w0}`;
  $('#wcOut').value = c0; $('#wwOut').value = w0;
}
['wc', 'ww'].forEach(id => $('#' + id).addEventListener('input', () => {
  $$('.pz').forEach(p => p.classList.remove('on'));
  paintPhantom();
}));
$$('.pz').forEach(p => p.addEventListener('click', () => {
  $$('.pz').forEach(q => q.classList.remove('on'));
  p.classList.add('on');
  $('#wc').value = p.dataset.c; $('#ww').value = p.dataset.w;
  paintPhantom();
}));
function track(e) {
  const b = cv.getBoundingClientRect();
  const pt = e.touches ? e.touches[0] : e;
  const c = Math.floor((pt.clientX - b.left) / b.width * N);
  const r = Math.floor((pt.clientY - b.top) / b.height * N);
  if (r >= 0 && r < N && c >= 0 && c < N) {
    cur = [c, r];
    $('#vHU').textContent = Math.round(hu[r * N + c]);
    paintPhantom();
  }
}
cv.addEventListener('mousemove', track);
cv.addEventListener('touchmove', e => { e.preventDefault(); track(e); }, { passive: false });
cv.addEventListener('mouseleave', () => { cur = null; $('#vHU').textContent = '—'; paintPhantom(); });
paintPhantom();

refresh();
route();
"""

JS = (JS.replace("__META__", json.dumps(meta, ensure_ascii=False))
        .replace("__MODS__", json.dumps(mod_meta, ensure_ascii=False))
        .replace("__ORDER__", json.dumps(order)))

HTML = f"""<meta charset="utf-8">
<title>医学影像 AI 自学室</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Sans:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap">
<style>{CSS}</style>

<div class="shell">
  <aside class="rail">
    <div class="brand">
      <div class="mark" aria-hidden="true"></div>
      <div><h1>医学影像 AI 自学室</h1><p>Radiomics · Self-study</p></div>
    </div>
    <div class="search"><input id="q" type="search" placeholder="搜索章节或小节…" aria-label="搜索"></div>
    <nav class="nav">
      <a class="ch" href="#/" style="margin:0 0 6px"><i class="dot"></i><span>首页</span></a>
      {nav_html}
    </nav>
    <div class="rail-foot">
      <button class="tbtn" id="themeBtn" type="button">切换明暗</button>
      <span style="font-family:var(--mono);font-size:11px;color:var(--faint)">共 {total_ch} 篇</span>
    </div>
  </aside>

  <div class="main">
    <div class="topbar">
      <button class="menu" id="menuBtn" type="button">目录</button>
      <span class="crumb" id="crumb"></span>
      <span class="readbar" id="readbar"></span>
    </div>
    <div class="scroll">
      <div id="home">{HOME}</div>
      {''.join(docs)}
    </div>
  </div>
</div>
<script>{JS}</script>
"""

OUT.write_text(HTML, encoding="utf-8")
print(f"written {OUT}  {OUT.stat().st_size/1024/1024:.2f} MB")
print(f"chapters: {len(chapters)}")
