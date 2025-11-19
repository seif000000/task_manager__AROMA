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

# أضف المجلد الحالي للـ sys.path عشان Python يقدر يلاقي backup_core.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import backup functions
try:
    from backup_core import run_backup, run_exe, init_db, CopySession, read_data_json, DATA_JSON
except ImportError:
    messagebox.showerror("خطأ", "لم يتم العثور على ملف backup_core.py في المجلد الحالي:\n" + current_dir)
    sys.exit(1)


class BackupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام النسخ الاحتياطي - Backup System")
        self.root.geometry("900x700")
        self.root.option_add('*Font', 'Arial 10')

        self.source_var = tk.StringVar()
        self.dest_var = tk.StringVar()
        self.status_var = tk.StringVar(value="جاهز")
        self.is_backing_up = False

        self.load_settings()
        self.create_widgets()
        self.auto_refresh_history()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=tk.YES)

        title_label = ttk.Label(
            main_frame, 
            text="🔄 نظام النسخ الاحتياطي الاحترافي",
            font=("Arial", 16, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))

        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ الإعدادات", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Source Path
        source_frame = ttk.Frame(settings_frame)
        source_frame.pack(fill=tk.X, pady=5)
        ttk.Label(source_frame, text="📁 المصدر:", width=15).pack(side=tk.LEFT)
        ttk.Entry(source_frame, textvariable=self.source_var).pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=5)
        ttk.Button(source_frame, text="تصفح", command=self.browse_source, bootstyle="info-outline", width=10).pack(side=tk.LEFT)

        # Destination Path
        dest_frame = ttk.Frame(settings_frame)
        dest_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dest_frame, text="📂 الوجهة:", width=15).pack(side=tk.LEFT)
        ttk.Entry(dest_frame, textvariable=self.dest_var).pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=5)
        ttk.Button(dest_frame, text="تصفح", command=self.browse_dest, bootstyle="info-outline", width=10).pack(side=tk.LEFT)

        ttk.Button(settings_frame, text="💾 حفظ الإعدادات", command=self.save_settings, bootstyle="success", width=20).pack(pady=(10, 0))

        # Control Frame
        control_frame = ttk.LabelFrame(main_frame, text="🎮 التحكم", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        button_frame = ttk.Frame(control_frame)
        button_frame.pack()
        self.backup_btn = ttk.Button(button_frame, text="▶️ بدء النسخ الاحتياطي", command=self.start_backup, bootstyle="primary", width=25)
        self.backup_btn.pack(side=tk.LEFT, padx=5)
        self.run_btn = ttk.Button(button_frame, text="🚀 نسخ وتشغيل ملف", command=self.backup_and_run, bootstyle="warning", width=25)
        self.run_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📂 فتح الوجهة", command=self.open_destination, bootstyle="info", width=25).pack(side=tk.LEFT, padx=5)

        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="📊 الحالة", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        status_label = ttk.Label(progress_frame, textvariable=self.status_var, font=("Arial", 11), bootstyle="inverse-primary")
        status_label.pack(pady=5)
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate', bootstyle="success-striped")
        self.progress.pack(fill=tk.X, pady=5)

        # History Frame
        history_frame = ttk.LabelFrame(main_frame, text="📜 سجل النسخ الاحتياطي", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=tk.YES)
        columns = ("ID", "المستخدم", "الجهاز", "المجلد", "التاريخ")
        self.tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=10)
        self.tree.heading("ID", text="ID")
        self.tree.heading("المستخدم", text="المستخدم")
        self.tree.heading("الجهاز", text="الجهاز")
        self.tree.heading("المجلد", text="المجلد")
        self.tree.heading("التاريخ", text="التاريخ والوقت")
        self.tree.column("ID", width=50)
        self.tree.column("المستخدم", width=120)
        self.tree.column("الجهاز", width=120)
        self.tree.column("المجلد", width=150)
        self.tree.column("التاريخ", width=180)
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Button(history_frame, text="🔄 تحديث السجل", command=self.load_history, bootstyle="secondary", width=15).pack(pady=(10, 0))

        self.load_history()

    def load_settings(self):
        try:
            source, dest = read_data_json()
            self.source_var.set(source)
            self.dest_var.set(dest)
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل تحميل الإعدادات: {e}")

    def save_settings(self):
        source = self.source_var.get().strip()
        dest = self.dest_var.get().strip()
        if not source or not dest:
            messagebox.showwarning("تحذير", "يرجى إدخال المصدر والوجهة")
            return
        if source == dest:
            messagebox.showerror("خطأ", "المصدر والوجهة لا يمكن أن يكونا نفس المسار")
            return
        try:
            data = {"source": source, "destination": dest}
            with open(DATA_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("نجح", "تم حفظ الإعدادات بنجاح ✓")
            self.update_status("تم حفظ الإعدادات بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل حفظ الإعدادات: {e}")

    def browse_source(self):
        folder = filedialog.askdirectory(title="اختر مجلد المصدر")
        if folder:
            self.source_var.set(folder)

    def browse_dest(self):
        folder = filedialog.askdirectory(title="اختر مجلد الوجهة")
        if folder:
            self.dest_var.set(folder)

    def update_status(self, message):
        self.status_var.set(f"{message} - {datetime.now().strftime('%H:%M:%S')}")

    def start_backup(self):
        if self.is_backing_up:
            messagebox.showwarning("تحذير", "النسخ الاحتياطي قيد التشغيل بالفعل")
            return
        source = self.source_var.get().strip()
        dest = self.dest_var.get().strip()
        if not source or not dest:
            messagebox.showwarning("تحذير", "يرجى حفظ الإعدادات أولاً")
            return
        if not os.path.exists(source):
            messagebox.showerror("خطأ", f"المصدر غير موجود: {source}")
            return
        self.is_backing_up = True
        self.backup_btn.config(state='disabled')
        self.run_btn.config(state='disabled')
        self.progress.start()
        self.update_status("جاري النسخ الاحتياطي...")
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
            self.update_status("✓ اكتمل النسخ الاحتياطي بنجاح")
            messagebox.showinfo("نجح", "تم النسخ الاحتياطي بنجاح! ✓")
            self.load_history()
        else:
            self.update_status("✗ فشل النسخ الاحتياطي")
            messagebox.showwarning("فشل", "فشل النسخ الاحتياطي أو تم تخطيه. تحقق من السجلات.")

    def backup_error(self, error_msg):
        self.is_backing_up = False
        self.backup_btn.config(state='normal')
        self.run_btn.config(state='normal')
        self.progress.stop()
        self.update_status(f"✗ خطأ: {error_msg}")
        messagebox.showerror("خطأ", f"حدث خطأ أثناء النسخ الاحتياطي:\n{error_msg}")

    def backup_and_run(self):
        if self.is_backing_up:
            messagebox.showwarning("تحذير", "النسخ الاحتياطي قيد التشغيل بالفعل")
            return
        filename = simpledialog.askstring("تشغيل ملف", "أدخل اسم الملف المراد تشغيله:\n(مثال: slack.exe أو run.bat أو script.py)", parent=self.root)
        if not filename:
            return
        source = self.source_var.get().strip()
        dest = self.dest_var.get().strip()
        if not source or not dest:
            messagebox.showwarning("تحذير", "يرجى حفظ الإعدادات أولاً")
            return
        if not os.path.exists(source):
            messagebox.showerror("خطأ", f"المصدر غير موجود: {source}")
            return
        self.is_backing_up = True
        self.backup_btn.config(state='disabled')
        self.run_btn.config(state='disabled')
        self.progress.start()
        self.update_status("جاري النسخ الاحتياطي...")
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
            self.update_status(f"✓ تم النسخ وتشغيل {filename} بنجاح")
            messagebox.showinfo("نجح", f"تم النسخ الاحتياطي وتشغيل {filename} بنجاح! ✓")
            self.load_history()
        else:
            self.update_status(f"✗ تم النسخ لكن فشل تشغيل {filename}")
            messagebox.showwarning("تحذير", f"تم النسخ الاحتياطي بنجاح\nلكن فشل تشغيل الملف: {filename}")
            self.load_history()

    def open_destination(self):
        dest = self.dest_var.get().strip()
        if not dest:
            messagebox.showwarning("تحذير", "لم يتم تعيين مجلد الوجهة")
            return
        if not os.path.exists(dest):
            messagebox.showwarning("تحذير", f"مجلد الوجهة غير موجود: {dest}")
            return
        try:
            if sys.platform == 'win32':
                os.startfile(dest)
            elif sys.platform == 'darwin':
                subprocess.run(['open', dest])
            else:
                subprocess.run(['xdg-open', dest])
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل فتح المجلد: {e}")

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
            messagebox.showerror("خطأ", f"فشل تحميل السجل: {e}")

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
        messagebox.showerror("خطأ فادح", f"فشل تشغيل التطبيق:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
