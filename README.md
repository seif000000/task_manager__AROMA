# 🛡️ Python Backup System: A Professional IT Backup Solution for Windows

!

A comprehensive and robust solution for managing backups in IT environments. It features automated scheduling via a Windows service, manual control via a Command Line Interface (CLI), and interactive management through a Graphical User Interface (GUI).

## ✨ Key Features

* **✅ Reliable Automation:** Scheduled and reliable automated backups executed by a **Windows Service** (`PythonBackupService.py`).
* **💻 Full CLI Control:** A command-line tool (`backup_cli.py`) for running immediate manual backups, optionally followed by file execution.
* **🖥️ Interactive GUI:** A `backup_gui.py` application with an **Arabic interface** for managing settings and viewing history.
* **🗂️ Backup History:** All backup sessions are stored in a local **SQLite** database (`backup_sessions.sqlite`) for easy tracking and auditing.
* **🌐 Arabic Support:** The GUI is specifically designed with an Arabic interface and intuitive controls.

---

## 📦 Installation and Setup

This project requires external packages for managing the Windows service and creating the GUI.

### Prerequisites

Ensure you have **Python 3.x** installed.

### Installing Dependencies

Run the following command to install the necessary packages:


pip install pywin32 ttkbootstrap

⚙️ Windows Service: PythonBackupService.py
This utility allows you to install, start, and manage the service responsible for scheduled and automated backups.


Action                                 	Command                                            Description
🔧 Install the Service	        python PythonBackupService.py         install	Registers the service with the Windows operating system.
▶️ Start the Service	          python PythonBackupService.py           start	Starts the service for automatic backup execution.
⏹️ Stop the Service	python      PythonBackupService.py stop	      Pauses the service operation.
❌ Remove the Service	python    PythonBackupService.py remove	  Unregisters and removes the service from the system.


🔍 Check Service Status
You can check the status of the PythonBackupService using two options:

1. Via the Services App (services.msc):

Open services.msc from the Start menu.

Find PythonBackupService.

Check the status (Running or Stopped) and manage it via right-click.

2. Via Command Prompt (CMD):

   sc query PythonBackupService
   If running: STATE : 4 RUNNING
   If stopped: STATE : 1 STOPPED

   
💻 CLI Tool: backup_cli.py
Allows you to run immediate manual backup operations, with an option to execute an external file after the backup completes.

Option	                             Command                              	Description
🔹 Copy Only	           python backup_cli.py -c	                           Performs the backup of the configured folders only.
🔹 Copy + Run File	     python backup_cli.py -r [FILE_TO_EXECUTE]	         Performs the backup then executes the specified file from the backup destination.


Example Usage
To run a backup followed by the execution of a deployment script (deploy.bat):
python backup_cli.py -r deploy.bat

💡 Note: The file to be executed can be an .exe, .bat, .py, etc. It will be executed directly from the backup destination path.****


🖥️ GUI Application: backup_gui.py
The graphical application provides an interactive, Arabic-language administrative interface.

Launch the Application
python backup_gui.py

GUI Features


Path Configuration: Browse and save source and destination folders easily.

Instant Start: Initiate a "Backup Only" or "Backup + Run File" operation directly from the interface.

Live History: View and auto-refresh the latest 50 backup sessions.

Direct Access: Button to open the backup destination folder directly.


📣 Logging & History
Operational information and session logs are saved to files and a database for easy review and auditing.


Component	            File/Database	                         Content
CLI Log	              run_history.log	          Log of manual backup operations executed via the CLI.
Service Log	           service.log	          Log of scheduled and automated operations run by the Windows Service.
Sessions History	  backup_sessions.sqlite	   Database storing a detailed record of all backup sessions.
Configuration	          Data.json	             File for storing saved source and destination paths.

Session History Details (Displayed in GUI)
The GUI displays the latest 50 sessions, including:

User Name

Device Name

Folder Name

Timestamp


🗂️ Project Structure (After Running)
This structure shows the main project files after initial execution (when log files and the database are created):

├── backup_cli.py           # CLI tool for manual operations
├── backup_core.py          # Core logic and backup functions
├── backup_gui.py           # GUI application
├── PythonBackupService.py  # Windows service code
├── CodeIWantToRun.py       # Example executable file
├── Data.json               # Saved source/destination paths configuration
├── backup_sessions.sqlite  # Backup history database
├── run_history.log         # CLI log file
├── service.log             # Service log file
└── README.md               # This documentation file

<img width="922" height="732" alt="image" src="https://github.com/user-attachments/assets/cadaf1a4-bdc0-4cfb-a72d-bcc0448f130c" />
<img width="807" height="593" alt="image" src="https://github.com/user-attachments/assets/a91a9dfa-22f0-4d6f-b071-7c88272191e1" />
<img width="882" height="728" alt="image" src="https://github.com/user-attachments/assets/362d728d-1df3-44ac-8163-bb9b55d92daf" />
<img width="405" height="470" alt="image" src="https://github.com/user-attachments/assets/05274f31-d95f-42f7-ba81-557a6ad8af60" />

in last image you should write the username of your device and the password 



