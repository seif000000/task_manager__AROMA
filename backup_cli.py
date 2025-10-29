import argparse
import sys
import os
from backup_core import run_backup, run_exe, cli_logger

def main():
    parser = argparse.ArgumentParser(description="Manual backup tool (IT). Options: -c (copy only), -r <file> (copy + run file).")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", action="store_true", help="Run backup once (copy only).")
    group.add_argument("-r", metavar="FILE", help="Run backup once, then run FILE from destination (FILE can be exe, bat, py, etc.).")

    args = parser.parse_args()

    verbose = True
    cli_logger.info(f"CLI started with args: {sys.argv[1:]}")

    cli_logger.info("CLI: Starting backup (manual)...")
    ok = run_backup(verbose=verbose)
    if not ok:
        cli_logger.error("CLI: Backup did not complete (skipped or failed). Exiting.")
        print("Backup skipped or failed. Check logs.")
        return 1

    cli_logger.info("CLI: Backup completed successfully.")

    if args.r:
        filename = args.r
        cli_logger.info(f"CLI: Attempting to run: {filename}")
        ok_run = run_exe(filename, verbose=verbose)
        if ok_run:
            cli_logger.info(f"CLI: Successfully started {filename}")
            print(f"Started {filename}")
        else:
            cli_logger.error(f"CLI: Failed to start {filename}")
            print(f"Failed to start {filename}. Check logs.")
            return 2
    else:
        cli_logger.info("CLI: -c specified (copy only). No run requested.")
        print("Backup completed (copy only).")

    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
