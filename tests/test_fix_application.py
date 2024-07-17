import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
import quickfix as fix
from src.fix_application import FIXApplication

class TestFIXApplication(unittest.TestCase):

    @patch('src.fix_application.logging.getLogger')
    @patch('src.fix_application.datetime')
    @patch('src.fix_application.os.makedirs')
    def setUp(self, mock_makedirs, mock_datetime, mock_getLogger):
        mock_datetime.now.return_value = datetime(2024, 7, 17)
        mock_getLogger.return_value = MagicMock()
        self.raw_data = "test_raw_data"
        self.app = FIXApplication(self.raw_data)

    def test_format_fix_message(self):
        message = MagicMock()
        message.toString.return_value = "8=FIX.4.4\x019=102\x01"
        formatted_message = self.app.format_fix_message(message)
        self.assertEqual(formatted_message, "8=FIX.4.4 | 9=102")

    def test_onCreate(self):
        sessionID = fix.SessionID("FIX.4.4", "SENDER", "TARGET")
        self.app.onCreate(sessionID)
        self.app.logger.info.assert_called_with(f'Session created: {sessionID}')

    def test_onLogon(self):
        sessionID = fix.SessionID("FIX.4.4", "SENDER", "TARGET")
        self.app.onLogon(sessionID)
        self.app.logger.info.assert_called_with(f'Successful logon to session {sessionID}')

    def test_onLogout(self):
        sessionID = fix.SessionID("FIX.4.4", "SENDER", "TARGET")
        self.app.onLogout(sessionID)
        self.app.logger.info.assert_called_with(f'Successful logout from session {sessionID}')

    def test_fromAdmin(self):
        message = MagicMock()
        sessionID = fix.SessionID("FIX.4.4", "SENDER", "TARGET")
        self.app.fromAdmin(message, sessionID)
        self.app.logger.debug.assert_called()

    def test_toApp(self):
        message = MagicMock()
        sessionID = fix.SessionID("FIX.4.4", "SENDER", "TARGET")
        self.app.toApp(message, sessionID)
        self.app.logger.debug.assert_called()

    def test_fromApp(self):
        message = MagicMock()
        msgType = fix.MsgType(fix.MsgType_ExecutionReport)
        message.getHeader.return_value.getField.return_value = msgType
        sessionID = fix.SessionID("FIX.4.4", "SENDER", "TARGET")
        self.app.fromApp(message, sessionID)
        self.app.logger.info.assert_called()

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_log_message_raw(self, mock_open):
        message = MagicMock()
        message.toString.return_value = "8=FIX.4.4\x019=102\x01"
        
        # Mock the session_message_log and communal_message_log to use mock_open
        self.app.session_message_log = mock_open.return_value
        self.app.communal_message_log = mock_open.return_value
        
        self.app.log_message_raw(message)
        mock_open().write.assert_any_call("8=FIX.4.4\x019=102\x01\n")
        mock_open().flush.assert_any_call()
        
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_log_to_file(self, mock_open):
        message = "Test log message"
        self.app.log_to_file(message)
        mock_open().write.assert_called_with("Test log message\n")

if __name__ == '__main__':
    unittest.main()
