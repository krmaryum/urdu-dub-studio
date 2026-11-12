from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import re
import shutil
from tempfile import TemporaryDirectory
from threading import Lock
from time import monotonic
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

from flask import Flask, jsonify, render_template_string, request, send_file

from dubbing import (
    MAX_DOWNLOAD_MINUTES, MAX_VIDEO_MINUTES, DubError, apply_line,
    download_video, make_dub, make_transcript, preview_line,
)

app = Flask(__name__, static_folder=None)
app.config.update(MAX_CONTENT_LENGTH=4096, TRUSTED_HOSTS=["127.0.0.1", "localhost"])
workspace = TemporaryDirectory(prefix="urdu-dub-")
pool = ThreadPoolExecutor(max_workers=1)
lock = Lock()
job = {}
OUTPUT_FILENAMES = {
    "dub": "Urdu-Dub.mp4",
    "download": "Original-Video.mp4",
    "transcript-en": "English-Transcript.txt",
    "transcript-ur": "Roman-Urdu-Transcript.txt",
}


def job_status():
    status = {key: job[key] for key in ("id", "status", "stage", "revision", "mode") if key in job}
    if "started_at" in job:
        end = monotonic() if job["status"] == "working" else job["finished_at"]
        status["elapsed_seconds"] = int(end - job["started_at"])
    return status


def youtube_url(value):
    if not isinstance(value, str) or len(value) > 1500:
        return None
    try:
        parsed = urlsplit(value.strip())
        host = parsed.hostname
        if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port:
            return None
    except ValueError:
        return None

    parts = parsed.path.strip("/").split("/")
    code = ""
    if host == "youtu.be" and len(parts) == 1:
        code = parts[0]
    elif host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parts == ["watch"]:
            code = parse_qs(parsed.query).get("v", [""])[0]
        elif len(parts) == 2 and parts[0] in {"shorts", "live", "embed"}:
            code = parts[1]
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", code):
        return f"https://www.youtube.com/watch?v={code}"
    return None


def process(source, output, mode):
    def update(stage):
        with lock:
            job["stage"] = stage

    try:
        if mode == "download":
            with TemporaryDirectory(prefix="source-", dir=output.parent) as temp:
                video, _ = download_video(source, Path(temp), original=True)
                video.replace(output)
            result = {"stage": "Your original video is ready to download."}
        elif mode in ("transcript-en", "transcript-ur"):
            make_transcript(source, output, update, roman_urdu=mode == "transcript-ur")
            result = {"stage": "Your timestamped and reading transcripts are ready."}
        else:
            rate, lines = make_dub(source, output, update)
            result = {"stage": "Your dubbed video and transcript are ready.", "rate": rate, "lines": lines}
    except DubError as error:
        result = {"status": "failed", "stage": str(error)}
    except Exception:
        app.logger.exception("Dubbing job failed")
        result = {"status": "failed", "stage": "Could not process the video. Check the app logs for details."}
    else:
        result["status"] = "ready"

    with lock:
        job.update(finished_at=monotonic(), **result)


@app.get("/")
def index():
    page = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
    return render_template_string(page, max_video_minutes=MAX_VIDEO_MINUTES, max_download_hours=MAX_DOWNLOAD_MINUTES // 60)


@app.post("/api/jobs")
def create_job():
    if request.headers.get("Origin") not in {None, request.host_url.rstrip("/")}:
        return jsonify(error="Open this app on localhost."), 403
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Invalid request."), 400
    mode = payload.get("mode", "dub")
    if not isinstance(mode, str) or mode not in OUTPUT_FILENAMES:
        return jsonify(error="Choose dubbing, original download, or a transcript language."), 400
    source = youtube_url(payload.get("url"))
    if not source:
        return jsonify(error="Paste a valid HTTPS link to a YouTube video or Short."), 400
    if payload.get("authorized") is not True:
        action = "dub" if mode == "dub" else "download"
        return jsonify(error=f"Confirm that you have permission to {action} the video."), 400

    with lock:
        if job.get("status") == "working" or job.get("busy"):
            return jsonify(error="A job or line edit is already in progress."), 409
        job_id = uuid4().hex
        folder = Path(workspace.name) / job_id
        output = folder / "0" / OUTPUT_FILENAMES[mode]
        output.parent.mkdir(parents=True)
        old_folder = job.get("folder")
        if old_folder:
            shutil.rmtree(old_folder, ignore_errors=True)
        job.clear()
        job.update(
            id=job_id, status="working",
            stage="Downloading the original video." if mode == "download" else "Preparing to import the video.",
            revision=0, folder=folder, output=output, mode=mode, started_at=monotonic(),
        )
        pool.submit(process, source, output, mode)
        return jsonify(job_status()), 202


@app.get("/api/jobs")
def get_job():
    with lock:
        return jsonify(job_status())


@app.get("/api/jobs/<job_id>/lines")
def review_lines(job_id):
    with lock:
        if job.get("id") != job_id or job.get("status") != "ready" or job.get("mode") != "dub":
            return jsonify(error="This dub is unavailable."), 404
        return jsonify(lines=[
            {"start": line.start / job["rate"], "english": line.english, "roman": line.roman}
            for line in job["lines"]
        ])


@app.post("/api/jobs/<job_id>/lines/<int:index>/preview")
def create_preview(job_id, index):
    if request.headers.get("Origin") not in {None, request.host_url.rstrip("/")}:
        return jsonify(error="Open this app on localhost."), 403
    payload = request.get_json(silent=True)
    roman = payload.get("roman") if isinstance(payload, dict) else None
    if not isinstance(roman, str) or not 1 <= len(roman.strip()) <= 800:
        return jsonify(error="Enter a Roman Urdu line up to 800 characters."), 400
    roman = " ".join(roman.split())
    with lock:
        if job.get("id") != job_id or job.get("status") != "ready" or index >= len(job.get("lines", ())):
            return jsonify(error="This line is unavailable."), 404
        if job.get("busy"):
            return jsonify(error="Another edit is in progress."), 409
        job["busy"] = True
        job.pop("preview", None)
        line = job["lines"][index]
        path = job["folder"] / "preview.wav"
    try:
        preview_line(line, roman, path)
        token = uuid4().hex
        with lock:
            job["preview"] = (token, index, roman, path)
        return jsonify(token=token)
    except DubError as error:
        return jsonify(error=str(error)), 422
    except Exception:
        app.logger.exception("Line preview failed")
        return jsonify(error="Could not preview this line. Check the WSL terminal."), 500
    finally:
        with lock:
            job["busy"] = False


@app.get("/api/jobs/<job_id>/preview/<token>")
def get_preview(job_id, token):
    with lock:
        preview = job.get("preview")
        if job.get("id") != job_id or not preview or preview[0] != token:
            return jsonify(error="This preview is unavailable."), 404
        return send_file(preview[3], mimetype="audio/wav")


@app.post("/api/jobs/<job_id>/preview/<token>/apply")
def save_preview(job_id, token):
    if request.headers.get("Origin") not in {None, request.host_url.rstrip("/")}:
        return jsonify(error="Open this app on localhost."), 403
    with lock:
        preview = job.get("preview")
        if job.get("id") != job_id or not preview or preview[0] != token:
            return jsonify(error="Preview the edited line before applying it."), 404
        if job.get("busy"):
            return jsonify(error="Another edit is in progress."), 409
        job["busy"] = True
        _, index, roman, path = preview
        previous, rate, lines = job["output"], job["rate"], job["lines"]
        revision = job["revision"] + 1
        output = job["folder"] / str(revision) / "Urdu-Dub.mp4"
    applied = False
    try:
        output.parent.mkdir()
        updated = apply_line(previous, output, path, rate, lines, index, roman)
        with lock:
            job.update(output=output, lines=updated, revision=revision, stage="Your edited dub is ready.")
            job.pop("preview", None)
            result = job_status()
        applied = True
        return jsonify(result)
    except DubError as error:
        return jsonify(error=str(error)), 422
    except Exception:
        app.logger.exception("Could not apply the line edit")
        return jsonify(error="Could not apply the edit. Your previous export is still available."), 500
    finally:
        shutil.rmtree(previous.parent if applied else output.parent, ignore_errors=True)
        with lock:
            job["busy"] = False


@app.get("/video/<job_id>")
def video(job_id):
    with lock:
        if job.get("id") != job_id or job.get("status") != "ready" or job["output"].suffix != ".mp4":
            return jsonify(error="This video is unavailable."), 404
        return send_file(
            job["output"],
            mimetype="video/mp4",
            as_attachment=request.args.get("download") == "1",
            download_name=job["output"].name,
        )


@app.get("/transcript/<job_id>")
def transcript(job_id):
    with lock:
        if job.get("id") != job_id or job.get("status") != "ready" or job.get("mode") == "download":
            return jsonify(error="This transcript is unavailable."), 404
        output = job["output"]
        reading = request.args.get("format") == "reading"
        if reading:
            if job["mode"] == "dub":
                return jsonify(error="The reading transcript is available in Transcript only mode."), 404
            output = output.with_suffix(".md")
        if job["mode"] == "dub":
            output = output.with_suffix(".txt")
        return send_file(
            output,
            mimetype="text/markdown" if reading else "text/plain",
            as_attachment=True,
            download_name="Roman-Urdu-Transcript.txt" if job["mode"] == "dub" else output.name,
        )


if __name__ == "__main__":
    app.run(host=os.environ.get("URDU_DUB_HOST", "127.0.0.1"), port=8765, threaded=True)
