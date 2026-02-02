import socket
import struct
import numpy as np
import cv2
from datetime import datetime

TARGET_IP = "0.0.0.0"  # Listen on all interfaces
TARGET_PORT = 8888

class ScreenReceiver:
    def __init__(self):
        self.server_socket = None
        self.client_socket = None
        
    def start_server(self):
        """Start TCP server and wait for connection"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((TARGET_IP, TARGET_PORT))
            self.server_socket.listen(1)
            print(f"[+] Listening on {TARGET_IP}:{TARGET_PORT}")
            print("[*] Waiting for incoming screen stream...")
            
            self.client_socket, client_addr = self.server_socket.accept()
            print(f"[+] Connection received from {client_addr[0]}:{client_addr[1]}")
            return True
            
        except Exception as e:
            print(f"[-] Server error: {e}")
            return False
    
    def receive_exact(self, size):
        """Receive exact number of bytes"""
        data = b''
        while len(data) < size:
            chunk = self.client_socket.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def receive_frame(self):
        """Receive a single frame with metadata"""
        try:
            # Receive frame header (12 bytes: frameSize, width, height)
            header = self.receive_exact(12)
            if not header:
                return None, None, None
            
            frame_size, width, height = struct.unpack('III', header)
            
            # Receive frame data
            frame_data = self.receive_exact(frame_size)
            if not frame_data:
                return None, None, None
            
            return frame_data, width, height
            
        except Exception as e:
            print(f"[-] Error receiving frame: {e}")
            return None, None, None
    
    def stream_loop(self):
        """Main loop to receive and display frames"""
        print("[*] Starting stream reception...")
        print("[*] Press 'q' to quit, 's' to save screenshot")
        
        frame_count = 0
        
        while True:
            frame_data, width, height = self.receive_frame()
            
            if frame_data is None:
                print("[-] Connection lost or error receiving frame")
                break
            
            frame_count += 1
            
            try:
                # Convert raw BGRA data to numpy array
                # DXGI typically outputs BGRA format
                frame_array = np.frombuffer(frame_data, dtype=np.uint8)
                
                # Calculate actual row pitch (may have padding)
                row_pitch = len(frame_data) // height
                
                # Reshape and extract BGR channels (ignore alpha)
                frame_array = frame_array.reshape((height, row_pitch // 4, 4))
                frame_bgr = frame_array[:, :width, :3]  # Take only BGR, drop alpha
                
                # Display frame
                cv2.imshow('Screen Stream', frame_bgr)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("[*] Quit requested")
                    break
                elif key == ord('s'):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshot_{timestamp}.png"
                    cv2.imwrite(filename, frame_bgr)
                    print(f"[+] Screenshot saved: {filename}")
                
                if frame_count % 30 == 0:  # Print every 30 frames
                    print(f"[*] Received {frame_count} frames ({width}x{height})")
                    
            except Exception as e:
                print(f"[-] Error processing frame {frame_count}: {e}")
                continue
        
        cv2.destroyAllWindows()
    
    def cleanup(self):
        """Close sockets"""
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        print("[*] Cleanup complete")

def main():
    print("=" * 60)
    print("Screen Stream Receiver")
    print("=" * 60)
    
    receiver = ScreenReceiver()
    
    try:
        if receiver.start_server():
            receiver.stream_loop()
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user")
    finally:
        receiver.cleanup()

if __name__ == "__main__":
    main()
