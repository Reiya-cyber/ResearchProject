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

try {
    Set-MpPreference -DisableRealtimeMonitoring $true
    Add-MpPreference -ExclusionPath "C:\Users\Reiya\Desktop\ResearchProject\Original\Resources\wget.cmd"
    Add-MpPreference -ExclusionProcess "yourtool.exe"

    Write-Host "Defender Real-Time Protection is now disabled." -ForegroundColor Green
} catch {
    Write-Error "Failed to disable Defender. Is Tamper Protection enabled?"
}
