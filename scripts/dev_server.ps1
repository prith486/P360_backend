# Development server startup script for Placement360 backend
Write-Host "Starting Placement360 Backend (Development Mode)..." -ForegroundColor Cyan

# Start uvicorn with development settings
uvicorn app.main:app `
    --reload `
    --host 0.0.0.0 `
    --port 8000 `
    --log-level debug `
    --reload-dir app `
    --reload-delay 0.5
