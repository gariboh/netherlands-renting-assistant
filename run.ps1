# NL Rental Bot — local runner for Windows Task Scheduler
# Fill in the four values below, then save. Do NOT commit this file after editing.

$EMAIL_SENDER    = "harijs.rozensteins@scandiweb.com"
$EMAIL_PASSWORD  = "ojtv tshg nesv nfkj"
$EMAIL_RECIPIENT = "harijs.rozensteins@scandiweb.com"
$GOOGLE_SHEET_ID = "1TMaNxddTOwA92hVOPiQjWECxibnz1xLDoI6_QJCOyOg"

# Path to your Google service account JSON (download from Google Cloud Console)
$CREDS_FILE = "$PSScriptRoot\credentials.json"

# ---- do not edit below this line ----
$env:EMAIL_SENDER              = $EMAIL_SENDER
$env:EMAIL_PASSWORD            = $EMAIL_PASSWORD
$env:EMAIL_RECIPIENT           = $EMAIL_RECIPIENT
$env:GOOGLE_SHEET_ID           = $GOOGLE_SHEET_ID
$env:GOOGLE_SHEETS_CREDENTIALS = Get-Content $CREDS_FILE -Raw -Encoding UTF8

$logFile = "$PSScriptRoot\run.log"
$stamp   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content $logFile "`n=== $stamp ==="

& "$PSScriptRoot\.venv\Scripts\python.exe" -u "$PSScriptRoot\main.py" 2>&1 |
    Tee-Object -Append -FilePath $logFile