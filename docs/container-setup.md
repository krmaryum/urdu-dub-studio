# Build and run from source

This path is useful when you want to change the code or try a revision without a published image. For the prebuilt image, follow the [beginner guide](../README.md).

## 1. Install the container runtime

On Windows, install [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/), start it, and enable WSL integration for the Ubuntu distribution where you will run the commands. On Ubuntu, install [Docker Engine and the Compose plugin](https://docs.docker.com/engine/install/ubuntu/). Follow Docker's setup instructions for access to the engine.

If you already extracted the project, open the folder containing `compose.yaml`. To get the source with Git, install Git, open PowerShell or Terminal, and run:

```text
git clone https://github.com/krmaryum/urdu-dub-studio.git
cd urdu-dub-studio
```

Confirm the engine and Compose are available:

```bash
docker info
docker compose version
docker compose config --quiet
```

## 2. Start the services

```bash
docker compose up --build -d
docker compose ps -a
```

The stack is CPU-only. The app image contains Python, FFmpeg, and Deno. A setup service waits for Ollama, pulls `qwen3.5:4b`, then exits. The browser app starts once that setup succeeds. On the first run, the model download can take several minutes.

```bash
docker compose logs model-setup
docker compose exec ollama ollama list
```

A setup service marked **Exited (0)** is expected. When the app is healthy, open [http://localhost:8765](http://localhost:8765). Only the app's localhost port is published.

[Compose startup ordering](https://docs.docker.com/compose/how-tos/startup-order/) · [Ollama container setup](https://docs.ollama.com/docker)

## 3. Verify the first dub

Start with a short English video that you have permission to dub. Confirm that the app can play the resulting MP4 and download the transcript. The first job downloads Whisper and the Fasih voice. Named volumes retain the downloaded models across normal restarts. The app keeps the current job in temporary storage, so download the outputs before stopping it.

## 4. Set a shorter dubbing limit

Dubbing and original downloads allow up to four hours by default. To limit dubbing to 15 minutes, add this to a file named `.env` alongside `compose.yaml`:

```dotenv
URDU_DUB_MAX_MINUTES=15
```

Run `docker compose up -d` again after saving any current exports. Refresh the browser and check the displayed limit. To restore the four-hour default, remove the setting from `.env`.

Start with a shorter dub before testing the upper limit. The app transcribes in overlapping ten-minute sections and writes the dubbed audio to disk as it goes. Allow enough temporary storage for the source video, WAV audio, and MP4 export. A multi-hour dub can run for many hours on CPU. Keep Docker running until you save the exports. An interrupted job starts from the beginning when submitted again.

## 5. Stop or update

```bash
docker compose down
```

To update after replacing the source with a newer revision, run `docker compose up --build -d`. Keep the same project name and location to reuse the existing volumes. A normal shutdown preserves the model downloads. The `--volumes` option removes them.

## Build verification on GitHub

The included workflow builds the app image on x86-64 and ARM64 Linux runners, checks the bundled commands, and starts the web app for a health check. The workflow skips model downloads and live YouTube imports. Complete a full dub on each architecture before tagging a release or publishing a prebuilt image.
