# Avvia VisionCaption sulla workstation: server, Ollama, Fish, client e tunnel.
#
#   .\scripts\windows\avvia.ps1             avvia tutto
#   .\scripts\windows\avvia.ps1 -Aggiorna   prima scarica codice e immagini nuove
#                                           e cancella le immagini vecchie
#
# Se Windows blocca lo script:
#   powershell -ExecutionPolicy Bypass -File .\scripts\windows\avvia.ps1

param([switch]$Aggiorna)

# Continue: in Windows PowerShell 5.1 con "Stop" ogni riga che docker scrive
# su stderr diventerebbe un errore fatale. Gli esiti si controllano con
# $LASTEXITCODE.
$ErrorActionPreference = "Continue"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")

function ValoreEnv($Nome) {
    $Riga = Select-String -Path .env -Pattern "^$Nome=(.*)$" | Select-Object -Last 1
    if ($Riga) { return $Riga.Matches.Groups[1].Value.Trim() }
    return ""
}

# Fish si accende solo se e' la voce scelta: altrimenti occupa memoria della
# GPU per niente.
$UsaFish = (ValoreEnv "TTS_PROVIDER") -eq "fish"
$Profili = @("--profile", "local-vlm", "--profile", "tunnel")
$Servizi = @("server", "ollama", "client", "tunnel")
if ($UsaFish) {
    $Profili += @("--profile", "local-tts-fish")
    $Servizi += "fish"
}

function Scrivi($Testo) { Write-Host "==> $Testo" -ForegroundColor Cyan }

function Attendi($Descrizione, $Secondi, [scriptblock]$Pronto) {
    $Scadenza = (Get-Date).AddSeconds($Secondi)
    while ((Get-Date) -lt $Scadenza) {
        if (& $Pronto) { return $true }
        Start-Sleep -Seconds 3
    }
    Write-Host "$Descrizione non pronto dopo $Secondi secondi." -ForegroundColor Yellow
    return $false
}

# 1. Docker Desktop
Scrivi "Controllo Docker"
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    $Desktop = @(
        "D:\Docker\Desktop\Docker Desktop.exe",
        "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $Desktop) { throw "Docker Desktop non trovato: avvialo a mano e riprova." }
    Scrivi "Avvio Docker Desktop"
    Start-Process $Desktop
    $ok = Attendi "Docker" 180 { docker info *> $null; $LASTEXITCODE -eq 0 }
    if (-not $ok) { throw "Docker non risponde." }
}

# 2. Aggiornamento facoltativo
if ($Aggiorna) {
    Scrivi "Aggiorno il codice"
    git pull
    Scrivi "Scarico le immagini nuove"
    docker compose @Profili pull server client ollama tunnel
}

# 3. Avvio
Scrivi "Avvio i servizi"
docker compose @Profili up -d @Servizi
if ($LASTEXITCODE -ne 0) { throw "docker compose up non riuscito." }

if ($Aggiorna) {
    Scrivi "Cancello le immagini vecchie"
    docker image prune -f
}

# 4. Server pronto: il server risponde solo dopo aver caricato in GPU anche
# il modello visivo, che da un disco lento richiede qualche minuto.
Scrivi "Attendo il server: carica RF-DETR e il modello visivo, anche qualche minuto"
$ok = Attendi "Server" 600 {
    try { (Invoke-WebRequest http://localhost:8765/health -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200 }
    catch { $false }
}
# Con la compilazione attiva Fish impiega qualche minuto al primo avvio.
if ($UsaFish) { $ok = $ok -and (Attendi "Fish" 600 {
    try { (Invoke-WebRequest http://localhost:8081/v1/health -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200 }
    catch { $false }
}) }

docker compose @Profili ps
if ($ok) {
    Write-Host ""
    Write-Host "VisionCaption pronto." -ForegroundColor Green
    Write-Host "Log del server: docker compose logs -f server"
} else {
    Write-Host "Qualcosa non e' partito: guarda docker compose logs server fish" -ForegroundColor Yellow
}
