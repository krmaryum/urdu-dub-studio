# Release notes

## Repository starter

- The baseline uses version 18's speech timing and three-line repeat check. The version 19 timing experiment did not shorten the measured pause around 1:41–1:44 in the Kubernetes test.
- Original downloads and dubbing both allow videos up to four hours by default. `URDU_DUB_MAX_MINUTES` can set a shorter dubbing limit.
- Long jobs transcribe in overlapping sections and write the dubbed soundtrack incrementally. An interrupted job must be submitted again.
- Before publishing a container image, run the included build checks and complete an actual dub on x86-64 and ARM64. Verify a clip that crosses a ten-minute transcription boundary, then test a single-line edit and download both exports.
- Long pauses and translation accuracy still need review in the completed export.

## Push the starter to GitHub

Create an empty GitHub repository called `urdu-dub-studio`. In the extracted project folder, initialize Git and replace `YOUR_GITHUB_USERNAME` with the owner of the repository.

```bash
git init -b main
git add .
git commit -m "Add Urdu Dub Studio with local and Docker setup"
git remote add origin git@github.com:YOUR_GITHUB_USERNAME/urdu-dub-studio.git
git push -u origin main
```

These commands use an SSH key configured for GitHub. Check the **Actions** tab for the x86-64 and ARM64 container checks after pushing.
