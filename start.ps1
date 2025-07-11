# Create logs directory if it doesn't exist
if (-Not (Test-Path -Path "logs")) {
    New-Item -ItemType Directory -Path "logs" > $null
}

# Create virtual environment if it doesn't exist
if (-Not (Test-Path -Path "venv")) {
    Write-Host "`nCreating virtual environment..." -NoNewline
    python -m venv venv
    Write-Host " Done.`n"
}

# Load environment variables from .env file
$envFile = ".env"

if (Test-Path -Path $envFile) {
    Write-Host "`nLoading environment variables from $envFile..." -NoNewline
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]*)\s*=\s*(.*)\s*$") {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
    Write-Host " Done.`n"
}
else {
    Write-Host "`n$envFile file not found. Please create it manually.`n"
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -NoNewline
& .\venv\Scripts\Activate
Write-Host " Done.`n"

# Install dependencies
Write-Host "`nCheck dependencies..." -NoNewline
Invoke-Expression "pip install -r requirements.txt" > logs/requirements.log 2>&1
Write-Host " Done.`n"

# Run the application in the background
Write-Host "`nStarting Flask server..." -NoNewline
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "run.py" -RedirectStandardOutput "logs/flask_output.log" -RedirectStandardError "logs/flask_error.log"
Write-Host " Done.`n"

# Wait for the server to start
Start-Sleep -Seconds 10

# Open the default web browser with the specified URL
Write-Host "`nOpening web browser..." -NoNewline
Start-Process "http://127.0.0.1:5000"
Write-Host " Done.`n"