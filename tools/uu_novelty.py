#!/usr/bin/env python3
"""Novelty gate: is a topic already covered on YouTube? Run BEFORE pitching any topic.

usage: uu_novelty.py "<query 1>" ["<query 2>" ...]     (give a Hindi-leaning and an English query per topic)

For each query: the top 15 YouTube results by view count, with views, upload date and title, plus a verdict:
  COVERED   any result over 500k views, or 3+ results over 100k  -> do NOT make it (the channel promise is "unknown")
  CROWDED   1-2 results over 100k                                 -> only with a genuinely new angle the others missed
  OPEN      nothing over 100k                                     -> fair game
Uses the channel's OAuth token in /home/claude/uu/ (search = 100 quota units per query; daily quota 10,000).
"""
import json, sys, urllib.parse, urllib.request

def token():
    cs = json.load(open("/home/claude/uu/client_secret.json")); cs = cs.get("installed") or cs.get("web")
    tk = json.load(open("/home/claude/uu/youtube_token.json"))
    d = urllib.parse.urlencode({"client_id": cs["client_id"], "client_secret": cs["client_secret"],
                                "refresh_token": tk["refresh_token"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", d))["access_token"]

def get(url, at):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": "Bearer " + at})))

def check(q, at):
    s = get("https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(
        {"part": "snippet", "q": q, "type": "video", "maxResults": 15, "order": "viewCount", "relevanceLanguage": "hi"}), at)
    ids = [x["id"]["videoId"] for x in s.get("items", [])]
    if not ids: return "OPEN", []
    v = get("https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=" + ",".join(ids), at)
    rows = sorted(((int(x["statistics"].get("viewCount", 0)), x["snippet"]["publishedAt"][:10], x["snippet"]["title"]) for x in v["items"]), reverse=True)
    big = [r for r in rows if r[0] > 100_000]
    verdict = "COVERED" if (rows and rows[0][0] > 500_000) or len(big) >= 3 else ("CROWDED" if big else "OPEN")
    return verdict, rows

if __name__ == "__main__":
    at = token()
    for q in sys.argv[1:]:
        verdict, rows = check(q, at)
        print(f"\n=== {q}  ->  {verdict}")
        for n, d, t in rows[:8]: print(f"  {n:>11,}  {d}  {t[:80]}")
