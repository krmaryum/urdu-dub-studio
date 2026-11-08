# Troubleshooting

| Symptom | Check |
| --- | --- |
| The page won't open | Confirm the app is running and open `http://localhost:8765`. If the port is already in use, stop the other Urdu Dub Studio instance before starting this one. |
| The translator is unavailable | Run `ollama list` locally. With Docker, run `docker compose logs model-setup` and `docker compose exec ollama ollama list`. Confirm `qwen3.5:4b` is listed. |
| The video won't import | Confirm the video opens in the browser and is within the configured duration. Check Deno and yt-dlp versions. Locally, update with `python -m pip install --upgrade 'yt-dlp[default]'`. With Docker, rebuild using `docker compose build --no-cache app` and restart the stack. |
| A model download stalls | Check free disk space and internet access. Read the WSL terminal output or `docker compose logs app model-setup`. |
| A line sounds wrong | Choose its timestamp in **Review and edit one line**. Compare the English source with the Roman Urdu. Fix the wording, preview it, then apply the edit. |
| **Apply to video** is disabled | Select **Preview edited line** and wait for a successful audio preview. Any new edit requires a fresh preview. |
| A dub contains a long pause | Compare the same timestamp in the original. If speech is missing, copy the English and Roman Urdu shown for the surrounding lines before restarting the app. |
