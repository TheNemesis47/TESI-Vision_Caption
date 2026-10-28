# Spegne VisionCaption: ferma e rimuove i contenitori.
# Modelli, log e campioni restano: stanno nei volumi e nelle cartelle
# logs\ e artifacts\.
#
#   .\scripts\windows\spegni.ps1
#
# Per riavviare: .\scripts\windows\spegni.ps1; .\scripts\windows\avvia.ps1

# Continue: in Windows PowerShell 5.1 con "Stop" ogni riga che docker scrive
# su stderr diventerebbe un errore fatale. Gli esiti si controllano con
# $LASTEXITCODE.
$ErrorActionPreference = "Continue"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")

$Profili = @("--profile", "local-vlm", "--profile", "local-tts-fish", "--profile", "tunnel")

Write-Host "==> Spengo i servizi" -ForegroundColor Cyan
docker compose @Profili down
if ($LASTEXITCODE -ne 0) { throw "docker compose down non riuscito." }
Write-Host "VisionCaption spento." -ForegroundColor Green
