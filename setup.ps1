# One-time setup — run this once after cloning the repo.
# Requires Python 3.10+ installed: https://www.python.org/downloads/

Set-Location $PSScriptRoot

Write-Host "Creating virtual environment..."
python -m venv .venv

Write-Host "Installing Python dependencies..."
& ".\.venv\Scripts\pip.exe" install --upgrade pip -q
& ".\.venv\Scripts\pip.exe" install -r requirements.txt

Write-Host "Installing Playwright browser..."
& ".\.venv\Scripts\playwright.exe" install chromium

Write-Host ""
Write-Host "Setup complete!"
Write-Host "Next steps:"
Write-Host "  1. Copy your Google service account JSON file to this folder as: credentials.json"
Write-Host "  2. Edit run.ps1 if you need to change any credentials"
Write-Host "  3. Run .\run.ps1 once to test it"
Write-Host "  4. Set up Task Scheduler (see README or ask Claude for the schtasks command)"