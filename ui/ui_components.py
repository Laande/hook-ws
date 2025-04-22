import tkinter as tk
import customtkinter as ctk
from ui.message_display import MessageDisplay

def setup_ui_components(root, connection_manager, preferences_manager):
    main_frame = ctk.CTkFrame(root, corner_radius=10)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    create_connection_frame(main_frame, connection_manager)
    create_options_frame(main_frame, preferences_manager, root)
    
    message_display = MessageDisplay(main_frame, preferences_manager)
    connection_manager.set_message_display(message_display)
    
    create_packet_frame(main_frame, connection_manager)
    
    preferences_manager.apply_preferences(root)
    message_display.add_message("SYSTEM", "Click 'Connect' to begin intercepting WebSocket traffic")

def create_connection_frame(parent, connection_manager):
    connection_frame = ctk.CTkFrame(parent, corner_radius=10)
    connection_frame.pack(fill="x", padx=10, pady=10)
    start_proxy_button = ctk.CTkButton(
        connection_frame, 
        text="Connect", 
        command=connection_manager.toggle_connection
    )
    start_proxy_button.pack(side="left", padx=5, pady=5)
    connection_manager.set_button(start_proxy_button)
    ws_name_label = ctk.CTkLabel(connection_frame, text="", fg_color="#2d2d2d")
    ws_name_label.pack(side="left", padx=5, pady=5)
    connection_manager.set_label(ws_name_label)
    clear_logs_button = ctk.CTkButton(
        connection_frame, 
        text="Clear Logs", 
        command=lambda: connection_manager.message_display.clear_logs()
    )
    clear_logs_button.pack(side="right", padx=5, pady=5)
    
    return connection_frame

def create_options_frame(parent, preferences_manager, root):
    options_frame = ctk.CTkFrame(parent, corner_radius=10)
    options_frame.pack(fill="x", padx=10, pady=10)
    ctk.CTkCheckBox(
        options_frame, 
        text="System", 
        variable=preferences_manager.show_system_var, 
        command=preferences_manager.save_preferences
    ).pack(side="left", padx=5, pady=5)
    
    ctk.CTkCheckBox(
        options_frame, 
        text="Error", 
        variable=preferences_manager.show_error_var, 
        command=preferences_manager.save_preferences
    ).pack(side="left", padx=5, pady=5)
    
    ctk.CTkCheckBox(
        options_frame, 
        text="Incoming", 
        variable=preferences_manager.show_incoming_var, 
        command=preferences_manager.save_preferences
    ).pack(side="left", padx=5, pady=5)
    
    ctk.CTkCheckBox(
        options_frame, 
        text="Outgoing", 
        variable=preferences_manager.show_outgoing_var, 
        command=preferences_manager.save_preferences
    ).pack(side="left", padx=5, pady=5)
    always_on_top_checkbox = ctk.CTkCheckBox(
        options_frame, 
        text="Always on Top", 
        variable=preferences_manager.always_on_top_var, 
        command=lambda: preferences_manager.toggle_always_on_top(root)
    )
    always_on_top_checkbox.pack(side="right", padx=5)
    
    return options_frame

def create_packet_frame(parent, connection_manager):
    packet_frame = ctk.CTkFrame(parent, corner_radius=10)
    packet_frame.pack(fill="x", padx=10, pady=10)
    direction_var = tk.StringVar(value="OUTGOING")
    direction_menu = ctk.CTkComboBox(
        packet_frame, 
        variable=direction_var, 
        values=["OUTGOING", "INCOMING"]
    )
    direction_menu.pack(side="left", padx=5)
    message_input = tk.Text(
        packet_frame, 
        height=5, 
        bg="#1e1e1e", 
        fg="#ffffff", 
        font=("Helvetica", 10), 
        width=50
    )
    message_input.pack(side="left", fill="x", expand=True, padx=5, pady=5)
    send_button = ctk.CTkButton(
        packet_frame, 
        text="Send", 
        command=lambda: connection_manager.send_message(message_input.get("1.0", "end").strip(), direction_var.get())
    )
    send_button.pack(side="right", padx=5)
    
    return packet_frame