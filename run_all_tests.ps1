$ErrorActionPreference = "Continue"

$root = $PSScriptRoot

$services = @(
    "services\user-service",
    "services\show-services",
    "services\booking-service",
    "services\payment-service",
    "services\notification-service"
)

$failed = @()
$passed = @()

foreach ($service in $services) {
    $path = Join-Path $root $service

    if (-not (Test-Path $path)) {
        Write-Host "[SKIP] Directory not found: $service" -ForegroundColor Yellow
        continue
    }

    Write-Host "`n===== Testing $service =====" -ForegroundColor Cyan

    Push-Location $path
    try {
        python -m pytest -v
        if ($LASTEXITCODE -eq 0) {
            $passed += $service
            Write-Host "[PASS] $service" -ForegroundColor Green
        }
        else {
            $failed += $service
            Write-Host "[FAIL] $service" -ForegroundColor Red
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host "`n===== FINAL TEST SUMMARY ====="
Write-Host "Passed: $($passed.Count)"
Write-Host "Failed: $($failed.Count)"

if ($failed.Count -gt 0) {
    $failed | ForEach-Object { Write-Host $_ }
    exit 1
}

if ($passed.Count -eq 0) {
    Write-Host "No test suites ran successfully." -ForegroundColor Yellow
    exit 1
}

Write-Host "All discovered service test suites passed." -ForegroundColor Green
