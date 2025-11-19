🛡️ Python Backup System
A professional backup solution for IT environments, featuring:

✅ Automated backups via a Windows service
💻 Manual control via a CLI tool
🖥️ Interactive management via a GUI application
🗂️ Backup history stored in a local SQLite database

📦 Installation
Install required dependencies:

pip install pywin32 ttkbootstrap

⚙️ Windows Service: PythonBackupService.py


🔧 Install the Service

python PythonBackupService.py install
▶️ Start the Service

python PythonBackupService.py start
⏹️ Stop the Service

python PythonBackupService.py stop
❌ Remove the Service

python PythonBackupService.py remove

🔍 Check Service Status

Option 1: Services App

Open services.msc from Start menu
Find PythonBackupService
Check status (Running or Stopped)
Right-click to start/stop

Option 2: CMD

sc query PythonBackupService
If running:

Code
STATE              : 4  RUNNING
If stopped:

Code
STATE              : 1  STOPPED

💻 CLI Tool: backup_cli.py
Run manual backups with optional file execution.

🔹 Copy Only

python backup_cli.py -c
🔹 Copy + Run File

python backup_cli.py -r <filename>

Example:

python backup_cli.py -r deploy.bat

<filename> can be .exe, .bat, .py, etc.

The file will be executed from the backup destination

🖥️ GUI Application: backup_gui.py
Launch the graphical interface:

python backup_gui.py

✨ Features
Arabic interface with intuitive controls
Browse and save source/destination folders
Start backup or backup + run file
View and auto-refresh backup history
Open destination folder directly

🗂️ Project Structure (After Running)
Code
.
├── backup_cli.py              # CLI tool
├── backup_core.py             # Core logic
├── backup_gui.py              # GUI application
├── PythonBackupService.py     # Windows service
├── CodeIWantToRun.py          # Example executable
├── Data.json                  # Saved source/destination paths
├── backup_sessions.sqlite     # Backup history database
├── run_history.log            # CLI log
├── service.log                # Service log
├── README.md                  # Documentation
📣 Logging & History

Logs are saved to run_history.log and service.log
Backup history is stored in backup_sessions.sqlite
GUI displays the latest 50 sessions with:

User name
Device name
Folder name
Timestamp


<img width="922" height="732" alt="image" src="https://github.com/user-attachments/assets/cadaf1a4-bdc0-4cfb-a72d-bcc0448f130c" />
<img width="807" height="593" alt="image" src="https://github.com/user-attachments/assets/a91a9dfa-22f0-4d6f-b071-7c88272191e1" />
<img width="882" height="728" alt="image" src="https://github.com/user-attachments/assets/362d728d-1df3-44ac-8163-bb9b55d92daf" />
<img width="405" height="470" alt="image" src="https://github.com/user-attachments/assets/05274f31-d95f-42f7-ba81-557a6ad8af60" />

in last image you should write the username of your device and the password 

