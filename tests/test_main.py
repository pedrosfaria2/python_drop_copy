import unittest
from unittest.mock import patch, mock_open, MagicMock
import yaml
import configparser

from src.fix_client import FIXClient
from src.fix_application import FIXApplication
from main import load_clients

class TestLoadClients(unittest.TestCase):
    
    @patch("builtins.open", new_callable=mock_open, read_data="""
    sessions:
      - config_file: "config1.cfg"
      - config_file: "config2.cfg"
    """)
    @patch("yaml.safe_load", return_value={
        "sessions": [
            {"config_file": "config1.cfg"},
            {"config_file": "config2.cfg"}
        ]
    })
    @patch("configparser.ConfigParser.read", return_value=None)
    @patch("configparser.ConfigParser.__getitem__", return_value={
        "RawData": "test_raw_data"
    })
    @patch("src.fix_client.FIXClient.__init__", return_value=None)
    def test_load_clients(self, mock_init, mock_getitem, mock_read, mock_safe_load, mock_open):
        clients = load_clients("config.yaml")
        self.assertEqual(len(clients), 2)
        mock_init.assert_called()

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load", side_effect=yaml.YAMLError("Error parsing YAML"))
    def test_load_clients_yaml_error(self, mock_safe_load, mock_open):
        clients = load_clients("config.yaml")
        self.assertEqual(len(clients), 0)
        mock_safe_load.assert_called()
    
    @patch("builtins.open", new_callable=mock_open, read_data="""
    sessions:
      - config_file: "config1.cfg"
    """)
    @patch("yaml.safe_load", return_value={
        "sessions": [
            {"config_file": "config1.cfg"}
        ]
    })
    @patch("configparser.ConfigParser.read", return_value=None)
    @patch("configparser.ConfigParser.__getitem__", side_effect=KeyError("RawData"))
    def test_load_clients_key_error(self, mock_getitem, mock_read, mock_safe_load, mock_open):
        clients = load_clients("config.yaml")
        self.assertEqual(len(clients), 0)
        mock_getitem.assert_called()

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load", return_value={
        "sessions": [
            {"config_file": "nonexistent.cfg"}
        ]
    })
    @patch("configparser.ConfigParser.read", side_effect=FileNotFoundError)
    def test_load_clients_file_not_found(self, mock_read, mock_safe_load, mock_open):
        clients = load_clients("config.yaml")
        self.assertEqual(len(clients), 0)
        mock_read.assert_called()

if __name__ == "__main__":
    unittest.main()
