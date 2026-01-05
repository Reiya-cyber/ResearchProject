# Research Project
By Reiya-Cyber and Hexahydride2

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
# Remote Access Tool (RAT) Development

This project is an educational red team simulation demonstrating the development and operation of a custom Remote Access Tool (RAT) using scripts and programming languages such as Powershell on the victim side and a Python-based CLI console on the attacker side (Kali Linux). It illustrates realistic techniques for initial access, defense evasion, persistence, reverse beaconing, and interactive post-exploitation, strictly within isolated lab environments. Key capabilities include bypassing Windows Defender via early exclusions, enabling WinRM for remote access, creating a hidden backdoor account, and capturing screenshots in the user's session through a scheduled task named "WindowsDisplayUpdate". The attacker-side Python console detects online victims via reverse beacons and provides a menu-driven interface with options like remote-connection (using evil-winrm), screenshot retrieval, credential dumping, and keylogger deployment. The simulation employs living-off-the-land techniques with native Windows tools and PowerShell to highlight modern persistence and post-exploitation methods. This project is intended solely for research, red team training, and enhancing blue team detection and hardening strategies.

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

# Infection Workflow

This section describes the initial infection, persistence, and remote access mechanism simulated in this research project. The workflow is designed to demonstrate common techniques used in real-world malware for staging, privilege escalation, defense evasion, reverse beaconing, screenshot capture, and post-exploitation capabilities. **All steps are for educational analysis only and should never be executed outside isolated lab environments.**

## Step-by-Step Execution Flow

### 1. Initial Execution
The attack chain begins with the execution of `initial3_risk.cmd` (or equivalent downloader) on the target machine.  
This file is typically delivered via user interaction, phishing simulation, or prior compromise in a lab environment.

### 2. Evasion Preparation
A downloader script (e.g., `wget.cmd`) performs the following:
- Enables **WinRM** (Windows Remote Management) to allow remote PowerShell access.
- Downloads `disableWinDef.ps1`.
- Executes `disableWinDef.ps1` to proactively add Windows Defender exclusions for:
  - `installer.ps1`
  - `defender_remover.exe`
  - The **%TEMP%** directory
- Downloads `installer.ps1`.
- Downloads `defender_remover.exe`.
- Executes `installer.ps1` (What `installer.ps1` does will be explained later)
- Executes `defender_remover.exe` to remove Windows Security and UAC
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
- Generates `sender.ps1` inside this directory. This script contains the core logic for outbound beaconing to send a connection signal (including the target's IP address) to the attacker.
- Creates a **scheduled task** named "WindowsDisplayUpdate" that runs as the logged-in user to capture screenshots of the desktop (required for access to the user session's graphics context).
- Creates an additional scheduled task to execute `sender.ps1` persistently (e.g., at logon or on a recurring schedule).
- Creates a new local administrative account named `Adm1nistartor` (hidden backdoor account).

### 6. Attacker-Side CLI Console and Post-Exploitation
- On the attacker machine (Kali Linux), a custom **Python-based CLI console** is launched. This console acts as the main command-and-control interface.
- When the victim beacons via `sender.ps1`, it sends a connection signal containing the target's IP address to the attacker's listener.
- The Python CLI console receives the signal, registers the victim (by IP and any additional metadata), and presents an interactive menu with multiple post-exploitation options.

#### Available Options in the Attacker CLI Console
The console provides the following commands/options (demonstrating various post-exploitation techniques):

- **remote-connection**  
  Establishes a full interactive remote shell using **evil-winrm**.  
  The console automatically uses the received victim IP and authenticates with the backdoor account (`Adm1nistartor`). Once connected, the attacker gains a persistent PowerShell session on the target for arbitrary command execution.

- **screenshot**  
  Triggers remote screenshot capture:  
  - Uses the active evil-winrm session (or establishes one if needed).  
  - Remotely starts the pre-installed "WindowsDisplayUpdate" scheduled task via `Start-ScheduledTask`.  
  - The task runs in the logged-in user's session, captures the current desktop, and saves the image to a predictable location (e.g., `%TEMP%`).  
  - The console then downloads the screenshot file using evil-winrm's `download` command and displays/saves it locally.

- **credential-dump**  
(JUST AN IDEA RIGHT NOW)
  Performs credential harvesting on the target:  
  - Executes common techniques such as Mimikatz, LaZagne, or built-in PowerShell equivalents (e.g., `Invoke-Mimikatz` if loaded).  
  - Dumps LSASS memory for hashes, extracts saved credentials from browsers/registries, or retrieves Wi-Fi passwords.  
  - Results are exfiltrated back through the WinRM channel and displayed/saved in the console.

- **keylogger**  
(JUST AN IDEA RIGHT NOW)
  Deploys and manages an on-demand keylogger:  
  - Uploads and executes a lightweight PowerShell or binary keylogger payload via the WinRM session.  
  - The keylogger runs in the user context, captures keystrokes, and periodically exfiltrates logs (e.g., via beaconing or on-demand retrieval).  
  - The console can start, stop, or retrieve captured logs.

## Key Techniques Demonstrated
- Early Defender exclusion to bypass real-time scanning
- Persistence via Startup folder and scheduled tasks
- Privilege escalation through UAC interaction
- Backdoor account creation
- Remote access enablement (WinRM)
- Reverse beaconing for dynamic IP discovery
- Screenshot capture in user context (bypassing Session 0 isolation)
- Interactive post-exploitation via evil-winrm
- Credential dumping, keylogging, and data exfiltration

## Defensive Recommendations
To detect or prevent this chain:
- Enable **Tamper Protection** in Windows Defender
- Restrict PowerShell and WinRM usage (AppLocker, GPO restrictions)
- Monitor for suspicious scheduled task creation and execution (especially user-context graphical tasks)
- Audit local admin account creation
- Block inbound/outbound WinRM traffic unless required
- Monitor for outbound beaconing and anomalous network connections
- Detect credential access techniques (e.g., LSASS access, Mimikatz signatures)
- Implement endpoint logging for keystrokes and screenshot file creation

**Note**: The Python CLI console serves as a unified attacker interface, automating victim discovery and providing menu-driven access to advanced post-exploitation features over the established WinRM channel. All functionality is intended strictly for red teaming and educational purposes in controlled environments.

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

### Running the console on Kali
1. Navigate to the project directory
```bash
cd ~/Research_Project/Attacker
```
2. Start the receiver
``` bash
python3 main.py
```
3. Expected Output
```output
:::::::::  :::::::::   ::::::::  ::::::::::: :::::::::: :::::::: :::::::::::
:+:    :+: :+:    :+: :+:    :+:     :+:     :+:       :+:    :+:    :+:
+:+    +:+ +:+    +:+ +:+    +:+     +:+     +:+       +:+           +:+
+#++:++#+  +#++:++#:  +#+    +:+     +#+     +#++:++#  +#+           +#+
+#+        +#+    +#+ +#+    +#+     +#+     +#+       +#+           +#+
#+#        #+#    #+# #+#    #+# #+# #+#     #+#       #+#    #+#    #+#
###        ###    ###  ########   #####      ########## ########     ###

[*] Type help or h to see all commands...

username@ResearchProject#
```
## Resources
- https://github.com/ionuttbara/windows-defender-remover/tree/main