# HD Social Video Downloader

A complete Android + Python backend starter project for downloading publicly accessible
Facebook, Instagram and TikTok video URLs at the highest available quality and saving
the result to the Android device's Movies/Gallery media library.

## Important
- Use only videos you own or are authorized to download.
- Public URLs only. Private/login-required videos are not supported.
- Social platforms can change their delivery systems, so extractor support can change.
- The Android app does not scrape social platforms directly; the backend uses yt-dlp.
- For production, put the backend behind HTTPS and authentication/rate limiting.

## Project structure
- `android/` Android Studio project
- `backend/` FastAPI + yt-dlp downloader

## Backend setup

Python 3.10+ recommended.

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Backend runs on `http://0.0.0.0:8000`.

For a real Android phone on the same Wi-Fi:
1. Find the computer's LAN IP, e.g. `192.168.1.20`.
2. Set the Android app's `SERVER_URL` in `android/app/src/main/java/com/example/hdvideodownloader/Config.kt`
   to `http://192.168.1.20:8000/`.
3. Allow TCP port 8000 through the computer firewall.

For production hosting, use HTTPS, e.g.:
`https://your-domain.example/`

## Android build

Open `android/` in Android Studio and build/run.

The app:
1. Accepts a social URL.
2. Sends it to the backend.
3. Backend resolves the best available video/audio formats.
4. Backend returns the generated MP4.
5. Android downloads it using DownloadManager.
6. Android registers the MP4 in MediaStore under `Movies/HD Social Downloader`, so it appears in Gallery/video apps.

## Notes about "HD"
The backend asks yt-dlp for the best available video+audio combination and merges to MP4.
If a source only provides 720p, 720p is the maximum available; the app cannot create true
1080p/4K detail that the source does not provide.
