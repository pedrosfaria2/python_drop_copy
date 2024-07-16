# main.py
import yaml
from src.fix_client import FIXClient
from src.fix_application import FIXApplication
from src.menu import main_menu
import quickfix as fix
import configparser

def main():
    with open("config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    
    clients = []
    for session in config['sessions']:
        config_file = session['config_file']
        
        # Carregar o raw_data diretamente do arquivo de configuração
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file)
        raw_data = config_parser['SESSION']['RawData']
        
        application = FIXApplication(raw_data)
        client = FIXClient(config_file, application)
        clients.append(client)
    
    main_menu(*clients)

if __name__ == "__main__":
    main()
