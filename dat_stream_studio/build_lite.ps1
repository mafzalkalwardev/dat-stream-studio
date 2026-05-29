$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
  py -3 -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install pyinstaller==6.11.1

.\.venv\Scripts\pyinstaller.exe --noconfirm --onefile --windowed `
  --name "DAT Stream Studio Lite" `
  --add-data "sample_streams.json;." `
  lite_app.py

Write-Host "Built dist\\DAT Stream Studio Lite.exe"
