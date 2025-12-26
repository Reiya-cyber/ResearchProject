# Research Project
By Reiya and Gabriel

## ⚠️ Disclaimer & Educational Use Only

This project is created **strictly for educational and research purposes**.

The goal of this repository is to study:
- malware behavior
- attack techniques
- defensive countermeasures
- security research concepts

**This project is NOT intended for use on systems without explicit permission.**

The authors **do not take any responsibility** for:
- misuse of this code
- damage to operating systems
- data loss
- security breaches
- legal consequences
- or any other harm caused by improper use

By using, cloning, or modifying this project, **you agree that you are solely responsible** for your actions and any consequences that may result.

Use this project **only in controlled environments**, such as:
- virtual machines
- lab setups
- systems you own and are authorized to test

---

## OverView
We are developing a remote access tool (RAT)

## Components
- Keylogger
- Screen shots
- Exfiltration
    - stealing documents
- Remote access
- Credential dump
    - computer
    - web
    - applications
- Privilege escalation
- Worm
- VM detector

## Roadmap
- initial script
    - Download a staging script from github repo
    - execute the staging script
    - self-deletion
- staging script
    - download needed files from github repo
        - Windowns defender disabler (or remover)
        - Keylogger
        - Screenshots
        - Credential dump
        - Remote access 
- develop tools
    - keylogger
    - Screenshots taker
- obfuscation
    - av protection
    - vm desction
    - disabling firewall and windows defender

## Infection Workflow

This section describes the initial infection and persistence mechanism simulated in this research project. The workflow is designed to demonstrate common techniques used in real-world malware for staging, privilege escalation, and defense evasion. **All steps are for educational analysis only and should never be executed outside isolated lab environments.**

## Step-by-Step Execution Flow

### 1. Initial Execution
The attack chain begins with the execution of `initial.cmd` (or equivalent downloader) on the target machine.  
This file is typically delivered via user interaction, phishing simulation, or prior compromise in a lab environment.

### 2. Evasion Preparation
A downloader script (e.g., `wget.cmd`) performs the following:
- Downloads `disableWinDef.ps1`.
- Executes `disableWinDef.ps1` to proactively add Windows Defender exclusions for:
  - `installer.ps1`
  - `defender_remover.exe`
  - The **%TEMP%** directory

This step ensures subsequent payloads are not flagged or quarantined by real-time protection.

### 3. Main Payload Download
The downloader then retrieves and saves the following files directly to the user's **Startup folder** for persistence across user logons:
- `installer.ps1`
- `defender_remover.exe`

### 4. Payload Execution
Both downloaded files are executed (typically triggering a UAC prompt for elevation in lab tests):
- `defender_remover.exe`: Permanently disables or removes Windows Defender components and may reduce UAC restrictions.
- `installer.ps1`: Proceeds with advanced staging.

### 5. Advanced Staging and Persistence
`installer.ps1` performs the following actions:
- Creates a temporary directory with a random name under `%TEMP%`.
- Generates `sender.ps1` inside this directory. This script contains the core logic for communication with the attacker-controlled machine (e.g., beaconing, command execution, data exfiltration).
- Creates a **scheduled task** to execute `sender.ps1` persistently (e.g., at logon or on a recurring schedule).
- Creates a new local administrative account named `Adm1nistartor` (hidden backdoor account).
- Enables **WinRM** (Windows Remote Management) to allow remote PowerShell access.

## Key Techniques Demonstrated
- Early Defender exclusion to bypass real-time scanning
- Persistence via Startup folder and scheduled tasks
- Privilege escalation through UAC interaction
- Backdoor account creation
- Remote access enablement (WinRM)

## Defensive Recommendations
To detect or prevent this chain:
- Enable **Tamper Protection** in Windows Defender
- Restrict PowerShell execution (e.g., via AppLocker or Constrained Language Mode)
- Monitor for suspicious scheduled task creation
- Audit local account creation (especially admin accounts)
- Block or alert on WinRM enablement
- Monitor network traffic for unexpected outbound connections

**Note**: Subsequent stages (e.g., keylogger deployment, screenshot capture, full remote access) would leverage the communication channel established in `sender.ps1`, as outlined in the project roadmap.

## Setups
### Network Configuration (Kali Linux)

This project assumes Kali Linux is configured with a **static IPv4 address** on an **internal network adapter** for isolated lab communication.

#### Network layout
- **Adapter 1**: NAT / Bridged (Internet access, DHCP)
- **Adapter 2**: Internal Network (Lab communication, Static IP)

Kali static IPv4 address: 192.168.0.1/24


#### 1. Identify network interfaces
List available interfaces and NetworkManager connections:
```bash
ip a
nmcli device status
nmcli connection show
```
#### 2. Bind the internal connection to the internal interface
```bash
sudo nmcli connection modify "Wired connection 2" connection.interface-name eth1
```
#### 3. Configure static IPv4 address
```bash
sudo nmcli connection modify "Wired connection 2" \
  ipv4.method manual \
  ipv4.addresses 192.168.0.1/24 \
  ipv4.gateway "" \
  ipv4.dns "" \
  ipv4.never-default yes
```
#### 4. Apply the configuration
```bash
sudo nmcli connection down "Wired connection 2"
sudo nmcli connection up "Wired connection 2"
```

### Network Configuration (Windows 11)

This project assumes the Windows 11 test machine is connected to the **same internal network** as Kali Linux using a **static IPv4 address**.  
This enables isolated lab communication without exposing services to external networks.

#### Network layout
- **Adapter 1**: NAT / Bridged (Internet access, DHCP)
- **Adapter 2**: Internal Network (Lab communication, Static IP)

Windows 11 static IPv4 address: Any address on 192.168.0.0/24 (exept for 192.168.0.1)

### Running the Receiver on Kali
1. Navigate to the project directory
```bash
cd ~/Research_Project/Attacker
```
2. Start the receiver
``` bash
python3 receiver.py
```
3. Expected Output
```output
Listening on port 8080...
```
## Resources
- https://github.com/ionuttbara/windows-defender-remover/tree/main