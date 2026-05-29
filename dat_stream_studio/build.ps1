$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
  py -3 -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

.\.venv\Scripts\pyinstaller.exe --noconfirm --onefile --windowed `
  --name "DAT Stream Studio" `
  --add-data "sample_streams.json;." `
  app.py

Write-Host "Built dist\\DAT Stream Studio.exe"
