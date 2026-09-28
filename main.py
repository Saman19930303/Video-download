import os
import re
import uuid
import shutil
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp

BASE = Path(__file__).resolve().parent
DOWNLOADS = BASE / "downloads"
DOWNLOADS.mkdir(exist_ok=True)

app = FastAPI(title="HD Social Video Downloader API", version="1.0.0")

ALLOWED_HOSTS = {
    "facebook.com", "www.facebook.com", "m.facebook.com", "fb.watch",
    "instagram.com", "www.instagram.com",
    "tiktok.com", "www.tiktok.com", "vm.tiktok.com", "vt.tiktok.com"
}

class DownloadRequest(BaseModel):
    url: str

def valid_social_url(url: str) -> bool:
    try:
        p = urlparse(url.strip())
        if p.scheme not in ("http", "https"):
            return False
        host = (p.hostname or "").lower()
        return any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS)
    except Exception:
        return False

def safe_name(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "_", name).strip()
    return (name[:90] or "video")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/download")
def download(req: DownloadRequest):
    url = req.url.strip()
    if not valid_social_url(url):
        raise HTTPException(400, "Only Facebook, Instagram and TikTok URLs are accepted.")

    job = uuid.uuid4().hex
    outdir = DOWNLOADS / job
    outdir.mkdir(parents=True, exist_ok=True)

    # Highest available video + audio, then merge to MP4 where possible.
    opts = {
        "format": "bestvideo*+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": str(outdir / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = safe_name(info.get("title") or "video")

        candidates = list(outdir.glob("*"))
        video = next((p for p in candidates if p.suffix.lower() == ".mp4"), None)
        if video is None:
            video = next((p for p in candidates if p.is_file()), None)

        if video is None:
            raise RuntimeError("No downloaded media file was produced.")

        # Return a stable generated filename while retaining a safe title.
        final_name = f"{title}_{job[:8]}{video.suffix.lower()}"
        final_path = outdir / final_name
        if video != final_path:
            video.rename(final_path)

        return {
            "ok": True,
            "filename": final_name,
            "download_url": f"/file/{job}/{final_name}"
        }
    except Exception as e:
        shutil.rmtree(outdir, ignore_errors=True)
        raise HTTPException(500, f"Download failed: {str(e)[:700]}")

@app.get("/file/{job}/{filename}")
def get_file(job: str, filename: str):
    base = (DOWNLOADS / job).resolve()
    path = (base / filename).resolve()
    if base not in path.parents or not path.is_file():
        raise HTTPException(404, "File not found.")
    return FileResponse(path, media_type="video/mp4", filename=path.name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
