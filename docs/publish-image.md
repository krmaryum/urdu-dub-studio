# Publish a Docker release

This guide is for the repository maintainer. A release pairs one versioned app image with a ready-to-run Compose file.

## 1. Check the commit

Push the changes to `main`. Open **Actions → Container checks**. Wait for both the x86-64 and ARM64 jobs to pass for the commit you plan to release. Test a short dub and an original download locally if either feature changed.

## 2. Create the release tag

From your clean local repository, confirm the commit before tagging it. The example uses `v0.1.0`; choose a new version if that tag is already in use.

```bash
git status --short
git log -1 --oneline
git tag v0.1.0
git push origin v0.1.0
```

In **Actions**, open **Publish Docker image**. It builds both architectures, pushes `ghcr.io/krmaryum/urdu-dub-studio:v0.1.0`, and attaches `compose.yaml` to the release. The release file uses the tagged image and keeps the same Ollama service and model volumes as the source setup.

## 3. Allow public downloads

GitHub Container Registry starts new packages as private. On GitHub, open the `urdu-dub-studio` container package, select **Package settings**, and change its visibility to **Public**. Only make this change if you intend to distribute the image publicly.

[GitHub Container Registry documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## 4. Check the release as a new user

Open the repository's **Releases** page and download `compose.yaml` from **Assets** into a clean test folder. From an account or Docker environment without registry credentials, run `docker compose pull`, then follow the README to start the app and test a short video. Test on both architectures before sharing the release link widely.
