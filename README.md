# Unknown Uncovered

Hindi data reels for YouTube: curious facts, hidden stories, world data, explained simply.

- `videos/`: every reel, with its title, description and tags (`meta.json`) and upload result (`uploaded.json`)
- `tools/`: voice, video, music and upload scripts
- `.github/workflows/upload.yml`: uploads new reels to YouTube automatically when they're pushed
- `site/`: homepage and privacy policy for the uploader app

## One-time setup
Add two secrets under **Settings → Secrets and variables → Actions → New repository secret**:
- `CLIENT_SECRET_JSON`: the full contents of the Google OAuth `client_secret_*.json` file
- `YOUTUBE_TOKEN_JSON`: the full contents of `youtube_token.json`
