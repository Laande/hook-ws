import tkinter as tk
import json
import os

class PreferencesManager:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.preferences_file = os.path.join(self.script_dir, "preferences.json")
        self.load_preferences()
        
        self.always_on_top_var = tk.BooleanVar(value=self.preferences["always_on_top"])
        self.show_system_var = tk.BooleanVar(value=self.preferences["show_system"])
        self.show_error_var = tk.BooleanVar(value=self.preferences["show_error"])
        self.show_incoming_var = tk.BooleanVar(value=self.preferences["show_incoming"])
        self.show_outgoing_var = tk.BooleanVar(value=self.preferences["show_outgoing"])
    
    def load_preferences(self):
        if os.path.exists(self.preferences_file):
            with open(self.preferences_file, "r") as f:
                self.preferences = json.load(f)
        else:
            self.preferences = {
                "always_on_top": False,
                "show_system": True,
                "show_error": True,
                "show_incoming": True,
                "show_outgoing": True
            }
    
    def toggle_always_on_top(self, root):
        root.attributes('-topmost', self.always_on_top_var.get())
        self.save_preferences()
    
    def save_preferences(self):
        self.preferences.update({
            "always_on_top": self.always_on_top_var.get(),
            "show_system": self.show_system_var.get(),
            "show_error": self.show_error_var.get(),
            "show_incoming": self.show_incoming_var.get(),
            "show_outgoing": self.show_outgoing_var.get()
        })
        with open(self.preferences_file, "w") as f:
            json.dump(self.preferences, f)
    
    def apply_preferences(self, root):
        root.attributes('-topmost', self.always_on_top_var.get())