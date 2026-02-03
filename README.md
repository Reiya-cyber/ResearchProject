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
    - evil-winrm
- Credential dump
    - computer
    - web
    - applications
- Privilege escalation
- Worm
- VM detector


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
  - `keylogger.exe`
  - The **%TEMP%** directory
- Downloads `installer.ps1`.
- Downloads `defender_remover.exe`.
- Downloads `keylogger.exe` to the user's Startup folder for persistence, ensuring it runs in the background every time the user logs in.
- Executes `installer.ps1` (What `installer.ps1` does will be explained later)
- Executes `defender_remover.exe` to remove Windows Security and UAC
This step ensures subsequent payloads are not flagged or quarantined by real-time protection.

### 3. Main Payload Download
The downloader then retrieves and saves the following files directly to the user's **Startup folder** for persistence across user logons:
- `installer.ps1`
- `defender_remover.exe`
- `keylogger.exe (as noted above, for background execution on login)`

### 4. Payload Execution
Both downloaded files are executed (typically triggering a UAC prompt for elevation in lab tests):
- `defender_remover.exe`: Permanently disables or removes Windows Defender components and may reduce UAC restrictions.
- `installer.ps1`: Proceeds with advanced staging.

### 5. Advanced Staging and Persistence
`installer.ps1` performs the following actions:
- Creates a temporary directory with a random name under `%TEMP%`.
- Generates `sender.ps1` inside this directory. This script contains the core logic for outbound beaconing to send a connection signal (including the target's IP address) to the attacker.
- Creates a **scheduled task** named "WindowsDisplayUpdate" that runs as the logged-in user to capture screenshots of the desktop (required for access to the user session's graphics context).
- Creates an additional scheduled task named `RunSenderPS1` to execute `sender.ps1` persistently (e.g., at logon or on a recurring schedule).
- Creates a new local administrative account named `Adm1nistartor` (hidden backdoor account).
- Creates a task schedule called dump.cmd for credential dumping (executed later via the Python console).
- Downloads webcam.ps1 and VLC under the temp folder and creates a scheduled task to run webcam.ps1.

### 6. Attacker-Side CLI Console and Post-Exploitation
- On the attacker machine (Kali Linux), a custom **Python-based CLI console** is launched. This console acts as the main command-and-control interface.
- When the victim beacons via `sender.ps1`, it sends a connection signal containing the target's IP address to the attacker's listener.
- The Python CLI console receives the signal, registers the victim (by IP and any additional metadata), and presents an interactive menu with multiple post-exploitation options.

#### Available Options in the Attacker CLI Console
The console provides the following commands/options (demonstrating various post-exploitation techniques):

- **remote-connection** \
  Establishes a full interactive remote shell using evil-winrm.  
  - The console automatically uses the received victim IP and authenticates with the backdoor account (`Adm1nistartor`). - Once connected, the attacker gains a persistent PowerShell session on the target for arbitrary command execution.

- **screenshot**  
  Triggers remote screenshot capture:  
  - Uses the active evil-winrm session (or establishes one if needed).  
  - Remotely starts the pre-installed "WindowsDisplayUpdate" scheduled task via `Start-ScheduledTask`.  
  - The task runs in the logged-in user's session, captures the current desktop, and saves the image to a predictable location (e.g., `%TEMP%`).  
  - The console then downloads the screenshot file using evil-winrm's `download` command and displays/saves it locally.

- **credential-dump** \
  Performs credential harvesting on the target:
  - Executes dump.cmd through evil-winrm.
  - dump.cmd downloads Mimikatz and performs an LSASS dump to retrieve local credentials.
  - Results are exfiltrated back through the WinRM channel and displayed/saved in the console.

- **keylogger** \
  Manages the keylogger:
  - The keylogger.exe (downloaded to Startup folder) constantly saves key log files under C:\Users\Public\Logs folder.
  - When the command is run, it downloads those log files via evil-winrm.

- **webcam** \
  Initiates webcam monitoring:
  - Invokes the scheduled task for webcam.ps1 through evil-winrm.
  - webcam.ps1 runs VLC as a background process and makes the webcam feed accessible through HTTP.

- **screen-stream** \
  Receives real-time desktop screen streaming from the target:

  - Uses DXGI (Desktop Duplication API) to capture the desktop at ~30 FPS directly from the GPU.
  - Attempts to establish a TCP connection to the attacker's IP (192.168.0.1) on port 8888.
  - On the attacker side, running the `screen-stream` command starts `screen_receiver.py`, which listens on port 8888.
  - The receiver decodes incoming frames and displays them in real-time, providing live desktop monitoring of the target machine.
  

## Key Techniques Demonstrated
- Early Defender exclusion to bypass real-time scanning
- Persistence via Startup folder and scheduled tasks
- Privilege escalation through UAC interaction
- Backdoor account creation
- Remote access enablement (WinRM)
- Reverse beaconing for dynamic IP discovery
- Screenshot capture in user context (bypassing Session 0 isolation)
- Interactive post-exploitation via evil-winrm
- Credential dumping via Mimikatz and LSASS dump
- Keylogging with persistent background execution and log exfiltration
- Webcam monitoring via VLC and HTTP access
- Data exfiltration

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
- Monitor file creation in public directories (e.g., C:\Users\Public\Logs) and Startup folders

**Note**: The Python CLI console serves as a unified attacker interface, automating victim discovery and providing menu-driven access to advanced post-exploitation features over the established WinRM channel. All functionality is intended strictly for red teaming and educational purposes in controlled environments.

# Setups
## Network Configuration (Kali Linux)

This project assumes Kali Linux is configured with a **static IPv4 address** on an **internal network adapter** for isolated lab communication.

### Network layout
- **Adapter 1**: NAT / Bridged (Internet access, DHCP)
- **Adapter 2**: Internal Network (Lab communication, Static IP)

Kali static IPv4 address: 192.168.0.1/24


### 1. Identify network interfaces
List available interfaces and NetworkManager connections:
```bash
ip a
nmcli device status
nmcli connection show
```
### 2. Bind the internal connection to the internal interface
```bash
sudo nmcli connection modify "Wired connection 2" connection.interface-name eth1
```
### 3. Configure static IPv4 address
```bash
sudo nmcli connection modify "Wired connection 2" \
  ipv4.method manual \
  ipv4.addresses 192.168.0.1/24 \
  ipv4.gateway "" \
  ipv4.dns "" \
  ipv4.never-default yes
```
### 4. Apply the configuration
```bash
sudo nmcli connection down "Wired connection 2"
sudo nmcli connection up "Wired connection 2"
```

### Download Tools (Kali Linux)
```bash
sudo apt update
sudo apt install vlc
sudo apt install python3-opencv
```

## Network Configuration (Windows 11)

This project assumes the Windows 11 test machine is connected to the **same internal network** as Kali Linux using a **static IPv4 address**.  
This enables isolated lab communication without exposing services to external networks.

### Network layout
- **Adapter 1**: NAT / Bridged (Internet access, DHCP)
- **Adapter 2**: Internal Network (Lab communication, Static IP)

Windows 11 static IPv4 address: Any address on 192.168.0.0/24 (exept for 192.168.0.1)

## Setup Email system between targets

### Part 1 – MailEnable Server Installation

1. On Victim1 Windows 11, go to: https://www.mailenable.com  
   Download **MailEnable Standard Edition** (free version)

2. Run the installer  
   → When error prompted **"Setup has detected that ..."** → Click **OK**

3. Welcome → **Next**

4. User/Company information  
   - Name: `RAT`  
   - Company: `ResearchProject`  
   → **Next**

5. License Agreement → **Next**

6. Select Components → leave defaults → **Next**

7. Destination Folder → leave default → **Next**

8. Ready to Install → **Next** → **Next** again

9. Postoffice Configuration  
   - Postoffice Name: `Default`  
   - Administrator password: `Pa$$w0rd`  
   → **Next**

10. Messaging Storage → leave defaults → **Next**

11. Default Domain  
    - Domain Name: `rat.gr`  
    - Leave other options default  
    → **Next**

12. Final screen → **Next**  
    Installation begins...

13. When finished → **Finish**

14. Launch **MailEnable Administration** (MailEnableAdmin) from Start Menu

### Part 2 – Create Test Mailboxes

1. Open **MailEnable Administration**

2. Go to:  
   **Messaging Manager** → **Post Offices** → **DEFAULT**

3. Right-click on **Mailboxes** → **New Mailbox**

4. Create first mailbox:  
   - **Mailbox Name**: `Victim1`  
   - **Password**: `Pa$$word`  
   - Leave other settings default  
   → **OK**

5. Create second mailbox:  
   - **Mailbox Name**: `Victim2`  
   - **Password**: `Pa$$word`  
   - Leave other settings default  
   → **OK**

### Part 3 - Firewall Setting
1. Press `Win + S` → type **Windows Defender Firewall** → open **Windows Defender Firewall with Advanced Security**

2. In the left pane, click **Inbound Rules**

3. In the right pane, click **New Rule...**

4. **Rule Type**: Select **Port** → **Next**

5. **Protocol and Ports**:  
   - Protocol: **TCP**  
   - Specific local ports: `25,143`  
   → **Next**

6. **Action**: Select **Allow the connection** → **Next**

7. **Profile**: Check **Domain**, **Private**, and **Public** 
→ **Next**

8. **Name**: Enter  
   `Allow SMTP and IMAP`  
   → **Finish**

### Part 4 – Install Thunderbird Email Client (on client machines)

**Repeat these steps on each client machine (e.g. Victim1 and Victim2 Windows 11 VMs)**

1. Go to: https://www.thunderbird.net

2. Download the installer

3. Run the installer  
   - Welcome → **Next**  
   - Setup Type: **Standard** → **Next**  
   - Installation path: leave default → **Install**

4. Launch Thunderbird after installation

5. In the "Set up your existing email address" screen:  
   - Your name: `Victim1`  
   - Email address: `Victim1@rat.gr`  
   - Password: `Pa$$w0rd`  
   → Click **Configure manually**

6. Manual configuration settings:

   **Incoming server (IMAP)**  
   - Protocol: **IMAP**  
   - Hostname: `192.168.0.10`  
   - Port: **143**  
   - Connection security: **None**  
   - Authentication method: **Normal password**  
   - Username: `Victim1`  *(just the mailbox name – NOT @rat.gr)*

   **Outgoing server (SMTP)**  
   - Hostname: `192.168.0.10`  
   - Port: **25**  
   - Connection security: **None**  
   - Authentication method: **Normal password**  
   - Username: `Victim1`

7. Click **Re-test**

8. If Thunderbird says:  
   *"The following settings were found by probing the given server"*  
   → Click **Done**

9. Security warning appears → Click **I understand the risks** → **Confirm**

10. Click **Finish**

11. Skip any integration / address book / calendar prompts

12. Repeat the entire Thunderbird setup process for **Victim2**  
    - Name: `Victim2`  
    - Email: `Victim2@rat.gr`  
    - Password: `Pa$$word`  
    - Username (incoming & outgoing): `Victim2`  
    - All other settings identical

### Part 5 – Create Personal Address Book Entry (Victim1 → Victim2)

**Performed on Victim1's Thunderbird**

1. Open Thunderbird on Victim1's machine

2. In the left sidebar, click **Address Book**  
   (If you don't see it, go to menu → **Tools** → **Address Book**, or press `Ctrl+Shift+B`)

3. In the Address Book window:  
   - Make sure **Personal Address Book** is selected in the left pane  
     (it should already be there by default)

4. Click the **New Contact** button  
   (or go to **File** → **New** → **Contact**)

5. Fill in the contact details:

   - **Name** / **Display Name**: `Victim2` 
   - **First Name**: `Victim2` (optional)
   - **Email**: `Victim2@rat.gr` 

6. Click **OK** to save the contact

### Quick Test

- From Victim1 Thunderbird: Compose email to `Victim2@rat.gr` and send
- From Victim2 Thunderbird: Check inbox — message should arrive

## Running the console on Kali
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
                .88888.              888888ba                                    
               d8'   `88             88    `8b                                   
               88                   a88aaaa8P'                                   
               88   YP88  88888888   88   `8b.                                   
               Y8.   .88             88     88                                   
                `88888'              dP     dP                                   
                                                                  
                                                                  
   888888ba  .d888888d888888P  d888888P.88888.  .88888. dP        
   88    `8bd8'    88   88        88  d8'   `8bd8'   `8b88        
  a88aaaa8P'88aaaaa88a  88        88  88     8888     8888        
   88   `8b.88     88   88        88  88     8888     8888        
   88     8888     88   88        88  Y8.   .8PY8.   .8P88        
   dP     dP88     88   dP        dP   `8888P'  `8888P' 88888888P 

[*] Type help or h to see all commands...

username@ResearchProject# help

        Available commands:
        help, h        Show this help menu
        set            Set a target IP address
        show           Show current target
        listen         Start listening for a target
        check          Check target connectivity (WinRM ports)
        evil-winrm     Connect to target using evil-winrm     
        key-logger     To be determined
        screen-shot    Take screenshot
        dump           Credentials dump
        webcam         Monitor the webcam on target
        exit, q        Exit the console

username@ResearchProject#
```
## Resources
- https://github.com/CosmodiumCS/MK01-OnlyRAT/tree/main (Basic Workflow idea)
- https://github.com/ionuttbara/windows-defender-remover/tree/main (Defender Remover)
- https://github.com/microsoft/terminal/issues/16072 (UAC prompt)
- https://github.com/Hackplayers/evil-winrm (Evil Winrm)
- https://github.com/ParrotSec/mimikatz (Mimikatz)
- https://www.videolan.org (Webcam Monitoring)
- https://github.com/lclevy/firepwd (Thunderbird credential dump)
- https://www.thunderbird.net (Officail Thunderbird app download page)
- https://www.mailenable.com/ (Free Email Server)