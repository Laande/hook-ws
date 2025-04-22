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
    
    def mitmdump_check(self, startupinfo):
        mitmdump_path = "mitmdump"
        try:
            subprocess.run(["mitmdump", "--version"], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            startupinfo=startupinfo,
                            check=True)
            return mitmdump_path
        except (subprocess.SubprocessError, FileNotFoundError):
            python_versions = ["Python312", "Python311", "Python310", "Python39", "Python38", "Python37"]
            try:
                result = subprocess.run(["python", "--version"], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE, 
                                        text=True,
                                        check=True)
                version_output = result.stdout.strip()
                if version_output.startswith("Python "):
                    version_parts = version_output.split(" ")[1].split(".")
                    if len(version_parts) >= 2:
                        detected_version = f"Python{version_parts[0]}{version_parts[1]}"
                        self.message_display.add_message("SYSTEM", f"Detected Python version: {detected_version}")
                        
                        python_versions = [detected_version]
            except Exception:
                pass
            
            possible_paths = []
            
            for version in python_versions:
                possible_paths.extend([
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", version, "Scripts", "mitmdump.exe"),
                    os.path.join(os.environ.get("APPDATA", ""), "Python", version, "Scripts", "mitmdump.exe"),
                    os.path.join(os.environ.get("PROGRAMFILES", ""), version, "Scripts", "mitmdump.exe"),
                    os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), version, "Scripts", "mitmdump.exe")
                ])
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.message_display.add_message("SYSTEM", f"Found mitmdump at: {path}")
                    return path
            else:
                self.message_display.add_message("ERROR", "mitmdump not found, install it with 'pip install mitmproxy'")
                return
    
    def install_certificate(self, mitmdump_path):
        try:
            self.message_display.add_message("SYSTEM", "Installing mitmproxy certificate...")
            
            cert_path = os.path.join(os.environ.get("USERPROFILE", ""), ".mitmproxy", "mitmproxy-ca-cert.cer")
            
            if not os.path.exists(cert_path):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 6
                
                temp_process = subprocess.Popen(
                    [mitmdump_path, "--no-http2"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    startupinfo=startupinfo
                )
                self.root.after(2000, lambda: temp_process.terminate())
            
            if os.path.exists(cert_path):
                try:
                    batch_path = os.path.join(self.script_dir, "install_cert.bat")
                    with open(batch_path, "w") as f:
                        f.write(f'@echo off\n')
                        f.write(f'echo Installing mitmproxy certificate...\n')
                        f.write(f'certutil -addstore -f "ROOT" "{cert_path}"\n')
                        f.write(f'if %ERRORLEVEL% EQU 0 (\n')
                        f.write(f'  echo Certificate installed successfully\n')
                        f.write(f') else (\n')
                        f.write(f'  echo Failed to install certificate\n')
                        f.write(f')\n')
                    
                    self.message_display.add_message("SYSTEM", "Please accept the UAC prompt to install the certificate")
                    os.startfile(batch_path, "runas")
                    
                    return True
                except Exception as e:
                    self.message_display.add_message("ERROR", f"Failed to run with admin rights: {e}")
                    try:
                        os.startfile(cert_path)
                        self.message_display.add_message("SYSTEM", "Please manually install the certificate to the Trusted Root store")
                        return True
                    except Exception as e2:
                        self.message_display.add_message("ERROR", f"Failed to open certificate: {e2}")
                        return False
            else:
                self.message_display.add_message("ERROR", "Certificate file not found")
                return False
                
        except Exception as e:
            self.message_display.add_message("ERROR", f"Failed to install certificate: {e}")
            return False
    
    def start_proxy(self):
        try:
            interceptor_path = os.path.join(self.script_dir, "interceptor", "websocket_interceptor.py")
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 6
            
            mitmdump_path = self.mitmdump_check(startupinfo)
            if not mitmdump_path:
                return
            
            if not self.preferences_manager.get_preference("certificate_installed", False):
                cert = self.install_certificate(mitmdump_path)
                if cert:
                    self.preferences_manager.set_preference("certificate_installed", True)
                else:
                    return
            
            self.proxy_process = subprocess.Popen(
                [mitmdump_path, "-s", interceptor_path],
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