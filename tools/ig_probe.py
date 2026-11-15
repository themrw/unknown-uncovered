#!/usr/bin/env python3
"""Diagnose Instagram Reel uploads WITHOUT publishing: for each duration, cut the video, create a
resumable REELS container, upload the bytes, poll the status, and report. Never calls media_publish."""
import json, os, subprocess, sys, tempfile, time, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uu_instagram as U

page_id, token, video = sys.argv[1], sys.argv[2], sys.argv[3]
durs = [int(x) for x in sys.argv[4].split(",")]
ig = U.page_ig(page_id, token); ig_id = ig["user_id"]
print("account:", ig.get("username"))
lim = U.call("GET", f"{U.FB_API}/{ig_id}/content_publishing_limit", {"fields": "config,quota_usage", "access_token": token})
print("publishing limit:", json.dumps(lim))
for d in durs:
    out = os.path.join(tempfile.mkdtemp(), f"cut{d}.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", video, "-t", str(d), "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out], check=True)
    size = os.path.getsize(out)
    res = {"duration_s": d, "size_mb": round(size / 1e6, 1)}
    try:
        c = U.call("POST", f"{U.FB_API}/{ig_id}/media", {"media_type": "REELS", "upload_type": "resumable",
                   "share_to_feed": "true", "access_token": token}, data=b"")
        with open(out, "rb") as f:
            r = U.call("POST", c["uri"], data=f.read(), headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)})
        res["rupload"] = r
        for _ in range(30):
            s = U.call("GET", f"{U.FB_API}/{c['id']}", {"fields": "status_code,status", "access_token": token})
            if s.get("status_code") in ("FINISHED", "ERROR", "EXPIRED"):
                break
            time.sleep(10)
        res["status"] = s
    except urllib.error.HTTPError as e:
        res["error"] = f"HTTP {e.code} {e.read().decode(errors='replace')[:200]}"
    print("RESULT", json.dumps(res))
print("Nothing was published.")
