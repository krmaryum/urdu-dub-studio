# Docker prerequisites

Choose a setup for your operating system. If Docker is already installed, skip to [Verify Docker](#verify-docker).

| Operating system | Install |
| --- | --- |
| Windows | [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/). Choose the installer for your processor, then launch Docker Desktop. If you run commands inside WSL, enable Docker Desktop integration for that distribution. |
| macOS | [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/). Choose Apple silicon or Intel, then launch Docker Desktop. |
| Linux | [Docker Engine](https://docs.docker.com/engine/install/) with the [Compose plugin](https://docs.docker.com/compose/install/linux/). See the steps below for Rocky Linux 9. [Docker Desktop for Linux](https://docs.docker.com/desktop/setup/install/linux/) is also available and includes Compose. |

The first startup needs an internet connection to download container images and models. The default Compose setup runs Ollama in a container. Git is needed only if you choose to clone the source.

## Rocky Linux 9

On a fresh Rocky Linux 9 system with sudo access, install Docker Engine and the Compose plugin:

```bash
sudo dnf install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

Verify that Docker can start a container and that Compose is available:

```bash
sudo docker run --rm hello-world
sudo docker compose version
```

[Rocky Linux Docker Engine guide](https://docs.rockylinux.org/gemstones/containers/docker/)

## Verify Docker

From PowerShell or a terminal, run:

```text
docker info
docker compose version
```

If the engine is stopped, open Docker Desktop or, for a standard Docker Engine installation on a systemd Linux host, run `sudo systemctl start docker`. If your Linux account needs administrator access to Docker Engine, use `sudo docker` for the Docker commands in the app guides.

Continue with [Step 2 of the quick start](../README.md#2-save-one-setup-file) to download the release's Compose file, or [build from source](container-setup.md).
