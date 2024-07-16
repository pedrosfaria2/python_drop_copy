import yaml
import configparser
from src.fix_client import FIXClient
from src.fix_application import FIXApplication
from src.menu import main_menu
from typing import List

def load_clients(config_path: str) -> List[FIXClient]:
    """
    Load FIX clients based on the provided configuration file.

    Args:
        config_path (str): Path to the YAML configuration file.

    Returns:
        List[FIXClient]: List of FIXClient instances.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    clients = []
    for session in config['sessions']:
        config_file = session['config_file']
        
        # Load raw_data directly from the configuration file
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file)
        raw_data = config_parser['SESSION']['RawData']
        
        application = FIXApplication(raw_data)
        client = FIXClient(config_file, application)
        clients.append(client)
    
    return clients

def main() -> None:
    """
    Main function to initialize and start the FIX clients.
    """
    config_path = "config.yaml"
    clients = load_clients(config_path)
    main_menu(*clients)

if __name__ == "__main__":
    main()
