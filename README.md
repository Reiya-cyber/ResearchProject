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

### Step-by-Step Flow

1. **Initial Execution**  
   The process begins with the execution of `initial.cmd` on the target (victim) machine. This script is placed in a location that ensures startup execution (e.g., via user interaction or prior compromise in a lab setting).

2. **Downloader Staging**  
   `initial.cmd` downloads `wget.cmd` and saves it directly to the user's Startup folder for persistence.

3. **Payload Download**  
   `wget.cmd` then downloads the main staging script `installer.ps1` from a remote location (e.g., a controlled GitHub repository in research simulations).

4. **Persistence and Evasion Setup**  
   `installer.ps1` performs the following actions:  
   - Creates a temporary directory with a random name under `%TEMP%` for staging additional components.  
   - Downloads two defense evasion tools to the Startup folder:  
     - `disableWinDef.ps1`  
     - `defender_remover.exe` (based on public research tools, see Resources section)

5. **Privilege Escalation and Execution**  
   `wget.cmd` is configured to trigger a UAC prompt, requesting administrative privileges. Upon approval (simulated in lab tests), it executes:  
   - `disableWinDef.ps1`: Temporarily disables Windows Defender real-time protection and adds exclusions for `defender_remover.exe`.  
   - `defender_remover.exe`: Permanently disables or removes Windows Defender components and UAC prompts to facilitate further stages (e.g., payload deployment).

This chain achieves persistence across reboots, elevates privileges, and evades basic endpoint protection—highlighting the importance of strong defenses like tamper protection, restricted script execution, and monitoring for suspicious downloads.

**Note**: Subsequent stages (e.g., keylogger, screenshots, remote access) would be deployed after successful evasion, as outlined in the Roadmap.

## Resources
- https://github.com/ionuttbara/windows-defender-remover/tree/main