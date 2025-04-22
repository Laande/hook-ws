import socket
import threading
import subprocess
import os

class ConnectionManager:
    def __init__(self, root, preferences_manager):
        self.root = root
        self.preferences_manager = preferences_manager
        self.client_socket = None
        self.proxy_process = None
        self.message_display = None
        self.button = None
        self.label = None
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def set_message_display(self, message_display):
        self.message_display = message_display
    
    def set_button(self, button):
        self.button = button
    
    def set_label(self, label):
        self.label = label
    
    def toggle_connection(self):
        if self.client_socket:
            self.disconnect_websocket()
        else:
            self.connect_to_websocket()
    
    def send_message(self, message, direction):
        if not message:
            return
        if self.client_socket:
            try:
                formatted_message = f"{direction}|{message}"
                self.client_socket.sendall(formatted_message.encode('utf-8'))
            except Exception as e:
                self.message_display.add_message("ERROR", f"Failed to send message: {e}")
        else:
            self.message_display.add_message("ERROR", "Not connected to interceptor")
    
    def receive_messages(self):
        try:
            while True:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                message = data.decode('utf-8')
                parts = message.split("|", 1)
                if len(parts) == 2:
                    direction, content = parts
                    self.message_display.add_message(direction, content)
        except Exception as e:
            if not self.proxy_process:
                self.message_display.add_message("ERROR", f"Connection lost: {e}")
        finally:
            self.client_socket = None
            self.update_button_text()
    
    def connect_to_interceptor(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('127.0.0.1', 8889))
            ws_url = self.client_socket.recv(4096).decode('utf-8')
            self.message_display.add_message("SYSTEM", f"Connected to: {ws_url}")
            self.label.configure(text=ws_url)
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.update_button_text()
            return True
        except Exception as e:
            return False
    
    def attempt_connection(self, attempt):
        if attempt > 3:
            self.message_display.add_message("SYSTEM", "Maximum connection attempts reached")
            return
        if self.connect_to_interceptor():
            return
        else:
            self.root.after(1000, lambda: self.attempt_connection(attempt + 1))
    
    def start_proxy(self):
        try:
            interceptor_path = os.path.join(self.script_dir, "interceptor", "websocket_interceptor.py")
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 6
            
            self.proxy_process = subprocess.Popen(
                ["mitmdump", "-s", interceptor_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                startupinfo=startupinfo
            )
            self.message_display.add_message("SYSTEM", "Proxy started on port 8080")
            threading.Thread(target=lambda: self.attempt_connection(1), daemon=True).start()
        except Exception as e:
            self.message_display.add_message("ERROR", f"Failed to start proxy: {e}")
    
    def connect_to_websocket(self):
        if not self.proxy_process:
            threading.Thread(target=self.start_proxy, daemon=True).start()
        else:
            threading.Thread(target=self.connect_to_interceptor, daemon=True).start()
    
    def disconnect_websocket(self):
        try:
            self.message_display.add_message("SYSTEM", "Disconnecting from WebSocket")
            self.label.configure(text="")
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            if self.proxy_process:
                self.proxy_process.terminate()
                self.message_display.add_message("SYSTEM", "Proxy terminated")
                self.proxy_process = None
            self.update_button_text()
        except Exception as e:
            self.message_display.add_message("ERROR", f"Failed to disconnect: {e}")
    
    def disconnect(self):
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        if self.proxy_process:
            try:
                self.proxy_process.terminate()
            except:
                pass
    
    def update_button_text(self):
        if self.button:
            if self.client_socket:
                self.button.configure(text="Disconnect")
            else:
                self.button.configure(text="Connect")