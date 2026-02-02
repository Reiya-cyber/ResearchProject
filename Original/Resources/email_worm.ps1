if (-not (Get-Module -ListAvailable -Name SQLite)) {
    Install-Module -Name SQLite -Scope CurrentUser -Force 
}
Import-Module SQLite

$profilesPath = "$env:APPDATA\Thunderbird\Profiles"
$profile = Get-ChildItem $profilesPath -Directory | Select-Object -First 1

if (-not $profile) { Write-Error "No Thunderbird profile found"; exit }

$prefsFile = "$($profile.FullName)\prefs.js"
$prefs = Get-Content $prefsFile

# Extract user email
$userEmailLine = $prefs | Select-String "useremail"
$userEmail = ($userEmailLine -replace '.*useremail","(.*)".*','$1').Trim()
Write-Host "User Email: $userEmail"

# Extract SMTP server
$smtpLine = $prefs | Select-String "mail.smtpserver.smtp"
$smtpServerLine = $smtpLine | Select-String "hostname"
$smtpServer = ($smtpServerLine -replace '.*hostname","(.*)".*','$1').Trim()
Write-Host "SMTP Server: $smtpServer"

# Extract contacts from abook.sqlite
$abookFile = "$($profile.FullName)\abook.sqlite"

if (-not (Test-Path $abookFile)) { Write-Error "Address book not found"; exit }

$conn = Connect-SQLite -DataSource $abookFile

$contacts = Invoke-SQLiteQuery -Connection $conn -Query "
    SELECT DisplayName, PrimaryEmail 
    FROM moz_abcontacts
" | Where-Object { $_.PrimaryEmail -ne $null }

Write-Host ("Found {0} contacts" -f $contacts.Count)

$credential = Get-Credential -Message "Enter SMTP username and password for $userEmail"

$subject = "Automated Email from Thunderbird CLI"
$body = "Hello! This is an automated email sent via PowerShell."

# Send to all contacts via BCC
$allEmails = ($contacts | Select-Object -ExpandProperty PrimaryEmail) -join ";"

Write-Host "Sending email to all contacts..."
Send-MailMessage -From $userEmail -To $userEmail -Bcc $allEmails  -Subject $subject -Body $body -SmtpServer $smtpServer -Port 143 -Credential $credential

Write-Host "Email sent successfully!"