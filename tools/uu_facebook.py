#!/usr/bin/env python3
"""Unknown Uncovered: Facebook Page Reels uploader (Graph API, stdlib only).

Commands:
  whoami  <page_id> <page_token>                       show the Page name
  upload  <page_id> <page_token> <video.mp4> <meta.json>  publish a Reel, print JSON with id + url

Caption: meta["fb_caption"] if present, else the same caption as Instagram.
If thumbnail.jpg sits next to the video it is set as the Reel's preferred thumbnail (best effort).
"""
import json, os, sys, time, uuid, urllib.parse, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uu_instagram import build_caption

API = "https://graph.facebook.com/v22.0"

def call(method, url, params=None, data=None, headers=None):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)

def whoami(page_id, token):
    return call("GET", f"{API}/{page_id}", {"fields": "id,name,link", "access_token": token})

def set_thumbnail(video_id, token, image):
    b = uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"is_preferred\"\r\n\r\ntrue\r\n"
            f"--{b}\r\nContent-Disposition: form-data; name=\"source\"; filename=\"thumb.jpg\"\r\n"
            f"Content-Type: image/jpeg\r\n\r\n").encode() + open(image, "rb").read() + f"\r\n--{b}--\r\n".encode()
    return call("POST", f"{API}/{video_id}/thumbnails", {"access_token": token}, data=body,
                headers={"Content-Type": f"multipart/form-data; boundary={b}"})

def upload(page_id, token, video, meta_path):
    m = json.load(open(meta_path))
    caption = m.get("fb_caption") or build_caption(m)
    size = os.path.getsize(video)
    s = call("POST", f"{API}/{page_id}/video_reels", {"upload_phase": "start", "access_token": token}, data=b"")
    vid, url = s["video_id"], s["upload_url"]
    with open(video, "rb") as f:
        r = call("POST", url, data=f.read(), headers={
            "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size),
            "Content-Type": "application/octet-stream"})
    if not r.get("success"):
        sys.exit("Upload failed: " + json.dumps(r))
    call("POST", f"{API}/{page_id}/video_reels", {
        "upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
        "description": caption, "access_token": token}, data=b"")
    status = {}
    for _ in range(60):
        status = call("GET", f"{API}/{vid}", {"fields": "status", "access_token": token}).get("status", {})
        vs = status.get("video_status")
        if vs in ("ready", "published") or status.get("publishing_phase", {}).get("status") == "complete":
            break
        if vs == "error":
            sys.exit("Facebook processing failed: " + json.dumps(status))
        time.sleep(10)
    thumb = os.path.join(os.path.dirname(video), "thumbnail.jpg")
    thumb_ok = False
    if os.path.exists(thumb):
        try:
            set_thumbnail(vid, token, thumb); thumb_ok = True
        except Exception as e:
            print(f"thumbnail not set: {e}", file=sys.stderr)
    print(json.dumps({"id": vid, "url": f"https://www.facebook.com/reel/{vid}",
                      "status": status.get("video_status"), "thumbnail": thumb_ok}, ensure_ascii=False))

if __name__ == "__main__":
    a = sys.argv[1:]
    try:
        if a[0] == "whoami":
            print(json.dumps(whoami(a[1], a[2])))
        elif a[0] == "upload":
            upload(a[1], a[2], a[3], a[4])
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode(errors='replace')[:800]}")
