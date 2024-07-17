import yaml
import configparser
import logging
from src.fix_client import FIXClient
from src.fix_application import FIXApplication
from src.menu import main_menu
from typing import List, Optional

# Configure the logger
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def load_clients(config_path: str) -> List[FIXClient]:
    """
    Load FIX clients based on the provided configuration file.

    Args:
        config_path (str): Path to the YAML configuration file.

    Returns:
        List[FIXClient]: List of FIXClient instances.
    """
    clients = []
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        logging.error(f"Configuration file {config_path} not found.")
        return clients
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML configuration: {e}")
        return clients

    for session in config.get('sessions', []):
        config_file = session.get('config_file')
        if not config_file:
            logging.warning("No config_file found for a session in the configuration.")
            continue

        try:
            # Load raw_data directly from the configuration file
            config_parser = configparser.ConfigParser()
            config_parser.read(config_file)
            raw_data = config_parser['SESSION']['RawData']
        except FileNotFoundError:
            logging.error(f"Config file {config_file} not found.")
            continue
        except KeyError as e:
            logging.error(f"Key error in config file {config_file}: {e}")
            continue
        except configparser.Error as e:
            logging.error(f"ConfigParser error reading {config_file}: {e}")
            continue

        try:
            application = FIXApplication(raw_data)
            client = FIXClient(config_file, application)
            clients.append(client)
        except Exception as e:
            logging.error(f"Error creating FIXClient for config file {config_file}: {e}")

    return clients

def main() -> None:
    """
    Main function to initialize and start the FIX clients.
    """
    config_path = "config.yaml"
    clients = load_clients(config_path)
    if not clients:
        logging.error("No clients loaded. Exiting.")
        return

    try:
        main_menu(*clients)
    except Exception as e:
        logging.error(f"An error occurred in the main menu: {e}")

if __name__ == "__main__":
    main()
