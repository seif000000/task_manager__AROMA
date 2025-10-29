
import os
import shutil
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
import logging


from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_JSON = os.path.join(BASE_DIR, "Data.json")
DB_PATH = os.path.join(BASE_DIR, "backup_sessions.sqlite")
LOCK_PATH = os.path.join(BASE_DIR, "backup.lock")
SERVICE_LOG = os.path.join(BASE_DIR, "service.log")
CLI_LOG = os.path.join(BASE_DIR, "run_history.log")
COPY_RETRY_SLEEP = 1  # seconds (used internally if wanted)

logging.basicConfig(
    filename=SERVICE_LOG,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

cli_logger = logging.getLogger("cli_logger")
cli_handler = logging.FileHandler(CLI_LOG)
cli_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
cli_handler.setFormatter(cli_formatter)
cli_logger.addHandler(cli_handler)
cli_logger.setLevel(logging.INFO)

Base = declarative_base()

class CopySession(Base):
    __tablename__ = "copy_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    current_user = Column(String, nullable=False)
    device_name = Column(String)
    folder_name = Column(String, nullable=False)
    source_path = Column(String, nullable=False)
    destination_path = Column(String, nullable=False)
    copied_at = Column(DateTime)

_engine = None
_Session = None

def init_db():
    global _engine, _Session
    if _engine is None:
        sqlite_url = f"sqlite:///{DB_PATH}"
        _engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(_engine)
        _Session = sessionmaker(bind=_engine)
    return _Session()

def read_data_json():
    try:
        with open(DATA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            source = data.get("source", "").strip()
            destination = data.get("destination", "").strip()
            return source, destination
    except FileNotFoundError:
        logging.error("Data.json not found.")
        return "", ""
    except Exception as e:
        logging.error(f"Error reading Data.json: {e}")
        return "", ""

def files_are_different(src, dst):
    try:
        with open(src, "rb") as f1, open(dst, "rb") as f2:
            return f1.read() != f2.read()
    except Exception:

        return True

def copy_folder(source, destination):
    """
    Recursive copy: copies files and folders from source -> destination.
    Uses copy2 to preserve metadata.
    """
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source path does not exist: {source}")

    os.makedirs(destination, exist_ok=True)

    for item in os.listdir(source):
        src_path = os.path.join(source, item)
        dst_path = os.path.join(destination, item)
        try:
            if os.path.isdir(src_path):
                copy_folder(src_path, dst_path)
            else:
                # file
                if not os.path.exists(dst_path) or files_are_different(src_path, dst_path):
                    shutil.copy2(src_path, dst_path)
        except Exception as e:
            logging.error(f"Error copying {src_path} -> {dst_path}: {e}")
            # continue with other files


def acquire_lock():
    """
    Try to create a lock file atomically.
    Return True if lock acquired, False if already locked.
    """
    try:
        fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"pid:{os.getpid()} time:{datetime.now().isoformat()}\n")
        return True
    except FileExistsError:
        return False
    except Exception as e:
        logging.error(f"Error acquiring lock: {e}")
        return False

def release_lock():
    try:
        if os.path.exists(LOCK_PATH):
            os.remove(LOCK_PATH)
    except Exception as e:
        logging.error(f"Error releasing lock: {e}")

def log_copy_session_to_db(source, destination):
    try:
        session = init_db()
        device_name = os.getenv("COMPUTERNAME") or os.getenv("HOSTNAME") or ""
        record = CopySession(
            current_user=os.getenv("USERNAME") or "unknown_user",
            device_name=device_name,
            folder_name=os.path.basename(os.path.normpath(source)),
            source_path=source,
            destination_path=destination,
            copied_at=datetime.now()
        )
        session.add(record)
        session.commit()
        session.close()
    except Exception as e:
        logging.error(f"Error logging to DB: {e}")

def run_backup(verbose=False):
    """
    Main function to run a single backup operation.
    Returns True on success, False on fail or if skipped due to lock.
    """
    if not acquire_lock():
        msg = "Backup skipped: another backup is running (lock present)."
        logging.info(msg)
        if verbose:
            cli_logger.info(msg)
        return False

    try:
        source, destination = read_data_json()
        if not source or not destination:
            msg = "Backup aborted: source or destination missing in Data.json"
            logging.error(msg)
            if verbose:
                cli_logger.error(msg)
            return False

        if os.path.abspath(source) == os.path.abspath(destination):
            msg = "Backup aborted: source and destination are the same."
            logging.error(msg)
            if verbose:
                cli_logger.error(msg)
            return False

        # Ensure source exists
        if not os.path.exists(source):
            msg = f"Backup aborted: source does not exist: {source}"
            logging.error(msg)
            if verbose:
                cli_logger.error(msg)
            return False

        # Create destination if needed
        os.makedirs(destination, exist_ok=True)

        logging.info(f"Starting backup: {source} -> {destination}")
        if verbose:
            cli_logger.info(f"Starting backup: {source} -> {destination}")

        # If destination empty copy tree else copy selectively
        try:
            # Use copy_folder for recursive copy
            copy_folder(source, destination)
        except Exception as e:
            logging.error(f"Error during copy_folder: {e}")
            if verbose:
                cli_logger.error(f"Error during copy_folder: {e}")
            return False


        try:
            log_copy_session_to_db(source, destination)
        except Exception as e:
            logging.error(f"Error logging to DB after backup: {e}")

        logging.info("Backup finished successfully.")
        if verbose:
            cli_logger.info("Backup finished successfully.")
        return True
    finally:
        release_lock()

def run_exe(filename, verbose=False):
    """
    filename: the name provided by user ('slack', 'slack.exe', 'run.bat', 'script.py')
    i'll search for this file inside the destination directory and if found run it.
    Returns True if process started, False otherwise.
    """
    source, destination = read_data_json()
    if not destination:
        msg = "run_exe aborted: destination not configured."
        logging.error(msg)
        if verbose:
            cli_logger.error(msg)
        return False

    candidates = []

    if os.path.isabs(filename):
        candidates.append(filename)
    else:
        target = os.path.join(destination, filename)
        candidates.append(target)
        name, ext = os.path.splitext(filename)
        if ext == "":
            for e in [".exe", ".bat", ".cmd", ".py", ".vbs"]:
                candidates.append(os.path.join(destination, filename + e))

        for root, _, files in os.walk(destination):
            for f in files:
                if f.lower() == filename.lower() or os.path.splitext(f)[0].lower() == filename.lower():
                    candidates.append(os.path.join(root, f))

    seen = set()
    existings = []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            if os.path.exists(c):
                existings.append(c)

    if not existings:
        msg = f"run_exe: file not found in destination: {filename}"
        logging.error(msg)
        if verbose:
            cli_logger.error(msg)
        return False

    exe_path = existings[0]
    try:
        logging.info(f"Running file: {exe_path}")
        if verbose:
            cli_logger.info(f"Running file: {exe_path}")

        ext = os.path.splitext(exe_path)[1].lower()
        if ext in [".bat", ".cmd"]:
            proc = subprocess.Popen(exe_path, shell=True, cwd=os.path.dirname(exe_path))
        elif ext == ".py":
            proc = subprocess.Popen([os.sys.executable, exe_path], cwd=os.path.dirname(exe_path))
        else:
            proc = subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
        return True
    except Exception as e:
        logging.error(f"Error running file {exe_path}: {e}")
        if verbose:
            cli_logger.error(f"Error running file {exe_path}: {e}")
        return False
