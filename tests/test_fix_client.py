import pytest
import configparser
from unittest.mock import MagicMock, patch
from src.fix_client import FIXClient
from src.fix_application import FIXApplication
import quickfix as fix

@pytest.fixture
def config_file(tmp_path):
    d = tmp_path / "config"
    d.mkdir()
    config_file = d / "config.cfg"
    config_file.write_text("""
[SESSION]
BeginString=FIX.4.4
SenderCompID=TEST_CLIENT
TargetCompID=TEST_SERVER
SocketConnectHostPrimary=127.0.0.1
SocketConnectHostSecondary=127.0.0.2
SocketConnectPort=5000
ConnectionType=initiator
""")
    return config_file

@pytest.fixture
def mock_fix_application():
    return MagicMock(spec=FIXApplication)

def test_initialize_settings(config_file, mock_fix_application):
    client = FIXClient(str(config_file), mock_fix_application)
    assert client.settings is not None
    assert client.storeFactory is not None
    assert client.logFactory is not None
    assert client.session_id is not None

def test_logon_primary_host(config_file, mock_fix_application):
    client = FIXClient(str(config_file), mock_fix_application)
    client._try_logon = MagicMock(return_value=True)
    with patch.object(client, '_get_hosts', return_value=("127.0.0.1", "127.0.0.2")):
        client.logon()
    client._try_logon.assert_called_with("127.0.0.1")

def test_logon_secondary_host(config_file, mock_fix_application):
    client = FIXClient(str(config_file), mock_fix_application)
    client._try_logon = MagicMock(side_effect=[False, True])
    with patch.object(client, '_get_hosts', return_value=("127.0.0.1", "127.0.0.2")):
        client.logon()
    client._try_logon.assert_any_call("127.0.0.1")
    client._try_logon.assert_any_call("127.0.0.2")

def test_logon_failure(config_file, mock_fix_application):
    client = FIXClient(str(config_file), mock_fix_application)
    client._try_logon = MagicMock(return_value=False)
    with patch.object(client, '_get_hosts', return_value=("127.0.0.1", "127.0.0.2")), pytest.raises(RuntimeError, match="Logon failed for both primary and secondary hosts."):
        client.logon()

def test_send_resend_request(config_file, mock_fix_application):
    client = FIXClient(str(config_file), mock_fix_application)
    client._send_message = MagicMock()
    client.send_resend_request(1, 1000)
    client._send_message.assert_called_once()
    args, _ = client._send_message.call_args
    message = args[0]
    assert message.getHeader().getField(fix.MsgType().getField()) == fix.MsgType_ResendRequest

def test_set_socket_connect_host(config_file, mock_fix_application):
    client = FIXClient(str(config_file), mock_fix_application)
    client._set_socket_connect_host("127.0.0.3")
    session_settings = client.settings.get(client.session_id)
    assert session_settings.getString("SocketConnectHost") == "127.0.0.3"
