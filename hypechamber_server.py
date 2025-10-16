# ...existing code...
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys

class CORSHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

class WinchamberServer:
    def __init__(self):
        self.server = None
        self.server_thread = None
        self.config_file = "winchamber_config.json"
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("Winchamber Video Server")
        self.root.geometry("500x160")
        
        # Folder selection
        tk.Label(self.root, text="Hyepchamber Ordner:", font=("Arial", 12)).pack(pady=10)
        
        self.folder_var = tk.StringVar()
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=5)
        
        tk.Entry(folder_frame, textvariable=self.folder_var, width=50, state="readonly").pack(side=tk.LEFT, padx=5)
        tk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT)
        
        # Status
        self.status_var = tk.StringVar(value="Server stopped")
        tk.Label(self.root, textvariable=self.status_var, font=("Arial", 10)).pack(pady=20)
        
        # Load saved config (will start server if folder exists)
        self.load_config()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Winchamber Videos Folder")
        if folder:
            # If server already running, restart it to serve the new folder
            if self.server:
                self.stop_server()
            self.folder_var.set(folder)
            self.save_config()
            self.start_server()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    folder = config.get('folder', '')
                    if folder and os.path.exists(folder):
                        self.folder_var.set(folder)
                        # start server automatically
                        self.start_server()
        except:
            pass
    
    def save_config(self):
        try:
            config = {'folder': self.folder_var.get()}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass
    
    def start_server(self):
        folder = self.folder_var.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Please select a valid video folder!")
            return
        
        if self.server:
            return  # already running
        
        try:
            os.chdir(folder)
            self.server = HTTPServer(('localhost', 8080), CORSHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.status_var.set("Server running on http://localhost:8080")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
            self.server = None
            self.server_thread = None
    
    def stop_server(self):
        if self.server:
            try:
                self.server.shutdown()
            except:
                pass
            self.server = None
            self.server_thread = None
            
            self.status_var.set("Server stopped")
    
    def on_closing(self):
        self.stop_server()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = WinchamberServer()
    app.run()