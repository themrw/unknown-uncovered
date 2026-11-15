# Unknown Uncovered: reel factory

This repo makes and publishes Hindi data reels for the YouTube channel **Unknown Uncovered**
(@unknown_uncovered_2026, channel id UCTW1fZGWSxLxkBBOlGSjE-g). Audience: India. Hindi voiceover,
English on-screen text, curious facts and world data explained simply.

## Layout
- `tools/uu_youtube.py`: YouTube uploader (stdlib only). Used by the GitHub Action.
- `tools/tts_template.py`: Kokoro Hindi TTS (voice `hm_omega`, speed 1.1, lang `hi`) → `vo_NN.wav` + `durs.json`.
- `tools/render_template.py`: 1080×1920 60 fps PIL renderer (radar, ticker, flags, typed text, glitch transitions). A template: copy it and write new scene functions for each topic.
- `tools/music_template.py`: synthesized military-style score + voice mix with ducking (imports the renderer as `render3`).
- `videos/NNN_slug/`: one folder per reel: `video.mp4`, `meta.json`, and `uploaded.json` once it's on YouTube.
- `.github/workflows/upload.yml`: on push of a `videos/*/meta.json`, uploads every folder with no `uploaded.json` and commits the result.
- `site/`: homepage + privacy policy for the Google OAuth consent screen.

## Making a reel
1. Research the topic with web search: current, sourced numbers only, never invented; neutral on politics.
2. Write 8–12 Hindi voiceover lines (hook → big number → items one by one → comparison → outro "फ़ॉलो करें"). Write numbers as Hindi words for TTS.
3. Setup in the workspace: `pip install --break-system-packages kokoro-onnx soundfile scipy`, then download `kokoro-v1.0.onnx` and `voices-v1.0.bin` from
   `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/` into `/home/claude/tts/`.
4. Copy the templates to `/home/claude/tts/tts.py`, `/home/claude/reel2/render3.py` and `/home/claude/reel2/music3.py` (these paths are hard-coded), adapt the lines, scenes and data, and render 2–3 stills to check before the full render.
5. Mux, check loudness (≈ −14 LUFS), then compress: `-crf 23 -maxrate 2400k -bufsize 4800k` (keep it under ~30 MB).
6. Write `meta.json`: title ≤100 chars (Hindi hook + English keywords + #Shorts); description with the hook, key numbers, an engagement question, a subscribe line, sources and 8–12 hashtags; 12–18 tags under 450 characters in total; `categoryId` 25 or 27; `privacyStatus` public; `madeForKids` false; `language` hi. No `<` or `>`.
7. Publish: commit `videos/NNN_slug/video.mp4` + `meta.json` (next free number) and push to master. The Action uploads it. Watch it with `gh api repos/themrw/unknown-uncovered/actions/runs?per_page=1`, then report the URL from `uploaded.json` after `git pull`.

## Limits
- Until Google's YouTube API audit passes, API uploads are forced to **Private**. The user flips them to Public in Studio.
- While the OAuth app is in Testing, the refresh token expires after about 7 days (the Action fails with `invalid_grant`). Run `tools/uu_youtube.py auth-url` with the client secret and have the user sign in and paste back the localhost URL. Run `exchange`, then the user pastes the new token JSON into the `YOUTUBE_TOKEN_JSON` secret.
- Never print or commit secrets. They live only in the repo's Actions secrets.
