from mitmproxy import http, ctx
import socket
import asyncio
import threading
import time

class WebSocketInterceptor:
    def __init__(self):
        self.active_flow = None
        self.injected_messages = set()
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('127.0.0.1', 8889))
        self.server_socket.listen(1)
        
        self.client_socket = None
        
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_event_loop, daemon=True).start()
        
        threading.Thread(target=self.accept_connections, daemon=True).start()
    
    def start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def accept_connections(self):
        print("Waiting for UI connection...")
        while True:
            try:
                client_socket, _ = self.server_socket.accept()
                self.client_socket = client_socket
                print("UI connected")
                
                asyncio.run_coroutine_threadsafe(self.receive_messages(), self.loop)
            except Exception as e:
                print(f"Error accepting connection: {e}")
                time.sleep(1)
    
    async def receive_messages(self):
        try:
            while True:
                data = await self.loop.run_in_executor(None, self.client_socket.recv, 4096)
                if not data:
                    continue
                
                message = data.decode('utf-8')
                parts = message.split("|", 1)
                if len(parts) == 2:
                    direction, content = parts
                    to_client = direction == "INCOMING"
                    
                    if self.active_flow:
                        try:
                            print(f"Injecting message: {content}")
                            try:
                                message_id = f"{direction}|{content}"
                                self.injected_messages.add(message_id)
                                
                                ctx.master.commands.call(
                                    "inject.websocket", 
                                    self.active_flow, 
                                    to_client, 
                                    content.encode('utf-8')
                                )
                                print("Direct injection successful")
                                self.send_to_ui(f"{direction} (injected)|{content}")
                            except Exception as e:
                                self.injected_messages.discard(message_id)
                                print(f"Direct injection error: {str(e)}")
                                self.send_to_ui(f"ERROR|Injection failed: {str(e)}")
                        except Exception as e:
                            print(f"Send error: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            self.send_to_ui(f"ERROR|{str(e)}")
                    else:
                        print("No active WebSocket connection")
                        self.send_to_ui("ERROR|No active WebSocket connection")
        except Exception as e:
            print(f"Error receiving message: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.client_socket = None
            print("UI disconnected")
    
    def send_to_ui(self, message):
        if self.client_socket:
            try:
                self.client_socket.sendall(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending to UI: {e}")
    
    def websocket_start(self, flow):
        self.active_flow = flow
        ws_url = flow.server_conn.address[0]
        self.send_to_ui(ws_url)
    
    def websocket_end(self, flow):
        if self.active_flow == flow:
            self.active_flow = None
            self.send_to_ui("SYSTEM|WebSocket connection closed")
    
    def websocket_message(self, flow):
        if hasattr(flow, 'websocket'):
            message = flow.websocket.messages[-1]
        else:
            message = flow.messages[-1]
            
        direction = "OUTGOING" if message.from_client else "INCOMING"
        payload = message.content
        
        if isinstance(payload, bytes):
            payload_str = payload.decode('utf-8', errors='ignore')
        else:
            payload_str = str(payload)
        
        message_id = f"{direction}|{payload_str}"
        if message_id in self.injected_messages:
            self.injected_messages.discard(message_id)
            return
        
        self.send_to_ui(f"{direction}|{payload_str}")

addons = [WebSocketInterceptor()]