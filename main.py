import os
import sys
import time
import shutil
import glob
import threading
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar
from datetime import datetime
import pystray
from PIL import Image, ImageDraw

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SaveMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Celebi")
        self.root.geometry("400x380")
        self.root.resizable(False, False)
        
        self.bg_color = "#E8F5E9"
        self.btn_color = "#A5D6A7"
        self.btn_active = "#81C784"
        self.text_color = "#1B5E20"
        self.font_main = ("Segoe UI", 10)
        self.font_bold = ("Segoe UI", 11, "bold")

        self.root.configure(bg=self.bg_color)

        self.icon_path = resource_path("Celebi.ico")

        try:
            self.root.iconbitmap(self.icon_path)
        except Exception:
            pass 

        self.local_appdata = os.getenv('LOCALAPPDATA')
        self.game_dir = os.path.join(self.local_appdata, 'PlatinumTogether', 'Game')
        self.backup_dir = os.path.join(self.local_appdata, 'Celebi_PT_Backups')
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

        self.is_monitoring = True
        self.max_backups = 5
        self.last_mod_time = 0

        self.setup_ui()

        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)

        self.monitor_thread = threading.Thread(target=self.monitor_saves, daemon=True)
        self.monitor_thread.start()

        self.update_backup_list()

    def setup_ui(self):
        self.lbl_status = tk.Label(self.root, text="Status: Monitoring...", fg=self.text_color, bg=self.bg_color, font=self.font_bold)
        self.lbl_status.pack(pady=10)

        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        self.listbox = Listbox(frame, selectmode=tk.SINGLE, font=self.font_main, bg="#FFFFFF", selectbackground="#4CAF50", fg="#333333")
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=15)

        btn_style = {
            "font": self.font_main, 
            "bg": self.btn_color, 
            "activebackground": self.btn_active, 
            "relief": tk.FLAT, 
            "width": 16,
            "cursor": "hand2"
        }

        tk.Button(btn_frame, text="Restore Selected", command=self.restore_backup, **btn_style).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Open Backups", command=self.open_folder, **btn_style).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(btn_frame, text="Open Game Saves", command=self.open_game_folder, **btn_style).grid(row=1, column=0, padx=5, pady=5)
        
        self.btn_toggle = tk.Button(btn_frame, text="Stop Monitoring", command=self.toggle_monitoring, **btn_style)
        self.btn_toggle.grid(row=1, column=1, padx=5, pady=5)

    def get_save_files(self):
        arquivos = []
        arquivos_exatos = ['save-good.bin', 'save.bin', 'save-previous.bin', 'save-auto.bin']
        for f in arquivos_exatos:
            path = os.path.join(self.game_dir, f)
            if os.path.exists(path):
                arquivos.append(path)
                
        arquivos.extend(glob.glob(os.path.join(self.game_dir, 'save-backup-*.bin')))
        return arquivos

    def manage_backup_limit(self):
        backups = sorted(glob.glob(os.path.join(self.backup_dir, "PlatinumTogether-Save-*")), key=os.path.getmtime)
        
        while len(backups) > self.max_backups:
            oldest = backups.pop(0)
            try:
                shutil.rmtree(oldest)
            except Exception as e:
                pass

    def monitor_saves(self):
        while True:
            if self.is_monitoring and os.path.exists(self.game_dir):
                current_files = self.get_save_files()
                
                if current_files:
                    latest_mod = max(os.path.getmtime(f) for f in current_files)
                    
                    if latest_mod > self.last_mod_time:
                        if self.last_mod_time != 0:
                            time.sleep(1) 
                            
                            data_hora = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                            backup_path = os.path.join(self.backup_dir, f"PlatinumTogether-Save-{data_hora}")
                            os.makedirs(backup_path, exist_ok=True)
                            
                            for f in current_files:
                                try:
                                    shutil.copy2(f, backup_path)
                                except Exception:
                                    pass 
                            
                            self.manage_backup_limit()
                            self.root.after(0, self.update_backup_list)

                        self.last_mod_time = latest_mod
            time.sleep(5)

    def update_backup_list(self):
        self.listbox.delete(0, tk.END)
        backups = sorted(glob.glob(os.path.join(self.backup_dir, "PlatinumTogether-Save-*")), reverse=True)
        for b in backups:
            self.listbox.insert(tk.END, os.path.basename(b))

    def restore_backup(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a backup to restore.")
            return

        folder_name = self.listbox.get(selection[0])
        source_dir = os.path.join(self.backup_dir, folder_name)

        if messagebox.askyesno("Confirm Restore", f"Are you sure you want to overwrite your current saves with:\n{folder_name}?"):
            files = glob.glob(os.path.join(source_dir, "*.bin"))
            for f in files:
                shutil.copy2(f, self.game_dir)
            messagebox.showinfo("Success", "Time travel successful! Save restored.")

    def open_folder(self):
        os.startfile(os.path.abspath(self.backup_dir))
        
    def open_game_folder(self):
        if os.path.exists(self.game_dir):
            os.startfile(os.path.abspath(self.game_dir))
        else:
            messagebox.showwarning("Not Found", "The game save folder does not exist yet.")

    def toggle_monitoring(self):
        self.is_monitoring = not self.is_monitoring
        if self.is_monitoring:
            self.lbl_status.config(text="Status: Monitoring...", fg=self.text_color)
            self.btn_toggle.config(text="Stop Monitoring")
        else:
            self.lbl_status.config(text="Status: Paused", fg="#D32F2F")
            self.btn_toggle.config(text="Start Monitoring")

    def create_fallback_image(self):
        image = Image.new('RGB', (64, 64), color=(165, 214, 167))
        d = ImageDraw.Draw(image)
        d.text((15, 25), "SAVE", fill=(27, 94, 32))
        return image

    def setup_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window, default=True),
            pystray.MenuItem("Quit", self.quit_app)
        )
        
        try:
            tray_image = Image.open(self.icon_path)
        except Exception:
            tray_image = self.create_fallback_image()
            
        self.icon = pystray.Icon("save_monitor", tray_image, "Celebi", menu)

    def hide_window(self):
        self.root.withdraw()
        self.setup_tray() 
        threading.Thread(target=self.icon.run, daemon=True).start()

    def show_window(self, icon, item):
        self.icon.stop() 
        self.root.after(0, self.root.deiconify) 

    def quit_app(self, icon, item):
        self.icon.stop()
        self.root.after(0, self.root.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    app = SaveMonitorApp(root)
    root.mainloop()