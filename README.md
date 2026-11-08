# Urdu Dub Studio

Turn an English YouTube video into a conversational Pakistani Urdu dub and a timestamped Roman Urdu transcript. Transcription, translation, and voice synthesis run on your computer. The app needs internet access to import videos and download its models.

## Quick start with Docker

Install Docker with Compose v2, then open a terminal in this project folder and run:

```bash
docker compose up --build -d
docker compose ps -a
```

The first startup builds the app image and pulls the Ollama model. Once the app is healthy, open [http://localhost:8765](http://localhost:8765). The first dub downloads the speech models. See the [container setup guide](docs/container-setup.md) for installation, startup progress, and shutdown.

## Create a dub

1. Paste the URL of an English YouTube video or Short. The default limit is five minutes. For longer clips, use the setting in the [local](docs/local-setup.md#enable-longer-videos) or [container guide](docs/container-setup.md#4-enable-longer-videos). Use a video you have permission to download and dub.
2. Confirm permission and choose **Start dubbing**.
3. Play the result. To correct a line, choose its timestamp under **Review and edit one line**, edit the Roman Urdu, and select **Preview edited line**. Select **Apply to video** once the preview is ready.
4. Download the MP4 and transcript before closing the app or starting another job.

## Download the original video

To save the original video with its audio, confirm you have permission to download it and choose **Download original video**. This mode prepares an MP4 up to 480p, allows videos up to three hours, and skips the dubbing pipeline. Once it is ready, select **Download original MP4**.

## Project guide

| Guide | Contents |
| --- | --- |
| [Local setup](docs/local-setup.md) | Install and verify Python, FFmpeg, Deno, and Ollama on Ubuntu or WSL |
| [Build guide](docs/build-guide.md) | Rebuild the app in stages and verify each piece |
| [Container setup](docs/container-setup.md) | Run the CPU stack with Docker Compose |
| [Troubleshooting](docs/troubleshooting.md) | Diagnose import, translation, audio, and editor problems |
| [Release notes](docs/release-notes.md) | Baseline behavior and checks before publishing an image |

This is a single-user app. Jobs and exports are temporary. Check technical wording and timing in the finished dub before using it.
