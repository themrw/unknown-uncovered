# Unknown Uncovered: reel factory

This repo makes and publishes Hindi data reels for the YouTube channel **Unknown Uncovered**
(@unknown_uncovered_2026, channel id UCTW1fZGWSxLxkBBOlGSjE-g). Audience: India. Hindi voiceover,
English on-screen text, curious facts and world data explained simply.

## Layout
- `tools/uu_youtube.py`: YouTube uploader (stdlib only). Used by the GitHub Action.
- `tools/uu_instagram.py`: Instagram Reels uploader (Instagram API with Instagram Login, resumable upload, stdlib only). Used by the GitHub Action with `INSTAGRAM_ACCESS_TOKEN`, or, if that's absent, through the Facebook Page's linked Instagram account using `FACEBOOK_PAGE_ID` + `FACEBOOK_PAGE_TOKEN` (graph.facebook.com). The Page route is the one in use: one never-expiring token covers Facebook and Instagram.
- `tools/uu_facebook.py`: Facebook Page Reels uploader (Graph API `video_reels`, resumable, sets the thumbnail). Used when the `FACEBOOK_PAGE_ID` and `FACEBOOK_PAGE_TOKEN` secrets exist. The caption is the same as Instagram's, or `fb_caption`.
- `tools/v2/` (**current pipeline, use this**): spec-driven, themed reels. One `spec.json` per reel drives everything:
  `uu_voice.py` (Kokoro per-scene narration, trimmed + polished → `vo/NN.wav`, `vo/durs.json`), `uu_render.py` (30 fps 1080×1920:
  themes `nuclear|war|money|space|history`, orthographic globe from Natural Earth, suspense-first scene types `hook`, `tease`, `stat`,
  `rank` (hidden-flag countdown reveal), `bars`, `roll` (rapid-fire countdown for short edits), `outro` (`"card": "youtube"` for short edits),
  channel logo always top-right), `uu_music.py` (themed score: drone, heartbeat accelerating through the countdown, Geiger clicks for nuclear,
  risers + impacts on reveals, voice ducking → `out/audio.wav`), `uu_thumb.py` (themed thumbnail from `spec["thumb"]`). Assets (fonts, geojson,
  logo) are in `tools/v2/assets/`. Worked example: `tools/v2/examples/002_nuclear/spec.json` (+ `ig/spec.json` for the Instagram edit).
- Legacy v1 templates (kept for reference only):
- `tools/tts_template.py`: Kokoro Hindi TTS (voice `hm_omega`, speed 1.1, lang `hi`) → `vo_NN.wav` + `durs.json`.
- `tools/render_template.py`: 1080×1920 60 fps PIL renderer (radar, ticker, flags, typed text, glitch transitions). A template: copy it and write new scene functions for each topic.
- `tools/thumbnail_template.py`: 1080×1920 thumbnail made with PIL. It uses the renderer's background, radar and flags, Mukta ExtraBold for Hindi (text shaped by raqm) and Anton for numbers. Copy it and redesign it for each topic.
- `tools/scenes_example_nuclear.py`: example scene set (reel 002) that shows how to restyle the renderer for a new topic.
- `tools/music_template.py`: synthesized military-style score + voice mix with ducking (imports the renderer as `render3`).
- `videos/NNN_slug/`: one folder per reel: `video.mp4`, `meta.json`, and `uploaded.json` once it's on YouTube.
- `.github/workflows/upload.yml`: on push of a `videos/*/meta.json`, uploads every folder with no `uploaded.json` to YouTube and every folder with no `instagram.json` to Instagram Reels, and every folder with no `facebook.json` to the Facebook Page as a Reel, then commits the results.
- `site/`: homepage + privacy policy for the Google OAuth consent screen.

## Making a reel
1. Research the topic with web search: current, sourced numbers only, never invented; neutral on politics.
2. Write the spec (copy `tools/v2/examples/002_nuclear/spec.json`): pick the `theme` that fits the content (add a new one to `THEMES` if none fits), `header`, `source`, `ticker`, and the scenes. Narration is **one flowing Hindi passage per scene** (`vo`), written as natural spoken sentences that connect to the next scene, never clipped fragments; numbers as Hindi words. Structure for suspense: `hook` (cold open, reveals nothing: no flags, no names) → `tease` (the big number + "?" cards) → `stat` → `rank` countdown from #N to #1 (each country hidden as a "?" silhouette until `reveal_at`) → `bars` comparison → `outro`. The outro narration always ends with the channel CTA covering every platform: "ऐसी ही छुपी कहानियों के लिए, अननोन अनकवर्ड को अभी सब्सक्राइब और फ़ॉलो करें।"
3. Setup in the workspace: `pip install --break-system-packages kokoro-onnx soundfile scipy`, then download `kokoro-v1.0.onnx` and `voices-v1.0.bin` from
   `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/` into `/home/claude/tts/`. Voice: `hm_psi`, speed 1.0 (1.1 for the Instagram edit).
4. Work in a folder outside the repo, e.g. `/home/claude/work/NNN/` holding `spec.json` and `ig/spec.json`. Run `python3 tools/v2/uu_voice.py spec.json`, then `python3 tools/v2/uu_render.py spec.json still 1,4` and look at the stills (scene-local times), fix layout, then `uu_render.py spec.json full` (~4 min for 100 s) and `uu_music.py spec.json`. Mux `out/video_only.mp4` + `out/audio.wav`.
5. **Thumbnail (always required).** Fill `spec["thumb"]` (Hindi `hook` lines, `number`, `number_label`, curiosity `sticker` such as "भारत कहाँ?", `highlight`ed countries shown unnamed in red, `view`, `mystery` silhouette flags) and run `python3 tools/v2/uu_thumb.py spec.json videos/NNN_slug/thumbnail.jpg` (1080×1920 JPG q88, key content inside the central 1080×1440). Look at the image before publishing.
6. Mux, check loudness (≈ −14 LUFS), then compress: `-crf 23 -maxrate 2400k -bufsize 4800k` (keep it under ~30 MB).
7. Write `meta.json`: title ≤100 chars (Hindi hook + English keywords + #Shorts); description with the hook, key numbers, an engagement question, a subscribe line, sources and 8–12 hashtags; 12–18 tags under 450 characters in total; `categoryId` 25 or 27; `privacyStatus` public; `madeForKids` false; `language` hi. No `<` or `>`.
   **Instagram length limit:** the Instagram API currently rejects Reels longer than about 30 s from this account (`ProcessingFailedError` / 2207076; probed Nov 2026 with `tools/ig_probe.py`). Every reel over 28 s therefore gets a **dedicated complete Instagram edit** `videos/NNN_slug/ig.mp4` (≤28 s, 30 fps): its own short Hindi voiceover (3–4 lines: hook → all items rapid-fire → takeaway + "पूरी वीडियो, यूट्यूब पर देखें"), built as `ig/spec.json` with scenes `hook` (short) → one `roll` with every item → `outro` with `"card": "youtube"` (see the example), then voice/render/music/mux exactly as the main reel. Set `"ig_video": "ig.mp4"` in meta.json. Fallback only if that isn't possible: `ig_segments`: whole narrated scenes as `[[start, end], ...]` in seconds, adding up to 28 s or less (hook + the 1–2 most gripping scenes, e.g. the India scene for this audience). The uploader joins them, adds the thumbnail as the cover and appends "Full video on YouTube" to the caption. Without `ig_segments` it uses the first 27.5 s.
   Optional for Instagram: `ig_thumb_offset_ms` (the cover frame, e.g. the first country card) and `ig_caption` (otherwise built from the title and description, with #Shorts removed and at most 30 hashtags).
8. Publish: commit `videos/NNN_slug/video.mp4` + `meta.json` (next free number) and push to master. The Action uploads it. Watch it with `gh api repos/themrw/unknown-uncovered/actions/runs?per_page=1`, then report the URLs from `uploaded.json` and `instagram.json` after `git pull`. The Action sets the YouTube thumbnail (`thumbnail.json` when done). If YouTube rate-limits it, the run retries every 6 hours on a schedule. On Instagram, the thumbnail is appended as a 0.2 s end card and used as the Reel cover.

## Limits
- Facebook Page token: made from a long-lived user token, so it doesn't expire unless the password changes or access is removed. If it fails, the user makes a new one (Graph API Explorer → extend → `me/accounts`) and updates `FACEBOOK_PAGE_TOKEN`.
- Instagram token: long-lived and lasts 60 days. Refresh it before then with `tools/uu_instagram.py refresh <token>` (needs graph.instagram.com reachable), or have the user generate a new one in the Meta app dashboard. The user pastes it into the `INSTAGRAM_ACCESS_TOKEN` secret. Instagram allows 50 API posts per 24 hours.
- Until Google's YouTube API audit passes, API uploads are forced to **Private**. The user flips them to Public in Studio.
- While the OAuth app is in Testing, the refresh token expires after about 7 days (the Action fails with `invalid_grant`). Run `tools/uu_youtube.py auth-url` with the client secret and have the user sign in and paste back the localhost URL. Run `exchange`, then the user pastes the new token JSON into the `YOUTUBE_TOKEN_JSON` secret.
- Never print or commit secrets. They live only in the repo's Actions secrets.
