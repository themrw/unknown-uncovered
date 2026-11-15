#!/usr/bin/env python3
"""Unknown Uncovered: YouTube uploader (no extra packages needed).

Commands:
  auth-url  <client_secret.json>                      print the Google sign-in link
  exchange  <client_secret.json> <code> <token.json>  turn the code into a saved token
  upload    <client_secret.json> <token.json> <video.mp4> <meta.json>
  whoami    <client_secret.json> <token.json>         show which channel the token belongs to

meta.json: {"title": "...", "description": "...", "tags": [...], "categoryId": "25",
            "privacyStatus": "public", "madeForKids": false, "language": "hi"}
"""
import json, os, sys, urllib.parse, urllib.request

SCOPES = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"
REDIRECT = "http://localhost"

def client(path):
    d = json.load(open(path))
    d = d.get("installed") or d.get("web") or d
    return d["client_id"], d["client_secret"]

def post_form(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method="POST")
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def access_token(cs, tok_path):
    cid, sec = client(cs)
    tok = json.load(open(tok_path))
    r = post_form("https://oauth2.googleapis.com/token", {
        "client_id": cid, "client_secret": sec,
        "refresh_token": tok["refresh_token"], "grant_type": "refresh_token"})
    return r["access_token"]

def cmd_auth_url(cs):
    cid, _ = client(cs)
    q = urllib.parse.urlencode({"client_id": cid, "redirect_uri": REDIRECT, "response_type": "code",
                                "scope": SCOPES, "access_type": "offline", "prompt": "consent"})
    print("https://accounts.google.com/o/oauth2/v2/auth?" + q)

def cmd_exchange(cs, code, tok_path):
    cid, sec = client(cs)
    if code.startswith("http"):
        code = urllib.parse.parse_qs(urllib.parse.urlparse(code).query)["code"][0]
    r = post_form("https://oauth2.googleapis.com/token", {
        "client_id": cid, "client_secret": sec, "code": code,
        "redirect_uri": REDIRECT, "grant_type": "authorization_code"})
    if "refresh_token" not in r:
        sys.exit("No refresh token returned: " + json.dumps(r))
    json.dump({"refresh_token": r["refresh_token"]}, open(tok_path, "w"))
    os.chmod(tok_path, 0o600)
    print("Saved token to", tok_path)

def cmd_whoami(cs, tok_path):
    at = access_token(cs, tok_path)
    req = urllib.request.Request("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
                                 headers={"Authorization": "Bearer " + at})
    with urllib.request.urlopen(req) as r:
        d = json.load(r)
    for it in d.get("items", []):
        print(it["id"], it["snippet"]["title"], it["snippet"].get("customUrl", ""))

def cmd_upload(cs, tok_path, video, meta_path):
    at = access_token(cs, tok_path)
    m = json.load(open(meta_path))
    body = {
        "snippet": {"title": m["title"][:100], "description": m["description"][:5000],
                    "tags": m.get("tags", []), "categoryId": m.get("categoryId", "25"),
                    "defaultLanguage": m.get("language", "hi"),
                    "defaultAudioLanguage": m.get("language", "hi")},
        "status": {"privacyStatus": m.get("privacyStatus", "public"),
                   "selfDeclaredMadeForKids": m.get("madeForKids", False),
                   "containsSyntheticMedia": m.get("syntheticMedia", False)},
    }
    size = os.path.getsize(video)
    init = urllib.request.Request(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": "Bearer " + at, "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)})
    with urllib.request.urlopen(init) as r:
        loc = r.headers["Location"]
    with open(video, "rb") as f:
        put = urllib.request.Request(loc, data=f.read(), method="PUT",
                                     headers={"Content-Type": "video/mp4", "Content-Length": str(size)})
        with urllib.request.urlopen(put) as r:
            res = json.load(r)
    vid = res["id"]
    print(json.dumps({"id": vid, "url": f"https://youtube.com/shorts/{vid}",
                      "privacyStatus": res.get("status", {}).get("privacyStatus"),
                      "uploadStatus": res.get("status", {}).get("uploadStatus")}, ensure_ascii=False))

if __name__ == "__main__":
    a = sys.argv[1:]
    try:
        {"auth-url": lambda: cmd_auth_url(a[1]),
         "exchange": lambda: cmd_exchange(a[1], a[2], a[3]),
         "whoami": lambda: cmd_whoami(a[1], a[2]),
         "upload": lambda: cmd_upload(a[1], a[2], a[3], a[4])}[a[0]]()
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode(errors='replace')[:800]}")
