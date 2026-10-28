<div align="center">

# DAT Stream Studio

<img src="https://readme-typing-svg.demolab.com?font=Inter&weight=700&size=28&duration=2800&pause=700&color=14B8A6&center=true&vCenter=true&width=900&lines=PyQt+DAT+Workspace;Stream+Shortcuts+%2B+Proxy+Profiles;Tabbed+Embedded+Browser;MV3+companion+extension" alt="Typing SVG" />

<p>
  <img src="https://komarev.com/ghpvc/?username=mafzalkalwardev&label=Project%20Views&color=14b8a6&style=for-the-badge" alt="Project views" />
  <img src="https://img.shields.io/github/stars/mafzalkalwardev/dat-stream-studio?style=for-the-badge&color=22c55e" alt="GitHub stars" />
  <img src="https://img.shields.io/github/forks/mafzalkalwardev/dat-stream-studio?style=for-the-badge&color=f59e0b" alt="GitHub forks" />
  <img src="https://img.shields.io/github/license/mafzalkalwardev/dat-stream-studio?style=for-the-badge&color=64748b" alt="License" />
</p>

<p>
  <img src="https://skillicons.dev/icons?i=python,qt,js,chrome" alt="Skill icons" />
</p>

<p>
  <strong>Clean PyQt DAT workspace with stream shortcuts, proxy profiles, tabbed embedded browser, and a Manifest V3 companion extension.</strong>
</p>

</div>

---

## Trophy Cards

<div align="center">
  <img src="https://github-profile-trophy.vercel.app/?username=mafzalkalwardev&theme=algolia&no-frame=true&no-bg=true&margin-w=12&margin-h=12&column=4" alt="GitHub trophy cards" />
</div>

---

## Stats Cards

<div align="center">
  <img height="165" src="https://github-readme-stats-sigma-five.vercel.app/api?username=mafzalkalwardev&show_icons=true&theme=tokyonight&hide_border=true&rank_icon=github" alt="GitHub stats" />
  <img height="165" src="https://github-readme-stats-sigma-five.vercel.app/api/top-langs/?username=mafzalkalwardev&layout=compact&theme=tokyonight&hide_border=true" alt="Top languages" />
</div>

---

## Activity Graph

<div align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=mafzalkalwardev&theme=react-dark&hide_border=true&area=true" alt="GitHub activity graph" />
</div>

---

## Contribution Snake

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mafzalkalwardev/google-voice-dispatch-agent/output/github-contribution-grid-snake-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/mafzalkalwardev/google-voice-dispatch-agent/output/github-contribution-grid-snake.svg">
    <img alt="Contribution snake" src="https://raw.githubusercontent.com/mafzalkalwardev/google-voice-dispatch-agent/output/github-contribution-grid-snake.svg">
  </picture>
</div>

---

## SEO Keywords

`DAT board` `PyQt` `proxy profiles` `Chrome extension`

---

## Screenshots

![Application screenshot](docs/screenshots/app.png)


## 🐍 Contribution graph

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mafzalkalwardev/dat-stream-studio/output/snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/mafzalkalwardev/dat-stream-studio/output/snake.svg" />
  <img alt="Contribution snake" src="https://raw.githubusercontent.com/mafzalkalwardev/dat-stream-studio/output/snake.svg" />
</picture>

---

A clean DAT workspace inspired by a reverse-engineering assignment.

This repository contains two pieces:

- `dat_stream_studio/`: PyQt6 desktop app with stream shortcuts, authorized proxy profiles, a tabbed embedded browser, persistent local browser profile, plus a no-install Tkinter fallback.
- `dat_companion_extension/`: Manifest V3 Chrome companion extension for DAT shortcuts and local DAT cookie count/clear tools.

The project intentionally avoids shared cookies, embedded DAT/Auth0 sessions, GitHub token cookie sync, automatic cookie merge/push, and UI suppression. Use only DAT accounts, sessions, and proxies you are authorized to use.

## Desktop App

No-install fallback:

```powershell
cd dat_stream_studio
py -3 lite_app.py
```

Full embedded-browser mode:

```powershell
cd dat_stream_studio
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

`app.py` prefers PySide6, then PyQt6, then PyQt5. The pinned assignment path uses PyQt6/PyQt6-WebEngine from `dat_stream_studio/requirements.txt`.

Build an EXE:

```powershell
cd dat_stream_studio
.\build_lite.ps1
```

## Companion Extension

1. Open `chrome://extensions`.
2. Enable Developer mode.
3. Click **Load unpacked**.
4. Select `dat_companion_extension`.

## Stream Configuration

Edit `dat_stream_studio/sample_streams.json`, or create `dat_stream_studio/streams.local.json` for local-only stream/proxy settings.
