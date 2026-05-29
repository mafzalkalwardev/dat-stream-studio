# Reverse-Engineering Summary

## EXE Findings

`Awwthat Pro v2.3.exe` is a PyInstaller one-file Python app using Python 3.12, PyQt5, QtWebEngine, requests, psutil, pytz, and Crypto.

Observed architecture:

- PyQt login screen
- version/update check against a remote server
- stream selector
- QtWebEngine tabbed browser
- DAT URLs such as `https://one.dat.com` and `https://power.dat.com`
- optional proxy configuration
- JavaScript injection into loaded pages
- embedded encrypted config that included DAT/login.dat.com session material

The clean rebuild keeps the desktop browser shell and stream workflow, but does not include embedded sessions, UI suppression, or blind remote self-update execution.

## Extension Findings

The DAT extension zip contained a Manifest V2 extension named `DatEx`.

Observed behavior:

- cookie synchronization via `chrome.cookies`
- GitHub Gist remote storage through `https://api.github.com`
- encrypted cookie payloads using a user-provided password
- local storage keys such as `__TOKEN__`, `__PASSWORD__`, `__GIST_ID__`, `__FILE_NAME__`, and `__DOMAIN_LIST__`
- auto-merge on new browser windows
- auto-push on cookie changes
- an obfuscated loader that fetched a remote Pastebin URL

The clean companion extension keeps only local shortcuts and explicit local DAT cookie count/clear actions. It does not sync cookies, store GitHub tokens, or load remote code.
