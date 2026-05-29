# DAT Stream Studio

A clean DAT workspace inspired by a reverse-engineering assignment.

This repository contains two pieces:

- `dat_stream_studio/`: PyQt5 desktop app with stream shortcuts, authorized proxy profiles, a tabbed embedded browser, persistent local browser profile, and PyInstaller packaging.
- `dat_companion_extension/`: Manifest V3 Chrome companion extension for DAT shortcuts and local DAT cookie count/clear tools.

The project intentionally avoids shared cookies, embedded DAT/Auth0 sessions, GitHub token cookie sync, automatic cookie merge/push, and UI suppression. Use only DAT accounts, sessions, and proxies you are authorized to use.

## Desktop App

```powershell
cd dat_stream_studio
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Build an EXE:

```powershell
cd dat_stream_studio
.\build.ps1
```

## Companion Extension

1. Open `chrome://extensions`.
2. Enable Developer mode.
3. Click **Load unpacked**.
4. Select `dat_companion_extension`.

## Stream Configuration

Edit `dat_stream_studio/sample_streams.json`, or create `dat_stream_studio/streams.local.json` for local-only stream/proxy settings.
