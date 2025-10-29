import win32serviceutil
import win32service
import win32event
import servicemanager
import threading
import time
import logging
import os
import subprocess

class PythonBackupService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PythonBackupService"
    _svc_display_name_ = "Python Backup Service"
    _svc_description_ = "A Python Windows Service that runs backup every 1 minute."

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

        # Logging
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(base_dir, "service.log")
        logging.basicConfig(filename=log_path, level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")

        self.script_path = os.path.join(base_dir, "CodeIWantToRun.py")

    def SvcDoRun(self):
        logging.info("Service started.")
        self.thread = threading.Thread(target=self.run_main_loop)
        self.thread.start()
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

    def run_main_loop(self):
        while self.running:
            try:
                from CodeIWantToRun import main
                main()
                logging.info("Backup executed successfully.")
            except Exception as e:
                logging.error(f"Execution error: {e}")

            time.sleep(60)

    def SvcStop(self):
        logging.info("Service stopping...")
        self.running = False
        win32event.SetEvent(self.stop_event)
        logging.info("Service stopped.")

if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(PythonBackupService)
    