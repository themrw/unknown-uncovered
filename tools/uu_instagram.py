#!/usr/bin/env python3
"""Unknown Uncovered: Instagram Reels uploader (Instagram API with Instagram Login, stdlib only).

Commands:
  whoami   <token>                        show the connected Instagram account
  upload   <token> <video.mp4> <meta.json> publish a Reel, print JSON with id + permalink
  refresh  <token>                        print a refreshed 60-day token (JSON)

Caption: meta["ig_caption"] if present, else built from meta title + description
(#Shorts removed, YouTube wording swapped, at most 30 hashtags, 2200 chars).
Cover frame: meta["ig_thumb_offset_ms"] (default 14000).
"""
import json, os, re, sys, time, urllib.parse, urllib.request, urllib.error

API = "https://graph.instagram.com/v22.0"

def call(method, url, params=None, data=None, headers=None):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)

def me(token):
    return call("GET", f"{API}/me", {"fields": "user_id,username,account_type", "access_token": token})

def build_caption(m):
    if m.get("ig_caption"):
        return m["ig_caption"][:2200]
    title = re.sub(r"\s*#shorts\b", "", m["title"], flags=re.I).strip()
    desc = m.get("description", "")
    desc = re.sub(r"#shorts\b\s*", "", desc, flags=re.I)
    desc = desc.replace("Subscribe to", "Follow")
    cap = f"{title}\n\n{desc}".strip()
    tags = re.findall(r"#\w+", cap)
    if len(tags) > 30:
        for t in tags[30:]:
            cap = cap.replace(t, "", 1)
    return cap[:2200]

def upload(token, video, meta_path):
    m = json.load(open(meta_path))
    ig = me(token)
    ig_id = ig.get("user_id") or ig["id"]
    size = os.path.getsize(video)
    c = call("POST", f"{API}/{ig_id}/media", {
        "media_type": "REELS", "upload_type": "resumable", "share_to_feed": "true",
        "caption": build_caption(m), "thumb_offset": str(m.get("ig_thumb_offset_ms", 14000)),
        "access_token": token}, data=b"")
    cid, uri = c["id"], c["uri"]
    with open(video, "rb") as f:
        r = call("POST", uri, data=f.read(), headers={
            "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size),
            "Content-Type": "application/octet-stream"})
    if not r.get("success"):
        sys.exit("Upload failed: " + json.dumps(r))
    for _ in range(60):
        s = call("GET", f"{API}/{cid}", {"fields": "status_code,status", "access_token": token})
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") in ("ERROR", "EXPIRED"):
            sys.exit("Instagram processing failed: " + json.dumps(s))
        time.sleep(10)
    else:
        sys.exit("Timed out waiting for Instagram to process the video")
    p = call("POST", f"{API}/{ig_id}/media_publish", {"creation_id": cid, "access_token": token}, data=b"")
    mid = p["id"]
    info = call("GET", f"{API}/{mid}", {"fields": "permalink", "access_token": token})
    print(json.dumps({"id": mid, "url": info.get("permalink"), "account": ig.get("username")}, ensure_ascii=False))

def refresh(token):
    print(json.dumps(call("GET", "https://graph.instagram.com/refresh_access_token",
                          {"grant_type": "ig_refresh_token", "access_token": token})))

if __name__ == "__main__":
    a = sys.argv[1:]
    try:
        if a[0] == "whoami":
            print(json.dumps(me(a[1])))
        elif a[0] == "upload":
            upload(a[1], a[2], a[3])
        elif a[0] == "refresh":
            refresh(a[1])
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode(errors='replace')[:800]}")
