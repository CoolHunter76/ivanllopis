#Requires -Version 5.1
[CmdletBinding()]
param(
    [string]$MainPath = (Join-Path $PSScriptRoot "..\main.py")
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

$resolvedMainPath = [System.IO.Path]::GetFullPath($MainPath)

if (-not (Test-Path -LiteralPath $resolvedMainPath -PathType Leaf)) {
    throw "No se ha encontrado main.py en: $resolvedMainPath"
}

$assistantPath = Join-Path (Split-Path -Parent $resolvedMainPath) "assistant.py"
if (-not (Test-Path -LiteralPath $assistantPath -PathType Leaf)) {
    throw "No se ha encontrado assistant.py en: $assistantPath"
}

Write-Info "Integrando el asistente en $resolvedMainPath"

$content = [System.IO.File]::ReadAllText($resolvedMainPath)
$content = $content.Replace("`r`n", "`n").Replace("`r", "`n")

$importLine = "from assistant import configure_assistant"
$configureLine = "configure_assistant(app)"

$importPattern = '(?m)^from assistant import configure_assistant\s*$'
$configurePattern = '(?m)^configure_assistant\(app\)\s*$'

if ($content -notmatch $importPattern) {
    $lines = $content -split "`n"
    $insertAt = 0

    if ($lines.Count -gt 0 -and $lines[0] -match '^#!') {
        $insertAt = 1
    }

    while ($insertAt -lt $lines.Count -and $lines[$insertAt] -match '^#.*coding[:=]') {
        $insertAt++
    }

    $before = @()
    $after = @()

    if ($insertAt -gt 0) {
        $before = $lines[0..($insertAt - 1)]
    }

    if ($insertAt -lt $lines.Count) {
        $after = $lines[$insertAt..($lines.Count - 1)]
    }

    $lines = @($before) + @($importLine) + @($after)
    $content = $lines -join "`n"
    Write-Info "Import de configure_assistant añadido."
}
else {
    Write-Info "El import ya existe. No se ha duplicado."
}

if ($content -notmatch $configurePattern) {
    $appPattern = '(?m)^(?<indent>[ \t]*)app\s*=\s*FastAPI\([^\r\n]*\)\s*$'
    $appMatch = [regex]::Match($content, $appPattern)

    if (-not $appMatch.Success) {
        throw "No se ha encontrado una línea compatible con app = FastAPI(...) en main.py."
    }

    $insertionPoint = $appMatch.Index + $appMatch.Length
    $content = $content.Insert($insertionPoint, "`n$configureLine")
    Write-Info "Llamada configure_assistant(app) añadida después de crear la aplicación."
}
else {
    Write-Info "La llamada configure_assistant(app) ya existe. No se ha duplicado."
}

$importCount = ([regex]::Matches($content, $importPattern)).Count
$configureCount = ([regex]::Matches($content, $configurePattern)).Count

if ($importCount -ne 1) {
    throw "Se esperaba exactamente un import del asistente, pero se encontraron $importCount."
}

if ($configureCount -ne 1) {
    throw "Se esperaba exactamente una llamada configure_assistant(app), pero se encontraron $configureCount."
}

$backupPath = "$resolvedMainPath.before-assistant.bak"
if (-not (Test-Path -LiteralPath $backupPath)) {
    Copy-Item -LiteralPath $resolvedMainPath -Destination $backupPath
    Write-Info "Copia de seguridad creada: $backupPath"
}
else {
    Write-Info "La copia de seguridad ya existe y se conserva sin sobrescribir."
}

$utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($resolvedMainPath, $content, $utf8WithoutBom)

Write-Success "Asistente integrado correctamente en main.py."
Write-Host ""
Write-Host "Validación recomendada:" -ForegroundColor Yellow
Write-Host "  python -m compileall -q main.py assistant.py"
Write-Host "  ruff check ."
Write-Host "  ruff format --check ."
Write-Host "  pytest"
