
# FIX Client Drop Copy

This project is a FIX (Financial Information Exchange) client application designed for drop copy functionalities. It utilizes the QuickFIX library for handling FIX messages and provides a user-friendly interface for interacting with the client, sending ResendRequests, managing log files, and handling secondary hosts for disaster recovery.

## Features

- Logon and logout clients.
- Send ResendRequest messages to clients.
- Handle secondary hosts for disaster recovery.
- Consolidate log files.
- User-friendly command-line interface using the Rich library.

## Requirements

- Python 3.8+
- QuickFIX
- Rich

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/pedrosfaria2/python_drop_copy.git
    cd python_drop_copy
    ```

2. Configure your FIX sessions in `config.yaml` and `config.cfg`.

## Configuration

### `config.yaml`

This YAML file defines the sessions and their respective configuration files.

```yaml
sessions:
  - config_file: "path/to/your/fix1.cfg"
  - config_file: "path/to/your/fix2.cfg"
  # Add more sessions as needed
```

### `config.cfg`

This is an example of a session configuration file.

```ini
[DEFAULT]
ConnectionType=initiator
ReconnectInterval=60
FileStorePath=store
FileLogPath=log
StartTime=00:00:00
EndTime=00:00:00
UseDataDictionary=Y
DataDictionary=data/FIX44.xml
ResetOnLogon=Y
ResetOnLogout=Y

[SESSION]
BeginString=FIX.4.4
TargetCompID=ABCDE1234
SenderCompID=FGHYJ6789
RawData=password
HeartBtInt=30
SocketConnectPort=port
SocketConnectHostPrimary=primary_ipAddress
SocketConnectHostSecondary=secondary_ipAddress
EncryptMethod=0
RawDataLength=len(RawData)
ResetSeqNumFlag=Y
```

## Usage

1. Run the main script:

    ```sh
    python main.py
    ```

2. Follow the on-screen instructions to logon, send ResendRequests, and logout.

## Project Structure

```plaintext
python_drop_copy
├── src/
│   ├── fix_application.py
│   ├── fix_client.py
│   ├── menu.py
│   ├── fix_field.py
│   ├── fix_message.py
├── config.yaml
├── config.cfg
├── main.py
└── tests/
    ├── test_fix_application.py
    ├── test_fix_client.py
    ├── test_main.py
```

## Testing

Unit tests are included. To run the tests, use the following command:

```sh
pytest
```

## Scripts

### `main.py`

This is the entry point of the application. It loads the client configurations and displays the main menu.

### `src/fix_application.py`

Defines the `FIXApplication` class, which handles FIX message events and logging.

### `src/fix_client.py`

Defines the `FIXClient` class, which manages the FIX session, sends messages, and handles secondary hosts for disaster recovery.

### `src/menu.py`

Handles the user interface and interactions using the Rich library.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [QuickFIX](http://www.quickfixengine.org/) - The FIX protocol engine.
- [Rich](https://github.com/Textualize/rich) - Python library for rich text and beautiful formatting in the terminal.
