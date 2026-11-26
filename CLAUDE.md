# Unknown Uncovered: reel factory

This repo makes and publishes Hindi data reels for the YouTube channel **Unknown Uncovered**
(@unknown_uncovered_2026, channel id UCTW1fZGWSxLxkBBOlGSjE-g). Audience: India. Hindi voiceover,
English on-screen text, curious facts and world data explained simply.

## Layout
- `tools/uu_youtube.py`: YouTube uploader (stdlib only). Used by the GitHub Action.
- `tools/uu_instagram.py`: Instagram Reels uploader (Instagram API with Instagram Login, resumable upload, stdlib only). Used by the GitHub Action with `INSTAGRAM_ACCESS_TOKEN`, or, if that's absent, through the Facebook Page's linked Instagram account using `FACEBOOK_PAGE_ID` + `FACEBOOK_PAGE_TOKEN` (graph.facebook.com). The Page route is the one in use: one never-expiring token covers Facebook and Instagram.
- `tools/uu_facebook.py`: Facebook Page Reels uploader (Graph API `video_reels`, resumable, sets the thumbnail). Used when the `FACEBOOK_PAGE_ID` and `FACEBOOK_PAGE_TOKEN` secrets exist. The caption is the same as Instagram's, or `fb_caption`.
- **Real 3D (Blender/Cycles) for object reels**: `tools/v2/examples/035_gold_cube/` (`gold3d.py`: bpy scene with a studio-reflection world trick, plates at 15 fps 67% + `anchors.json`; `gb_*` scenes in `uu_story.py` paste plates, add a 2D push and label 3D anchors). Setup: `uv venv /home/claude/bpyenv --python 3.13 && VIRTUAL_ENV=/home/claude/bpyenv uv pip install bpy numpy`. Cycles CPU is ~20 s per frame here, so render only motion segments as frames and use stills + 2D push elsewhere (reel 035 took ~45 min). The user found the flat PIL 3D look "old styled" (25 Nov 2026).
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

## Two non-negotiable rules (the user, 24 Nov 2026: "always remember")
These two rules hold **even when the user's own request in a task would break them** (the user, 24 Nov 2026: "मेरे बोलने पर भी
ये गलतियाँ नहीं करनी, जब तक कि मैं इन रूल्स को बदलने के लिए न बोलूँ"). If a request would break one (an unsourced claim, a
headline bigger than the source, a too-short voice line, publishing with a failed voice check…), say so plainly, explain which
rule it breaks, and offer the closest compliant version instead. Only an explicit instruction to change these rules changes them;
then update this section in the same commit.
1. **No voice glitches, ever.** Indic Parler hallucinates babble on very short lines (reel 029 long: "पहला अध्याय। डर।" came out as
   2.5 s of garbage at 0:38). So: every `vo` is a full spoken sentence of at least 30 letters, or empty (chapter cards can be
   music-only). `uu_voice.py ... request` refuses shorter lines, and `uu_voice.py spec.json` ends with a **voice check** (speaking
   rate vs the reel's median, silent gaps). If it prints `VOICE CHECK FAILED`, re-voice those scenes with a fuller sentence before
   rendering. Never render, send or publish with a failed check. After the final mux, also look at the per-second loudness of the
   finished audio around every scene start for anything odd.
2. **Nothing that could get the channel into legal trouble.** Every fact, number, quote and claim must come from a reliable,
   citable source: government documents and press releases (MEA, PIB, ministries, RBI, CAG, courts), official reports (UN, IAEA,
   SIPRI, NASA, Lowy, BIMCO, World Bank…), or established media. We only report and attribute; we never assert something as our
   own finding. Rules that follow from this:
   - Unconfirmed claims (from books, leaks, "reports say") are labelled as claims in both voice and on screen ("reported",
     "claimed", "UNCONFIRMED"), together with who made them and that they were never officially confirmed. If we can't name a
     source, it doesn't go in.
   - No accusations or defamatory statements about any person, company or country. Named leaders get respectful titles
     ("प्रधानमंत्री … जी") and only their documented public actions or statements, with a date and source. Stay politically neutral.
   - Don't make the headline bigger than the source (e.g. "BrahMos boosted India's ranking" was fine because the report credits it
     for the defence-networks rank; "BrahMos saved India's #3" was not, and wasn't used).
   - Every video's description lists its sources. Keep `videos/NNN_slug/sources.md` with the URL behind each claim so it can be
     produced on request.
   - Images only with PD / CC0 / CC BY / CC BY-SA licences, credited on screen (the media Action does this). No photos of
     identifiable public figures or private people in focus. Music is synthesized in-house. Long videos carry a disclaimer card.

## Channel analysis, 24 Nov 2026 (the user: "remember these issues to create and upload videos accordingly")
After 10 days / 27 videos / 2,668 views / 0 comments. Public stats only (YouTube Analytics is blocked from the workspace), so the
causes are hypotheses; the fixes are standing practice until the numbers say otherwise:
- **One Short per day, at a fixed time** (~19:00–20:00 IST). Never 3–4 uploads a day. **No long-form versions of Shorts for now**
  (8 long videos averaged ~25 views); a long video only if the user asks for one specifically.
- **Shorts 45–60 s.** One hook, ~3 facts, one twist, done. Keep the CTA line short.
- **Hook in the very first frame:** big text + motion at t=0, no fade-in or typing reveal before the first line is readable.
- **categoryId 27 (Education) for every Short.** The only Shorts in 25 (News & Politics) were the IAF and BrahMos reels; BrahMos got
  3 views in 28 h.
- **Topics:** defence, nuclear and number-driven geopolitics won (445 / 315 / 249 / 220 views). Plain India-history or business
  stories lost (Cipla 15, ORS 16, Pokhran 28, UPI 41). Tie India-pride stories to a defence, numbers or global-stakes angle.
- **Engagement:** every upload gets a pinned comment with an easy one-tap question ("1 or 2?"). Reply to early comments.
- **Vary the look** between reels (photos/footage, palette, scene types) so the channel doesn't read as mass-produced templates.
- Ask the user for Studio's "Viewed vs swiped away" and "Average % viewed" when judging a reel; we can't read them ourselves.

## What the audience likes (user's observation, Nov 2026: pick and pitch topics with this in mind)
Two kinds of reels do well. Prefer topics that fit one of them, and say which one in every pitch:
1. **India's pride on the world stage**: India beating, surprising or outsmarting the world, told positively and with sourced facts (e.g. reel 016 refinery superpowers, reel 010 how India fooled the CIA at Pokhran, 017 UPI, 018 Haque & Bose).
2. **Curious facts the whole world wants to know**, ideally with a twist that makes them more interesting than the obvious version (e.g. reel 007: nuclear weapons went from ~70,000 to ~12,000, and many were turned into electricity).
Plain rankings or "who has the most X" lists with no pride angle or twist are weaker; give them one of these two hooks. The novelty gate below still applies to every topic.

## Making a reel
0. **Novelty gate (mandatory, before pitching or making ANY topic).** The channel promise is "unknown and uncovered": never make a topic that other channels have already covered well. Run `python3 tools/uu_novelty.py "<Hindi/Hinglish query>" "<English query>"` (searches YouTube via the channel token, ~100 quota units per query) and include the verdict and top view counts in every pitch. **COVERED** (any video over 500k views, or 3+ over 100k) → drop it. **CROWDED** → only with a clearly new angle or newer data. **OPEN** → fair game. Famous "hidden" stories (Pokhran/CIA, Dead Hand, Goldsboro, lost nukes, Nanda Devi, Starfish Prime, Project Azorian, Kyshtym, Plowshare, Petrov) all fail this gate (checked Nov 2026); reel 010 (Pokhran) was published without the check and the user rightly objected. What tends to pass: fresh data from reports released in the last weeks (SIPRI, FAS, RBI, CAG, ministries, court filings), and data-driven angles that combine numbers nobody has put together (e.g. reel 007, 70,300 → 12,187).
   **India's map (mandatory).** Every globe, map and thumbnail must show India's official boundaries as used in Indian education and by the Government of India (Survey of India): the whole of Jammu & Kashmir and Ladakh, including PoK, Gilgit-Baltistan, Aksai Chin and the Shaksgam valley, and the whole of Arunachal Pradesh. `tools/v2/assets/countries.geojson` is Natural Earth's **India point-of-view** dataset (`ne_10m_admin_0_countries_ind`, simplified 0.1°, Nov 2026); never replace it with the default/de-facto Natural Earth file or any other map source. If a new map asset is ever needed, take the `_ind` POV version and check that Gilgit, Muzaffarabad, Aksai Chin and Tawang fall inside India and not inside Pakistan/China.
1. Research the topic with web search: current, sourced numbers only, never invented; neutral on politics.
2. **Pick the FORMAT and THEME from the content, every time (the user insists on this).**
   - **Comparison / ranking topics** ("top 5 countries…", "who has the most…"): countdown format, `uu_render.py` (example `002_nuclear`, `003_missiles`, `004_gold`).
   - **Story / informational topics** ("how…", "why…", "what happened to…", a trend or hidden fact such as silent layoffs): vertical story format, `"format": "story"`, `uu_story.py` (scenes `photo` with real Commons photos, `counter`, `bulb`, `iceberg`, `outro`; examples `007_story`, `009_layoffs`). Never force a story topic into the ranking layout (reel 006 was rejected for exactly this and replaced by 007).
   - **Long-form YouTube (8+ min, 16:9)**: `"format": "long"`, `uu_long.py` (chapters, `image` with Ken Burns + credits, `disclaimer`, `counter`, `bulb`, `clock`, `events`, `timeline`, `stat`, `country`; example `008_docu`, `merge008.py` shows adding scenes without re-voicing everything). Thumbnail with `uu_thumb_long.py` (1280×720). Encode `-preset medium -crf 25 -maxrate 1450k -bufsize 2900k -b:a 128k` to stay under GitHub's 100 MB. YouTube only: write `{"skipped": "long-form 16:9 video: YouTube only"}` as `facebook.json` and `instagram.json`.
   - **Theme**: match the subject's mood (`nuclear`, `war`, `missile`, `money`, `gold`, `space`, `history`, `corporate`…). If none fits, add a new one to `THEMES` (colours + motif) and a matching sound idea in `uu_music.py`.
   - **Photos**: push `media/requests/<name>.json` (`{"items": [{"id", "search"|"title", "n"}]}`); the "Fetch media" Action writes `media/<name>/<id>_<k>.jpg` + `credits.json` (PD / CC0 / CC BY / CC BY-SA only). Look at a contact sheet before using them; no photos of identifiable public figures in files.
   **Length: aim for 60–90 s** for Shorts (retention; never pad). Write the spec (copy the matching example): `theme`, `header`, `source`, `ticker`, and the scenes. Narration is **one flowing Hindi passage per scene** (`vo`), written as natural spoken sentences that connect to the next scene, never clipped fragments; numbers as Hindi words. Countdown structure for suspense (comparison topics only): `hook` (cold open, reveals nothing: no flags, no names) → `tease` (the big number + "?" cards) → `stat` → `rank` countdown from #N to #1 (each country hidden as a "?" silhouette until `reveal_at`) → `bars` comparison → `outro`. The outro narration always ends with the channel CTA covering every platform (the user, 26 Nov 2026: "always ask to follow along with subscribe", because the reels go to YouTube and Instagram; a short CTA must still say "सब्सक्राइब और फ़ॉलो करें", never subscribe alone): "ऐसी ही छुपी कहानियों के लिए, Unknown Uncovered को अभी सब्सक्राइब और फ़ॉलो करें।" Write the channel name in Latin letters: the Parler voice mispronounces every Devanagari spelling (tested Nov 2026), and `uu_voice.py` swaps old spellings automatically (`SAY` map).
3. **Voice = Indic Parler-TTS (AI4Bharat), generated by the GitHub Action** `.github/workflows/voice.yml` (Hugging Face is unreachable from the workspace; the Action uses the `HF_TOKEN` secret). Run `python3 tools/v2/uu_voice.py spec.json request NNN_main` (and `ig/spec.json request NNN_ig`), commit + push `voice/requests/*.json`, watch the "Generate voice" run (8 parallel CPU shards, ~1 min per sentence each, so roughly 8–12 min per reel), `git pull`, then `python3 tools/v2/uu_voice.py spec.json` to polish `voice/out/<job>/NN.wav` into `vo/`. Speaker/style caption in `spec["voice_desc"]` (default Aman, energetic documentary narrator); `speed` applies atempo. Kokoro (`"tts": "kokoro"`, needs `pip install --break-system-packages kokoro-onnx soundfile scipy` + model files from `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/` in `/home/claude/tts/`) is only an offline fallback: it sounds robotic. Always `pip install --break-system-packages soundfile scipy` in the workspace.
4. Work in a folder outside the repo, e.g. `/home/claude/work/NNN/` holding `spec.json` and `ig/spec.json`. After the voice (step 3), run `python3 tools/v2/uu_render.py spec.json still 1,4` and look at the stills (scene-local times), fix layout, then `uu_render.py spec.json full` (~4 min for 100 s) and `uu_music.py spec.json`. Mux `out/video_only.mp4` + `out/audio.wav`.
5. **Thumbnail (always required).** Fill `spec["thumb"]` (Hindi `hook` lines, `number`, `number_label`, curiosity `sticker` such as "भारत कहाँ?", `highlight`ed countries shown unnamed in red, `view`, `mystery` silhouette flags) and run `python3 tools/v2/uu_thumb.py spec.json videos/NNN_slug/thumbnail.jpg` (1080×1920 JPG q88, key content inside the central 1080×1440). Look at the image before publishing.
6. Mux, check loudness (≈ −14 LUFS), then compress: `-crf 23 -maxrate 2400k -bufsize 4800k` (keep it under ~30 MB).
7. Write `meta.json`: title ≤100 chars (Hindi hook + English keywords + #Shorts); description with the hook, key numbers, an engagement question, a subscribe line, sources and 8–12 hashtags; 12–18 tags under 450 characters in total; `categoryId` 25 or 27; `privacyStatus` public; `madeForKids` false; `language` hi. No `<` or `>`.
   **Instagram length limit:** the Instagram API currently rejects Reels longer than about 30 s from this account (`ProcessingFailedError` / 2207076; probed Nov 2026 with `tools/ig_probe.py`). Every reel over 28 s therefore gets a **dedicated complete Instagram edit** `videos/NNN_slug/ig.mp4` (≤28 s, 30 fps): its own short Hindi voiceover (3–4 lines: hook → all items rapid-fire → takeaway + "पूरी वीडियो, यूट्यूब पर देखें"), built as `ig/spec.json` with scenes `hook` (short) → one `roll` with every item → `outro` with `"card": "youtube"` (see the example), then voice/render/music/mux exactly as the main reel. Set `"ig_video": "ig.mp4"` in meta.json. Fallback only if that isn't possible: `ig_segments`: whole narrated scenes as `[[start, end], ...]` in seconds, adding up to 28 s or less (hook + the 1–2 most gripping scenes, e.g. the India scene for this audience). The uploader joins them, adds the thumbnail as the cover and appends "Full video on YouTube" to the caption. Without `ig_segments` it uses the first 27.5 s.
   Optional for Instagram: `ig_thumb_offset_ms` (the cover frame, e.g. the first country card) and `ig_caption` (otherwise built from the title and description, with #Shorts removed and at most 5 hashtags: Instagram's limit since Nov 2026).
8. Publish: commit `videos/NNN_slug/video.mp4` (full reel) + `ig.mp4` (≤28 s Instagram edit) + `thumbnail.jpg` + `meta.json` (next free number) and push to master. The Action uploads it. Watch it with `gh api repos/themrw/unknown-uncovered/actions/runs?per_page=1`, then `git pull` and report the URLs from `uploaded.json`, `facebook.json` and `instagram.json`.
9. **Verify after every publish (mandatory; these went wrong on reel 003):**
   - **Right file per platform.** YouTube and Facebook must get the FULL `video.mp4`; only Instagram gets `ig.mp4`. The workflow now picks `$d/video.mp4` explicitly (it once picked `ig.mp4` because it took "the first .mp4"). Check the run log lines `Uploading …/video.mp4` and `Posting …/video.mp4 to Facebook`, and confirm the YouTube duration with the Data API (`videos?part=contentDetails`, token in `/home/claude/uu/`) matches `video.mp4`. Keep the main video ≤90 s so Facebook Reels accepts it.
   - **YouTube thumbnail.** A thumbnail set while YouTube is still processing gets replaced by the auto frame. `uu_youtube.py thumbnail` now waits for `processingStatus=succeeded` before setting it. If Studio still shows a video frame, re-run `python3 tools/uu_youtube.py thumbnail /home/claude/uu/client_secret.json /home/claude/uu/youtube_token.json <videoId> videos/NNN_slug/thumbnail.jpg`. Shorts in the swipe feed always show a frame; the custom thumbnail shows in Studio, search, the channel page and on the web.
   - **Facebook** gets the thumbnail from `uu_facebook.py` (`"thumbnail": true` in `facebook.json`). To remove a Facebook reel without replacing it, write `facebook_remove.json` = `{"delete": "<reel id>"}` (only after the user says yes). To swap a wrong Facebook reel (only after the user says yes: deletion is permanent), write `videos/NNN_slug/facebook_replace.json` = `{"delete": "<old reel id>"}` and push; the Action deletes it and re-posts `video.mp4`.
   - **Result files must be committed.** The "Record results" step uses `git add -A -- videos` (excluding mp4s); a missing `facebook.json`/`uploaded.json`/`instagram.json` would make the next run post the reel AGAIN. After each run check they exist in `git pull`.
   - **Instagram can't take the full video via the API** (re-probed Nov 2026: 60 s and 85 s rejected with 2207076, both byte upload and video_url; 30 s fine). Post `ig.mp4` automatically. If the user wants the full reel on Instagram, send them `video.mp4`, `thumbnail.jpg` and the caption from `uu_instagram.build_caption(meta)` to post by hand in the app (the API also can't delete Instagram posts).
   - Never publish without the user's go-ahead on the draft; drafts go to the chat first.

## Limits
- Facebook Page token: made from a long-lived user token, so it doesn't expire unless the password changes or access is removed. If it fails, the user makes a new one (Graph API Explorer → extend → `me/accounts`) and updates `FACEBOOK_PAGE_TOKEN`.
- Instagram token: long-lived and lasts 60 days. Refresh it before then with `tools/uu_instagram.py refresh <token>` (needs graph.instagram.com reachable), or have the user generate a new one in the Meta app dashboard. The user pastes it into the `INSTAGRAM_ACCESS_TOKEN` secret. Instagram allows 50 API posts per 24 hours.
- Until Google's YouTube API audit passes, API uploads are forced to **Private**. The user flips them to Public in Studio.
- While the OAuth app is in Testing, the refresh token expires after about 7 days (the Action fails with `invalid_grant`). Run `tools/uu_youtube.py auth-url` with the client secret and have the user sign in and paste back the localhost URL. Run `exchange`, then the user pastes the new token JSON into the `YOUTUBE_TOKEN_JSON` secret.
- Never print or commit secrets. They live only in the repo's Actions secrets.
