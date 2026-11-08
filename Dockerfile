FROM ghcr.io/denoland/deno:bin-2.9.7 AS deno
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/home/studio/.cache/huggingface

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates ffmpeg libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 studio \
    && install -d -o studio -g studio "$HF_HOME"

COPY --from=deno /deno /usr/local/bin/deno
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt && python -m pip check
COPY app.py dubbing.py local_translation.py index.html ./

USER studio
EXPOSE 8765
CMD ["python", "app.py"]
