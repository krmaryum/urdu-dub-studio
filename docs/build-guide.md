# Build the app in stages

Complete the [local setup](local-setup.md) first. Start with a 20–60 second English video you own or have permission to dub. Use the same clip for each stage so you can trace a line from the source to the final export.

## 1. Serve the page and validate links

**Goal.** Accept a single YouTube video link and return a job status the browser can poll.

**Design decision.** Use Flask and one background worker. A long CPU job can run while the browser continues to poll for progress.

**Implementation.** In `app.py`, implement `youtube_url` to validate and normalize watch, short, and share links. Add the job routes and an in-memory job record. In `index.html`, submit the URL and permission checkbox, then poll `/api/jobs`.

**Verify.** Start Flask. Open the page and confirm a non-YouTube URL is rejected and a valid link requires the permission checkbox.

## 2. Download the video and extract English speech

**Goal.** Get a local video and produce English text with timing.

**Design decision.** Use yt-dlp with Deno for import and faster-whisper `small.en` with CPU INT8 inference. Keep word timestamps so later stages can group by speech boundaries.

**Implementation.** In `dubbing.py`, use `download_video` and FFprobe to enforce the duration limit. In `make_dub`, extract mono 16 kHz audio, transcribe it, and pass the results through `group_speech`. That groups words by punctuation, pauses, and segment limits.

**Verify.** Call `download_video` with your authorized URL and a temporary directory. Use `ffprobe` on the result. Step through `make_dub` or temporarily log the grouped segments and confirm that their text and timestamps match the English audio.

## 3. Generate matching Urdu and Roman Urdu lines

**Goal.** Produce natural Pakistani Urdu for speech and matching Roman Urdu for download.

**Design decision.** Use local Ollama with `qwen3.5:4b`. Send nearby context and the available seconds alongside each segment. Request structured output so returned lines can be matched to their inputs.

**Implementation.** In `local_translation.py`, implement `request_lines` and `translate_segments`. Validate both scripts, preserve technical acronyms, and retry obvious copied, incomplete, or repeated lines. The repeat check looks back three accepted lines and allows similar English source lines to repeat.

**Verify.** Inspect the English and Roman Urdu in **Review and edit one line**. Include a technical term, a number, and a negative statement in the test clip. Confirm that the translation preserves all three.

## 4. Synthesize and export

**Goal.** Replace the English soundtrack with timed Urdu and export a readable transcript.

**Design decision.** Use the Pakistani Urdu Fasih voice through Piper. Place each line on the original timeline, then fit its duration to the available audio slot.

**Implementation.** In `dubbing.py`, use `synthesize_line` for pronunciation handling, `voice_track` and `fit_speech` for timing, and `render` to mux the dubbed audio with the video. Use `write_transcript` for timestamped Roman Urdu.

**Verify.** Download the MP4 and transcript. Use FFprobe to confirm the MP4 contains video and audio. Listen near the beginning and end, and check that transcript timestamps match the narration.

## 5. Add single-line correction

**Goal.** Let a user fix one line without rerunning the full pipeline.

**Design decision.** Preview the replacement before applying it. Use a separate output revision so a failed edit leaves the current export available.

**Implementation.** Add the review, preview, and apply routes in `app.py`. Wire the controls in `index.html`. Use `preview_line` and `apply_line` in `dubbing.py` to synthesize a replacement, write it into the line's slot, and update the transcript.

**Verify.** Edit one short line and preview it. Apply it, download both files again, and confirm that the corrected words appear in the video and transcript while the surrounding narration stays in place.
