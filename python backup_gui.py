import sys
import os
import threading
import json
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

# Add the current folder to sys.path so Python can find backup_core.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import backup functions
try:
    from backup_core import run_backup, run_exe, init_db, CopySession, read_data_json, DATA_JSON
except ImportError:
    messagebox.showerror("Error", "Could not find backup_core.py in the current folder:\n" + current_dir)
    sys.exit(1)


class BackupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup System")
        self.root.geometry("900x700")
        self.root.option_add('*Font', 'Arial 10')

        self.source_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.is_backing_up = False

        self.load_settings()
        self.create_widgets()
        self.auto_refresh_history()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=tk.YES)

        title_label = ttk.Label(
            main_frame, 
            text="🔄 Professional Backup System",
            font=("Arial", 16, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))

        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Source Path
        source_frame = ttk.Frame(settings_frame)
        source_frame.pack(fill=tk.X, pady=5)
        ttk.Label(source_frame, text="📁 Source:", width=15).pack(side=tk.LEFT)
        ttk.Entry(source_frame, textvariable=self.source_var).pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=5)
        ttk.Button(source_frame, text="Browse", command=self.browse_source, bootstyle="info-outline", width=10).pack(side=tk.LEFT)

        # Destination Path
        dest_frame = ttk.Frame(settings_frame)
        dest_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dest_frame, text="📂 Destination:", width=15).pack(side=tk.LEFT)
        ttk.Entry(dest_frame, textvariable=self.dest_var).pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=5)
        ttk.Button(dest_frame, text="Browse", command=self.browse_dest, bootstyle="info-outline", width=10).pack(side=tk.LEFT)

        ttk.Button(settings_frame, text="💾 Save Settings", command=self.save_settings, bootstyle="success", width=20).pack(pady=(10, 0))

        # Control Frame
        control_frame = ttk.LabelFrame(main_frame, text="🎮 Controls", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        button_frame = ttk.Frame(control_frame)
        button_frame.pack()
        self.backup_btn = ttk.Button(button_frame, text="▶️ Start Backup", command=self.start_backup, bootstyle="primary", width=25)
        self.backup_btn.pack(side=tk.LEFT, padx=5)
        self.run_btn = ttk.Button(button_frame, text="🚀 Backup & Run File", command=self.backup_and_run, bootstyle="warning", width=25)
        self.run_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📂 Open Destination", command=self.open_destination, bootstyle="info", width=25).pack(side=tk.LEFT, padx=5)

        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Status", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        status_label = ttk.Label(progress_frame, textvariable=self.status_var, font=("Arial", 11), bootstyle="inverse-primary")
        status_label.pack(pady=5)
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate', bootstyle="success-striped")
        self.progress.pack(fill=tk.X, pady=5)

        # History Frame
        history_frame = ttk.LabelFrame(main_frame, text="📜 Backup History", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=tk.YES)
        columns = ("ID", "User", "Device", "Folder", "Date")
        self.tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=10)
        self.tree.heading("ID", text="ID")
        self.tree.heading("User", text="User")
        self.tree.heading("Device", text="Device")
        self.tree.heading("Folder", text="Folder")
        self.tree.heading("Date", text="Date & Time")
        self.tree.column("ID", width=50)
        self.tree.column("User", width=120)
        self.tree.column("Device", width=120)
        self.tree.column("Folder", width=150)
        self.tree.column("Date", width=180)
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Button(history_frame, text="🔄 Refresh History", command=self.load_history, bootstyle="secondary", width=15).pack(pady=(10, 0))

        self.load_history()

    def load_settings(self):
        try:
            source, dest = read_data_json()
            self.source_var.set(source)
            self.dest_var.set(dest)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {e}")

    def save_settings(self):
        source = self.source_var.get().strip()
        dest = self.dest_var.get().strip()
        if not source or not dest:
            messagebox.showwarning("Warning", "Please enter both source and destination")
            return
        if source == dest:
            messagebox.showerror("Error", "Source and destination cannot be the same")
            return
        try:
            data = {"source": source, "destination": dest}
            with open(DATA_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success", "Settings saved successfully ✓")
            self.update_status("Settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_var.set(folder)

    def browse_dest(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_var.set(folder)

    def update_status(self, message):
        self.status_var.set(f"{message} - {datetime.now().strftime('%H:%M:%S')}")

    def start_backup(self):
        if self.is_backing_up:
            messagebox.showwarning("Warning", "Backup is already running")
            return
        source = self.source_var.get().strip()
        dest = self.dest_var.get().strip()
        if not source or not dest:
            messagebox.showwarning("Warning", "Please save settings first")
            return
        if not os.path.exists(source):
            messagebox.showerror("Error", f"Source folder does not exist: {source}")
            return
        self.is_backing_up = True
        self.backup_btn.config(state='disabled')
        self.run_btn.config(state='disabled')
        self.progress.start()
        self.update_status("Backing up...")
        thread = threading.Thread(target=self.backup_thread, daemon=True)
        thread.start()

    def backup_thread(self):
        try:
            success = run_backup(verbose=False)
            if success:
                self.root.after(0, lambda: self.backup_complete(True))
            else:
                self.root.after(0, lambda: self.backup_complete(False))
        except Exception as e:
            self.root.after(0, lambda: self.backup_error(str(e)))

    def backup_complete(self, success):
        self.is_backing_up = False
        self.backup_btn.config(state='normal')
        self.run_btn.config(state='normal')
        self.progress.stop()
        if success:
            self.update_status("✓ Backup completed successfully")
            messagebox.showinfo("Success", "Backup completed successfully! ✓")
            self.load_history()
        else:
            self.update_status("✗ Backup failed")
            messagebox.showwarning("Failed", "Backup failed or skipped. Check logs.")

    def backup_error(self, error_msg):
        self.is_backing_up = False
        self.backup_btn.config(state='normal')
        self.run_btn.config(state='normal')
        self.progress.stop()
        self.update_status(f"✗ Error: {error_msg}")
        messagebox.showerror("Error", f"An error occurred during backup:\n{error_msg}")

    def backup_and_run(self):
        if self.is_backing_up:
            messagebox.showwarning("Warning", "Backup is already running")
            return
        filename = simpledialog.askstring("Run File", "Enter the filename to run:\n(e.g., slack.exe, run.bat, script.py)", parent=self.root)
        if not filename:
            return
        source = self.source_var.get().strip()
        dest = self.dest_var.get().strip()
        if not source or not dest:
            messagebox.showwarning("Warning", "Please save settings first")
            return
        if not os.path.exists(source):
            messagebox.showerror("Error", f"Source folder does not exist: {source}")
            return
        self.is_backing_up = True
        self.backup_btn.config(state='disabled')
        self.run_btn.config(state='disabled')
        self.progress.start()
        self.update_status("Backing up...")
        thread = threading.Thread(target=self.backup_and_run_thread, args=(filename,), daemon=True)
        thread.start()

    def backup_and_run_thread(self, filename):
        try:
            success = run_backup(verbose=False)
            if not success:
                self.root.after(0, lambda: self.backup_complete(False))
                return
            run_success = run_exe(filename, verbose=False)
            if run_success:
                self.root.after(0, lambda: self.run_complete(filename, True))
            else:
                self.root.after(0, lambda: self.run_complete(filename, False))
        except Exception as e:
            self.root.after(0, lambda: self.backup_error(str(e)))

    def run_complete(self, filename, success):
        self.is_backing_up = False
        self.backup_btn.config(state='normal')
        self.run_btn.config(state='normal')
        self.progress.stop()
        if success:
            self.update_status(f"✓ Backup & Run of {filename} succeeded")
            messagebox.showinfo("Success", f"Backup and run of {filename} completed successfully! ✓")
            self.load_history()
        else:
            self.update_status(f"✗ Backup succeeded but running {filename} failed")
            messagebox.showwarning("Warning", f"Backup succeeded\nBut running the file {filename} failed")
            self.load_history()

    def open_destination(self):
        dest = self.dest_var.get().strip()
        if not dest:
            messagebox.showwarning("Warning", "Destination folder not set")
            return
        if not os.path.exists(dest):
            messagebox.showwarning("Warning", f"Destination folder does not exist: {dest}")
            return
        try:
            if sys.platform == 'win32':
                os.startfile(dest)
            elif sys.platform == 'darwin':
                subprocess.run(['open', dest])
            else:
                subprocess.run(['xdg-open', dest])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {e}")

    def load_history(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            session = init_db()
            records = session.query(CopySession).order_by(CopySession.copied_at.desc()).limit(50).all()
            for record in records:
                date_str = record.copied_at.strftime("%Y-%m-%d %H:%M:%S") if record.copied_at else ""
                self.tree.insert('', 'end', values=(record.id, record.current_user, record.device_name or "", record.folder_name, date_str))
            session.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history: {e}")

    def auto_refresh_history(self):
        if not self.is_backing_up:
            self.load_history()
        self.root.after(5000, self.auto_refresh_history)


def main():
    try:
        root = ttkb.Window(themename="cosmo")
        app = BackupGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Failed to run application:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
