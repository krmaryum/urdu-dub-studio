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
    download_video, make_dub, make_transcript, preview_line, write_bilingual_transcripts,
    URDU_TRANSCRIPT_TITLE, write_reading_transcript, write_transcript, make_urdu_roman_export,
    TranslationError,
)

app = Flask(__name__, static_folder=None)
app.config.update(MAX_CONTENT_LENGTH=32768, TRUSTED_HOSTS=["127.0.0.1", "localhost"])
workspace = TemporaryDirectory(prefix="urdu-dub-")
pool = ThreadPoolExecutor(max_workers=1)
lock = Lock()
job = {}
MAX_UPLOAD_BYTES = 256 * 1024 * 1024
UPLOAD_SUFFIXES = {".mp4", ".mov", ".webm", ".mkv", ".m4a", ".mp3", ".wav"}
OUTPUT_FILENAMES = {
    "dub": "Urdu-Dub.mp4",
    "download": "Original-Video.mp4",
    "transcript-en": "English-Transcript.txt",
    "transcript-urdu-script": "Urdu-Script-Transcript.txt",
    "transcript-ur": "Roman-Urdu-Transcript.txt",
    "transcript-bilingual": "English-Roman-Urdu-Transcript.txt",
}


def job_status():
    status = {key: job[key] for key in ("id", "status", "stage", "revision", "mode") if key in job}
    if job.get("mode") == "transcript-urdu-script":
        status.update(
            roman_busy=bool(job.get("busy")),
            roman_ready="roman_output" in job,
            roman_stage=job.get("roman_stage", ""),
        )
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


def process(source, output, mode, technical_terms=""):
    def update(stage):
        with lock:
            job["stage"] = stage

    try:
        if mode == "download":
            with TemporaryDirectory(prefix="source-", dir=output.parent) as temp:
                video, _ = download_video(source, Path(temp), original=True)
                video.replace(output)
            result = {"stage": "Your original video is ready to download."}
        elif mode.startswith("transcript-"):
            transcript_lines = make_transcript(
                source, output, update,
                roman_urdu=mode in ("transcript-ur", "transcript-bilingual"),
                spoken_language="ur" if mode == "transcript-urdu-script" else "en",
                technical_terms=technical_terms,
                bilingual=mode == "transcript-bilingual",
            )
            result = {"stage": "Your timestamped and reading transcripts are ready."}
            if mode in ("transcript-bilingual", "transcript-urdu-script"):
                result["transcript_lines"] = transcript_lines
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

    finally:
        if isinstance(source, Path):
            try:
                source.unlink(missing_ok=True)
            except OSError:
                app.logger.exception("Could not remove the temporary upload")

    with lock:
        job.update(finished_at=monotonic(), **result)


@app.get("/")
def index():
    page = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
    return render_template_string(page, max_video_minutes=MAX_VIDEO_MINUTES, max_download_hours=MAX_DOWNLOAD_MINUTES // 60)


@app.errorhandler(413)
def request_too_large(_error):
    return jsonify(error="File too large. Choose a file smaller than 256 MB."), 413


@app.post("/api/jobs")
def create_job():
    if request.headers.get("Origin") not in {None, request.host_url.rstrip("/")}:
        return jsonify(error="Open this app on localhost."), 403
    is_upload = request.mimetype == "multipart/form-data"
    upload = None
    if is_upload:
        request.max_content_length = MAX_UPLOAD_BYTES + 64 * 1024
        payload = request.form.to_dict()
        payload["authorized"] = payload.get("authorized") == "true"
        upload = request.files.get("media")
        if not upload or Path(upload.filename).suffix.lower() not in UPLOAD_SUFFIXES:
            return jsonify(error="Choose an MP4, MOV, WebM, MKV, M4A, MP3, or WAV file."), 400
    else:
        payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Invalid request."), 400
    mode = payload.get("mode", "dub")
    if not isinstance(mode, str) or mode not in OUTPUT_FILENAMES:
        return jsonify(error="Choose dubbing, original download, or a transcript language."), 400
    technical_terms = payload.get("technical_terms", "") if mode == "transcript-urdu-script" else ""
    if not isinstance(technical_terms, str) or len(technical_terms) > 300:
        return jsonify(error="Enter up to 300 characters of technical terms."), 400
    technical_terms = " ".join(technical_terms.split())
    if is_upload and not mode.startswith("transcript-"):
        return jsonify(error="Local files are available with Transcript only."), 400
    source = None if is_upload else youtube_url(payload.get("url"))
    if not is_upload and not source:
        return jsonify(error="Paste a valid HTTPS link to a YouTube video or Short."), 400
    if payload.get("authorized") is not True:
        action = "transcribe" if is_upload else "dub" if mode == "dub" else "download"
        return jsonify(error=f"Confirm that you have permission to {action} the video."), 400

    with lock:
        if job.get("status") == "working" or job.get("busy"):
            return jsonify(error="A job or line edit is already in progress."), 409
        job_id = uuid4().hex
        folder = Path(workspace.name) / job_id
        output = folder / "0" / OUTPUT_FILENAMES[mode]
        output.parent.mkdir(parents=True)
        if upload is not None:
            source = folder / ("upload" + Path(upload.filename).suffix.lower())
            try:
                upload.save(source)
                size = source.stat().st_size
            except OSError:
                shutil.rmtree(folder, ignore_errors=True)
                app.logger.exception("Could not save the upload")
                return jsonify(error="Could not save the uploaded file."), 500
            if size == 0 or size > MAX_UPLOAD_BYTES:
                shutil.rmtree(folder, ignore_errors=True)
                return jsonify(error="Choose a nonempty file no larger than 256 MB."), 400
        old_folder = job.get("folder")
        if old_folder:
            shutil.rmtree(old_folder, ignore_errors=True)
        job.clear()
        job.update(
            id=job_id, status="working",
            stage="Downloading the original video." if mode == "download" else "Preparing to import the video.",
            revision=0, folder=folder, output=output, mode=mode, started_at=monotonic(),
        )
        pool.submit(process, source, output, mode, technical_terms)
        return jsonify(job_status()), 202


@app.get("/api/jobs")
def get_job():
    with lock:
        return jsonify(job_status())


@app.get("/api/jobs/<job_id>/lines")
def review_lines(job_id):
    with lock:
        if job.get("id") != job_id or job.get("status") != "ready":
            return jsonify(error="This result is unavailable."), 404
        if job["mode"] in ("transcript-bilingual", "transcript-urdu-script"):
            return jsonify(lines=[
                {"start": segment.start, "english": segment.text, "roman": roman}
                for segment, roman in job["transcript_lines"]
            ], revision=job["revision"], paired_roman=job.get("paired_roman"))
        if job["mode"] != "dub":
            return jsonify(error="This dub is unavailable."), 404
        return jsonify(lines=[
            {"start": line.start / job["rate"], "english": line.english, "roman": line.roman}
            for line in job["lines"]
        ])


@app.post("/api/jobs/<job_id>/lines/<int:index>/transcript")
def save_transcript_line(job_id, index):
    if request.headers.get("Origin") not in {None, request.host_url.rstrip("/")}:
        return jsonify(error="Open this app on localhost."), 403
    payload = request.get_json(silent=True)
    roman = payload.get("roman") if isinstance(payload, dict) else None
    if not isinstance(roman, str) or not 1 <= len(roman.strip()) <= 800:
        return jsonify(error="Enter a transcript line up to 800 characters."), 400
    roman = " ".join(roman.split())
    with lock:
        lines = job.get("transcript_lines", ())
        if job.get("id") != job_id or job.get("status") != "ready" or index >= len(lines):
            return jsonify(error="This transcript line is unavailable."), 404
        if job.get("busy"):
            return jsonify(error="Wait for Roman Urdu generation to finish."), 409
        if payload.get("revision") != job["revision"]:
            return jsonify(error="The transcript changed. Refresh and try again."), 409
        updated = list(lines)
        updated[index] = (updated[index][0], roman)
        revision = job["revision"] + 1
        output = job["folder"] / str(revision) / job["output"].name
        try:
            output.parent.mkdir()
            segments, texts = zip(*updated)
            if job["mode"] == "transcript-urdu-script":
                write_transcript(output, ((segment.start, text) for segment, text in updated))
                write_reading_transcript(output.with_suffix(".md"), URDU_TRANSCRIPT_TITLE, segments, texts)
            else:
                write_bilingual_transcripts(output, segments, texts)
        except OSError:
            shutil.rmtree(output.parent, ignore_errors=True)
            app.logger.exception("Could not save transcript edit")
            return jsonify(error="Could not save this edit. Try again."), 500
        previous = job["output"].parent
        job.pop("roman_output", None)
        job.pop("paired_roman", None)
        job.pop("roman_stage", None)
        job.update(output=output, revision=revision, transcript_lines=updated)
        shutil.rmtree(previous, ignore_errors=True)
        return jsonify(job_status())


@app.post("/api/jobs/<job_id>/lines/<int:index>/paired-roman")
def save_paired_roman(job_id, index):
    if request.headers.get("Origin") not in {None, request.host_url.rstrip("/")}:
        return jsonify(error="Open this app on localhost."), 403
    payload = request.get_json(silent=True)
    text = payload.get("roman") if isinstance(payload, dict) else None
    if not isinstance(text, str) or not 1 <= len(text.strip()) <= 3000:
        return jsonify(error="Enter a Roman Urdu line up to 3000 characters."), 400
    text = " ".join(text.split())
    with lock:
        translations = job.get("paired_roman", ())
        if job.get("id") != job_id or index >= len(translations):
            return jsonify(error="This Roman Urdu line is unavailable."), 404
        if job.get("busy") or payload.get("revision") != job["revision"]:
            return jsonify(error="The transcript changed. Refresh and try again."), 409
        updated = list(translations)
        updated[index] = text
        revision = job["revision"] + 1
        folder = job["output"].parent / f"paired-{revision}"
        output = folder / job["roman_output"].name
        try:
            folder.mkdir()
            segments = [segment._replace(text=saved) for segment, saved in job["transcript_lines"]]
            write_bilingual_transcripts(output, segments, updated, source_label="Urdu script")
        except OSError:
            shutil.rmtree(folder, ignore_errors=True)
            app.logger.exception("Could not save Roman Urdu edit")
            return jsonify(error="Could not save this edit. Try again."), 500
        previous = job["roman_output"]
        job.update(roman_output=output, paired_roman=updated, revision=revision)
        if previous.parent != job["output"].parent:
            shutil.rmtree(previous.parent, ignore_errors=True)
        return jsonify(job_status())


def generate_roman_export(output, lines):
    def update(stage):
        with lock:
            job["roman_stage"] = stage

    try:
        translations = make_urdu_roman_export(output, lines, update)
    except TranslationError as error:
        stage = str(error)
    except Exception:
        app.logger.exception("Could not generate Roman Urdu")
        stage = "Could not generate Roman Urdu. Try again."
    else:
        with lock:
            job.update(roman_output=output, paired_roman=translations)
        stage = "Urdu script + Roman Urdu downloads are ready."
    finally:
        with lock:
            job["roman_stage"] = stage
            job["busy"] = False


@app.post("/api/jobs/<job_id>/roman-export")
def start_roman_export(job_id):
    if request.headers.get("Origin") not in {None, request.host_url.rstrip("/")}:
        return jsonify(error="Open this app on localhost."), 403
    with lock:
        if job.get("id") != job_id or job.get("status") != "ready" or job.get("mode") != "transcript-urdu-script":
            return jsonify(error="This Urdu transcript is unavailable."), 404
        if job.get("busy"):
            return jsonify(error="A job or line edit is already in progress."), 409
        if "roman_output" in job:
            return jsonify(job_status())
        output = job["output"].with_name("Urdu-Script-and-Roman-Urdu.txt")
        job.update(busy=True, roman_stage="Preparing Roman Urdu…")
        pool.submit(generate_roman_export, output, list(job["transcript_lines"]))
        return jsonify(job_status()), 202


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
        if request.args.get("script") == "paired":
            output = job.get("roman_output")
            if output is None:
                return jsonify(error="The paired transcript is unavailable."), 404
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
