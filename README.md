# Urdu Dub Studio

Turn an English YouTube video into a conversational Pakistani Urdu dub and a timestamped Roman Urdu transcript. You can also save the original video with its audio. The app runs on your computer and uses the internet to fetch videos and models.

[Roman Urdu guide](README-roman-urdu.md)

[Workshop flow in English and Roman Urdu](docs/workshop/Urdu-Dub-Studio-Workshop-Flow.md)

## 1. Get Docker ready

- **Windows or macOS:** Install Docker Desktop, open it, and wait for the engine to start. On Windows, select the installer that matches your PC's processor.
- **Ubuntu:** Install Docker Engine and the Compose plugin. Open Terminal and confirm your account can access Docker.

Open PowerShell on Windows or Terminal on macOS or Linux. Run these commands one at a time:

```text
docker info
docker compose version
```

If Docker reports it cannot connect, make sure Docker Desktop or the Docker service is running before continuing.

[Docker Desktop installation](https://docs.docker.com/desktop/) · [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

## 2. Save one setup file

1. Open [Urdu Dub Studio Releases](https://github.com/krmaryum/urdu-dub-studio/releases).
2. Open **Assets** on the latest release and download **compose.yaml**.
3. In your Downloads folder, create a folder named **urdu-dub-studio** and move `compose.yaml` into it. Keep the filename exactly as shown.
4. In PowerShell or Terminal, enter the folder and check the file:

```text
cd ~/Downloads/urdu-dub-studio
docker compose config --quiet
```

If your browser saves downloads somewhere else, use that folder's path. The Compose file tells Docker which services and images to run. A successful configuration check prints nothing.

If the release asset is unavailable, use the [source build instructions](docs/container-setup.md). The release image supports **x86-64 and ARM64**.

## 3. Start the app

Run this from the folder containing `compose.yaml`:

```text
docker compose up -d
docker compose ps -a
```

Docker pulls the prebuilt app image and starts Ollama. The first startup can take several minutes while the translation model downloads. When **app** shows **healthy**, open [http://localhost:8765](http://localhost:8765). A **model-setup** row showing **Exited (0)** means the setup step finished successfully.

## 4. Make your first dub

1. Paste a short English YouTube link you have permission to download and dub.
2. Tick the permission checkbox and choose **Start dubbing**. The first dub downloads the transcription and voice models.
3. When the dub is ready, play it and select **Download MP4** and **Download Roman Urdu transcript**. Save both before starting another job or stopping the app.
4. To correct a line, open **Review and edit one line**, choose its timestamp, and change the Roman Urdu. Click **Preview edited line** first, then **Apply to video**. Download the updated MP4 and transcript.

## 5. Save the original video

Paste a link you have permission to download, tick the checkbox, and select **Download original video**. After the preview is ready, click **Download original MP4**. This mode keeps the original audio, downloads up to 480p, and accepts videos up to four hours.

## 6. Set a shorter dubbing limit

Dubbing allows up to **four hours (240 minutes)** by default. If you prefer a shorter limit, create a file named `.env` beside `compose.yaml` and put this line in it:

```dotenv
URDU_DUB_MAX_MINUTES=15
```

Use a whole number from **1 to 240**. On Windows, check that the file is named `.env` exactly. Save any current exports, run `docker compose up -d` again, and refresh the page to check the displayed limit. Longer dubs can take considerable time on CPU. If a job is interrupted, it starts from the beginning when submitted again.

## 7. Close and reopen the app

Closing the browser tab leaves the containers running. To stop the app after saving your exports, return to the same folder in PowerShell or Terminal and run:

```text
docker compose stop
```

Next time, start Docker Desktop if needed, return to the same folder, and run:

```text
docker compose up -d
```

Open [http://localhost:8765](http://localhost:8765) again. Docker keeps the downloaded models. To update, save your exports, replace `compose.yaml` with the file from the newer release in the **same folder**, then run `docker compose pull` followed by `docker compose up -d`.

## More guides

| Guide | Use it to |
| --- | --- |
| [Local setup](docs/local-setup.md) | Run directly in Ubuntu or WSL with Python |
| [Build guide](docs/build-guide.md) | Follow the code from video import to the finished dub |
| [Container setup](docs/container-setup.md) | Build the Docker image from source |
| [Troubleshooting](docs/troubleshooting.md) | Fix startup, import, audio, or editor issues |
| [Release notes](docs/release-notes.md) | Review the changes and test status |
| [Publish a Docker release](docs/publish-image.md) | Build and distribute an image as the repository maintainer |

This is a single-user app. Review technical wording and timing in the finished dub before using it.
