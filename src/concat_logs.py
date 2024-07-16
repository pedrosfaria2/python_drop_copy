import os
import time
import logging
import glob
import configparser
from datetime import datetime

running = True

def setup_logger():
    log_date = datetime.now().strftime("%Y-%m-%d")
    log_filename = f"human_readable_logs/{log_date}_consolidation.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    logging.basicConfig(filename=log_filename,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_log_directory_from_cfg(cfg_file):
    config = configparser.ConfigParser()
    config.read(cfg_file)
    return config['DEFAULT'].get('FileLogPath', 'log')

def consolidate_logs():
    if not running:
        return

    # Obter o caminho do diretório de logs do arquivo .cfg
    cfg_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.cfg')
    log_directory = get_log_directory_from_cfg(cfg_file)

    logging.info(f"Looking for log files in directory: {log_directory}")

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    consolidated_log_file = os.path.join(log_directory, "consolidated_log.log")

    log_files = glob.glob(os.path.join(log_directory, '*messages.current.log'))

    logging.info(f"Found {len(log_files)} log files to consolidate.")

    if not log_files:
        logging.warning("No log files found to consolidate.")
        return

    def line_filter(line):
        return 'CNOV0012' not in line and '35=0' not in line

    with open(consolidated_log_file, 'w') as consolidated_file:
        for log_file in log_files:
            try:
                with open(log_file, 'r') as current_file:
                    for line in current_file:
                        if line_filter(line):
                            consolidated_file.write(line)
                logging.info(f"Consolidated {log_file}")
            except Exception as e:
                logging.error(f"Error processing file {log_file}: {e}")

interval = 5

if __name__ == "__main__":
    setup_logger()
    try:
        while running:
            consolidate_logs()
            time.sleep(interval)
    except KeyboardInterrupt:
        running = False
        logging.info("Log consolidation interrupted and stopped.")
