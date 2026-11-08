# Local setup on Ubuntu or WSL

The commands target Ubuntu 24.04 and Python 3.12. On Windows, install Ubuntu under WSL if needed. Run `wsl --install -d Ubuntu-24.04` from an elevated PowerShell, restart if prompted, then launch Ubuntu and finish its user setup. Run the remaining commands in the Ubuntu terminal.

[Microsoft WSL installation guide](https://learn.microsoft.com/windows/wsl/install)

## 1. Open the source folder

Extract the project archive, then open the directory containing `app.py`. If you extracted it to Windows Downloads, replace the username in the example.

```bash
cd /mnt/c/Users/YOUR_WINDOWS_USERNAME/Downloads/urdu-dub-studio
ls app.py requirements.txt
```

On a native Ubuntu installation, use the path where you extracted or cloned the project.

## 2. Install system packages

FFmpeg reads and renders video. FFprobe reports duration and stream information. The virtual environment keeps the Python packages separate from Ubuntu's system Python.

```bash
sudo apt update
sudo apt install -y python3 python3-venv ffmpeg libgomp1 curl unzip zstd ca-certificates
python3 --version
ffmpeg -version | head -n 1
ffprobe -version | head -n 1
```

## 3. Install Python dependencies

```bash
mkdir -p "$HOME/.venvs"
python3 -m venv "$HOME/.venvs/urdu-dub"
source "$HOME/.venvs/urdu-dub/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
python -m yt_dlp --version
```

## 4. Install Deno

Deno provides the JavaScript runtime used by yt-dlp for YouTube imports.

```bash
curl -fsSL https://deno.land/install.sh -o /tmp/urdu-dub-deno-install.sh
sh /tmp/urdu-dub-deno-install.sh
export PATH="$HOME/.deno/bin:$PATH"
deno --version
```

[Deno installation guide](https://docs.deno.com/runtime/getting_started/installation/) · [yt-dlp JavaScript setup](https://github.com/yt-dlp/yt-dlp/wiki/EJS)

## 5. Install the local translator

```bash
curl -fsSL https://ollama.com/install.sh -o /tmp/urdu-dub-ollama-install.sh
sh /tmp/urdu-dub-ollama-install.sh
ollama --version
ollama pull qwen3.5:4b
ollama list
```

If `ollama list` cannot connect, run `ollama serve` in a separate terminal, leave it open, and repeat the pull and list commands. The app connects to `127.0.0.1:11434` by default.

[Ollama on Linux](https://docs.ollama.com/linux) · [Qwen 3.5 4B model](https://ollama.com/library/qwen3.5:4b)

## 6. Start and verify the app

From the project folder:

```bash
source "$HOME/.venvs/urdu-dub/bin/activate"
export PATH="$HOME/.deno/bin:$PATH"
python app.py
```

Open [http://localhost:8765](http://localhost:8765). Submit a short English clip you have permission to dub. Verify that the finished MP4 plays, the transcript downloads, and a previewed edit can be applied. The first run downloads Whisper and the Fasih voice. After downloading your exports, stop the app with `Ctrl+C`. Run `deactivate` to leave the virtual environment.

## Set a shorter dubbing limit

Dubbing allows up to four hours by default. To limit dubbing to 15 minutes for this run, use:

```bash
URDU_DUB_MAX_MINUTES=15 python app.py
```

Use a whole number from 1 to 240 and check the limit displayed on the home page after restarting. A long dub uses temporary disk storage for the source, WAV, and MP4. Keep the app running until you save the exports. An interrupted job starts from the beginning when submitted again.
