# DAT Stream Studio Delivery

## What To Demonstrate

Run:

```powershell
dist\DAT Stream Studio Lite.exe
```

The app opens a single-screen DAT workspace with:

- profile/unlock screen
- DAT One stream shortcut
- DAT Power stream shortcut
- connection speed shortcut
- stream configuration loaded from JSON
- authorized proxy fields represented in config

The full Qt/WebEngine implementation is in `dat_stream_studio/app.py`. The no-install fallback is `dat_stream_studio/lite_app.py`, which runs on standard Python and was packaged into the EXE.

## Chrome Companion Extension

Load `dat_companion_extension` from `chrome://extensions` with Developer Mode enabled.

It provides:

- DAT One / DAT Power shortcuts
- saved custom shortcuts
- local DAT cookie count
- explicit local DAT cookie clear action

## Safety Boundary

This clean version does not include shared DAT cookies, GitHub token cookie sync, embedded sessions, remote code loading, or DAT UI bypass code.
