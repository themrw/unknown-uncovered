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
(#Shorts removed, YouTube wording swapped, at most 5 hashtags, 2200 chars).
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
    if len(tags) > 5:                                  # Instagram now allows only 5 hashtags (Nov 2026)
        for t in tags[5:]:
            cap = cap.replace(t, "", 1)
    return cap[:2200]

def with_cover(video, thumb):
    """Return (path, cover_offset_ms) for a copy of video with the thumbnail appended as a short end card."""
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", video]).decode().strip())
    out = os.path.join(tempfile.mkdtemp(), "ig.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", video,
                    "-loop", "1", "-framerate", "30", "-t", "0.2", "-i", thumb,
                    "-f", "lavfi", "-t", "0.2", "-i", "anullsrc=r=44100:cl=stereo",
                    "-filter_complex", "[1:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[c];"
                    "[0:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[v0];"
                    "[0:a]aresample=44100,aformat=channel_layouts=stereo[a0];"
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

def safe_encode(video, thumb=None):
    """Conservative Reels encode: 1080x1920, 30 fps, H.264 main 4.1, AAC 128k 44.1 kHz stereo, optional cover end card."""
    out = os.path.join(tempfile.mkdtemp(), "ig_safe.mp4")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", video]).decode().strip())
    if thumb:
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", video, "-loop", "1", "-framerate", "30", "-t", "0.3", "-i", thumb,
               "-f", "lavfi", "-t", "0.3", "-i", "anullsrc=r=44100:cl=stereo",
               "-filter_complex", "[1:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[c];"
               "[0:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[v0];"
               "[0:a]aresample=44100,aformat=channel_layouts=stereo[a0];"
               "[v0][a0][c][2:a]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]"]
        offset = int(dur * 1000) + 150
    else:
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", video, "-vf", "scale=1080:1920,setsar=1,fps=30,format=yuv420p",
               "-ar", "44100", "-ac", "2"]
        offset = None
    cmd += ["-c:v", "libx264", "-profile:v", "main", "-level", "4.1", "-preset", "medium", "-b:v", "5M",
            "-maxrate", "6M", "-bufsize", "12M", "-g", "60", "-keyint_min", "60", "-sc_threshold", "0",
            "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    return out, offset

def _publish(token, video, m, caption, offset, api, ig_id):
    size = os.path.getsize(video)
    try:
        c = call("POST", f"{api}/{ig_id}/media", {
            "media_type": "REELS", "upload_type": "resumable", "share_to_feed": "true",
            "caption": caption, "thumb_offset": str(offset), "access_token": token}, data=b"")
    except urllib.error.HTTPError as e:
        raise RuntimeError("create container: HTTP %s %s" % (e.code, e.read().decode(errors="replace")[:400]))
    cid, uri = c["id"], c["uri"]
    try:
        with open(video, "rb") as f:
            r = call("POST", uri, data=f.read(), headers={
                "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)})
    except urllib.error.HTTPError as e:
        raise RuntimeError("upload bytes: HTTP %s %s" % (e.code, e.read().decode(errors="replace")[:400]))
    if not r.get("success"):
        raise RuntimeError("upload bytes: " + json.dumps(r))
    s = {}
    for _ in range(60):
        s = call("GET", f"{api}/{cid}", {"fields": "status_code,status", "access_token": token})
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError("processing: " + json.dumps(s))
        time.sleep(10)
    else:
        raise RuntimeError("processing timed out: " + json.dumps(s))
    try:
        p = call("POST", f"{api}/{ig_id}/media_publish", {"creation_id": cid, "access_token": token}, data=b"")
    except urllib.error.HTTPError as e:
        raise RuntimeError("publish: HTTP %s %s" % (e.code, e.read().decode(errors="replace")[:400]))
    return p["id"]

def _publish_url(token, video_url, caption, offset, api, ig_id, cover_url=None):
    params = {"media_type": "REELS", "video_url": video_url, "share_to_feed": "true",
              "caption": caption, "access_token": token}
    if cover_url:
        params["cover_url"] = cover_url
    else:
        params["thumb_offset"] = str(offset)
    try:
        c = call("POST", f"{api}/{ig_id}/media", params, data=b"")
    except urllib.error.HTTPError as e:
        raise RuntimeError("create container (url): HTTP %s %s" % (e.code, e.read().decode(errors="replace")[:400]))
    cid = c["id"]
    s = {}
    for _ in range(90):
        s = call("GET", f"{api}/{cid}", {"fields": "status_code,status", "access_token": token})
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError("processing (url): " + json.dumps(s))
        time.sleep(10)
    else:
        raise RuntimeError("processing (url) timed out: " + json.dumps(s))
    try:
        p = call("POST", f"{api}/{ig_id}/media_publish", {"creation_id": cid, "access_token": token}, data=b"")
    except urllib.error.HTTPError as e:
        raise RuntimeError("publish (url): HTTP %s %s" % (e.code, e.read().decode(errors="replace")[:400]))
    return p["id"]

def facebook_source(token, fb_video_id):
    """Public CDN URLs of a video already posted to the Facebook Page, plus its preferred thumbnail."""
    d = call("GET", f"{FB_API}/{fb_video_id}", {"fields": "source,thumbnails{uri,is_preferred}", "access_token": token})
    thumbs = d.get("thumbnails", {}).get("data", [])
    pref = next((t["uri"] for t in thumbs if t.get("is_preferred")), None)
    return d.get("source"), pref

IG_MAX_S = 28.0   # Instagram's API currently rejects longer Reels from this account (probed Nov 2026)
YT_LINE = "\n\n\u25b6\ufe0f Full video on YouTube: @Unknown_Uncovered_2026"

def _dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path]).decode().strip())

def instagram_cut(video, segments, thumb=None):
    """Join whole scenes [[start, end], ...] into one <= IG_MAX_S clip (30 fps, safe encode), short audio fades
    at each join, plus a 0.3 s thumbnail end card used as the cover. Returns (path, cover_offset_ms)."""
    out = os.path.join(tempfile.mkdtemp(), "ig_cut.mp4")
    inputs, parts, n = ["-i", video], [], 0
    for i, (st, en) in enumerate(segments):
        d = en - st
        parts.append(f"[0:v]trim={st}:{en},setpts=PTS-STARTPTS,scale=1080:1920,setsar=1,fps=30,format=yuv420p[v{i}];"
                     f"[0:a]atrim={st}:{en},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo,"
                     f"afade=t=in:d=0.08,afade=t=out:st={max(0, d - 0.12)}:d=0.12[a{i}];")
        n += 1
    labels = "".join(f"[v{i}][a{i}]" for i in range(n))
    total = sum(en - st for st, en in segments)
    if thumb:
        inputs += ["-loop", "1", "-framerate", "30", "-t", "0.3", "-i", thumb, "-f", "lavfi", "-t", "0.3", "-i", "anullsrc=r=44100:cl=stereo"]
        parts.append("[1:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[vc];")
        labels += "[vc][2:a]"; n += 1
    fc = "".join(parts) + f"{labels}concat=n={n}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y"] + inputs + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.1", "-preset", "medium", "-b:v", "5M",
                    "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", out], check=True)
    return out, (int(total * 1000) + 100 if thumb else 0)

def prepare(video, m):
    folder = os.path.dirname(video)
    thumb = os.path.join(folder, "thumbnail.jpg")
    thumb = thumb if os.path.exists(thumb) else None
    igv = os.path.join(folder, m["ig_video"]) if m.get("ig_video") else None
    if igv and os.path.exists(igv):
        if _dur(igv) > IG_MAX_S:
            sys.exit(f"{m['ig_video']} is longer than {IG_MAX_S}s")
        return (with_cover(igv, thumb) if thumb else (igv, 0)), True
    if _dur(video) <= IG_MAX_S:
        return (with_cover(video, thumb) if thumb else (video, m.get("ig_thumb_offset_ms", 0))), False
    segs = m.get("ig_segments") or [[0, IG_MAX_S - 0.5]]
    if sum(e - s for s, e in segs) > IG_MAX_S:
        sys.exit(f"ig_segments add up to more than {IG_MAX_S}s")
    return instagram_cut(video, segs, thumb), True

def upload(token, video, meta_path, api=None, ig=None):
    api = api or API
    m = json.load(open(meta_path))
    ig = ig or me(token)
    ig_id = ig.get("user_id") or ig["id"]
    (path, offset), was_cut = prepare(video, m)
    caption = build_caption(m)
    if was_cut and "Full video" not in caption:
        caption = (caption[:2200 - len(YT_LINE)] + YT_LINE)
    print(f"Instagram file: {round(_dur(path), 1)} s, cut={was_cut}", file=sys.stderr)
    errors = []
    for attempt in range(1, 5):
        try:
            mid = _publish(token, path, m, caption, offset, api, ig_id)
            break
        except Exception as e:
            errors.append(f"attempt {attempt}: {e}")
            print(f"Instagram attempt {attempt} failed: {e}", file=sys.stderr)
            time.sleep(20 * attempt)
    else:
        sys.exit("Instagram upload failed: " + " | ".join(errors))
    info = call("GET", f"{api}/{mid}", {"fields": "permalink", "access_token": token})
    print(json.dumps({"id": mid, "url": info.get("permalink"), "account": ig.get("username"),
                      "instagram_cut_seconds": round(_dur(path), 1) if was_cut else None}, ensure_ascii=False))

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
