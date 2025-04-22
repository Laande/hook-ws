import customtkinter as ctk
from ui.ui_components import setup_ui_components
from utils.connection_manager import ConnectionManager
from utils.preferences import PreferencesManager

def start_ui():
    root = ctk.CTk()
    root.title("WebSocket Interceptor")
    root.geometry("750x600")
    
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    preferences_manager = PreferencesManager()
    connection_manager = ConnectionManager(root, preferences_manager)
    
    setup_ui_components(root, connection_manager, preferences_manager)
    
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, connection_manager))
    root.mainloop()

def on_closing(root, connection_manager):
    connection_manager.disconnect()
    root.destroy()