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

## Workflow
This project follows a multi-stage architecture to study Remote Access Tool behavior, privilege escalation, and defensive control interaction in controlled environments.

### Stage 1: Initial Entry (initial.cmd)
- **initial.cmd** serves as the initial execution vector.
Its responsibility is to initiate the workflow and retrieve the next-stage component.

- Persistence mechanisms are introduced to ensure continuity after reboot.

- Once the handoff is complete, the script removes itself to minimize artifacts.

### Stage 2: Staging (wget.cmd)
- **wget.cmd** functions as the staging script.

- It retrieves additional research components required for later stages.

- This script coordinates the execution order of subsequent payloads.

- Elevated privileges may be requested at this stage to enable system-level research actions.

### Stage 3: Installer & Environment Setup (installer.ps1)
- **installer.ps1** prepares the runtime environment for the project.

- It creates temporary working directories using randomized names.

- Additional research files are placed in predefined locations to support persistence and execution.

- This script acts as the central orchestrator for the setup phase.

### Stage 4: Defensive Interaction Scripts

**disableWinDef.ps1**
- Temporarily modifies Windows Defender behavior for research observation purposes.

- Used to study how endpoint protection reacts to staged threats.

- Creates exclusions for executing experimental binaries.

 **defender_remover.exe**

- Experimental binary used to analyze system behavior when core security components are absent.

- Enables post-compromise research such as persistence and long-term access analysis.

## Resources
- https://github.com/ionuttbara/windows-defender-remover/tree/main