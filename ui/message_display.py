import tkinter as tk
import customtkinter as ctk
import datetime

class MessageDisplay:
    def __init__(self, parent, preferences_manager):
        self.preferences_manager = preferences_manager
        
        self.frame = ctk.CTkFrame(parent, corner_radius=10)
        self.frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.text_display = tk.Text(
            self.frame, 
            wrap="word", 
            state="disabled", 
            bg="#1e1e1e", 
            fg="#ffffff", 
            font=("Helvetica", 10)
        )
        self.text_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.text_display.tag_configure("ERROR", foreground="#ff0000")
        self.text_display.tag_configure("SYSTEM", foreground="#00ff00")
        self.text_display.tag_configure("OUTGOING", foreground="#0096FF")
        self.text_display.tag_configure("INCOMING", foreground="#800080")
        self.text_display.tag_configure("timestamp", foreground="#aaaaaa")
        self.text_display.tag_configure("message_padding", spacing1=2, spacing3=5)
    
    def add_message(self, direction, message):
        if (direction == "SYSTEM" and not self.preferences_manager.show_system_var.get()) or \
           (direction == "ERROR" and not self.preferences_manager.show_error_var.get()) or \
           (direction == "INCOMING" and not self.preferences_manager.show_incoming_var.get()) or \
           (direction == "OUTGOING" and not self.preferences_manager.show_outgoing_var.get()):
            return
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.text_display.configure(state="normal")
        
        self.text_display.insert("end", f"[{timestamp}] ", "timestamp")
        self.text_display.insert("end", f"{direction}\n", direction)
        self.text_display.insert("end", f"{message}\n", "message_padding")
        
        self.text_display.configure(state="disabled")
        self.text_display.see("end")
    
    def clear_logs(self):
        self.text_display.configure(state="normal")
        self.text_display.delete("1.0", "end")
        self.text_display.configure(state="disabled")