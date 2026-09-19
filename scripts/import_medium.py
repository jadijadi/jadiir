"""Convert saved Medium post pages (<dir>/<id>.html) into Hugo page bundles under content/blog/<slug>/.

Usage:  python3 scripts/import_medium.py [dir-with-html] [post-id ...]
Needs:  pip install beautifulsoup4 lxml pillow
Get the HTML with e.g.  curl -H 'X-Return-Format: html' https://r.jina.ai/<medium-url> -o <dir>/<id>.html
(Medium blocks direct curl; the Wayback Machine raw view web.archive.org/web/<ts>id_/<url> also works.)

Renders Markdown from the structured post JSON Medium embeds in every page
(Apollo cache on new pages, inline GLOBALS/obvInit JSON on old ones)."""
import re, os, sys, json, datetime, urllib.request, urllib.parse
from bs4 import BeautifulSoup

SRC = sys.argv[1] if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else "wb"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content", "blog")
UA = "Mozilla/5.0"

PTYPES = {1: "P", 2: "H2", 3: "H3", 4: "IMG", 6: "BQ", 7: "PQ", 8: "PRE", 9: "OLI", 10: "ULI",
          11: "IFRAME", 13: "H4", 14: "MIXTAPE_EMBED", 15: "SECTION_CAPTION"}
MTYPES = {1: "STRONG", 2: "EM", 3: "A", 10: "CODE"}


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
            f.write(r.read())
        return True
    except Exception as e:
        print("   ! image failed:", url, e)
        return False


def shrink(path, max_w=1400):
    """Downscale big originals; the site only needs web-sized images."""
    from PIL import Image
    try:
        im = Image.open(path)
        if getattr(im, "is_animated", False) or im.format == "GIF": return
        if im.width > max_w:
            im = im.convert("RGB") if im.mode not in ("RGB", "RGBA", "P", "L") else im
            im.thumbnail((max_w, max_w * 4))
        if im.format == "JPEG": im.convert("RGB").save(path, "JPEG", quality=85, optimize=True)
        elif im.format == "PNG": im.save(path, "PNG", optimize=True)
        else: im.save(path)
    except Exception as e:
        print("   ! shrink failed:", path, e)


def json_object_at(s, j):
    """Return the JSON object literal starting at s[j] == '{'."""
    depth, k, instr, esc = 0, j, False, False
    while True:
        ch = s[k]
        if instr:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': instr = False
        else:
            if ch == '"': instr = True
            elif ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(s[j:k + 1])
        k += 1


def resolve(state, o, depth=0):
    """Resolve Apollo cache references ({"__ref": k} or {"type": "id", "id": k}) recursively."""
    if depth > 6: return o
    if isinstance(o, dict):
        if "__ref" in o and o["__ref"] in state: return resolve(state, state[o["__ref"]], depth + 1)
        if o.get("type") == "id" and o.get("id") in state: return resolve(state, state[o["id"]], depth + 1)
        return {k: resolve(state, v, depth + 1) for k, v in o.items()}
    if isinstance(o, list): return [resolve(state, v, depth + 1) for v in o]
    return o


def find_key(o, key):
    if isinstance(o, dict):
        if key in o: return o
        for v in o.values():
            r = find_key(v, key)
            if r: return r
    if isinstance(o, list):
        for v in o:
            r = find_key(v, key)
            if r: return r


def apply_markups(text, markups):
    """Insert Markdown inline markup using Medium's UTF-16 offsets."""
    u16 = text.encode("utf-16-le")
    def sub(a, b): return u16[2 * a:2 * b].decode("utf-16-le", errors="replace")
    events = []  # (pos, order, string)
    for m in markups:
        t = MTYPES.get(m["type"], m["type"])
        a, b = m["start"], m["end"]
        if a >= b: continue
        if t == "STRONG": o, c = "**", "**"
        elif t == "EM": o, c = "*", "*"
        elif t == "CODE": o, c = "`", "`"
        elif t == "A":
            href = m.get("href") or ""
            o, c = "[", f"]({href})"
        else: continue
        span = b - a
        events.append((a, 1, -span, o))   # opens: longer spans first
        events.append((b, 0, span, c))    # closes before opens at same pos; shorter spans first
    events.sort(key=lambda e: (e[0], e[1], e[2]))
    out, pos = [], 0
    for p, _, _, s in events:
        out.append(sub(pos, p)); out.append(s); pos = p
    out.append(sub(pos, len(u16) // 2))
    return "".join(out)


def escape_tags(md):
    """Escape '<tag' outside backtick code spans so Goldmark renders it as text, not HTML."""
    parts = md.split("`")
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"<(?=[A-Za-z/!])", "&lt;", parts[i])
    return "`".join(parts)


def embed_md(url, title=""):
    m = re.search(r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    if m:
        return f"{{{{< youtube {m.group(1)} >}}}}"
    return f"[{title or url}]({url})"


def render(paras, ctx):
    """ctx: dict(title, image_url(meta)->local, media_url(paragraph)->(url,title))"""
    out, i, n = [], 0, len(paras)
    while i < n:
        p = paras[i]
        t = PTYPES.get(p["type"], p["type"])
        text = p.get("text") or ""
        md = escape_tags(apply_markups(text, p.get("markups") or [])) if t != "PRE" else text
        norm = lambda x: re.sub(r"[^a-z0-9]+", "", x.lower())
        if i == 0 and t in ("H2", "H3", "H4") and norm(text) == norm(ctx["title"]):
            i += 1; continue
        if i <= 1 and t in ("H2", "H3", "H4") and norm(text) == norm(ctx.get("subtitle", "")):
            i += 1; continue   # Medium subtitle: kept as front-matter description
        if t in ("OLI", "ULI"):
            j = i
            while j < n and PTYPES.get(paras[j]["type"], paras[j]["type"]) == t:
                q = paras[j]
                out.append(("1. " if t == "OLI" else "- ") + escape_tags(apply_markups(q.get("text") or "", q.get("markups") or [])))
                j += 1
            out.append(""); i = j; continue
        if t == "P": out.append(md + "\n")
        elif t == "H2": out.append("## " + md + "\n")
        elif t == "H3": out.append("## " + md + "\n")
        elif t == "H4": out.append("### " + md + "\n")
        elif t in ("BQ", "PQ"): out.append("> " + md.replace("\n", "\n> ") + "\n")
        elif t == "PRE":
            out.append(f"```\n{text}\n```\n")
        elif t == "IMG":
            local = ctx["image"](p.get("metadata") or {})
            if local:
                alt = ((p.get("metadata") or {}).get("alt") or text or ctx["title"]).replace("]", "")
                out.append(f"![{alt}]({local})")
                out.append(f"*{md}*\n" if md.strip() else "")
        elif t == "IFRAME":
            url, title = ctx["media"](p)
            if url: out.append(embed_md(url, title) + "\n")
        elif t == "MIXTAPE_EMBED":
            href = (p.get("mixtapeMetadata") or {}).get("href") or p.get("href") or ""
            label = text.split("\n")[0].strip() or href
            if href: out.append(f"[{label}]({href})\n")
        elif t == "SECTION_CAPTION": pass
        else:
            print("   ? unknown paragraph type", t); out.append(md + "\n")
        i += 1
    return "\n".join(out)


def convert(pid):
    raw = open(f"{SRC}/{pid}.html", encoding="utf-8", errors="replace").read()
    soup = BeautifulSoup(raw, "lxml")
    og = lambda prop: (soup.find("meta", property=prop) or {}).get("content")
    title = og("og:title") or soup.title.get_text()
    title = re.sub(r"\s*[–—-]\s*(jadi\s*[–—-]\s*)?Medium$", "", title).strip()
    url = ((soup.find("link", rel="canonical") or {}).get("href") or og("og:url")).split("?")[0]
    slug = re.sub(r"-[0-9a-f]{12}$", "", url.rstrip("/").split("/")[-1])
    bundle = os.path.join(OUT, slug); os.makedirs(bundle, exist_ok=True)
    counter = [0]

    def image(meta):
        iid = meta.get("id") or (meta.get("__ref", "").split(":", 1)[1] if meta.get("__ref") else None)
        if not iid: return None
        if state: meta = resolve(state, meta)
        iid = meta.get("id", iid)
        counter[0] += 1
        ext = os.path.splitext(iid)[1] or ".jpg"
        fname = f"img-{counter[0]:02d}{ext}"
        dest = os.path.join(bundle, fname)
        if not fetch(f"https://miro.medium.com/v2/{iid}", dest):
            return f"https://miro.medium.com/v2/{iid}"
        shrink(dest)
        return fname

    m = re.search(r"window\.__APOLLO_STATE__\s*=\s*\{", raw)
    if m:
        state = json_object_at(raw, m.end() - 1)
        post = state.get(f"Post:{pid}") or next(v for k, v in state.items() if k.startswith("Post:") and any(kk.startswith("content") for kk in v))
        content = resolve(state, next(v for k, v in post.items() if k.startswith("content")))
        paras = resolve(state, content["bodyModel"]["paragraphs"])
        date = og("article:published_time") or (datetime.datetime.fromtimestamp(post["firstPublishedAt"] / 1000, datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ") if post.get("firstPublishedAt") else None)
        tags = sorted({a["href"].split("/tag/")[1].split("?")[0] for a in soup.find_all("a", href=re.compile(rf"/tag/[^?]+\?source=post_page-----{pid}"))})
        if not tags:
            tags = sorted({a["href"].split("/tag/")[1].split("?")[0] for a in soup.find_all("a", href=re.compile(r"^(https://medium\.com)?/tag/"))})
        subtitle = ((post.get("previewContent") or {}).get("subtitle")) or ""
        locked = bool(content.get("isLockedPreviewOnly"))
        def media(p):
            mr = resolve(state, (p.get("iframe") or {}).get("mediaResource") or {})
            src = mr.get("iframeSrc") or mr.get("href") or ""
            q = urllib.parse.parse_qs(urllib.parse.urlparse(src).query)
            return (q.get("url", [None])[0] or q.get("src", [None])[0] or src), mr.get("title") or ""
    else:
        state = None
        fixed = re.sub(r"\\x([0-9a-fA-F]{2})", r"\\u00\1", raw)
        post = data = None
        for marker in ('window["obvInit"](', "var GLOBALS = "):
            g = fixed.find(marker)
            if g < 0: continue
            data = json_object_at(fixed, fixed.find("{", g))
            post = find_key(data, "bodyModel")
            if post: break
        paras = post["bodyModel"]["paragraphs"]
        ts = (find_key(data, "firstPublishedAt") or {}).get("firstPublishedAt")
        date = og("article:published_time") or (datetime.datetime.fromtimestamp(ts / 1000, datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ") if ts else None)
        tags = sorted({a["href"].split("/tag/")[1].split("?")[0] for a in soup.find_all("a", href=re.compile(r"medium\.com/tag/"))})
        subtitle = post.get("subtitle") or ""
        locked = False
        def media(p):
            mid = (p.get("iframe") or {}).get("mediaResourceId")
            fr = soup.find("iframe", attrs={"data-media-id": mid}) if mid else None
            src = (fr.get("data-src") or fr.get("src")) if fr else (f"https://medium.com/media/{mid}" if mid else "")
            return src, ""

    md = render(paras, {"title": title, "subtitle": subtitle, "image": image, "media": media})
    if locked:
        md += "\n\n> **Note:** this post is member-only on Medium, so only the preview could be imported. The full text is on Medium."
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    md = re.sub(r"\?source=post_page[^)\s]*", "", md)
    fm = ["+++", f"title = {json.dumps(title, ensure_ascii=False)}"]
    if subtitle and subtitle.strip() != title.strip(): fm.append(f"description = {json.dumps(subtitle.strip(), ensure_ascii=False)}")
    if date: fm.append(f"date = {date}")
    fm.append(f"tags = {json.dumps(tags)}")
    fm.append(f"medium = {json.dumps(url)}")
    fm.append("+++")
    with open(os.path.join(bundle, "index.md"), "w") as f:
        f.write("\n".join(fm) + "\n\n" + md + f"\n\n---\n*Originally published on [Medium]({url}).*\n")
    print(f"{pid}  {(date or '????-??-??')[:10]}  {slug}  ({counter[0]} images, {len(md)} chars, tags={tags})")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not os.path.isdir(a)]
    ids = args or sorted(f[:-5] for f in os.listdir(SRC) if f.endswith(".html"))
    for pid in ids:
        try: convert(pid)
        except Exception as e:
            print(pid, "FAILED:", repr(e))
