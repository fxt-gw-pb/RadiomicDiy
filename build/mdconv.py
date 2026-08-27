"""Markdown -> HTML converter tailored to this knowledge base."""
from __future__ import annotations

import base64
import html
import io
import os
import re
from pathlib import Path

from PIL import Image

# 知识库 Markdown 的位置；换机器时用 MIA_ROOT 环境变量覆盖
ROOT = Path(os.environ.get(
    "MIA_ROOT",
    "/Users/fpb/Obsidian_Vault/self-learning/radiomics/medical_imaging_ai_selfstudy"))

# ---------------------------------------------------------------- images
_image_cache: dict[str, str] = {}


def _find_asset(name: str) -> Path | None:
    for base in ROOT.rglob(name):
        return base
    return None


def data_uri(path: Path, max_width: int = 1080, quality: int = 74) -> str:
    key = str(path)
    if key in _image_cache:
        return _image_cache[key]
    im = Image.open(path)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    if im.width > max_width:
        h = round(im.height * max_width / im.width)
        im = im.resize((max_width, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="WEBP", quality=quality, method=5)
    uri = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
    _image_cache[key] = uri
    return uri


# ---------------------------------------------------------------- math
GREEK = {"sigma": "σ", "mu": "μ", "alpha": "α", "beta": "β", "gamma": "γ",
         "Delta": "Δ", "delta": "δ", "theta": "θ", "lambda": "λ", "pi": "π"}
SYMBOLS = {"times": "×", "cdot": "·", "le": "≤", "ge": "≥", "leq": "≤", "geq": "≥",
           "approx": "≈", "pm": "±", "cap": "∩", "cup": "∪", "to": "→",
           "rightarrow": "→", "ldots": "…", "dots": "…", "infty": "∞", "neq": "≠"}


def _take_group(s: str, i: int) -> tuple[str, int]:
    """s[i] == '{' -> return (inner, index after matching '}')."""
    depth, j = 0, i
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def _matrix(body: str) -> str:
    rows = [r.strip() for r in body.split(r"\\") if r.strip()]
    cells = "".join(f"<span class='mrow'>{tex(r)}</span>" for r in rows)
    return f"<span class='mat'>{cells}</span>"


def tex(s: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+)", s[i:])
            if m:
                name = m.group(1)
                i += len(m.group(0))
                if name in ("text", "mathrm", "mathbf", "operatorname"):
                    if i < len(s) and s[i] == "{":
                        inner, i = _take_group(s, i)
                        cls = "mup mbold" if name == "mathbf" else "mup"
                        out.append(f"<span class='{cls}'>{html.escape(inner)}</span>")
                    continue
                if name in ("frac", "dfrac", "tfrac"):
                    num, i = _take_group(s, i) if i < len(s) and s[i] == "{" else ("", i)
                    while i < len(s) and s[i] == " ":
                        i += 1
                    den, i = _take_group(s, i) if i < len(s) and s[i] == "{" else ("", i)
                    out.append("<span class='frac'><span class='fnum'>"
                               f"{tex(num)}</span><span class='fden'>{tex(den)}</span></span>")
                    continue
                if name == "begin":
                    env, i = _take_group(s, i)
                    end = s.find("\\end{" + env + "}", i)
                    body = s[i:end if end != -1 else len(s)]
                    i = (end + len("\\end{" + env + "}")) if end != -1 else len(s)
                    out.append(_matrix(body))
                    continue
                if name in ("left", "right"):
                    continue
                if name in GREEK:
                    out.append(f"<i>{GREEK[name]}</i>")
                    continue
                if name in SYMBOLS:
                    out.append(f"<span class='mop'>{SYMBOLS[name]}</span>")
                    continue
                continue
            i += 1
            if i <= len(s) and s[i - 1] in ",;! ":
                out.append("<span class='mthin'></span>")
            continue
        if c in "_^":
            i += 1
            if i < len(s) and s[i] == "{":
                inner, i = _take_group(s, i)
            else:
                inner, i = s[i], i + 1
            tag = "sub" if c == "_" else "sup"
            out.append(f"<{tag}>{tex(inner)}</{tag}>")
            continue
        if c == "{" :
            inner, i = _take_group(s, i)
            out.append(tex(inner))
            continue
        if c.isalpha():
            j = i
            while j < len(s) and s[j].isalpha():
                j += 1
            word = s[i:j]
            i = j
            out.append(f"<i>{html.escape(word)}</i>" if len(word) <= 2
                       else f"<span class='mup'>{html.escape(word)}</span>")
            continue
        if c in "+-=<>":
            out.append(f"<span class='mop'>{html.escape(c)}</span>")
            i += 1
            continue
        out.append(html.escape(c))
        i += 1
    return "".join(out)


def render_math(text: str, display: bool = False) -> str:
    cls = "math math-display" if display else "math"
    return f"<span class='{cls}'>{tex(text.strip())}</span>"


# ---------------------------------------------------------------- inline
def inline(text: str, link_resolver=None) -> str:
    parts: list[str] = []
    # protect code spans and math first
    tokens: list[str] = []

    def stash(rendered: str) -> str:
        tokens.append(rendered)
        return f"\x00{len(tokens) - 1}\x00"

    def repl_code(m):
        return stash(f"<code>{html.escape(m.group(1))}</code>")

    def repl_math(m):
        return stash(render_math(m.group(1)))

    text = re.sub(r"`([^`]+)`", repl_code, text)
    text = re.sub(r"\$([^$\n]+)\$", repl_math, text)

    text = html.escape(text)

    def repl_link(m):
        label, target = m.group(1), m.group(2)
        href = link_resolver(target) if link_resolver else target
        if href is None:
            return f"<span class='soft-link'>{label}</span>"
        if href.startswith("http"):
            return (f"<a href='{href}' target='_blank' rel='noopener' "
                    f"class='ext'>{label}</a>")
        return f"<a href='{href}' class='xref'>{label}</a>"

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl_link, text)
    text = re.sub(r"(?<!\")(?<![>=])(https?://[^\s<>\u4e00-\u9fff）)，。]+)",
                  lambda m: stash("<a href='" + m.group(1) + "' target='_blank' "
                                  "rel='noopener' class='ext'>" + m.group(1) + "</a>"), text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![A-Za-z0-9])_([^_\n]+)_(?![A-Za-z0-9])", r"<em>\1</em>", text)
    text = text.replace("\n", "<br>")
    for idx, tok in enumerate(tokens):
        text = text.replace(f"\x00{idx}\x00", tok)
    parts.append(text)
    return "".join(parts)


# ---------------------------------------------------------------- blocks
def _join(segments: list[str]) -> str:
    """Join wrapped lines; two trailing spaces mean a hard line break."""
    out = ""
    for k, seg in enumerate(segments):
        if k:
            out += "\n" if out.endswith("  ") else " "
        out += seg
    return out


Q3D = chr(34) * 3
Q3S = chr(39) * 3

PROMPT_RE = re.compile(r"图片生成提示词\s+(IMG-\d{3})")


class Converter:
    def __init__(self, source: Path, link_resolver=None):
        self.source = source
        self.dir = source.parent
        self.link_resolver = link_resolver
        self.headings: list[tuple[int, str, str]] = []
        self._hid = 0

    # -- helpers
    def _il(self, t: str) -> str:
        return inline(t, self.link_resolver)

    def _heading_id(self, text: str) -> str:
        self._hid += 1
        return f"h{self._hid}"

    def _image_html(self, spec: str, caption: str = "") -> str:
        spec = spec.strip()
        path = None
        if spec.startswith("Pasted image") or "/" not in spec:
            path = _find_asset(spec)
        if path is None:
            candidate = (self.dir / spec).resolve()
            if candidate.is_file():
                path = candidate
        if path is None or not path.is_file():
            return (f"<figure class='fig missing'><div class='fig-missing'>"
                    f"缺少图片：{html.escape(spec)}</div></figure>")
        uri = data_uri(path)
        cap = f"<figcaption>{self._il(caption)}</figcaption>" if caption else ""
        return (f"<figure class='fig'><img src='{uri}' alt='{html.escape(caption or spec)}' "
                f"loading='lazy'>{cap}</figure>")

    # -- main
    def convert(self, text: str) -> str:
        lines = text.split("\n")
        out: list[str] = []
        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]
            stripped = line.strip()

            if not stripped:
                i += 1
                continue

            # display math
            if stripped == "$$":
                j = i + 1
                buf = []
                while j < n and lines[j].strip() != "$$":
                    buf.append(lines[j])
                    j += 1
                out.append(f"<div class='eq'>{render_math(' '.join(buf), True)}</div>")
                i = j + 1
                continue

            # fenced code
            if stripped.startswith("```"):
                lang = stripped[3:].strip() or "text"
                j = i + 1
                buf = []
                while j < n and not lines[j].strip().startswith("```"):
                    buf.append(lines[j])
                    j += 1
                out.append(self._code_block("\n".join(buf), lang))
                i = j + 1
                continue

            # headings
            m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
            if m:
                level = len(m.group(1))
                title = m.group(2).strip()
                if level == 1:
                    i += 1
                    continue  # page title handled outside
                hid = self._heading_id(title)
                self.headings.append((level, title, hid))
                out.append(f"<h{level} id='{hid}'>{self._il(title)}</h{level}>")
                i += 1
                continue

            # obsidian embed
            m = re.match(r"^!\[\[([^\]]+)\]\]$", stripped)
            if m:
                out.append(self._image_html(m.group(1)))
                i += 1
                continue

            # markdown image
            m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
            if m:
                out.append(self._image_html(m.group(2), m.group(1)))
                i += 1
                continue

            # blockquote (image prompt or plain)
            if stripped.startswith(">"):
                j = i
                buf = []
                while j < n and (lines[j].strip().startswith(">") or
                                 (lines[j].strip() == "" and j + 1 < n
                                  and lines[j + 1].strip().startswith(">"))):
                    buf.append(re.sub(r"^\s*>\s?", "", lines[j]))
                    j += 1
                block = "\n".join(buf)
                # trailing embedded picture belongs to the prompt card
                pic = ""
                k = j
                while k < n and lines[k].strip() == "":
                    k += 1
                if k < n:
                    mm = re.match(r"^!\[\[([^\]]+)\]\]$", lines[k].strip())
                    if mm and PROMPT_RE.search(block):
                        pic = self._image_html(mm.group(1))
                        j = k + 1
                out.append(self._quote_block(block, pic))
                i = j
                continue

            # table
            if stripped.startswith("|"):
                j = i
                buf = []
                while j < n and lines[j].strip().startswith("|"):
                    buf.append(lines[j].strip())
                    j += 1
                out.append(self._table(buf))
                i = j
                continue

            # lists (blank lines between items keep the same list)
            if re.match(r"^([-*]|\d+\.)\s+", stripped):
                j, buf = i, []
                while j < n:
                    ln = lines[j]
                    if re.match(r"^\s*([-*]|\d+\.)\s+", ln) or (ln.startswith("  ") and ln.strip()):
                        buf.append(ln.rstrip() + ("  " if ln.endswith("  ") else ""))
                        j += 1
                        continue
                    if not ln.strip():
                        k = j + 1
                        while k < n and not lines[k].strip():
                            k += 1
                        if k < n and re.match(r"^\s*([-*]|\d+\.)\s+", lines[k]):
                            j = k
                            continue
                    break
                out.append(self._list(buf))
                i = j
                continue

            # paragraph
            j, buf = i, []
            while j < n and lines[j].strip() and not re.match(
                    r"^\s*(#{1,4}\s|[-*]\s|\d+\.\s|\||>|```|\$\$|!\[)", lines[j]):
                buf.append(lines[j].strip() + ("  " if lines[j].endswith("  ") else ""))
                j += 1
            if not buf:
                buf = [stripped]
                j = i + 1
            para = _join(buf)
            out.append(f"<p>{self._il(para)}</p>")
            i = j
        return "\n".join(out)

    # -- block builders
    def _code_block(self, code: str, lang: str) -> str:
        label = {"python": "Python", "bash": "终端", "text": "输出",
                 "markdown": "Markdown"}.get(lang, lang)
        body = self._highlight(code, lang)
        return (f"<div class='code' data-lang='{html.escape(label)}'>"
                f"<button class='copy' type='button' aria-label='复制代码'>复制</button>"
                f"<pre><code>{body}</code></pre></div>")

    @staticmethod
    def _highlight(code: str, lang: str) -> str:
        """Line-based Python tokenizer; escapes as it goes so markup never re-matches."""
        def esc(s: str) -> str:
            return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

        if lang != "python":
            return esc(code)

        kw = {"import", "from", "def", "class", "return", "if", "elif", "else", "for",
              "while", "in", "not", "and", "or", "None", "True", "False", "with", "as",
              "try", "except", "raise", "assert", "lambda", "print"}
        out_lines = []
        for line in code.split("\n"):
            buf, i, n = [], 0, len(line)
            while i < n:
                ch = line[i]
                if ch == "#":
                    buf.append(f"<span class='c-com'>{esc(line[i:])}</span>")
                    break
                if ch in "\"'":
                    # 三引号（docstring）要整段当成字符串，否则中间的词会被误着色
                    quote3 = line[i:i + 3]
                    if quote3 in (Q3D, Q3S):
                        end = line.find(quote3, i + 3)
                        j = (end + 3) if end != -1 else n
                    else:
                        j = i + 1
                        while j < n and line[j] != ch:
                            j += 2 if line[j] == "\\" else 1
                        j = min(j + 1, n)
                    buf.append(f"<span class='c-str'>{esc(line[i:j])}</span>")
                    i = j
                    continue
                if ch.isalpha() or ch == "_":
                    j = i
                    while j < n and (line[j].isalnum() or line[j] == "_"):
                        j += 1
                    word = line[i:j]
                    buf.append(f"<span class='c-kw'>{word}</span>" if word in kw else esc(word))
                    i = j
                    continue
                if ch.isdigit():
                    j = i
                    while j < n and (line[j].isdigit() or line[j] == "."):
                        j += 1
                    buf.append(f"<span class='c-num'>{line[i:j]}</span>")
                    i = j
                    continue
                buf.append(esc(ch))
                i += 1
            out_lines.append("".join(buf))
        return "\n".join(out_lines)

    def _quote_block(self, block: str, pic: str) -> str:
        m = PROMPT_RE.search(block)
        if not m:
            return f"<blockquote class='pull'>{self.convert(block)}</blockquote>"
        img_id = m.group(1)
        fields: dict[str, str] = {}
        prompt_text = ""
        fence = re.search(r"```\n(.*?)\n```", block, re.S)
        if fence:
            prompt_text = fence.group(1).strip()
            block = block[:fence.start()] + block[fence.end():]
        for key in ("插图目的", "建议位置", "建议画面类型", "建议比例", "建议图注"):
            mm = re.search(rf"\*\*{key}：\*\*\s*\n?([^\n*]*)", block)
            if mm:
                fields[key] = mm.group(1).strip()
        caption = fields.get("建议图注", "")
        if pic:
            if caption:
                pic = pic.replace("</figure>",
                                  f"<figcaption>{self._il(caption)}</figcaption></figure>")
            return pic
        # 还没有配图的插图位：正文里不显示 prompt，留一个安静的占位
        return (f"<div class='pending' data-img='{img_id}'>此处插图待补</div>")

    def _table(self, rows: list[str]) -> str:
        def cells(r: str) -> list[str]:
            return [c.strip() for c in r.strip().strip("|").split("|")]
        if len(rows) >= 2 and set(rows[1].replace("|", "").replace(" ", "")) <= set("-:"):
            head, body = cells(rows[0]), rows[2:]
        else:
            head, body = [], rows
        thead = ("<thead><tr>" + "".join(f"<th>{self._il(c)}</th>" for c in head)
                 + "</tr></thead>") if head else ""
        tbody = "<tbody>" + "".join(
            "<tr>" + "".join(f"<td>{self._il(c)}</td>" for c in cells(r)) + "</tr>"
            for r in body) + "</tbody>"
        return f"<div class='tw'><table>{thead}{tbody}</table></div>"

    def _list(self, lines: list[str]) -> str:
        ordered = bool(re.match(r"^\s*\d+\.\s", lines[0]))
        items: list[list[str]] = []
        for ln in lines:
            if re.match(r"^\s*([-*]|\d+\.)\s", ln) and not ln.startswith("  "):
                items.append([re.sub(r"^\s*([-*]|\d+\.)\s+", "", ln.rstrip("\n"))])
            elif items:
                items[-1].append(ln.strip() if not ln.endswith("  ") else ln.strip() + "  ")
            else:
                items.append([ln.strip()])
        tag = "ol" if ordered else "ul"
        body = ""
        for seg in items:
            raw = _join(seg)
            cls = " class='task'" if re.match(r"^\[[ xX]\]\s", raw) else ""
            body += f"<li{cls}>{self._render_item(raw)}</li>"
        return f"<{tag}>{body}</{tag}>"

    def _render_item(self, text: str) -> str:
        text = re.sub(r"^\[[ x]\]\s*", "", text)
        return self._il(text)


def convert_file(path: Path, link_resolver=None) -> tuple[str, str, list]:
    raw = path.read_text(encoding="utf-8")
    m = re.search(r"^#\s+(.*)$", raw, re.M)
    title = m.group(1).strip() if m else path.stem
    conv = Converter(path, link_resolver)
    body = conv.convert(raw)
    return title, body, conv.headings
