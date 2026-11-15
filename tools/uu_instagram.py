#!/usr/bin/env python3
"""Unknown Uncovered: Instagram Reels uploader (Instagram API with Instagram Login, stdlib only).

Commands:
  whoami   <token>                        show the connected Instagram account
  upload   <token> <video.mp4> <meta.json> publish a Reel, print JSON with id + permalink
  refresh  <token>                        print a refreshed 60-day token (JSON)
  whoami-page  <page_id> <page_token>     show the Instagram account linked to a Facebook Page
  upload-page  <page_id> <page_token> <video.mp4> <meta.json>
                                          publish a Reel through the Page's linked Instagram account
                                          (Instagram API with Facebook Login, graph.facebook.com)

Caption: meta["ig_caption"] if present, else built from meta title + description
(#Shorts removed, YouTube wording swapped, at most 30 hashtags, 2200 chars).
Cover: if thumbnail.jpg sits next to the video and ffmpeg is available, a 0.2 s still of it is
appended to the end of the Instagram copy and used as the Reel cover; otherwise the frame at
meta["ig_thumb_offset_ms"] (default 14000) is used.
"""
import json, os, re, shutil, subprocess, sys, tempfile, time, urllib.parse, urllib.request, urllib.error

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

def with_cover(video, thumb):
    """Return (path, cover_offset_ms) for a copy of video with the thumbnail appended as a short end card."""
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", video]).decode().strip())
    out = os.path.join(tempfile.mkdtemp(), "ig.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", video,
                    "-loop", "1", "-framerate", "60", "-t", "0.2", "-i", thumb,
                    "-f", "lavfi", "-t", "0.2", "-i", "anullsrc=r=48000:cl=stereo",
                    "-filter_complex", "[1:v]scale=1080:1920,setsar=1,fps=60,format=yuv420p[c];"
                    "[0:v]scale=1080:1920,setsar=1,fps=60,format=yuv420p[v0];"
                    "[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];"
                    "[v0][a0][c][2:a]concat=n=2:v=1:a=1[v][a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-maxrate", "3500k", "-bufsize", "7000k", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
    return out, int(dur * 1000) + 100

FB_API = "https://graph.facebook.com/v22.0"

def page_ig(page_id, token):
    d = call("GET", f"{FB_API}/{page_id}", {"fields": "name,instagram_business_account{id,username}", "access_token": token})
    ig = d.get("instagram_business_account")
    if not ig:
        sys.exit("No Instagram account is linked to this Facebook Page (Page settings > Linked accounts > Instagram).")
    return {"user_id": ig["id"], "username": ig.get("username"), "page": d.get("name")}

def upload(token, video, meta_path, api=None, ig=None):
    api = api or API
    m = json.load(open(meta_path))
    offset = m.get("ig_thumb_offset_ms", 14000)
    thumb = os.path.join(os.path.dirname(video), "thumbnail.jpg")
    if os.path.exists(thumb) and shutil.which("ffmpeg"):
        video, offset = with_cover(video, thumb)
    ig = ig or me(token)
    ig_id = ig.get("user_id") or ig["id"]
    size = os.path.getsize(video)
    c = call("POST", f"{api}/{ig_id}/media", {
        "media_type": "REELS", "upload_type": "resumable", "share_to_feed": "true",
        "caption": build_caption(m), "thumb_offset": str(offset),
        "access_token": token}, data=b"")
    cid, uri = c["id"], c["uri"]
    with open(video, "rb") as f:
        r = call("POST", uri, data=f.read(), headers={
            "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size),
            "Content-Type": "application/octet-stream"})
    if not r.get("success"):
        sys.exit("Upload failed: " + json.dumps(r))
    for _ in range(60):
        s = call("GET", f"{api}/{cid}", {"fields": "status_code,status", "access_token": token})
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") in ("ERROR", "EXPIRED"):
            sys.exit("Instagram processing failed: " + json.dumps(s))
        time.sleep(10)
    else:
        sys.exit("Timed out waiting for Instagram to process the video")
    p = call("POST", f"{api}/{ig_id}/media_publish", {"creation_id": cid, "access_token": token}, data=b"")
    mid = p["id"]
    info = call("GET", f"{api}/{mid}", {"fields": "permalink", "access_token": token})
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
        elif a[0] == "whoami-page":
            print(json.dumps(page_ig(a[1], a[2])))
        elif a[0] == "upload-page":
            upload(a[2], a[3], a[4], api=FB_API, ig=page_ig(a[1], a[2]))
        elif a[0] == "refresh":
            refresh(a[1])
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode(errors='replace')[:800]}")
