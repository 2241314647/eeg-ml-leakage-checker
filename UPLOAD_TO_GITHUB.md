# Upload to GitHub

Automated upload has now been completed once for this project.

Repository:

```text
https://github.com/2241314647/eeg-ml-leakage-checker
```

The reusable workflow is:

Run these commands from inside your local `eeg-ml-leakage-checker` folder after logging in with GitHub CLI:

```powershell
$env:HTTP_PROXY="http://127.0.0.1:7897"
$env:HTTPS_PROXY="http://127.0.0.1:7897"
$env:ALL_PROXY="http://127.0.0.1:7897"
$env:http_proxy="http://127.0.0.1:7897"
$env:https_proxy="http://127.0.0.1:7897"
$env:all_proxy="http://127.0.0.1:7897"

gh auth login
gh repo create 2241314647/eeg-ml-leakage-checker --public --description "Local EEG/BCI ML data leakage checker"
git remote add origin https://github.com/2241314647/eeg-ml-leakage-checker.git
git push -u origin main
```

If the repository already exists:

```powershell
git remote add origin https://github.com/2241314647/eeg-ml-leakage-checker.git
git push -u origin main
```
