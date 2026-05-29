# DAT Stream Studio

Clean desktop rebuild based on the analyzed app architecture.

This version keeps the useful structure:

- single-window PyQt desktop app
- login/unlock screen
- stream selector
- authorized proxy support per stream
- tabbed embedded browser
- DAT One / DAT Power shortcuts
- speed-test tab
- PyInstaller packaging

It intentionally does not include:

- embedded DAT cookies
- shared Auth0/DAT sessions
- GitHub token based cookie sync
- JavaScript that hides DAT controls
- remote self-update execution
- multi-screen/session bypass logic

## Run

```powershell
cd dat_stream_studio
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## Configure Streams

Edit `sample_streams.json`, or create `streams.local.json` next to `app.py`.

Example stream:

```json
{
  "id": "dat-one-authorized-proxy",
  "label": "DAT One - West",
  "url": "https://one.dat.com",
  "description": "Authorized west-coast connection",
  "proxy": {
    "enabled": true,
    "host": "proxy.example.com",
    "port": 8080,
    "username": "user",
    "password": "password"
  }
}
```

Use only proxies/accounts you are authorized to use.

## Build EXE

```powershell
cd dat_stream_studio
.\build.ps1
```
