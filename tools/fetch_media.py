#!/usr/bin/env python3
"""Fetch openly licensed images from Wikimedia Commons (run by the "Fetch media" Action; the workspace can't reach Commons).

Request: media/requests/<name>.json = {"items": [{"id": "trinity", "title": "File:Trinity Detonation T&B.jpg"},
                                                 {"id": "minuteman", "search": "Minuteman III launch", "n": 3}, ...]}
Writes media/<name>/<id>_<k>.jpg (max 1920 px wide) and media/<name>/credits.json with title, license, artist, source URL.
Only public-domain / CC0 / CC BY / CC BY-SA / OGL / GODL licences are accepted; everything else is skipped.
"""
import glob, html, json, os, re, sys, time, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "UnknownUncoveredBot/1.0 (https://github.com/themrw/unknown-uncovered; educational videos)"}
OK = re.compile(r"(public domain|^pd|cc0|cc[- ]by(-sa)?[- ]?\d|cc[- ]by(-sa)?$|ogl|open government|godl)", re.I)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def api(params):
    params = dict(params, action="query", format="json", formatversion=2)
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            print("retry", e); time.sleep(3 * (i + 1))
    raise SystemExit("API failed")

def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()

def info(pages):
    out = []
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata", {})
        lic = clean(md.get("LicenseShortName", {}).get("value", ""))
        mime = ii.get("mime", "")
        if not ii or not mime.startswith("image/") or "svg" in mime: continue
        if not OK.search(lic): print("skip licence", p["title"], lic); continue
        if ii.get("width", 0) < 900: continue
        out.append({"title": p["title"], "license": lic, "artist": clean(md.get("Artist", {}).get("value", ""))[:120],
                    "credit": clean(md.get("Credit", {}).get("value", ""))[:160],
                    "description": clean(md.get("ImageDescription", {}).get("value", ""))[:300],
                    "url": ii.get("thumburl") or ii["url"], "page": ii.get("descriptionurl", "")})
    return out

PROPS = {"prop": "imageinfo", "iiprop": "url|mime|size|extmetadata", "iiurlwidth": 1920}

def find(item):
    if item.get("title"):
        return info(api(dict(PROPS, titles=item["title"])).get("query", {}).get("pages", []))
    r = api(dict(PROPS, generator="search", gsrnamespace=6, gsrsearch=item["search"], gsrlimit=15))
    pages = sorted(r.get("query", {}).get("pages", []), key=lambda p: p.get("index", 99))
    return info(pages)[: item.get("n", 3)]

def main():
    for req in sorted(glob.glob(os.path.join(ROOT, "media", "requests", "*.json"))):
        name = os.path.splitext(os.path.basename(req))[0]; out = os.path.join(ROOT, "media", name)
        if os.path.exists(os.path.join(out, "credits.json")): continue
        os.makedirs(out, exist_ok=True); credits = {}
        for item in json.load(open(req))["items"]:
            try:
                found = find(item)
            except SystemExit as e:
                print("failed", item, e); continue
            for k, f in enumerate(found):
                fn = f"{item['id']}_{k}.jpg"
                try:
                    data = urllib.request.urlopen(urllib.request.Request(f["url"], headers=UA), timeout=120).read()
                except Exception as e:
                    print("download failed", f["title"], e); continue
                from PIL import Image; import io
                im = Image.open(io.BytesIO(data)); im.seek(0); im = im.convert("RGB"); im.thumbnail((1920, 1920))
                im.save(os.path.join(out, fn), quality=88)
                credits[fn] = f; print("ok", fn, f["title"], f["license"])
                time.sleep(0.5)
        json.dump(credits, open(os.path.join(out, "credits.json"), "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
