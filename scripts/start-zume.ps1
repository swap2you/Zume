[CmdletBinding()]
param(
    [int]$Port = 8787,
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $root
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Zume is not installed. Run .\scripts\install-zume.ps1 first."
}

if (Test-Path "apps\web\package.json") {
    if (-not (Test-Path "apps\web\dist\index.html")) {
        Push-Location "apps\web"
        try {
            npm ci
            if ($LASTEXITCODE -ne 0) { throw "npm ci failed." }
            npm run build
            if ($LASTEXITCODE -ne 0) { throw "Frontend build failed." }
        }
        finally {
            Pop-Location
        }
    }
}

$arguments = @("-m", "zume", "serve", "--port", $Port)
if ($NoOpen) { $arguments += "--no-open" }
& $python @arguments
