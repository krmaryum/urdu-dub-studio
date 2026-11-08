# Run with Docker Compose

## 1. Install the container runtime

On Windows, install [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/), start it, and enable WSL integration for the Ubuntu distribution where you will run the commands. On Ubuntu, install [Docker Engine and the Compose plugin](https://docs.docker.com/engine/install/ubuntu/). Follow Docker's setup instructions for access to the engine.

Open the folder containing `compose.yaml` and confirm the engine and Compose are available:

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

## 4. Enable longer videos

The default limit is five minutes. To allow up to 15 minutes, add this to a file named `.env` alongside `compose.yaml`:

```dotenv
URDU_DUB_MAX_MINUTES=15
```

Run `docker compose up -d` again after saving any current exports. Refresh the browser and check the displayed limit. The accepted settings are whole numbers from 1 to 30. Try a six- to ten-minute clip before using the upper limit. Longer clips use more CPU time, memory, and temporary disk space. Keep the service running while processing.

## 5. Stop or update

```bash
docker compose down
```

To update after replacing the source with a newer revision, run `docker compose up --build -d`. Keep the same project name and location to reuse the existing volumes. A normal shutdown preserves the model downloads. The `--volumes` option removes them.

## Build verification on GitHub

The included workflow builds the app image on x86-64 and ARM64 Linux runners, checks the bundled commands, and starts the web app for a health check. The workflow skips model downloads and live YouTube imports. Complete a full dub on each architecture before tagging a release or publishing a prebuilt image.
